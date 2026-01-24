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


def _build_prompt(script_content: str, dj: str, content_type: str = "song_intro") -> str:
    # Clarified prompt: weights are metadata, LLM returns 1-10 scores only
    system = (
        "You are a script auditor for an AI radio station. Your job is to evaluate DJ scripts for character accuracy and quality.\n\n"
        "Character Reference: Julie\n"
        "- Voice: conversational, uses filler words, sometimes rambling.\n"
        "- Era: Modern American; avoid 1950s slang.\n"
        "- Tone: Warm, hopeful, friendly.\n"
        "- Typical patterns: longish sentences, friendly asides, filler words like 'you know' or 'right'.\n\n"
        "Character Reference: Mr. New Vegas\n"
        "- Voice: smooth, suave, romantic.\n"
        "- Era: 1950s Vegas lounge; avoid modern slang or emojis.\n"
        "- Tone: Intimate, sophisticated.\n"
        "- Typical patterns: short, polished sentences, romantic descriptors, references to lounge/city.\n\n"
        "Evaluation Criteria (score each 1-10):\n"
        "1. character_voice: How well does the script match the DJ's voice? Julie should sound casual/rambling/grounded, Mr. NV should sound smooth/romantic. Generic DJ speak, flowery language for Julie, or wrong personality = FAIL.\n"
        "2. era_appropriateness: Any anachronisms, modern slang, or DATES/YEARS mentioned? Check carefully.\n"
        "3. forbidden_elements: **CRITICAL** - ANY emoji, profanity, mean comments, meta-commentary in parentheses, placeholder text ('Artist 4'), dates/years ('1948 tune'), or TTS-breaking punctuation = automatic score of 1.\n"
        "4. natural_flow: Does it read naturally? Too long (>100 words), too flowery/elaborate, or rambling after song introduction = lower score.\n"
        "5. length: Appropriate length? MUST end with song introduction (artist/title). Any text after song intro = FAIL.\n\n"
        "Scoring Scale (1-10 for each criterion):\n"
        "- 10: Perfect\n"
        "- 8-9: Strong\n"
        "- 6-7: Acceptable (PASS)\n"
        "- 4-5: Weak (FAIL)\n"
        "- 1-3: Major issues (FAIL)\n\n"
        "Pass Threshold: Overall weighted score >= 6.0 (calculated from individual criteria)\n\n"
        "**STRICT RULES:**\n"
        "- If script contains ANY emoji (😀🎵❤️👍 etc.), forbidden_elements MUST = 1\n"
        "- If script has meta-commentary like '(1 sentence intro...)', forbidden_elements MUST = 1\n"
        "- If script has placeholder text like 'Artist 4' or 'Test Song', forbidden_elements MUST = 1\n"
        "- If script mentions dates/years (like '1948 tune', '1960s classic'), forbidden_elements MUST ≤ 3\n"
        "- If script has TTS-breaking punctuation (standalone '-', multiple '...', ',?'), forbidden_elements MUST ≤ 3\n"
        "- If script continues AFTER song introduction (artist/title), length MUST ≤ 4\n"
        "- If Julie uses flowery/elaborate language ('inimitable', 'tailor made', 'semblance of tranquility'), character_voice MUST ≤ 4\n"
        "- If Julie sounds formal/polished (like Mr. NV), character_voice MUST ≤ 4\n"
        "- If Mr. NV sounds uncertain/rambling (like Julie), character_voice MUST ≤ 4\n"
        "- Generic radio clichés ('welcome back', 'like and subscribe') = era_appropriateness ≤ 4\n"
        "- If script is too long (>100 words), natural_flow MUST ≤ 6\n\n"
        "Instructions: Respond ONLY with valid JSON containing:\n"
        "{\n"
        "  \"criteria_scores\": {\"character_voice\": <1-10>, \"era_appropriateness\": <1-10>, \"forbidden_elements\": <1-10>, \"natural_flow\": <1-10>, \"length\": <1-10>},\n"
        "  \"issues\": [\"list specific problems if failing\"],\n"
        "  \"notes\": \"brief summary\"\n"
        "}\n\n"
        "DO NOT include 'score' or 'passed' in your JSON - they will be calculated from criteria_scores.\n"
    )
    user = f"Evaluate this {content_type} script for {dj}:\n---\n{script_content}\n---\n"
    return system + "\n" + user


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
        
        # Robust extraction with key name variations
        criteria_scores = {
            "character_voice": _get_criterion_value(criteria, "character_voice"),
            "era_appropriateness": _get_criterion_value(criteria, "era_appropriateness"),
            "forbidden_elements": _get_criterion_value(criteria, "forbidden_elements"),
            "natural_flow": _get_criterion_value(criteria, "natural_flow"),
            "length": _get_criterion_value(criteria, "length"),
        }
        
        # Normalization: if LLM returned 0-100 scale, normalize to 1-10
        max_raw_score = max(criteria_scores.values())
        if max_raw_score > 10:
            criteria_scores = {k: (v / 10.0) for k, v in criteria_scores.items()}
        
        # Clamp to 1-10 range
        criteria_scores = {k: max(1.0, min(10.0, v)) for k, v in criteria_scores.items()}
        
        # Compute weighted average (Option B: weights in code)
        score = sum(criteria_scores[k] * WEIGHTS[k] for k in WEIGHTS.keys())
        score = max(1.0, min(10.0, score))
        passed = score >= 6.0

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
            raw_response=raw,
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
