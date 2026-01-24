# Checkpoint 2.1: Prompt Architecture Design

## Goal
Design the structure of the new prompt system

## Tasks

1. Define prompt components and their order
2. Determine token budget allocation
3. Design the example selection strategy
4. Plan for content-type variations (intro, outro, time, weather)

## Prompt Structure

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM PROMPT                                                │
├─────────────────────────────────────────────────────────────┤
│ 1. Role Definition (who you are)                            │
│ 2. Character Voice Summary (how you speak)                  │
│ 3. Era Constraints (vocabulary rules)                       │
│ 4. Forbidden Elements (what to never do)                    │
│ 5. Few-Shot Examples (3-5 actual character lines)           │
├─────────────────────────────────────────────────────────────┤
│ USER PROMPT                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. Content Type (intro, outro, time, weather)               │
│ 2. Song Information (artist, title, year)                   │
│ 3. Lyrics Context (if available - mood, key lines)          │
│ 4. Specific Instructions                                     │
│ 5. Output Format Requirements                                │
└─────────────────────────────────────────────────────────────┘
```

## Token Budget Considerations

- Stheno 8B context window: ~4096 tokens typical
- System prompt: ~500-800 tokens
- User prompt: ~200-400 tokens
- Leave room for generation: ~500-1000 tokens

## Output

`docs/script_improvement/PROMPT_ARCHITECTURE.md`

## Success Criteria

- [x] Prompt structure documented
- [x] Token estimates for each section
- [x] Example selection strategy defined
- [x] Content-type variations planned

## Note

Example selection strategy has been added to `docs/script_improvement/PROMPT_ARCHITECTURE.md`. Content-type variations are implemented in `src/ai_radio/generation/prompts_v2.py`.

## Status

**✅ COMPLETE** - Architecture documented
