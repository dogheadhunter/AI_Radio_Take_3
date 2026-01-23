
# 📋 PHASE 1: Style Guide Extraction

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Extract speech patterns from voice line transcripts into usable style guides |
| **Duration** | 1-2 sessions |
| **Complexity** | Medium |
| **Dependencies** | Voice line transcripts exist |
| **Outputs** | `STYLE_GUIDE_JULIE.md`, `STYLE_GUIDE_MR_NEW_VEGAS.md` |

---

## Why This Phase Matters

The current prompts fail because they describe the characters abstractly ("friendly", "suave") instead of showing what they actually sound like. By extracting concrete patterns from the real voice lines, we create a reference that:

1. Provides actual example sentences the LLM can mimic
2. Identifies vocabulary the character uses
3. Documents sentence structures and rhythms
4. Captures how they introduce and close songs

---

## Checkpoints

### Checkpoint 1.1: Transcript Preprocessing

**Goal:** Clean and prepare transcripts for analysis

**Tasks:**
1. Remove timestamps from Julie's transcript (`00:00:00 Speaker:` prefixes)
2. Split transcripts into individual lines/segments
3. Categorize segments by type (intro, outro, commentary, etc.)
4. Save cleaned transcripts for reference

**Input Files:**
- `assets/voice_references/Julie/Julie_Full_Voicelines_Script.txt`
- `assets/voice_references/Mister_New_Vegas/Mister_New_Vegas_Voice_Files_Script.txt`

**Output Files:**
- `data/style_analysis/julie_cleaned.txt`
- `data/style_analysis/mr_new_vegas_cleaned.txt`
- `data/style_analysis/julie_categorized.json`
- `data/style_analysis/mr_new_vegas_categorized.json`

**Success Criteria:**
- [ ] Timestamps removed from all lines
- [ ] Each line is a complete thought/segment
- [ ] Categories identified: `song_intro`, `song_outro`, `commentary`, `time`, `weather`, `other`
- [ ] At least 20 segments categorized for each DJ

**Validation:**
```bash
# Check cleaned file has no timestamps
grep -c "00:00:00" data/style_analysis/julie_cleaned.txt
# Expected: 0

# Check categorization file exists and has data
python -c "import json; d=json.load(open('data/style_analysis/julie_categorized.json')); print(f'Categories: {list(d.keys())}')"
```

---

### Checkpoint 1.2: Julie Pattern Extraction

**Goal:** Analyze Julie's speech to identify characteristic patterns

**Tasks:**
1. Extract song introduction patterns (how she introduces songs)
2. Extract song outro patterns (how she transitions away)
3. Identify filler word usage frequency and placement
4. Document sentence starters she commonly uses
5. Identify vocabulary unique to her voice
6. Note things she explicitly avoids

**Analysis Categories:**

| Category | What to Extract |
|----------|-----------------|
| **Intro Patterns** | How she announces songs (5-10 examples) |
| **Outro Patterns** | How she closes out songs (5-10 examples) |
| **Filler Words** | Which ones, how often, where in sentences |
| **Sentence Starters** | Common ways she begins thoughts |
| **Personal Touches** | How she adds her own opinions/feelings |
| **Vocabulary** | Era-appropriate words she uses |
| **Forbidden** | Words/phrases she never uses |

**Output File:** `docs/script_improvement/STYLE_GUIDE_JULIE.md`

**Success Criteria:**
- [ ] At least 10 song intro examples extracted
- [ ] At least 5 song outro examples extracted
- [ ] Filler word inventory complete with usage notes
- [ ] At least 10 sentence starters documented
- [ ] Vocabulary list of 20+ characteristic words
- [ ] Forbidden list includes modern slang, profanity

**Validation:**
- Human review: Do the extracted patterns "sound like Julie"?
- Cross-reference with MVP goal document character description

---

### Checkpoint 1.3: Mr. New Vegas Pattern Extraction

**Goal:** Analyze Mr. New Vegas's speech to identify characteristic patterns

**Tasks:**
1. Extract song introduction patterns
2. Extract song outro patterns
3. Identify 1950s vocabulary usage
4. Document romantic/intimate phrasing
5. Note deliberate pacing markers (pauses, emphasis)
6. Identify signature phrases and their usage

**Analysis Categories:**

| Category | What to Extract |
|----------|-----------------|
| **Intro Patterns** | How he announces songs (5-10 examples) |
| **Outro Patterns** | How he closes out songs (5-10 examples) |
| **Romantic Phrasing** | How he addresses the listener |
| **1950s Vocabulary** | Era-specific words and phrases |
| **Pacing Markers** | Where he pauses, what he emphasizes |
| **Signature Phrases** | Recurring lines and when he uses them |
| **Forbidden** | Modern slang, breaking character |

**Output File:** `docs/script_improvement/STYLE_GUIDE_MR_NEW_VEGAS.md`

**Success Criteria:**
- [ ] At least 10 song intro examples extracted
- [ ] At least 5 song outro examples extracted
- [ ] 1950s vocabulary list of 15+ words
- [ ] Romantic phrasing examples (10+)
- [ ] Signature phrases documented with usage context
- [ ] Forbidden list complete

**Validation:**
- Human review: Do the extracted patterns "sound like Mr. New Vegas"?
- Cross-reference with MVP goal document character description

---

### Checkpoint 1.4: Comparative Analysis

**Goal:** Document the differences between Julie and Mr. New Vegas

**Tasks:**
1. Create side-by-side comparison of key differences
2. Identify what makes each voice unique
3. Document "contamination" risks (Julie sounding like Mr. NV or vice versa)
4. Create quick-reference differentiation guide

**Output Section:** Add to both style guides as "Differentiation" section

**Comparison Areas:**

| Aspect | Julie | Mr. New Vegas |
|--------|-------|---------------|
| **Tone** | ? | ? |
| **Pacing** | ? | ? |
| **Formality** | ? | ? |
| **Listener Relationship** | ? | ? |
| **Vocabulary Era** | ? | ? |
| **Signature Elements** | ? | ? |

**Success Criteria:**
- [ ] Clear distinctions documented for all comparison areas
- [ ] "Red flags" identified for each DJ (signs the script is wrong character)
- [ ] Quick differentiation checklist created

---

## Phase 1 Gate: Style Guides Complete

### All Criteria Must Pass

| Criterion | Validation Method |
|-----------|-------------------|
| Julie transcript cleaned | File exists, no timestamps |
| Mr. NV transcript cleaned | File exists, no timestamps |
| Julie categorized segments | JSON file with 20+ entries |
| Mr. NV categorized segments | JSON file with 20+ entries |
| Julie style guide complete | All sections filled |
| Mr. NV style guide complete | All sections filled |
| Comparison analysis done | Side-by-side differences documented |
| Human validation | Patterns "sound right" |

### Required Artifacts

1. `data/style_analysis/julie_cleaned.txt`
2. `data/style_analysis/mr_new_vegas_cleaned.txt`
3. `data/style_analysis/julie_categorized.json`
4. `data/style_analysis/mr_new_vegas_categorized.json`
5. `docs/script_improvement/STYLE_GUIDE_JULIE.md`
6. `docs/script_improvement/STYLE_GUIDE_MR_NEW_VEGAS.md`

### Human Validation Required

1. Read 10 random Julie examples - do they capture her voice?
2. Read 10 random Mr. NV examples - do they capture his voice?
3. Can you tell them apart without being told which is which?

**Git Commit:** `docs(style): extract DJ style guides from voice transcripts`

**Git Tag:** `v0.9.1-style-guides`

---

## Style Guide Template

Use this structure for both `STYLE_GUIDE_JULIE.md` and `STYLE_GUIDE_MR_NEW_VEGAS.md`:

```markdown
# Style Guide: [DJ Name]

## Character Summary
[Brief description from MVP goal document]

## Song Introduction Patterns

### Pattern 1: [Name]
**Example:** "[Actual quote from transcript]"
**When to use:** [Context]
**Key elements:** [What makes this work]

### Pattern 2: [Name]
...

## Song Outro Patterns
[Same structure as intros]

## Vocabulary

### Words/Phrases to USE
| Word/Phrase | Example Usage | Notes |
|-------------|---------------|-------|
| | | |

### Words/Phrases to AVOID
| Word/Phrase | Why | Alternative |
|-------------|-----|-------------|
| | | |

## Sentence Structures

### Common Starters
- "[Example]"
- "[Example]"

### Common Endings
- "[Example]"
- "[Example]"

## Emotional Range
[How they express different moods]

## Pacing and Rhythm
[Notes on delivery speed, pauses, emphasis]

## Differentiation Checklist
[What makes this DJ unique vs. the other]

## Red Flags
[Signs that a script sounds wrong for this character]
```

---

## Notes for Implementation

### Transcript Format Handling

Julie's transcript has timestamps to remove:
```
00:00:00 Speaker: Now we've got Cass Daley...
```

Process:
1. Read each line
2. Strip timestamp prefix with regex: `^\d{2}:\d{2}:\d{2}\s+Speaker:\s*`
3. Keep the content

Mr. New Vegas's transcript may have similar formatting - verify and adjust.

### Categorization Heuristics

How to identify segment types:
- **Song Intro**: Contains artist name, song title, or "next song/tune"
- **Song Outro**: Follows a song, transitional language
- **Commentary**: General observations, stories, not about specific songs
- **Time**: Contains clock references
- **Weather**: Contains weather-related words
- **Other**: Doesn't fit above categories

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Phase 1 specification created |

---
---
---