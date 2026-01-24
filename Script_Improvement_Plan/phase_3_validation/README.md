# Phase 3: Multi-Stage Validation System

## Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Build a multi-stage validation system to catch quality issues automatically |
| **Duration** | 3 sessions |
| **Complexity** | High |
| **Dependencies** | Phase 2 complete (prompts v2 exist) |
| **Status** | ✅ **COMPLETE** |

## Why This Phase Matters

LLM-generated scripts need automated quality control because:

1. **Inconsistent character voice** - DJs sound generic or wrong
2. **Encoding issues** - UTF-8 double-encoding creates gibberish
3. **Metadata leaks** - File info like "(take)" appears in scripts
4. **Flowery language** - Scripts sound literary instead of conversational
5. **Character bleed** - Julie uses Mr. NV patterns (and vice versa)

**Key Learning:** Single LLM auditor insufficient - need multi-stage approach with deterministic rules + subjective validation

## Architecture

**Multi-Stage Pipeline:**
```
Generation → Rule Validator → Character Validator → Human Review
     ↓              ↓                  ↓                 ↓
  (Fluffy)    (Deterministic)    (Dolphin LLM)    (Calibration)
     ↑              ↑                  ↑
     └──────────────┴──────────────────┘
           Auto-regenerate (max 3x)
```

## Checkpoints

1. **Checkpoint 3.1:** Multi-Stage Architecture Design
2. **Checkpoint 3.2:** Rule-Based Validator Implementation
3. **Checkpoint 3.3:** Character Validator with Dolphin LLM
4. **Checkpoint 3.4:** Batch Ordering Optimization
5. **Checkpoint 3.5:** Integration and Testing

## Deliverables

- `docs/decisions/ADR-005-multi-stage-validation.md`
- `src/ai_radio/generation/validators/rule_based.py`
- `src/ai_radio/generation/validators/character.py`
- `src/ai_radio/generation/validated_pipeline.py`

## Key Learning

**Batch Ordering Discovery:**
- Character bleed-through drops from 78% to 20% when generating all scripts for one DJ before switching to the other
- ALWAYS generate all Julie scripts, THEN all Mr. NV scripts

## Gate Status

✅ **PASSED** - 100% final pass rate achieved

See `GATE.md` for detailed gate criteria.
