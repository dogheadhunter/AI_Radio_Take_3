# 🎙️ Script Generation Improvement — Master Plan

## Document Purpose
This document outlines the vision and high-level architecture for improving DJ script generation for the AI Radio Station. The goal is to make Julie and Mr. New Vegas sound authentically like their Fallout counterparts through better prompts, a two-model generation/audit pipeline, and systematic quality validation.

**Read this at project start** to understand the overall vision. For current status, see `CURRENT_STATUS.md`. For critical learnings, see `CRITICAL_CONTEXT.md`.

---

## Current State Assessment

### What Exists
- ✅ Working MVP with 24 hours of generated scripts
- ✅ Generation pipeline (LLM → TTS)
- ✅ Julie and Mr. New Vegas voice line transcripts (~30 min and ~20 min)
- ✅ Music library with paired lyrics files
- ✅ Basic prompt templates in `src/ai_radio/generation/prompts.py`

### What's Wrong
| Problem | Example |
|---------|---------|
| Scripts sound generic | "Ladies and gentlemen, boys and girls, let's get this party started!" |
| Wrong era vocabulary | "Rise and shine, beautiful people!" (modern influencer speak) |
| Emojis in scripts | "🌅 Rise and shine!" |
| No character voice | Could be any DJ, not specifically Julie or Mr. New Vegas |
| Forced catchphrases | Previous attempts made catchphrases appear in every script |
| No quality validation | Bad scripts make it through without review |

### Root Cause
The current prompts are too vague:
```python
# Current (bad)
traits = "A friendly, earnest DJ who uses warm, conversational language and mild filler words."
```

This gives the LLM no concrete examples of what Julie actually sounds like.

---

## Target State

### What Success Looks Like

**Julie Scripts Should:**
- Sound conversational and rambling (like talking to a friend)
- Include natural filler words ("um", "like", "you know") without forcing them
- Reference songs with personal opinions and connections
- Feel warm, hopeful, and slightly vulnerable
- Match the pacing and vocabulary from her actual voice lines

**Mr. New Vegas Scripts Should:**
- Sound smooth, deliberate, and romantic
- Use 1950s vocabulary naturally ("swell", "dig", "baby")
- Address the listener intimately
- Feel timeless and sophisticated
- Match the suave delivery from his actual voice lines

**The System Should:**
- Generate scripts using a writer model
- Audit scripts using a separate auditor model
- Flag failures with notes (not force immediate regeneration)
- Process in batches to manage GPU memory
- Support lyrics integration for richer intros

---

## Architecture Overview

### Two-Model Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GENERATION PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 1: SCRIPT GENERATION                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Song       │     │   Writer     │     │   Script     │                 │
│  │   Metadata   │ ──▶ │   Model      │ ──▶ │   .txt       │                 │
│  │   + Lyrics   │     │ (Stheno 8B)  │     │   Files      │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                   │                          │
│                              ┌────────────────────┘                          │
│                              ▼                                               │
│  PHASE 2: SCRIPT AUDITING   (After writer model unloaded)                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Script     │     │   Auditor    │     │   Audit      │                 │
│  │   .txt       │ ──▶ │   Model      │ ──▶ │   Results    │                 │
│  │   Files      │     │ (Dolphin)    │     │   + Notes    │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                   │                          │
│                              ┌────────────────────┘                          │
│                              ▼                                               │
│  PHASE 3: AUDIO GENERATION  (After auditor model unloaded)                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Passed     │     │  Chatterbox  │     │   Audio      │                 │
│  │   Scripts    │ ──▶ │   TTS        │ ──▶ │   .wav       │                 │
│  │   Only       │     │              │     │   Files      │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### GPU Memory Management

```
Step 1: Load Writer Model (Stheno 8B)
        ↓ Generate all scripts
        ↓ Unload Writer Model

Step 2: Load Auditor Model (Dolphin-Llama3)
        ↓ Audit all scripts
        ↓ Unload Auditor Model

Step 3: Load Chatterbox TTS
        ↓ Generate audio for PASSED scripts only
        ↓ Complete
```

---

## Phase Summary

| Phase | Name | Goal | Deliverables |
|-------|------|------|--------------|
| **1** | Style Guide Extraction | Extract patterns from voice transcripts | `STYLE_GUIDE_JULIE.md`, `STYLE_GUIDE_MR_NEW_VEGAS.md` |
| **2** | Prompt Engineering | Create new prompt templates using style guides | `prompts_v2.py`, improved character prompts |
| **3** | Auditor System | Build the script auditing pipeline | `auditor.py`, audit criteria, scoring system |
| **4** | Lyrics Integration | Connect lyrics to generation pipeline | Lyrics parser, context injection |
| **5** | Batch Pipeline | Full generation→audit→audio workflow | `generate_with_audit.py`, batch processing |
| **6** | Testing & Refinement | Iterate until quality targets met | Refined prompts, validated outputs |

### Phase Dependencies

```
Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──┐
                                  │
Phase 4 (can parallel Phase 2-3) ─┤
                                  │
                                  ▼
                              Phase 5 ──▶ Phase 6
```

---

## Success Metrics

### Overall Project Success

| Metric | Target | Measurement |
|--------|--------|-------------|
| Audit pass rate | >80% | Scripts passing auditor on first attempt |
| Character recognition | >90% | Human can identify DJ from script alone |
| Era appropriateness | >95% | No modern slang or emojis |
| Natural flow | >85% | Scripts don't sound forced or clunky |

### Per-Phase Gates

Each phase has specific success criteria that must be met before advancing. See individual phase documents for details.

---

## Model Configuration

### Writer Model: fluffy/I3-8b-stheno-v3.2
- **Purpose**: Creative script generation
- **Strengths**: Character voice, creative writing
- **Token limit**: Consider for prompt length

### Auditor Model: dolphin-llama3
- **Purpose**: Quality validation and scoring
- **Strengths**: Instruction following, analysis
- **Output**: Score (1-10) with notes

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-24 | Master plan created from original Plan_Summery.md |

---

*This is the master plan. For current status, see CURRENT_STATUS.md. For critical learnings, see CRITICAL_CONTEXT.md. For detailed checkpoints, see individual phase folders.*
