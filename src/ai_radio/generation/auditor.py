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
    # Full system prompt matching Phase 3 spec with character refs and scoring rules
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
        "Scoring Criteria (weights):\n"
        "1. Character Voice (30%): How well does the script match the DJ's voice?\n"
        "2. Era Appropriateness (25%): Any anachronisms or modern slang present?\n"
        "3. Forbidden Elements (20%): Emojis, profanity, or mean comments (absolute fail).\n"
        "4. Natural Flow (15%): Does it read naturally or sound forced?\n"
        "5. Length (10%): Is it appropriate for the content type?\n\n"
        "Scoring Scale: 10=Perfect, 8-9=Strong, 6-7=Acceptable (PASS), 4-5=Weak (FAIL), 1-3=Major issues (FAIL).\n\n"
        "Instructions: Evaluate the script and respond ONLY with valid JSON in EXACT format with keys: score, passed, criteria_scores, issues (list), notes (brief). Use the scoring scale above and set 'passed' true if overall score >= 6. Give specific issues when failing.\n"
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

        score = float(parsed.get("score", 1))
        score = max(1.0, min(10.0, score))
        passed = bool(parsed.get("passed", score >= 6))

        criteria = parsed.get("criteria_scores", {})
        # Ensure all criteria exist
        criteria_scores = {
            "character_voice": float(criteria.get("character_voice", 1)),
            "era_appropriateness": float(criteria.get("era_appropriateness", 1)),
            "forbidden_elements": float(criteria.get("forbidden_elements", 1)),
            "natural_flow": float(criteria.get("natural_flow", 1)),
            "length": float(criteria.get("length", 1)),
        }

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
