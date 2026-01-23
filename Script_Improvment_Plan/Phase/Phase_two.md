# 📋 PHASE 2: Prompt Engineering

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Create improved prompt templates using extracted style guides |
| **Duration** | 2-3 sessions |
| **Complexity** | High |
| **Dependencies** | Phase 1 complete (style guides exist) |
| **Outputs** | `prompts_v2.py`, tested prompt templates |

---

## Why This Phase Matters

The style guides from Phase 1 give us the raw materials. This phase transforms those materials into effective prompts that:

1. Show the LLM exactly how the character speaks (few-shot examples)
2. Provide negative constraints (what NOT to do)
3. Include context-appropriate information (lyrics, song info)
4. Are optimized for the writer model (Stheno 8B)

---

## Checkpoints

### Checkpoint 2.1: Prompt Architecture Design

**Goal:** Design the structure of the new prompt system

**Tasks:**
1. Define prompt components and their order
2. Determine token budget allocation
3. Design the example selection strategy
4. Plan for content-type variations (intro, outro, time, weather)

**Prompt Structure:**

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

**Token Budget Considerations:**
- Stheno 8B context window: ~4096 tokens typical
- System prompt: ~500-800 tokens
- User prompt: ~200-400 tokens
- Leave room for generation: ~500-1000 tokens

**Output:** `docs/script_improvement/PROMPT_ARCHITECTURE.md`

**Success Criteria:**
- [ ] Prompt structure documented
- [ ] Token estimates for each section
- [ ] Example selection strategy defined
- [ ] Content-type variations planned

---

### Checkpoint 2.2: Julie Prompt Template

**Goal:** Create the complete prompt template for Julie

**Tasks:**
1. Write system prompt using Julie style guide
2. Select 5 best example lines for few-shot
3. Create user prompt template with placeholders
4. Test prompt with 3 different songs manually
5. Iterate based on output quality

**System Prompt Components:**

1. **Role Definition:**
   - You are Julie, the radio DJ
   - Brief character summary

2. **Voice Description:**
   - Pulled from style guide
   - Specific, not vague

3. **Era Constraints:**
   - Modern words to avoid
   - Period-appropriate alternatives

4. **Forbidden Elements:**
   - Emojis
   - Profanity
   - Mean comments about listeners
   - Forced catchphrases
   - Modern slang list

5. **Few-Shot Examples:**
   - 3-5 actual Julie lines from transcript
   - Mix of intro types
   - Show the variety

**User Prompt Template:**
```
Generate a song intro for:
Artist: {artist}
Title: {title}
Year: {year}

Song context: {lyrics_summary or "No lyrics available"}

Requirements:
- Length: 2-4 sentences
- Must sound natural and conversational
- Do not force filler words if they don't fit naturally
- Do not include the exact song title if it sounds clunky
```

**Output File:** `src/ai_radio/generation/prompts_v2.py` (Julie section)

**Success Criteria:**
- [ ] System prompt complete (<800 tokens)
- [ ] 5 example lines selected and included
- [ ] User prompt template with all placeholders
- [ ] Manual test: 3 songs generated and reviewed
- [ ] Human validation: scripts sound like Julie

**Manual Test Protocol:**
1. Run prompt manually with Ollama
2. Generate intro for 3 different songs
3. Rate each 1-10 on "sounds like Julie"
4. Document what works and what doesn't
5. Iterate if average score < 7

---

### Checkpoint 2.3: Mr. New Vegas Prompt Template

**Goal:** Create the complete prompt template for Mr. New Vegas

**Tasks:**
1. Write system prompt using Mr. NV style guide
2. Select 5 best example lines for few-shot
3. Create user prompt template with placeholders
4. Test prompt with 3 different songs manually
5. Iterate based on output quality

**Same structure as Julie, but with:**
- Different character voice
- 1950s vocabulary emphasis
- Romantic/intimate listener address
- No filler words
- Different example lines

**Output File:** `src/ai_radio/generation/prompts_v2.py` (Mr. NV section)

**Success Criteria:**
- [ ] System prompt complete (<800 tokens)
- [ ] 5 example lines selected and included
- [ ] User prompt template with all placeholders
- [ ] Manual test: 3 songs generated and reviewed
- [ ] Human validation: scripts sound like Mr. New Vegas
- [ ] Scripts clearly different from Julie's style

**Differentiation Test:**
- Generate same song intro for both DJs
- They should sound distinctly different
- Neither should be confusable for the other

---

### Checkpoint 2.4: Content Type Variations

**Goal:** Create prompt variations for different content types

**Content Types:**
1. Song Intros (primary focus)
2. Song Outros
3. Time Announcements
4. Weather Announcements

**Tasks:**
1. Adapt base prompts for each content type
2. Adjust examples to match content type
3. Modify length/format requirements
4. Test each variation

**Variation Strategy:**

| Content Type | Example Count | Length | Special Requirements |
|--------------|---------------|--------|---------------------|
| Song Intro | 5 examples | 2-4 sentences | Include artist context |
| Song Outro | 3 examples | 1-2 sentences | Transitional feel |
| Time | 3 examples | 1 sentence | Include time naturally |
| Weather | 3 examples | 2-3 sentences | Period-style weather |

**Output:** Additional functions in `prompts_v2.py`:
- `build_song_intro_prompt_v2()`
- `build_song_outro_prompt_v2()`
- `build_time_prompt_v2()`
- `build_weather_prompt_v2()`

**Success Criteria:**
- [ ] All 4 content types have prompts
- [ ] Each type tested with 2 examples per DJ
- [ ] Outputs match expected format and length
- [ ] Human validation: content sounds appropriate

---

### Checkpoint 2.5: Prompt Integration

**Goal:** Integrate new prompts into the generation system

**Tasks:**
1. Create `prompts_v2.py` with all new prompt functions
2. Maintain backward compatibility with existing system
3. Add configuration to switch between old/new prompts
4. Create tests for new prompt functions

**File Structure:**
```python
# src/ai_radio/generation/prompts_v2.py

"""
Improved prompt templates for DJ personalities.
Version 2: Uses extracted style guides and few-shot examples.
"""

from enum import Enum
from typing import Optional, Dict, Any

class DJ(Enum):
    JULIE = "julie"
    MR_NEW_VEGAS = "mr_new_vegas"

# Style guide content (extracted from Phase 1)
JULIE_EXAMPLES = [
    "...",
    "...",
]

MR_NV_EXAMPLES = [
    "...",
    "...",
]

FORBIDDEN_WORDS = [
    "awesome", "cool", "vibe", "party started",
    # ... more from style guides
]

def build_song_intro_prompt_v2(
    dj: DJ,
    artist: str,
    title: str,
    year: Optional[int] = None,
    lyrics_context: Optional[str] = None,
) -> Dict[str, str]:
    """
    Build improved song intro prompt.
    
    Returns dict with 'system' and 'user' prompts.
    """
    # Implementation
    pass
```

**Test File:** `tests/generation/test_prompts_v2.py`

**Success Criteria:**
- [ ] `prompts_v2.py` created with all functions
- [ ] All functions return proper prompt structure
- [ ] Tests verify prompt content includes examples
- [ ] Tests verify forbidden words are mentioned
- [ ] No breaking changes to existing generation

---

## Phase 2 Gate: Prompts Complete

### All Criteria Must Pass

| Criterion | Validation Method |
|-----------|-------------------|
| Prompt architecture documented | `PROMPT_ARCHITECTURE.md` exists |
| Julie prompt template complete | Function exists, tests pass |
| Mr. NV prompt template complete | Function exists, tests pass |
| All content types covered | 4 prompt functions exist |
| Manual testing passed | Average score >7/10 |
| Differentiation verified | Same song produces different outputs |
| Tests pass | `pytest tests/generation/test_prompts_v2.py -v` |

### Required Artifacts

1. `docs/script_improvement/PROMPT_ARCHITECTURE.md`
2. `src/ai_radio/generation/prompts_v2.py`
3. `tests/generation/test_prompts_v2.py`
4. Manual test results documented

### Human Validation Required

1. Generate 10 Julie song intros with new prompts
2. Generate 10 Mr. NV song intros with new prompts
3. Rate each 1-10 on character accuracy
4. Average must be >7 to pass
5. Confirm the two DJs sound distinctly different

**Validation Template:**
```markdown
## Manual Prompt Validation

### Julie Intros
| Song | Score (1-10) | Notes |
|------|--------------|-------|
| Song 1 | | |
| Song 2 | | |
...
| **Average** | **X.X** | |

### Mr. New Vegas Intros
| Song | Score (1-10) | Notes |
|------|--------------|-------|
| Song 1 | | |
| Song 2 | | |
...
| **Average** | **X.X** | |

### Differentiation Test
- Same song, both DJs: Can you tell them apart? Y/N
- Character bleed-through detected? Y/N

### Overall Pass: Y/N
```

**Git Commit:** `feat(generation): add improved prompt templates v2`

**Git Tag:** `v0.9.2-prompts`

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Phase 2 specification created |

---
---
---