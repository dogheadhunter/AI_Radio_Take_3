# Manual Prompt Validation Template

Use this template to perform manual validation for Phase 2 prompts.

## Setup
1. Ensure Ollama (or your chosen LLM) is running and available. If you wish, use the `prompts_v2.py` system+user separation.
2. Recommended: run in a local environment where you can control the model chosen (Stheno 8B or similar).

## Instructions
1. Generate 10 song intros for Julie using the v2 prompt:
   - Use `src/ai_radio/generation/prompts_v2.py` -> `build_song_intro_prompt_v2()` to build prompts.
   - Feed the `system` and `user` content to your LLM (system goes into system role if supported).
2. Save the outputs to a file (e.g., `data/manual_validation/julie_intros.md`).
3. Repeat the same for Mr. New Vegas.
4. Rate each output 1-10 on "sounds like <DJ>" and add notes.
5. For differentiation test: generate the same song for both DJs and confirm they are distinct.

## Validation Template

### Julie Intros
| Song | Score (1-10) | Notes |
|------|--------------|-------|
| Song 1 | | |
| Song 2 | | |
| ... | | |
| **Average** | **X.X** | |

### Mr. New Vegas Intros
| Song | Score (1-10) | Notes |
|------|--------------|-------|
| Song 1 | | |
| Song 2 | | |
| ... | | |
| **Average** | **X.X** | |

### Differentiation Test
- Same song, both DJs: Can you tell them apart? Y/N
- Character bleed-through detected? Y/N

### Overall Pass: Y/N


> When manual validation is complete, copy results into `Script_Improvment_Plan/Phase/Phase_two.md` under the Manual Test Protocol section, mark the manual test & human validation boxes as complete, commit, and push with the message `test(prompts): manual validation results for Phase 2`.
