# Checkpoint 2.3: Mr. New Vegas Prompt Template

## Goal
Create the complete prompt template for Mr. New Vegas

## Tasks

1. Write system prompt using Mr. NV style guide
2. Select 5 best example lines for few-shot
3. Create user prompt template with placeholders
4. Test prompt with 3 different songs manually
5. Iterate based on output quality

## Character Elements

Same structure as Julie, but with:
- Different character voice
- 1950s vocabulary emphasis
- Romantic/intimate listener address
- No filler words
- Different example lines

## Output File

`src/ai_radio/generation/prompts_v2.py` (Mr. NV section)

## Success Criteria

- [x] System prompt complete (<800 tokens)
- [x] 5 example lines selected and included
- [x] User prompt template with all placeholders
- [x] Manual test: 3 songs generated and reviewed
- [x] Human validation: scripts sound like Mr. New Vegas
- [x] Scripts clearly different from Julie's style

## Validation Results

**10 intros generated and rated. Average score: 8.4/10** ✅ PASS (solid)

Differentiation test confirmed distinct personalities with no character bleed-through.

See `data/manual_validation/VALIDATION_RESULTS_PHASE_2.md`.

**Issues Identified:**
- "Gather 'round" in 50% of scripts
- "Sit back, relax" overused
- Overall better adherence to character voice than Julie

## Differentiation Test

- Generate same song intro for both DJs
- They should sound distinctly different
- Neither should be confusable for the other

✅ **PASSED** - Clear differentiation confirmed

## Status

**✅ COMPLETE** - Validated with 9.0/10 average (after refinement)
