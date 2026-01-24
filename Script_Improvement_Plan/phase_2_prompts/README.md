# Phase 2: Prompt Engineering

## Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Create improved prompt templates using extracted style guides |
| **Duration** | 2-3 sessions |
| **Complexity** | High |
| **Dependencies** | Phase 1 complete (style guides exist) |
| **Status** | ✅ **COMPLETE** |

## Why This Phase Matters

The style guides from Phase 1 give us the raw materials. This phase transforms those materials into effective prompts that:

1. Show the LLM exactly how the character speaks (few-shot examples)
2. Provide negative constraints (what NOT to do)
3. Include context-appropriate information (lyrics, song info)
4. Are optimized for the writer model (Stheno 8B)

## Checkpoints

1. **Checkpoint 2.1:** Prompt Architecture Design
2. **Checkpoint 2.2:** Julie Prompt Template
3. **Checkpoint 2.3:** Mr. New Vegas Prompt Template
4. **Checkpoint 2.4:** Content Type Variations
5. **Checkpoint 2.5:** Prompt Integration

## Deliverables

- `docs/script_improvement/PROMPT_ARCHITECTURE.md`
- `src/ai_radio/generation/prompts_v2.py`
- `tests/generation/test_prompts_v2.py`

## Key Learning

**Voice-First Prompting Breakthrough:**
- LLM learns voice from demonstration, not restriction
- Use authentic few-shot examples instead of forbidden words lists
- Focus on "sound like this" rather than "don't say that"

## Gate Status

✅ **PASSED** - Julie 8.5/10, Mr. New Vegas 9.0/10

See `GATE.md` for detailed gate criteria.
