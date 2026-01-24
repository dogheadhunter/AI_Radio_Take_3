"""
LLM-based character validator for script quality.

Uses Dolphin model to check subjective qualities:
- Does the script sound like the DJ?
- Is it natural for the content category?
- Is the flow smooth (not clunky)?

This runs AFTER rule-based validation passes.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
import logging

from src.ai_radio.generation import llm_client
from src.ai_radio.generation.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class CharacterValidationResult:
    """Result of LLM character validation."""
    passed: bool
    score: float  # 1-10
    character_voice_score: float  # How well it matches DJ
    naturalness_score: float  # Flow and readability
    issues: List[str] = field(default_factory=list)
    notes: str = ""
    raw_response: str = ""


# Simple, focused prompt for character validation
SYSTEM_PROMPT = """You are a character voice validator for an AI radio station.

Your ONLY job is to check if the script sounds like the correct DJ and is natural to read aloud.

DJ CHARACTERS:

JULIE (Appalachian Radio):
- Casual, conversational, sometimes rambling
- Uses filler words: "you know", "I wonder", "folks"
- Asks rhetorical questions
- Warm, hopeful, friendly tone
- GROUNDED language, not flowery or elaborate
- Should feel like a friend chatting

MR. NEW VEGAS (Radio New Vegas):
- Smooth, suave, romantic
- Formal but warm: "Ladies and gentlemen", "dear listeners"
- **DECLARATIVE statements, NOT rhetorical questions**
- Short, polished sentences
- Intimate, sophisticated tone
- May reference the Mojave wasteland, New Vegas Strip
- Should feel like a confident lounge singer hosting

VALIDATION FOCUS:
1. character_voice (1-10): Does this script sound like this specific DJ?
   - Julie should NOT sound formal, flowery, or elaborate
   - Julie CAN use rhetorical questions ("I wonder...", "don't you think?")
   - Mr. NV should NOT sound uncertain, rambling, or casual
   - Mr. NV should use DECLARATIVE statements, NOT questions
   - Mr. NV asking rhetorical questions = score 3-4
   - Generic "DJ speak" = score 3-4

2. naturalness (1-10): Is this smooth to read aloud for TTS?
   - Clunky phrasing = lower score
   - Awkward sentence breaks = lower score
   - Run-on sentences = lower score
   - Too long (>80 words) = score 5-6

PASS: Both scores >= 6
FAIL: Either score < 6

Respond with ONLY valid JSON:
{
  "character_voice": <1-10>,
  "naturalness": <1-10>,
  "issues": ["list problems if any"],
  "notes": "brief summary"
}
"""


def validate_character(
    client: Optional[LLMClient],
    text: str,
    dj: str,
    content_type: str = "song_intro",
) -> CharacterValidationResult:
    """
    Validate script for character voice and naturalness.
    
    Args:
        client: LLM client (uses default if None)
        text: Script content to validate
        dj: DJ name ("julie" or "mr_new_vegas")
        content_type: Type of content
    
    Returns:
        CharacterValidationResult with scores and pass/fail
    """
    user_prompt = f"""Validate this {content_type} script for {dj}:

---
{text}
---

Is this natural to read aloud? Does it sound like {dj}?"""

    full_prompt = SYSTEM_PROMPT + "\n\n" + user_prompt
    
    raw = ""
    try:
        raw = llm_client.generate_text(client, full_prompt)
        
        # Try to extract JSON from response
        # Sometimes LLM wraps in markdown code blocks
        json_match = raw
        if '```' in raw:
            import re
            json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
            match = re.search(json_pattern, raw)
            if match:
                json_match = match.group(1).strip()
        
        parsed = json.loads(json_match)
        
        char_score = float(parsed.get("character_voice", 5))
        nat_score = float(parsed.get("naturalness", 5))
        
        # Clamp to 1-10
        char_score = max(1.0, min(10.0, char_score))
        nat_score = max(1.0, min(10.0, nat_score))
        
        # Average for overall score
        score = (char_score + nat_score) / 2.0
        
        # Pass if both >= 6
        passed = char_score >= 6.0 and nat_score >= 6.0
        
        issues = parsed.get("issues", []) or []
        notes = parsed.get("notes", "")
        
        return CharacterValidationResult(
            passed=passed,
            score=score,
            character_voice_score=char_score,
            naturalness_score=nat_score,
            issues=issues,
            notes=notes,
            raw_response=raw,
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse character validation response: {e}")
        logger.debug(f"Raw response: {raw}")
        return CharacterValidationResult(
            passed=False,
            score=1.0,
            character_voice_score=1.0,
            naturalness_score=1.0,
            issues=["Failed to parse LLM response"],
            notes=f"JSON parse error: {e}",
            raw_response=raw,
        )
    except Exception as e:
        logger.error(f"Character validation error: {e}")
        return CharacterValidationResult(
            passed=False,
            score=1.0,
            character_voice_score=1.0,
            naturalness_score=1.0,
            issues=[f"Validation error: {e}"],
            raw_response=raw,
        )
