# 📋 PHASE 3: Auditor System

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Build a system to validate script quality using a second LLM |
| **Duration** | 2-3 sessions |
| **Complexity** | High |
| **Dependencies** | Phase 2 complete (prompts exist to generate scripts) |
| **Outputs** | `auditor.py`, audit pipeline, scoring system |

---

## Why This Phase Matters

Even with improved prompts, some scripts will be off-character. The auditor:

1. Catches scripts that don't sound like the character
2. Identifies era-inappropriate language
3. Flags formatting issues (emojis, wrong length)
4. Provides notes explaining why scripts failed
5. Enables iterative improvement without constant human review

---

## Checkpoints

### Checkpoint 3.1: Audit Criteria Definition

**Goal:** Define exactly what the auditor checks and how it scores

**Tasks:**
1. Define all audit criteria
2. Assign weights to each criterion
3. Define scoring scale (1-10)
4. Define pass/fail threshold
5. Define note format for failures

**Audit Criteria:**

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Character Voice | 30% | Does it sound like Julie/Mr. NV? |
| Era Appropriateness | 25% | No modern slang or anachronisms |
| Forbidden Elements | 20% | No emojis, profanity, mean comments |
| Natural Flow | 15% | Doesn't sound forced or clunky |
| Length Appropriate | 10% | Within expected range |

**Scoring Scale:**
- 10: Perfect, exemplary character voice
- 8-9: Strong, clearly the character
- 6-7: Acceptable, minor issues
- 4-5: Weak, character voice inconsistent
- 1-3: Fail, wrong character or major issues

**Pass Threshold:** Score ≥ 6

**Audit Note Format:**
```json
{
  "script_id": "artist-title_dj_0",
  "dj": "julie",
  "score": 7,
  "passed": true,
  "criteria_scores": {
    "character_voice": 8,
    "era_appropriateness": 7,
    "forbidden_elements": 10,
    "natural_flow": 6,
    "length": 8
  },
  "issues": [],
  "notes": "Good overall, slight clunkiness in second sentence"
}
```

**Failed Audit Note Format:**
```json
{
  "script_id": "artist-title_dj_0",
  "dj": "julie",
  "score": 4,
  "passed": false,
  "criteria_scores": {
    "character_voice": 3,
    "era_appropriateness": 5,
    "forbidden_elements": 10,
    "natural_flow": 4,
    "length": 6
  },
  "issues": [
    "Uses 'awesome' - modern slang",
    "Sounds more like generic DJ than Julie",
    "Missing filler words that Julie would use"
  ],
  "notes": "Script lacks Julie's conversational warmth. Too polished."
}
```

**Output:** `docs/script_improvement/AUDIT_CRITERIA.md`

**Success Criteria:**
- [ ] All criteria defined with weights
- [ ] Scoring scale documented
- [ ] Pass/fail threshold set
- [ ] Note format defined
- [ ] Example pass and fail notes created

---

### Checkpoint 3.2: Auditor Prompt Engineering

**Goal:** Create prompts for the auditor model (Dolphin-Llama3)

**Tasks:**
1. Write system prompt for auditor role
2. Include criteria and scoring instructions
3. Include character reference (from style guides)
4. Define output format (JSON)
5. Test with sample scripts

**Auditor System Prompt Structure:**
```
You are a script auditor for an AI radio station.
Your job is to evaluate DJ scripts for character accuracy.

[Character Reference: Julie]
- Voice: conversational, uses filler words, rambling
- Era: Modern American, not 1950s
- Tone: Warm, hopeful, friendly
- Key patterns: [from style guide]

[Character Reference: Mr. New Vegas]
- Voice: smooth, suave, romantic
- Era: 1950s Vegas lounge
- Tone: Intimate, sophisticated
- Key patterns: [from style guide]

[Scoring Criteria]
1. Character Voice (30%): Does it sound like the specified DJ?
2. Era Appropriateness (25%): Is vocabulary era-appropriate?
3. Forbidden Elements (20%): No emojis, profanity, modern slang
4. Natural Flow (15%): Does it sound natural or forced?
5. Length (10%): Is it appropriate length for content type?

[Scoring Scale]
10: Perfect
8-9: Strong
6-7: Acceptable (PASS)
4-5: Weak (FAIL)
1-3: Major issues (FAIL)

[Output Format]
Respond ONLY with valid JSON in this exact format:
{
  "score": <number 1-10>,
  "passed": <true if score >= 6, false otherwise>,
  "criteria_scores": {
    "character_voice": <1-10>,
    "era_appropriateness": <1-10>,
    "forbidden_elements": <1-10>,
    "natural_flow": <1-10>,
    "length": <1-10>
  },
  "issues": [<list of specific problems found>],
  "notes": "<brief overall assessment>"
}
```

**Auditor User Prompt:**
```
Evaluate this {content_type} script for {dj}:

---
{script_content}
---

Remember:
- Score 1-10, pass threshold is 6
- Respond with JSON only
```

**Output File:** Add to `src/ai_radio/generation/auditor.py`

**Success Criteria:**
- [ ] Auditor prompt complete
- [ ] Output format is parseable JSON
- [ ] Test with 5 sample scripts (mix of good/bad)
- [ ] Auditor correctly identifies good scripts
- [ ] Auditor correctly flags bad scripts with reasons

**Manual Test Protocol:**
1. Create 2 intentionally good scripts
2. Create 2 intentionally bad scripts (modern slang, wrong character)
3. Create 1 borderline script
4. Run auditor on all 5
5. Verify auditor scores match expectation

---

### Checkpoint 3.3: Auditor Implementation

**Goal:** Implement the auditor as a Python module

**Tasks:**
1. Create `auditor.py` with core functions
2. Implement LLM client integration
3. Implement JSON parsing with error handling
4. Implement batch auditing
5. Implement result storage

**File: `src/ai_radio/generation/auditor.py`**

```python
"""
Script auditor for quality validation.

Uses a separate LLM to evaluate generated scripts
and flag those that don't meet quality standards.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from src.ai_radio.generation.llm_client import LLMClient, generate_text
from src.ai_radio.utils.logging import setup_logging


@dataclass
class AuditResult:
    """Result of auditing a single script."""
    script_id: str
    script_path: Path
    dj: str
    content_type: str
    score: float
    passed: bool
    criteria_scores: Dict[str, float]
    issues: List[str]
    notes: str
    raw_response: str  # For debugging


def audit_script(
    client: LLMClient,
    script_content: str,
    script_id: str,
    dj: str,
    content_type: str = "song_intro",
) -> AuditResult:
    """
    Audit a single script for quality.
    
    Args:
        client: LLM client for auditor model
        script_content: The script text to audit
        script_id: Identifier for the script
        dj: "julie" or "mr_new_vegas"
        content_type: Type of content (song_intro, outro, etc.)
    
    Returns:
        AuditResult with scores and notes
    """
    pass


def audit_batch(
    scripts: List[Dict[str, Any]],
    output_dir: Path,
    progress_callback: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    Audit a batch of scripts.
    
    Args:
        scripts: List of dicts with script_path, script_id, dj, content_type
        output_dir: Where to save audit results
        progress_callback: Called with progress updates
    
    Returns:
        Summary dict with pass/fail counts
    """
    pass


def save_audit_result(result: AuditResult, output_dir: Path) -> Path:
    """Save audit result to appropriate folder (passed/failed)."""
    pass


def load_audit_results(output_dir: Path) -> List[AuditResult]:
    """Load all audit results from a directory."""
    pass
```

**Test File:** `tests/generation/test_auditor.py`

```python
"""Tests for script auditor."""
import pytest
from src.ai_radio.generation.auditor import (
    audit_script,
    AuditResult,
    audit_batch,
)


class TestAuditScript:
    """Test single script auditing."""
    
    def test_returns_audit_result(self, mock_llm_auditor):
        """Must return an AuditResult object."""
        result = audit_script(
            client=mock_llm_auditor,
            script_content="Test script",
            script_id="test_1",
            dj="julie",
        )
        assert isinstance(result, AuditResult)
    
    def test_score_in_range(self, mock_llm_auditor):
        """Score must be between 1 and 10."""
        result = audit_script(
            client=mock_llm_auditor,
            script_content="Test script",
            script_id="test_1",
            dj="julie",
        )
        assert 1 <= result.score <= 10
    
    def test_passed_reflects_threshold(self, mock_llm_auditor):
        """passed=True if score >= 6."""
        # Test with mock that returns score 7
        result = audit_script(...)
        assert result.passed == (result.score >= 6)
    
    def test_handles_malformed_json(self, mock_llm_bad_json):
        """Must handle non-JSON response gracefully."""
        # Should not crash, should return failed result
        result = audit_script(...)
        assert result.passed == False
        assert "parse error" in result.notes.lower()
```

**Success Criteria:**
- [ ] `auditor.py` created with all functions
- [ ] All tests pass
- [ ] JSON parsing handles errors gracefully
- [ ] Results saved to correct folders (passed/failed)
- [ ] Batch processing works

---

### Checkpoint 3.4: Auditor Integration Test

**Goal:** Test the full audit workflow with real scripts

**Tasks:**
1. Generate 10 scripts with new prompts (5 Julie, 5 Mr. NV)
2. Run auditor on all 10
3. Review audit results
4. Verify auditor decisions match human judgment
5. Adjust auditor prompt if needed

**Test Protocol:**
1. Generate scripts with `prompts_v2.py`
2. Unload writer model
3. Load auditor model
4. Run `audit_batch()` on generated scripts
5. Review results in `data/audit/`

**Validation:**
- Human reviews all 10 scripts independently
- Compare human ratings to auditor ratings
- Calculate agreement rate
- Threshold: >80% agreement on pass/fail

**Output:** Test results documented in `docs/script_improvement/AUDITOR_VALIDATION.md`

**Success Criteria:**
- [ ] 10 scripts generated and audited
- [ ] Results saved to `data/audit/`
- [ ] Human/auditor agreement >80%
- [ ] False positives (passed but bad) <10%
- [ ] False negatives (failed but good) <20%

---

## Phase 3 Gate: Auditor Complete

### All Criteria Must Pass

| Criterion | Validation Method |
|-----------|-------------------|
| Audit criteria documented | `AUDIT_CRITERIA.md` exists |
| Auditor prompt works | Manual testing passed |
| `auditor.py` complete | All functions implemented |
| Tests pass | `pytest tests/generation/test_auditor.py -v` |
| Integration test passed | 10 scripts audited, >80% agreement |
| Results storage works | Files in `data/audit/passed/` and `failed/` |

### Required Artifacts

1. `docs/script_improvement/AUDIT_CRITERIA.md`
2. `src/ai_radio/generation/auditor.py`
3. `tests/generation/test_auditor.py`
4. `docs/script_improvement/AUDITOR_VALIDATION.md`
5. Sample audit results in `data/audit/`

### Human Validation Required

1. Review 5 randomly selected passed scripts - agree they're good?
2. Review 5 randomly selected failed scripts - agree they're bad?
3. Review failure notes - are they helpful?

**Git Commit:** `feat(generation): add script auditor system`

**Git Tag:** `v0.9.3-auditor`

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Phase 3 specification created |

---
---
---