# ADR-005: Multi-Stage Validation Pipeline

## Status
Implemented

## Context
The current auditor uses a single LLM call to validate everything - grammar, punctuation, encoding, character voice, and flow. This is fundamentally flawed because:

1. **LLMs are unreliable for deterministic checks**: Double periods, malformed characters (â€¦), missing punctuation are objective issues that should be caught by rules, not probabilistic models.

2. **Mixing concerns causes failures**: The LLM passes scripts with obvious errors because it's trying to judge too many things at once.

3. **No regeneration loop**: Currently, if a script fails, nothing happens. It should regenerate until it passes or hits a retry limit.

4. **Human review is positioned as a gate, not refinement**: Human review should calibrate the validators, not serve as the final quality gate for every script.

## Decision
Implement a multi-stage validation pipeline:

### Stage 1: Generation (Fluffy Model)
- Use creative model (fluffy) for generation
- Include song lyrics in prompt for thematic bridging (intros/outros)
- Generate based on prompts_v2 templates

### Stage 2: Rule-Based Validation
**Deterministic checks that MUST pass before LLM evaluation:**
- `check_encoding()`: No malformed characters (â€¦, etc.)
- `check_punctuation()`: No double periods, proper quote pairing, sentence endings
- `check_grammar()`: Basic subject-verb agreement, complete sentences
- `check_structure()`: Must end with song intro (for song_intro type)
- `check_forbidden()`: No emojis, no parenthetical meta-commentary

**If any rule fails → regenerate (max 3 attempts)**

### Stage 3: LLM Character Validation (Dolphin Model)
**Subjective checks after rules pass:**
- Does it sound like the DJ (Julie vs Mr. NV)?
- Is it natural for the category (intro/outro/weather/time)?
- Is it not clunky or awkward?

**If LLM fails → regenerate (max 3 attempts)**

### Stage 4: Human Review (Refinement Only)
- Compare human judgment to validator scores
- Identify edge cases where validators need tuning
- NOT a permanent gate for production scripts

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    GenerationPipeline                            │
│  ┌─────────────┐                                                 │
│  │  Fluffy LLM │ ◄─── prompts_v2 + lyrics context               │
│  └──────┬──────┘                                                 │
│         │ raw script                                             │
│         ▼                                                        │
│  ┌──────────────────┐                                            │
│  │ RuleBasedValidator│ ◄─── deterministic checks                 │
│  │  - encoding       │                                           │
│  │  - punctuation    │                                           │
│  │  - grammar        │                                           │
│  │  - structure      │                                           │
│  │  - forbidden      │                                           │
│  └──────┬───────────┘                                            │
│         │ FAIL? → regenerate (max 3)                             │
│         │ PASS ↓                                                 │
│  ┌──────────────────┐                                            │
│  │ LLMCharValidator │ ◄─── Dolphin model                         │
│  │  - character_voice│                                           │
│  │  - category_fit   │                                           │
│  │  - naturalness    │                                           │
│  └──────┬───────────┘                                            │
│         │ FAIL? → regenerate (max 3)                             │
│         │ PASS ↓                                                 │
│  ┌──────────────────┐                                            │
│  │  Final Output    │                                            │
│  └──────────────────┘                                            │
└──────────────────────────────────────────────────────────────────┘

Human Review (separate process):
- Periodic batches sampled from production
- Compares human pass/fail to validator results
- Feeds back to tune rules and LLM prompts
```

## Implementation Plan

1. **Create `src/ai_radio/generation/validators/rule_based.py`**
   - Pure Python, no LLM dependency
   - Fast, deterministic, testable

2. **Create `src/ai_radio/generation/validators/character.py`**
   - Uses Dolphin for subjective evaluation
   - Simplified prompt focused only on voice/naturalness

3. **Refactor `GenerationPipeline.generate_*()` methods**
   - Add regeneration loop with validation
   - Max 3 retries per stage

4. **Update `scripts/generate_with_audit.py`**
   - Use new pipeline with built-in validation
   - Remove post-hoc auditing

5. **Add lyrics loading to generation context**
   - Read from `music_with_lyrics/{title}.txt`
   - Include relevant lines in prompt

## Consequences

### Positive
- Deterministic issues caught 100% of the time
- Faster validation (rule checks before expensive LLM)
- Clearer separation of concerns
- Regeneration loop ensures quality
- Human review becomes calibration, not bottleneck

### Negative
- More complex pipeline
- Need to maintain rule-based checks
- Regeneration increases latency (but improves quality)

## References
- User feedback from validation rounds 1-4
- Original auditor: `src/ai_radio/generation/auditor.py`
