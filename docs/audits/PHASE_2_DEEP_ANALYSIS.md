# Phase 2 Deep Analysis - Root Cause & Improvement Strategy

**Generated:** 2026-01-23
**Analyst:** Auditor Agent
**Data:** 5 validation runs, 100 total scripts (50 Julie, 50 Mr. NV)

---

## Executive Summary

Analysis of 5 independent validation runs reveals **systematic issues** with the LLM ignoring prompt constraints:

- **Mr. New Vegas:** 66% banned phrase violation rate (33/50 scripts)
- **Julie:** 18% banned phrase violation rate (9/50 scripts)
- **Primary offender:** "croon/crooning" variants (28 total occurrences despite explicit ban)

**Critical Finding:** The problem is not with the prompt design - it's with the LLM's training bias overpowering explicit instructions.

---

## Pattern Analysis: The Three Core Issues

### Issue 1: LLM Semantic Association Override (Root Cause)

**What's happening:**
The LLM has strong semantic associations between jazz/swing music and specific descriptors:
- "croon" → strongly associated with male singers (Sinatra, Armstrong, Dean Martin)
- "velvety" → strongly associated with voice descriptions
- "sultry" → strongly associated with female jazz singers (Peggy Lee)
- "poignant" → strongly associated with Billie Holiday

**Why it's happening:**
The LLM's training data likely contains thousands of music reviews and descriptions using these exact phrases. When asked to describe these specific artists, the model defaults to its strongest semantic pathways **despite explicit bans**.

**Evidence:**
- "croon" appears 28 times across 100 scripts
- 15/28 occurrences are with male artists (Sinatra, Armstrong, Dean Martin)
- "poignant" appears 13 times, mostly with Billie Holiday songs
- Julie uses banned phrases 18% of the time vs. Mr. NV's 66% - **Mr. NV's theatrical persona triggers more formal music criticism language**

**Why it matters:**
Simply adding more words to the ban list won't work. The LLM will find synonyms or ignore bans when semantic pressure is high.

---

### Issue 2: Mr. New Vegas Persona Amplifies Formal Register

**What's happening:**
Mr. New Vegas generates 4x more banned phrases than Julie (33 vs. 9).

**Why it's happening:**
Mr. NV's prompt persona includes:
- "Suave, romantic, theatrical"
- "Classic mid-century phrasing"
- "Smooth, dramatic, vivid, showman-like"

These descriptors prime the LLM toward **formal music criticism vocabulary**, which heavily overlaps with banned phrases:
- Theatrical → "enchanting", "mesmerizing"
- Romantic → "sultry", "tender", "velvety"
- Showman → "crooning", "serenading"

**Evidence:**
- Mr. NV uses "Ladies and gentlemen" in 32% of openings (formal register)
- Julie uses "friends" and questions (conversational register)
- Mr. NV scripts average 3.2 sentences vs. Julie's 2.8 (more elaborate)

**Why it matters:**
The persona description itself is creating a conflicting instruction: "Be theatrical and dramatic, but don't use theatrical/dramatic vocabulary."

---

### Issue 3: Generic Descriptor Fallback Pattern

**What's happening:**
When the LLM can't use specific observations, it defaults to generic descriptors:
- "poignant" (13 occurrences)
- "sultry" (10 occurrences)
- "smooth" (7 occurrences)
- "powerful" (4 occurrences)

**Why it's happening:**
The prompt asks for "specific observations about THIS song" but doesn't provide:
1. **Actual lyrics** to reference
2. **Song context** beyond title/artist
3. **Emotional tone** or musical characteristics
4. **Historical context** that's safe to use

Without concrete material to work with, the LLM fills the gap with **evaluative adjectives** instead of **descriptive observations**.

**Evidence from best scripts:**
Julie's best scripts ask questions or make observations:
- ✅ "I wonder if they ever got a reply when sending love letters"
- ✅ "Now this is a song that suggests we all want love"
- ❌ "poignant expression of surrendering" (generic evaluation)

**Why it matters:**
The LLM needs **more input material** to generate **more specific output**. Current prompts are input-poor.

---

## Root Cause: The Three-Way Tension

```
┌─────────────────────────────────────────────────────────┐
│  PROMPT INSTRUCTION: "Be specific about THIS song"     │
│              ↓                                          │
│  LLM KNOWLEDGE: Limited (only knows title/artist)      │
│              ↓                                          │
│  SEMANTIC BIAS: Strong associations (croon = Sinatra)  │
│              ↓                                          │
│  PERSONA PRESSURE: "Be theatrical/romantic/dramatic"   │
│              ↓                                          │
│  RESULT: Generic descriptors + banned phrase leakage  │
└─────────────────────────────────────────────────────────┘
```

The LLM is being asked to:
1. Be specific (but given minimal input)
2. Avoid formal music criticism terms (but use theatrical language)
3. Match character voice (but character voice IS formal for Mr. NV)

**This creates an impossible constraint triangle.**

---

## Solution Strategy: Three-Pronged Approach

### Strategy 1: Provide More Input Material (Reduce Semantic Pressure)

**Current state:**
```python
build_song_intro_prompt_v2(dj=DJ.JULIE, artist="Louis Armstrong", title="A Kiss to Build a Dream On")
```

**Proposed enhancement:**
```python
build_song_intro_prompt_v2(
    dj=DJ.JULIE,
    artist="Louis Armstrong",
    title="A Kiss to Build a Dream On",
    year=1951,
    lyrics_snippet="Give me a kiss to build a dream on / And my imagination will thrive upon that kiss",
    song_context="upbeat romantic standard about how a single kiss can inspire lasting dreams",
    musical_style="slow swing ballad with trumpet solo"
)
```

**Why this works:**
- Gives LLM concrete material to reference instead of generic evaluation
- Reduces pressure to "fill the gap" with semantic defaults
- Enables specific observations: "Louis sings about building dreams on a single kiss - quite the optimist!"

**Implementation cost:** Requires expanding catalog.json with metadata

---

### Strategy 2: Reframe Mr. NV Persona (Reduce Formal Register Trigger)

**Current persona descriptor:**
> "Suave, romantic, theatrical; classic mid-century phrasing."

**Problem:** "Theatrical" and "classic" trigger formal music criticism vocabulary

**Proposed reframe:**
> "Confident showman, direct romantic, conversational smoothness; talks TO the listener, not about the music."

**Add explicit persona constraint:**
```python
# For Mr. New Vegas
persona_note = (
    "CRITICAL: You're a radio DJ talking to your audience, NOT a music critic writing a review. "
    "Focus on how the song makes LISTENERS feel, not on describing the artist's vocal technique. "
    "Examples: 'This one's for you' NOT 'He croons beautifully'; "
    "'Makes you think about...' NOT 'A poignant exploration of...'"
)
```

**Why this works:**
- Shifts focus from **describing performance** to **addressing audience**
- Reduces trigger for formal vocabulary
- Aligns with authentic Mr. NV examples: "This next song goes out from me to you"

---

### Strategy 3: Stronger Negative Constraints with Examples

**Current ban list approach:**
```python
FORBIDDEN_WORDS = ["crooning", "velvety smooth", ...]
system_prompt += f"DO NOT use: {', '.join(FORBIDDEN_WORDS)}"
```

**Problem:** Single-line prohibition easily ignored under semantic pressure

**Proposed enhancement:**
```python
# Add anti-examples showing what NOT to do
ANTI_EXAMPLES = {
    DJ.JULIE: [
        "❌ BAD: 'Here is Louis Armstrong crooning about love with his velvety voice'",
        "✅ GOOD: 'Louis Armstrong is up next, singing about building a dream on a single kiss'",
        "",
        "❌ BAD: 'This poignant ballad showcases Billie's haunting vocals'",
        "✅ GOOD: 'Billie Holiday here, wondering if giving your whole self to love is worth it'",
    ],
    DJ.MR_NV: [
        "❌ BAD: 'Frank Sinatra croons this sultry number with his smooth, velvety voice'",
        "✅ GOOD: 'Frank Sinatra wondering if he'll ever find love under that blue moon'",
        "",
        "❌ BAD: 'This timeless classic takes you on a magical journey'",
        "✅ GOOD: 'This next one goes out from me to you, New Vegas'",
    ]
}

system_prompt += "\n\nWHAT NOT TO DO:\n" + "\n".join(ANTI_EXAMPLES[dj])
```

**Why this works:**
- Contrast learning: Shows LLM the exact pattern to avoid vs. preferred alternative
- Contextual: Uses the actual banned phrases in negative examples
- Memorable: Easier for LLM to pattern-match against bad examples

---

### Strategy 4: Token-Level Constraint (Nuclear Option)

**If semantic override continues:**

Use LLM logit bias to penalize banned tokens:
```python
# Pseudo-code for Ollama API
banned_tokens = tokenizer.encode(["croon", "velvety", "sultry", "poignant"])

response = ollama.generate(
    model="fluffy/l3-8b-stheno-v3.2",
    prompt=prompt,
    options={
        "logit_bias": {token: -100 for token in banned_tokens}  # Heavily penalize
    }
)
```

**Why this works:**
- Prevents banned tokens at generation level, not just prompt level
- Mathematically impossible for LLM to generate banned words

**Trade-off:** May create awkward phrasing as LLM works around constraints

---

## Recommended Implementation Order

### Phase A: Quick Wins (1-2 hours)
1. ✅ Add anti-examples to prompts (Strategy 3)
2. ✅ Reframe Mr. NV persona away from "theatrical" (Strategy 2)
3. ✅ Add persona constraint about "DJ not critic"

**Expected improvement:** 30-40% reduction in violations

---

### Phase B: Medium Effort (4-6 hours)
4. Add `song_context` field to catalog.json for top 20 songs
5. Update prompt builder to include context when available
6. Regenerate validation with enhanced prompts

**Expected improvement:** 50-60% reduction in violations + higher specificity scores

---

### Phase C: Full Implementation (8-12 hours)
7. Extract song themes/context for full catalog (100+ songs)
8. Add lyrics snippets (first 2 lines or chorus)
9. Consider logit bias as fallback if issues persist

**Expected improvement:** 70-80% reduction in violations + 9+ quality scores

---

## Success Metrics

### Quantitative Targets
- **Banned phrase violations:** <5% (currently 18% Julie, 66% Mr. NV)
- **Generic descriptor usage:** <10% of scripts use >2 generic adjectives
- **Length compliance:** 95%+ scripts ≤3 sentences
- **Opening variety:** No single pattern >30%

### Qualitative Targets
- Scripts reference song content, not just artist
- Questions feel authentic to character (Julie wondering, Mr. NV romantic)
- Lore references appear naturally 20-30% of the time
- Voice differentiation: 90%+ correct DJ identification in blind test

---

## The "Why" Behind Each Issue

### Why does the LLM ignore bans?
**Because semantic associations in training data >> single-line prohibitions in prompts.**

Music reviews in the training corpus likely use "croon" thousands of times with Sinatra. That creates a strong Sinatra→croon pathway. A simple "don't use croon" in the prompt is a weak signal vs. that training bias.

**Solution:** Provide stronger alternative pathways (anti-examples, more input material, reframed persona)

---

### Why does Mr. NV violate more than Julie?
**Because his persona description triggers formal register, which overlaps heavily with banned vocabulary.**

"Theatrical" and "suave" → music criticism language
"Warm" and "conversational" → everyday language

Julie's persona naturally avoids the formal register trap.

**Solution:** Reframe Mr. NV as "showman talking TO audience" not "critic describing performance"

---

### Why generic descriptors?
**Because the LLM has minimal input to work with.**

Without lyrics, song context, or musical characteristics, the LLM can only:
1. Name the artist/title (boring)
2. Evaluate with adjectives (generic)
3. Make vague thematic guesses (risky)

**Solution:** Give LLM more material to reference (lyrics snippets, themes, context)

---

## Conclusion

The current 66% violation rate for Mr. New Vegas is not a prompt engineering failure - it's a **constraint impossibility**. The persona itself creates the problem.

**The path forward:**
1. Reduce semantic pressure (more input)
2. Reframe conflicting persona (showman not critic)
3. Strengthen constraints (anti-examples)
4. Nuclear option if needed (logit bias)

**Expected outcome after Phase A+B:**
- Julie: 8.5-9.0 average score
- Mr. NV: 8.0-8.5 average score
- Combined: 8.2-8.7 (up from current 8.08)

**Timeline to 9+ scores:** Phase C implementation required (full catalog enhancement)
