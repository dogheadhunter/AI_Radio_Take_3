"""
Script auditor for quality validation.

Uses a separate LLM to evaluate generated scripts
and flag those that don't meet quality standards.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from src.ai_radio.generation import llm_client
from src.ai_radio.generation.llm_client import LLMClient  # keep class for typing
from src.ai_radio.generation.voice_samples import format_voice_samples

# Criterion weights for computing overall score (Option B: weights in code)
WEIGHTS = {
    "character_voice": 0.30,
    "era_appropriateness": 0.25,
    "forbidden_elements": 0.20,
    "natural_flow": 0.15,
    "length": 0.10,
}

def _get_criterion_value(criteria: Dict[str, Any], key: str) -> float:
    """Robust extraction handling key variations (character_voice vs character-voice)."""
    variants = [key, key.replace("_", "-"), key.replace("-", "_")]
    for variant in variants:
        if variant in criteria:
            return float(criteria[variant])
    return 1.0  # Default fail score if missing


@dataclass
class AuditResult:
    """Result of auditing a single script."""
    script_id: str
    script_path: Optional[Path]
    dj: str
    content_type: str
    score: float
    passed: bool
    criteria_scores: Dict[str, float]
    issues: List[str]
    notes: str
    raw_response: str  # For debugging


def _build_time_audit_prompt(script_content: str, dj: str) -> str:
    """Audit prompt for time announcements with voice samples for comparison."""
    from src.ai_radio.generation.voice_samples import format_voice_samples
    
    voice_samples = format_voice_samples(dj)
    dj_name = "Julie" if dj.lower() == "julie" else "Mr. New Vegas"
    
    prompt = f"""You are auditing a radio DJ time announcement. Score each criterion 1-10.

HOW {dj_name.upper()} SOUNDS (reference samples):
{voice_samples}

SCRIPT TO EVALUATE:
"{script_content}"

SCORING CRITERIA (1-10 each, where 10=perfect, 7=good, 4=poor):
1. character_voice: Does script sound like the voice samples above?
2. natural_flow: Does it sound natural and conversational?
3. brevity: Is it appropriately short? (1-2 sentences is GOOD=8-10, 3 sentences is OK=6-7)

Respond with ONLY this JSON format:
{{"criteria_scores": {{"character_voice": N, "natural_flow": N, "brevity": N}}, "notes": "brief summary"}}"""
    
    return prompt


def _build_weather_audit_prompt(script_content: str, dj: str) -> str:
    """Audit prompt for weather announcements with voice samples for comparison."""
    from src.ai_radio.generation.voice_samples import format_voice_samples
    
    voice_samples = format_voice_samples(dj)
    dj_name = "Julie" if dj.lower() == "julie" else "Mr. New Vegas"
    
    prompt = f"""You are auditing a radio DJ weather announcement. Score each criterion 1-10.

HOW {dj_name.upper()} SOUNDS (reference samples):
{voice_samples}

SCRIPT TO EVALUATE:
"{script_content}"

SCORING CRITERIA (1-10 each, where 10=perfect, 7=good, 4=poor):
1. character_voice: Does script sound like the voice samples above?
2. natural_flow: Does it sound natural and conversational?
3. length: Is it appropriate length? (2-3 sentences is GOOD=8-10)
4. subtlety: Does it avoid post-apocalyptic words? (radiation, nuclear, fallout, wasteland, vault, mutant = score 3 or less)

Respond with ONLY this JSON format:
{{"criteria_scores": {{"character_voice": N, "natural_flow": N, "length": N, "subtlety": N}}, "notes": "brief summary"}}"""
    
    return prompt


def _build_song_intro_audit_prompt(script_content: str, dj: str, song_title: str = "", artist: str = "", lyrics: str = "") -> str:
    """Compact audit prompt for song intros using voice samples + lyrics."""
    voice_samples = format_voice_samples(dj)
    dj_name = "Julie" if dj.lower() == "julie" else "Mr. New Vegas"
    
    # Truncate lyrics if too long (keep first ~500 chars for context)
    lyrics_section = ""
    if lyrics and lyrics.strip():
        truncated = lyrics[:500] + "..." if len(lyrics) > 500 else lyrics
        lyrics_section = f"\nSONG LYRICS:\n{truncated}\n"
    
    prompt = f"""You are auditing a radio DJ script. Score each criterion 1-10.

HOW {dj_name.upper()} SOUNDS (reference samples):
{voice_samples}

SONG INFO: "{song_title}" by {artist}{lyrics_section}
SCRIPT TO EVALUATE:
"{script_content}"

SCORING CRITERIA (1-10 each, where 10=perfect, 6-7=acceptable, 1-3=major fail):

1. character_voice: Does the script sound like the voice samples above? 
2. era_appropriateness: Uses 1950s language, no modern slang, no dates/years mentioned?
3. forbidden_elements: CLEAN=10, VIOLATIONS=1. Give 10 if NO emoji/no meta-commentary/no placeholders. Give 1-3 only if these appear.
4. natural_flow: Reads naturally, not too long (under 120 words)?
5. length: 1-5 sentences, must END with introducing the song (artist/title)?

IMPORTANT SCORING RULES:
- forbidden_elements: Default to 10 if script is clean. Only score low if emoji, "(note:...)", or [[placeholder]] text actually appears.
- If dates/years mentioned: era_appropriateness must be 3 or less  
- If text continues AFTER the song introduction: length must be 4 or less
- If script sounds too formal/flowery for Julie: character_voice must be 4 or less

Respond with ONLY this JSON format:
{{"criteria_scores": {{"character_voice": N, "era_appropriateness": N, "forbidden_elements": N, "natural_flow": N, "length": N}}, "issues": ["list any problems"], "notes": "brief summary"}}"""
    
    return prompt


def _build_song_outro_audit_prompt(script_content: str, dj: str, song_title: str = "", artist: str = "", lyrics: str = "") -> str:
    """Compact audit prompt for song outros using voice samples + lyrics."""
    voice_samples = format_voice_samples(dj)
    dj_name = "Julie" if dj.lower() == "julie" else "Mr. New Vegas"
    
    # Truncate lyrics if too long
    lyrics_section = ""
    if lyrics and lyrics.strip():
        truncated = lyrics[:500] + "..." if len(lyrics) > 500 else lyrics
        lyrics_section = f"\nSONG LYRICS:\n{truncated}\n"
    
    prompt = f"""You are auditing a radio DJ script. Score each criterion 1-10.

HOW {dj_name.upper()} SOUNDS (reference samples):
{voice_samples}

SONG THAT JUST FINISHED: "{song_title}" by {artist}{lyrics_section}
SCRIPT TO EVALUATE:
"{script_content}"

SCORING CRITERIA (1-10 each, where 10=perfect, 6-7=acceptable, 1-3=major fail):

1. character_voice: Does the script sound like the voice samples above?
2. era_appropriateness: Uses 1950s language, no modern slang, no dates/years mentioned?
3. forbidden_elements: CLEAN=10, VIOLATIONS=1. Give 10 if NO emoji/no meta-commentary/no placeholders. Give 1-3 only if these appear.
4. natural_flow: Reads naturally, not too long (under 80 words)?
5. past_tense_usage: Uses PAST tense? ("That was...", "Hope you enjoyed...") NOT present tense intro.

IMPORTANT SCORING RULES:
- forbidden_elements: Default to 10 if script is clean. Only score low if emoji, "(note:...)", or [[placeholder]] text actually appears.
- If uses present tense like "Here is..." or "This is...": past_tense_usage must be 3 or less
- If dates/years mentioned: era_appropriateness must be 3 or less

Respond with ONLY this JSON format:
{{"criteria_scores": {{"character_voice": N, "era_appropriateness": N, "forbidden_elements": N, "natural_flow": N, "past_tense_usage": N}}, "issues": ["list any problems"], "notes": "brief summary"}}"""
    
    return prompt


# Legacy wrappers for backward compatibility (no lyrics passed)
def _build_song_intro_audit_prompt_julie(script_content: str) -> str:
    return _build_song_intro_audit_prompt(script_content, "julie")

def _build_song_intro_audit_prompt_mr_new_vegas(script_content: str) -> str:
    return _build_song_intro_audit_prompt(script_content, "mr_new_vegas")

def _build_song_outro_audit_prompt_julie(script_content: str) -> str:
    return _build_song_outro_audit_prompt(script_content, "julie")

def _build_song_outro_audit_prompt_mr_new_vegas(script_content: str) -> str:
    return _build_song_outro_audit_prompt(script_content, "mr_new_vegas")


def _build_prompt(script_content: str, dj: str, content_type: str = "song_intro") -> str:
    # Time and weather announcements have simplified, separate prompts
    if content_type == "time_announcement":
        return _build_time_audit_prompt(script_content, dj)
    
    if content_type == "weather_announcement":
        return _build_weather_audit_prompt(script_content, dj)
    
    # Song intro/outro - use DJ-specific prompts
    if content_type == "song_intro":
        if dj.lower() == "julie":
            return _build_song_intro_audit_prompt_julie(script_content)
        else:  # mr_new_vegas
            return _build_song_intro_audit_prompt_mr_new_vegas(script_content)
    
    if content_type == "song_outro":
        if dj.lower() == "julie":
            return _build_song_outro_audit_prompt_julie(script_content)
        else:  # mr_new_vegas
            return _build_song_outro_audit_prompt_mr_new_vegas(script_content)
    
    # Fallback for unknown content types (shouldn't happen)
    raise ValueError(f"Unknown content type: {content_type}")


def audit_script(
    client: Optional[LLMClient],
    script_content: str,
    script_id: str,
    dj: str,
    content_type: str = "song_intro",
) -> AuditResult:
    """
    Audit a single script for quality.
    """
    prompt = _build_prompt(script_content, dj, content_type)
    raw = ""
    try:
        raw = llm_client.generate_text(client, prompt)
        parsed = json.loads(raw)

        criteria = parsed.get("criteria_scores", {})
        
        # Time announcements use simplified 3-criterion scoring
        if content_type == "time_announcement":
            time_criteria = ["character_voice", "natural_flow", "brevity"]
            criteria_scores = {}
            for key in time_criteria:
                criteria_scores[key] = _get_criterion_value(criteria, key)
            
            # Normalize if needed
            max_raw_score = max(criteria_scores.values()) if criteria_scores else 1.0
            if max_raw_score > 10:
                criteria_scores = {k: (v / 10.0) for k, v in criteria_scores.items()}
            
            # Clamp to 1-10
            criteria_scores = {k: max(1.0, min(10.0, v)) for k, v in criteria_scores.items()}
            
            # Simple average for time (all criteria equal weight)
            score = sum(criteria_scores.values()) / len(criteria_scores)
            passed = score >= 6.0  # Lower threshold for time (simpler content)
            
            issues = parsed.get("issues", []) or []
            notes = parsed.get("notes", "")
            
            return AuditResult(
                script_id=script_id,
                script_path=None,
                dj=dj,
                content_type=content_type,
                score=score,
                passed=passed,
                criteria_scores=criteria_scores,
                issues=issues,
                notes=notes,
                raw_response=raw
            )
        
        # Weather announcements use simplified 4-criterion scoring
        if content_type == "weather_announcement":
            weather_criteria = ["character_voice", "natural_flow", "length", "subtlety"]
            criteria_scores = {}
            for key in weather_criteria:
                criteria_scores[key] = _get_criterion_value(criteria, key)
            
            # Normalize if needed
            max_raw_score = max(criteria_scores.values()) if criteria_scores else 1.0
            if max_raw_score > 10:
                criteria_scores = {k: (v / 10.0) for k, v in criteria_scores.items()}
            
            # Clamp to 1-10
            criteria_scores = {k: max(1.0, min(10.0, v)) for k, v in criteria_scores.items()}
            
            # Simple average for weather (all criteria equal weight)
            score = sum(criteria_scores.values()) / len(criteria_scores)
            passed = score >= 6.5  # Slightly higher than time (includes weather content requirement)
            
            issues = parsed.get("issues", []) or []
            notes = parsed.get("notes", "")
            
            return AuditResult(
                script_id=script_id,
                script_path=None,
                dj=dj,
                content_type=content_type,
                score=score,
                passed=passed,
                criteria_scores=criteria_scores,
                issues=issues,
                notes=notes,
                raw_response=raw
            )
        
        # Song intro/outro use full 5-criterion scoring
        common_criteria = ["character_voice", "era_appropriateness", "forbidden_elements", "natural_flow"]
        
        # Content-type specific 5th criterion
        if content_type == "song_outro":
            fifth_criterion = "past_tense_usage"
        else:
            fifth_criterion = "length"
        
        # Robust extraction with key name variations
        criteria_scores = {}
        for key in common_criteria + [fifth_criterion]:
            criteria_scores[key] = _get_criterion_value(criteria, key)
        
        # Normalization: if LLM returned 0-100 scale, normalize to 1-10
        max_raw_score = max(criteria_scores.values())
        if max_raw_score > 10:
            criteria_scores = {k: (v / 10.0) for k, v in criteria_scores.items()}
        
        # Clamp to 1-10 range
        criteria_scores = {k: max(1.0, min(10.0, v)) for k, v in criteria_scores.items()}
        
        # Compute weighted average (Option B: weights in code)
        # Use same weights for both intro and outro (5th criterion gets 0.10 weight)
        score = sum(criteria_scores[k] * WEIGHTS[k] for k in common_criteria)
        score += criteria_scores[fifth_criterion] * 0.10  # 5th criterion weight
        score = max(1.0, min(10.0, score))
        passed = score >= 7.5

        issues = parsed.get("issues", []) or []
        notes = parsed.get("notes", "")

        return AuditResult(
            script_id=script_id,
            script_path=None,
            dj=dj,
            content_type=content_type,
            score=score,
            passed=passed,
            criteria_scores=criteria_scores,
            issues=issues,
            notes=notes,
            raw_response=raw
        )
    except json.JSONDecodeError:
        # Malformed JSON from auditor model
        return AuditResult(
            script_id=script_id,
            script_path=None,
            dj=dj,
            content_type=content_type,
            score=1.0,
            passed=False,
            criteria_scores={
                "character_voice": 1.0,
                "era_appropriateness": 1.0,
                "forbidden_elements": 1.0,
                "natural_flow": 1.0,
                "length": 1.0,
            },
            issues=["parse error: auditor returned non-JSON response"],
            notes="Parse error from auditor response",
            raw_response=raw,
        )
    except Exception as exc:
        # Any other failure should return a failed AuditResult
        return AuditResult(
            script_id=script_id,
            script_path=None,
            dj=dj,
            content_type=content_type,
            score=1.0,
            passed=False,
            criteria_scores={
                "character_voice": 1.0,
                "era_appropriateness": 1.0,
                "forbidden_elements": 1.0,
                "natural_flow": 1.0,
                "length": 1.0,
            },
            issues=[f"auditor error: {str(exc)}"],
            notes="Auditor failed to produce a valid response",
            raw_response=raw,
        )


def save_audit_result(result: AuditResult, output_dir: Path) -> Path:
    """Save audit result to appropriate folder (passed/failed)."""
    out_dir = output_dir / ("passed" if result.passed else "failed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{result.script_id}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "script_id": result.script_id,
            "dj": result.dj,
            "content_type": result.content_type,
            "score": result.score,
            "passed": result.passed,
            "criteria_scores": result.criteria_scores,
            "issues": result.issues,
            "notes": result.notes,
            "raw_response": result.raw_response,
        }, f, indent=2, ensure_ascii=False)

    return out_path


def audit_batch(
    scripts: List[Dict[str, Any]],
    output_dir: Path,
    client: Optional[LLMClient] = None,
    progress_callback: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    Audit a batch of scripts.
    Returns a summary dict with pass/fail counts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {"total": 0, "passed": 0, "failed": 0}

    for i, s in enumerate(scripts, 1):
        script_id = s.get("script_id")
        content = s.get("script_content", "")
        dj = s.get("dj", "")
        content_type = s.get("content_type", "song_intro")

        result = audit_script(client, content, script_id, dj, content_type)
        save_audit_result(result, output_dir)

        summary["total"] += 1
        if result.passed:
            summary["passed"] += 1
        else:
            summary["failed"] += 1

        if progress_callback:
            progress_callback(i, len(scripts), result)

    return summary


def load_audit_results(output_dir: Path) -> List[AuditResult]:
    """Load all audit results from a directory."""
    results: List[AuditResult] = []
    for sub in (output_dir / "passed", output_dir / "failed"):
        if not sub.exists():
            continue
        for p in sub.glob("*.json"):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append(
                AuditResult(
                    script_id=data.get("script_id"),
                    script_path=p,
                    dj=data.get("dj"),
                    content_type=data.get("content_type"),
                    score=float(data.get("score", 1)),
                    passed=bool(data.get("passed", False)),
                    criteria_scores=data.get("criteria_scores", {}),
                    issues=data.get("issues", []),
                    notes=data.get("notes", ""),
                    raw_response=data.get("raw_response", ""),
                )
            )
    return results
