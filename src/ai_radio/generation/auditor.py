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
    """Simplified audit prompt for time announcements only.
    
    Time announcements are simple - just check:
    1. Does it sound like the character?
    2. Is it brief and natural?
    """
    dj_desc = "Julie (casual, warm, friendly)" if dj.lower() == "julie" else "Mr. New Vegas (smooth, suave, polished)"
    
    prompt = f"""Evaluate this time announcement for {dj_desc}.

Script: "{script_content}"

Score these 3 criteria (1-10 each):
1. character_voice: Does it sound like {dj}? (casual/warm for Julie, smooth/suave for Mr. NV)
2. natural_flow: Does it sound natural and conversational?
3. brevity: Is it appropriately short (1-2 sentences)?

Respond with ONLY valid JSON:
{{"criteria_scores": {{"character_voice": <1-10>, "natural_flow": <1-10>, "brevity": <1-10>}}, "notes": "brief summary"}}"""
    
    return prompt


def _build_weather_audit_prompt(script_content: str, dj: str) -> str:
    """Simplified audit prompt for weather announcements.
    
    Weather announcements check:
    1. Character voice
    2. Natural flow
    3. Appropriate length (2-3 sentences)
    4. Mentions the weather
    """
    dj_desc = "Julie (casual, warm, friendly)" if dj.lower() == "julie" else "Mr. New Vegas (smooth, suave, polished)"
    
    prompt = f"""Evaluate this weather announcement for {dj_desc}.

Script: "{script_content}"

Score these 4 criteria (1-10 each):
1. character_voice: Does it sound like {dj}? (casual/warm for Julie, smooth/suave for Mr. NV)
2. natural_flow: Does it sound natural and conversational?
3. length: Is it appropriate length (2-3 sentences, ~20-60 words)?
4. weather_mention: Does it clearly describe weather conditions?

Respond with ONLY valid JSON:
{{"criteria_scores": {{"character_voice": <1-10>, "natural_flow": <1-10>, "length": <1-10>, "weather_mention": <1-10>}}, "notes": "brief summary"}}"""
    
    return prompt


def _build_song_intro_audit_prompt_julie(script_content: str) -> str:
    """Build audit prompt for Julie's song intros."""
    system = (
        "You are a script auditor for an AI radio station. Your job is to evaluate DJ scripts for character accuracy and quality.\n\n"
        "Character Reference: Julie\n"
        "- Voice: conversational, uses filler words, sometimes rambling.\n"
        "- Era: Modern American; avoid 1950s slang.\n"
        "- Tone: Warm, hopeful, friendly.\n"
        "- Typical patterns: longish sentences, friendly asides, filler words like 'you know' or 'right'.\n\n"
        "Evaluation Criteria for SONG INTRO (score each 1-10):\n"
        "1. character_voice: Does this sound like Julie? Should be casual/rambling/grounded with filler words. Generic DJ speak, flowery language, or overly polished = FAIL.\n"
        "2. era_appropriateness: Any anachronisms, modern slang, or DATES/YEARS mentioned? Check carefully.\n"
        "3. forbidden_elements: **CRITICAL** - ANY emoji, profanity, mean comments, meta-commentary in parentheses, placeholder text ('Artist 4'), dates/years ('1948 tune'), or TTS-breaking punctuation = automatic score of 1.\n"
        "4. natural_flow: Does it read naturally? Too long (>120 words), too flowery/elaborate, or rambling after song introduction = lower score.\n"
        "5. length: Appropriate length (1-3 optimal, 5 max sentences)? MUST end with song introduction (artist/title). Any text after song intro = FAIL.\n\n"
        "Scoring Scale (1-10 for each criterion):\n"
        "- 10: Perfect\n"
        "- 8-9: Strong\n"
        "- 6-7: Acceptable (PASS)\n"
        "- 4-5: Weak (FAIL)\n"
        "- 1-3: Major issues (FAIL)\n\n"
        "Pass Threshold: Overall weighted score >= 7.5 (calculated from individual criteria)\n\n"
        "**STRICT RULES FOR JULIE INTROS:**\n"
        "- If script contains ANY emoji (😀🎵❤️👍 etc.), forbidden_elements MUST = 1\n"
        "- If script has meta-commentary like '(1 sentence intro...)', forbidden_elements MUST = 1\n"
        "- If script has placeholder text like 'Artist 4' or 'Test Song', forbidden_elements MUST = 1\n"
        "- If script mentions dates/years (like '1948 tune', '1960s classic'), forbidden_elements MUST ≤ 3\n"
        "- If script has TTS-breaking punctuation (standalone '-', multiple '...', ',?'), forbidden_elements MUST ≤ 3\n"
        "- If script continues AFTER song introduction (artist/title), length MUST ≤ 4\n"
        "- If Julie uses flowery/elaborate language ('inimitable', 'tailor made', 'semblance of tranquility'), character_voice MUST ≤ 4\n"
        "- If Julie sounds formal/polished (like Mr. NV would), character_voice MUST ≤ 4\n"
        "- Generic radio clichés ('welcome back', 'like and subscribe') = era_appropriateness ≤ 4\n"
        "- If script is too long (>120 words), natural_flow MUST ≤ 6\n\n"
        "Instructions: Respond ONLY with valid JSON containing:\n"
        "{\n"
        "  \"criteria_scores\": {\"character_voice\": <1-10>, \"era_appropriateness\": <1-10>, \"forbidden_elements\": <1-10>, \"natural_flow\": <1-10>, \"length\": <1-10>},\n"
        "  \"issues\": [\"list specific problems if failing\"],\n"
        "  \"notes\": \"brief summary\"\n"
        "}\n\n"
        "DO NOT include 'score' or 'passed' in your JSON - they will be calculated from criteria_scores.\n"
    )
    
    user = f"Evaluate this song_intro script for Julie:\n---\n{script_content}\n---\n"
    return system + "\n" + user


def _build_song_intro_audit_prompt_mr_new_vegas(script_content: str) -> str:
    """Build audit prompt for Mr. New Vegas's song intros."""
    system = (
        "You are a script auditor for an AI radio station. Your job is to evaluate DJ scripts for character accuracy and quality.\n\n"
        "Character Reference: Mr. New Vegas\n"
        "- Voice: smooth, suave, romantic.\n"
        "- Era: 1950s Vegas lounge; avoid modern slang or emojis.\n"
        "- Tone: Intimate, sophisticated.\n"
        "- Typical patterns: short, polished sentences, romantic descriptors, references to lounge/city.\n\n"
        "Evaluation Criteria for SONG INTRO (score each 1-10):\n"
        "1. character_voice: Does this sound like Mr. New Vegas? Should be smooth/romantic/polished. Generic DJ speak, rambling, or casual filler words = FAIL.\n"
        "2. era_appropriateness: Any anachronisms, modern slang, or DATES/YEARS mentioned? Check carefully.\n"
        "3. forbidden_elements: **CRITICAL** - ANY emoji, profanity, mean comments, meta-commentary in parentheses, placeholder text ('Artist 4'), dates/years ('1948 tune'), or TTS-breaking punctuation = automatic score of 1.\n"
        "4. natural_flow: Does it read naturally? Too long (>120 words), too flowery/elaborate, or rambling after song introduction = lower score.\n"
        "5. length: Appropriate length (1-3 optimal, 5 max sentences)? MUST end with song introduction (artist/title). Any text after song intro = FAIL.\n\n"
        "Scoring Scale (1-10 for each criterion):\n"
        "- 10: Perfect\n"
        "- 8-9: Strong\n"
        "- 6-7: Acceptable (PASS)\n"
        "- 4-5: Weak (FAIL)\n"
        "- 1-3: Major issues (FAIL)\n\n"
        "Pass Threshold: Overall weighted score >= 7.5 (calculated from individual criteria)\n\n"
        "**STRICT RULES FOR MR. NEW VEGAS INTROS:**\n"
        "- If script contains ANY emoji (😀🎵❤️👍 etc.), forbidden_elements MUST = 1\n"
        "- If script has meta-commentary like '(1 sentence intro...)', forbidden_elements MUST = 1\n"
        "- If script has placeholder text like 'Artist 4' or 'Test Song', forbidden_elements MUST = 1\n"
        "- If script mentions dates/years (like '1948 tune', '1960s classic'), forbidden_elements MUST ≤ 3\n"
        "- If script has TTS-breaking punctuation (standalone '-', multiple '...', ',?'), forbidden_elements MUST ≤ 3\n"
        "- If script continues AFTER song introduction (artist/title), length MUST ≤ 4\n"
        "- If Mr. NV sounds uncertain/rambling (like Julie would), character_voice MUST ≤ 4\n"
        "- Generic radio clichés ('welcome back', 'like and subscribe') = era_appropriateness ≤ 4\n"
        "- If script is too long (>120 words), natural_flow MUST ≤ 6\n\n"
        "Instructions: Respond ONLY with valid JSON containing:\n"
        "{\n"
        "  \"criteria_scores\": {\"character_voice\": <1-10>, \"era_appropriateness\": <1-10>, \"forbidden_elements\": <1-10>, \"natural_flow\": <1-10>, \"length\": <1-10>},\n"
        "  \"issues\": [\"list specific problems if failing\"],\n"
        "  \"notes\": \"brief summary\"\n"
        "}\n\n"
        "DO NOT include 'score' or 'passed' in your JSON - they will be calculated from criteria_scores.\n"
    )
    
    user = f"Evaluate this song_intro script for Mr. New Vegas:\n---\n{script_content}\n---\n"
    return system + "\n" + user


def _build_song_outro_audit_prompt_julie(script_content: str) -> str:
    """Build audit prompt for Julie's song outros."""
    system = (
        "You are a script auditor for an AI radio station. Your job is to evaluate DJ scripts for character accuracy and quality.\n\n"
        "Character Reference: Julie\n"
        "- Voice: conversational, uses filler words, sometimes rambling.\n"
        "- Era: Modern American; avoid 1950s slang.\n"
        "- Tone: Warm, hopeful, friendly.\n"
        "- Typical patterns: longish sentences, friendly asides, filler words like 'you know' or 'right'.\n\n"
        "Evaluation Criteria for SONG OUTRO (score each 1-10):\n"
        "1. character_voice: Does this sound like Julie? Should be casual/warm/reflective. Generic DJ speak, flowery language = FAIL.\n"
        "2. era_appropriateness: Any anachronisms, modern slang, or DATES/YEARS mentioned? Check carefully.\n"
        "3. forbidden_elements: **CRITICAL** - ANY emoji, profanity, meta-commentary in parentheses, placeholder text, dates/years, or TTS-breaking punctuation = automatic score of 1.\n"
        "4. natural_flow: Does it read naturally? Too long (>80 words for outro), too flowery/elaborate = lower score.\n"
        "5. past_tense_usage: **OUTRO-SPECIFIC** - Must use past tense (song just played). 'That was...', 'Hope you enjoyed...', NOT 'Here is...' or 'Coming up...'. Present tense intro of song that already played = FAIL (score ≤ 3).\n\n"
        "Scoring Scale (1-10 for each criterion):\n"
        "- 10: Perfect\n"
        "- 8-9: Strong\n"
        "- 6-7: Acceptable (PASS)\n"
        "- 4-5: Weak (FAIL)\n"
        "- 1-3: Major issues (FAIL)\n\n"
        "Pass Threshold: Overall weighted score >= 7.5 (calculated from individual criteria)\n\n"
        "**STRICT RULES FOR JULIE OUTROS:**\n"
        "- If outro uses PRESENT TENSE to introduce song ('Here is...', 'This is...'), past_tense_usage MUST = 1-3\n"
        "- If outro is too long (>80 words), natural_flow MUST ≤ 5\n"
        "- If outro has long commentary about song that just played (>5 sentences), natural_flow MUST ≤ 6\n"
        "- All other forbidden_elements rules apply (emoji, dates, meta-commentary, etc.)\n"
        "- If Julie uses flowery/elaborate language, character_voice MUST ≤ 4\n"
        "- Generic radio clichés ('thanks for tuning in', 'stay tuned') = era_appropriateness ≤ 6\n\n"
        "Instructions: Respond ONLY with valid JSON containing:\n"
        "{\n"
        "  \"criteria_scores\": {\"character_voice\": <1-10>, \"era_appropriateness\": <1-10>, \"forbidden_elements\": <1-10>, \"natural_flow\": <1-10>, \"past_tense_usage\": <1-10>},\n"
        "  \"issues\": [\"list specific problems if failing\"],\n"
        "  \"notes\": \"brief summary\"\n"
        "}\n\n"
        "DO NOT include 'score' or 'passed' in your JSON - they will be calculated from criteria_scores.\n"
    )
    
    user = f"Evaluate this song_outro script for Julie:\n---\n{script_content}\n---\n"
    return system + "\n" + user


def _build_song_outro_audit_prompt_mr_new_vegas(script_content: str) -> str:
    """Build audit prompt for Mr. New Vegas's song outros."""
    system = (
        "You are a script auditor for an AI radio station. Your job is to evaluate DJ scripts for character accuracy and quality.\n\n"
        "Character Reference: Mr. New Vegas\n"
        "- Voice: smooth, suave, romantic.\n"
        "- Era: 1950s Vegas lounge; avoid modern slang or emojis.\n"
        "- Tone: Intimate, sophisticated.\n"
        "- Typical patterns: short, polished sentences, romantic descriptors, references to lounge/city.\n\n"
        "Evaluation Criteria for SONG OUTRO (score each 1-10):\n"
        "1. character_voice: Does this sound like Mr. New Vegas? Should be smooth/romantic. Generic DJ speak, rambling = FAIL.\n"
        "2. era_appropriateness: Any anachronisms, modern slang, or DATES/YEARS mentioned? Check carefully.\n"
        "3. forbidden_elements: **CRITICAL** - ANY emoji, profanity, meta-commentary in parentheses, placeholder text, dates/years, or TTS-breaking punctuation = automatic score of 1.\n"
        "4. natural_flow: Does it read naturally? Too long (>80 words for outro), too flowery/elaborate = lower score.\n"
        "5. past_tense_usage: **OUTRO-SPECIFIC** - Must use past tense (song just played). 'That was...', 'Hope you enjoyed...', NOT 'Here is...' or 'Coming up...'. Present tense intro of song that already played = FAIL (score ≤ 3).\n\n"
        "Scoring Scale (1-10 for each criterion):\n"
        "- 10: Perfect\n"
        "- 8-9: Strong\n"
        "- 6-7: Acceptable (PASS)\n"
        "- 4-5: Weak (FAIL)\n"
        "- 1-3: Major issues (FAIL)\n\n"
        "Pass Threshold: Overall weighted score >= 7.5 (calculated from individual criteria)\n\n"
        "**STRICT RULES FOR MR. NEW VEGAS OUTROS:**\n"
        "- If outro uses PRESENT TENSE to introduce song ('Here is...', 'This is...'), past_tense_usage MUST = 1-3\n"
        "- If outro is too long (>80 words), natural_flow MUST ≤ 5\n"
        "- If outro has long commentary about song that just played (>5 sentences), natural_flow MUST ≤ 6\n"
        "- All other forbidden_elements rules apply (emoji, dates, meta-commentary, etc.)\n"
        "- Generic radio clichés ('thanks for tuning in', 'stay tuned') = era_appropriateness ≤ 6\n\n"
        "Instructions: Respond ONLY with valid JSON containing:\n"
        "{\n"
        "  \"criteria_scores\": {\"character_voice\": <1-10>, \"era_appropriateness\": <1-10>, \"forbidden_elements\": <1-10>, \"natural_flow\": <1-10>, \"past_tense_usage\": <1-10>},\n"
        "  \"issues\": [\"list specific problems if failing\"],\n"
        "  \"notes\": \"brief summary\"\n"
        "}\n\n"
        "DO NOT include 'score' or 'passed' in your JSON - they will be calculated from criteria_scores.\n"
    )
    
    user = f"Evaluate this song_outro script for Mr. New Vegas:\n---\n{script_content}\n---\n"
    return system + "\n" + user


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
            weather_criteria = ["character_voice", "natural_flow", "length", "weather_mention"]
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
