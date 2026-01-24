# 🎙️ Script Generation Improvement — Master Plan

## Document Purpose
This document outlines a phased approach to improving DJ script generation for the AI Radio Station. The goal is to make Julie and Mr. New Vegas sound authentically like their Fallout counterparts through better prompts, a two-model generation/audit pipeline, and systematic quality validation.

---

## 📋 Table of Contents
1. [Current State Assessment](#current-state-assessment)
2. [Target State](#target-state)
3. [Architecture Overview](#architecture-overview)
4. [Phase Summary](#phase-summary)
5. [File Organization](#file-organization)
6. [Success Metrics](#success-metrics)
7. [Context Management](#context-management)

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
│  │   Metadata   �� ──▶ │   Model      │ ──▶ │   .txt       │                 │
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

## File Organization

### New Files to Create

```
AI_Radio_Take_3/
├── docs/
│   ├── script_improvement/
│   │   ├── MASTER_PLAN.md              # This document
│   │   ├── PHASE_1_STYLE_GUIDES.md     # Phase 1 specification
│   │   ├── PHASE_2_PROMPTS.md          # Phase 2 specification
│   │   ├── PHASE_3_AUDITOR.md          # Phase 3 specification
│   │   ├── PHASE_4_LYRICS.md           # Phase 4 specification
│   │   ├── PHASE_5_PIPELINE.md         # Phase 5 specification
│   │   ├── PHASE_6_REFINEMENT.md       # Phase 6 specification
│   │   ├── STYLE_GUIDE_JULIE.md        # Extracted Julie patterns
│   │   └── STYLE_GUIDE_MR_NEW_VEGAS.md # Extracted Mr. NV patterns
│   │
├── src/ai_radio/generation/
│   ├── prompts.py                      # Existing (keep for reference)
│   ├── prompts_v2.py                   # NEW: Improved prompts
│   ├── auditor.py                      # NEW: Audit system
│   ├── lyrics_parser.py                # NEW: Lyrics integration
│   └── batch_pipeline.py               # NEW: Full pipeline
│
├── scripts/
│   ├── generate_content.py             # Existing
│   ├── generate_with_audit.py          # NEW: Audited generation
│   └── extract_style_patterns.py       # NEW: Style extraction tool
│
├── data/
│   ├── generated/                      # Existing
│   │   ├── intros/
│   │   ├── outros/
│   │   └── ...
│   │
│   └── audit/                          # NEW: Audit results
│       ├── julie/
│       │   ├── passed/
│       │   └── failed/
│       └── mr_new_vegas/
│           ├── passed/
│           └── failed/
│
└── tests/
    └── generation/
        ├── test_prompts_v2.py          # NEW
        ├── test_auditor.py             # NEW
        └── test_lyrics_parser.py       # NEW
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

## Context Management

### Preventing Context Rot

Each phase is a separate document to:
1. Keep LLM context focused on one task
2. Allow resuming work without re-reading everything
3. Provide clear checkpoints and validation

### Session Protocol

**Starting a Phase:**
1. Read the MASTER_PLAN.md (this document)
2. Read the specific PHASE_X.md document
3. Review any previous phase outputs needed
4. Begin work on current checkpoint

**Completing a Phase:**
1. Validate all success criteria
2. Create required artifacts
3. Commit changes with appropriate message
4. Update phase document with completion status

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

## Quick Reference

### Phase Files

| Phase | Document | Status |
|-------|----------|--------|
| 1 | `PHASE_1_STYLE_GUIDES.md` | Not Started |
| 2 | `PHASE_2_PROMPTS.md` | Not Started |
| 3 | `PHASE_3_AUDITOR.md` | Not Started |
| 4 | `PHASE_4_LYRICS.md` | Not Started |
| 5 | `PHASE_5_PIPELINE.md` | Not Started |
| 6 | `PHASE_6_REFINEMENT.md` | Not Started |

### Command Cheat Sheet

```bash
# Run style extraction (Phase 1)
python scripts/extract_style_patterns.py

# Test new prompts (Phase 2)
python scripts/generate_with_audit.py --test --limit 10

# Run full pipeline (Phase 5)
python scripts/generate_with_audit.py --intros --dj all

# Review audit results
ls data/audit/julie/failed/
cat data/audit/julie/failed/song_id_audit.json
```

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Initial master plan created |

---

*This is the master plan. Individual phase specifications follow in separate documents.*

---
---
---
