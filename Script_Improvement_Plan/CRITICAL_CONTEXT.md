# Critical Context - Must Read Every Session

**Purpose:** This document contains hard-won learnings that MUST carry forward into every work session. Read this before starting any checkpoint work.

---

## 🎯 Voice-First Prompting (Phase 2 Learning)

**The Breakthrough Discovery:**

The project initially attempted to control script quality through **restriction-heavy prompts** (forbidden words lists, vocabulary policing, era constraints). This approach was **counterproductive** and fought against the LLM's natural language strengths.

**DO:**
- ✅ Teach voice through authentic few-shot examples from actual transcripts
- ✅ Focus on "sound like this" through demonstration
- ✅ Use minimal constraints (only true anachronisms that break immersion)
- ✅ Emphasize character differentiation through examples

**DON'T:**
- ❌ Use restriction-heavy prompts with forbidden words lists
- ❌ Over-police vocabulary with extensive "don't say" rules
- ❌ Try to control voice through prohibition
- ❌ Force catchphrases or formulaic patterns

**Why This Matters:**
The LLM learns voice from **authentic examples**, not from being told what NOT to do. When you teach "this is how Julie sounds" through demonstration, the model naturally emulates the patterns.

**Results:**
- Julie: 8.5/10 (authentic voice, natural warmth)
- Mr. New Vegas: 9.0/10 (excellent voice, romantic confidence)
- Zero character bleed-through
- Natural variety (no formulaic repetition)

---

## 🔄 Batch Ordering Matters (Phase 3 Learning)

**Critical Discovery:**

The order in which you generate scripts has a **massive impact** on character bleed-through.

**DO:**
- ✅ Generate ALL Julie scripts first
- ✅ THEN generate ALL Mr. New Vegas scripts
- ✅ Process in complete batches per character

**DON'T:**
- ❌ Alternate DJs per song
- ❌ Mix Julie and Mr. NV generation
- ❌ Generate in random order

**Why This Matters:**
LLM context carries forward. When you alternate between characters, the model starts blending their voices.

**Results:**
- **Alternating order:** 78% character bleed-through (unacceptable)
- **Batch ordering:** 20% character bleed-through (acceptable)
- **Impact:** 58 percentage point improvement!

**Implementation:**
The pipeline automatically batches by DJ. Never override this behavior.

---

## 🎭 Multi-Stage Validation Architecture (Phase 3)

**Why Single-Stage Validation Failed:**
LLMs are unreliable for deterministic checks (encoding, punctuation, metadata leaks).

**The Solution: Three-Stage Pipeline**

### Stage 1: Rule-Based Validation (FAST, Deterministic)
- Encoding issues (UTF-8 double-encoding: â€™, â€¦)
- Punctuation problems (double periods, unbalanced quotes)
- Forbidden content (emojis, meta-commentary, placeholder text)
- Metadata leaks: (take), (version), (demo), (live), (remaster)
- Generic clichés: "timeless classic", "welcome back"
- Structure: Must mention artist/title
- Word count: Warnings at 80+, errors at 100+

**Speed:** <100ms per script

### Stage 2: LLM Character Validation (Subjective, Dolphin)
- Character voice accuracy (1-10)
- Naturalness for TTS (1-10)
- Pass threshold: Both scores ≥ 6

### Stage 3: Human Calibration
- Review batches to refine validators
- Identify false positives/negatives
- Adjust criteria weights

**Why This Matters:**
Each stage catches different types of issues. Don't skip stages or combine them.

---

## 🚨 Red Flags by DJ

### Julie - REJECT if script contains:

**Flowery/Poetic Language:**
- "fleeting promise"
- "palpable ache"
- "tender touch"
- Any overly elaborate descriptions

**Literary Phrasing:**
- "as she so poignently expresses"
- Music critic language
- Formal/academic tone

**Character Voice:**
- Julie is GROUNDED, SIMPLE - kitchen table talk, not literary
- She uses filler words naturally: "you know", "I wonder", "folks"
- Rhetorical questions are GOOD for Julie (shows vulnerability)
- Casual, conversational, sometimes rambling

### Mr. New Vegas - REJECT if script contains:

**Aggressive Openings:**
- "Listen up!"
- "Hey there!"
- Any forceful commands

**Preachy Questions:**
- "Who among us..."
- "Don't we all..."
- Philosophical moralizing

**Music Critic Language:**
- "masterclass"
- "tour de force"
- Academic analysis

**Character Voice:**
- Mr. New Vegas is smooth, suave, romantic lounge host
- Formal but warm: "Ladies and gentlemen"
- Confident declarative statements
- CAN use tag questions for intimate engagement: "doesn't it?"
- Never aggressive or preachy

---

## 📊 Success Thresholds

| Metric | Target | Why |
|--------|--------|-----|
| Audit pass rate | >80% | Balance between quality and efficiency |
| Character voice score | ≥6/10 | Minimum acceptable character accuracy |
| Naturalness score | ≥6/10 | Must sound good when read by TTS |
| Character recognition | >90% | Human should identify DJ from script alone |

---

## 🔧 Technical Best Practices

### GPU Memory Management
1. Load Writer Model (Stheno 8B)
2. Generate all scripts
3. **Unload Writer Model** (critical!)
4. Load Auditor Model (Dolphin)
5. Audit all scripts
6. **Unload Auditor Model** (critical!)
7. Load Chatterbox TTS
8. Generate audio for PASSED scripts only

**Never skip unloading steps** - you'll run out of GPU memory.

### Checkpoint/Resume
- Save progress after each major stage
- Pipeline state stored in `data/pipeline_state.json`
- `--resume` flag picks up where you left off
- Within stages, track which items are processed

---

## 📝 Workflow Rules

1. **Work on ONE checkpoint at a time** - don't jump ahead
2. **Read only the checkpoint file you're working on** - avoid context overload
3. **Complete ALL success criteria** before moving on
4. **Update CURRENT_STATUS.md** at session end
5. **Use Auditor Agent** to verify before progression

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-24 | Initial critical context created from Phases 1-3 learnings |

---

*These learnings must carry forward. Don't rediscover them the hard way.*
