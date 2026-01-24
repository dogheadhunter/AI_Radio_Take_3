# 📋 PHASE 5: Batch Pipeline

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Create the complete generation→audit→audio pipeline |
| **Duration** | 2-3 sessions |
| **Complexity** | High |
| **Dependencies** | Phases 2, 3, 4 complete |
| **Outputs** | `generate_with_audit.py`, complete workflow |

---

## Why This Phase Matters

This phase combines all previous work into a cohesive, GPU-efficient pipeline that:

1. Generates scripts with improved prompts
2. Audits scripts with quality validation
3. Generates audio only for passed scripts
4. Manages GPU memory by sequential model loading
5. Supports batch processing with checkpoints

---

## Checkpoints

### Checkpoint 5.1: Pipeline Architecture

**Goal:** Design the complete pipeline with GPU memory management

**Pipeline Stages:**

```
Stage 1: GENERATE SCRIPTS
├── Load Writer Model (Stheno 8B)
├── Load Lyrics Data
├── Load Song Catalog
├── For each song:
│   ├── Build prompt with lyrics context
│   ├── Generate script
│   └── Save to data/generated/scripts/
├── Unload Writer Model
└── Save checkpoint

Stage 2: AUDIT SCRIPTS
├── Load Auditor Model (Dolphin-Llama3)
├── For each generated script:
│   ├── Run audit
│   ├── Save result to data/audit/
│   └── Categorize as passed/failed
├── Unload Auditor Model
└── Generate audit summary

Stage 3: GENERATE AUDIO (passed only)
├── Load Chatterbox TTS
├── Load voice references
├── For each passed script:
│   └── Generate audio file
├── Unload TTS
└── Complete
```

**Checkpoint System:**
- After each stage, save progress to `data/pipeline_state.json`
- On resume, skip completed stages
- Within stages, track which items are processed

**Output:** `docs/script_improvement/PIPELINE_ARCHITECTURE.md`

**Success Criteria:**
- [x] All stages documented
- [x] GPU memory transitions clear
- [x] Checkpoint/resume strategy defined
- [x] Error handling planned for each stage

---

### Checkpoint 5.2: Script Generation Stage

**Goal:** Implement Stage 1 with batching and checkpoints

**Tasks:**
1. Create main pipeline script
2. Implement writer model loading/unloading
3. Implement batch script generation
4. Implement progress tracking
5. Implement checkpoint saving

**File: `scripts/generate_with_audit.py`**

```python
"""
Complete generation pipeline with auditing.

Usage:
    # Full run
    python scripts/generate_with_audit.py --intros --dj all
    
    # Test run (10 songs)
    python scripts/generate_with_audit.py --intros --dj julie --test --limit 10
    
    # Resume interrupted run
    python scripts/generate_with_audit.py --resume
    
    # Specific stage only
    python scripts/generate_with_audit.py --stage generate
    python scripts/generate_with_audit.py --stage audit
    python scripts/generate_with_audit.py --stage audio
"""
```

**Success Criteria:**
- [x] Script generation works in batch
- [x] Progress displayed during generation
- [x] Checkpoint saved after completion
- [x] Writer model properly unloaded
- [x] `--limit` flag works for testing

---

### Checkpoint 5.3: Audit Stage

**Goal:** Implement Stage 2 with result organization

**Tasks:**
1. Implement auditor model loading/unloading
2. Implement batch auditing
3. Organize results into passed/failed folders
4. Generate audit summary report
5. Handle auditor errors gracefully

**Audit Output Structure:**
```
data/audit/
├── julie/
│   ├── passed/
│   │   ├── artist-song_audit.json
│   │   └── ...
│   └── failed/
│       ├── artist-song_audit.json
│       └── ...
├── mr_new_vegas/
│   ├── passed/
│   └── failed/
└── summary.json  # Overall stats
```

**Summary Format:**
```json
{
  "timestamp": "2026-01-23T12:00:00",
  "total_scripts": 100,
  "passed": 85,
  "failed": 15,
  "pass_rate": 0.85,
  "by_dj": {
    "julie": {"passed": 42, "failed": 8},
    "mr_new_vegas": {"passed": 43, "failed": 7}
  },
  "common_issues": [
    {"issue": "modern slang", "count": 5},
    {"issue": "wrong character voice", "count": 4}
  ]
}
```

**Success Criteria:**
- [x] Auditor model properly loaded/unloaded
- [x] Results saved to correct folders
- [x] Summary generated with statistics
- [x] Common issues identified
- [x] Checkpoint updated after completion

---

### Checkpoint 5.4: Audio Generation Stage

**Goal:** Implement Stage 3 for passed scripts only

**Tasks:**
1. Filter to passed scripts only
2. Load TTS and voice references
3. Generate audio files
4. Handle TTS errors gracefully
5. Track completion

**Success Criteria:**
- [x] Only passed scripts get audio
- [x] Audio saved to `data/generated/intros/` etc.
- [x] Failed scripts remain as text only
- [x] Progress tracking works
- [x] Resume capability for interrupted audio generation

---

### Checkpoint 5.5: CLI and Options

**Goal:** Create comprehensive command-line interface

**CLI Options:**

```bash
# Content type selection
--intros          Generate song intros
--outros          Generate song outros
--time            Generate time announcements
--weather         Generate weather announcements
--all-content     Generate everything

# DJ selection
--dj julie|mr_new_vegas|all

# Mode selection
--test            Test mode (limit 10, specific songs)
--limit N         Process only N items
--random          Random selection (for testing)
--same-set        Use same N items as last --test run

# Stage control
--stage generate|audit|audio|all
--skip-audio      Generate and audit but skip audio
--resume          Resume from last checkpoint

# Output
--dry-run         Show what would be generated
--verbose         Detailed logging
```

**Success Criteria:**
- [x] All options implemented
- [x] `--test` and `--same-set` work for iteration
- [x] `--resume` correctly skips completed work
- [x] Help text is clear and complete

---

## Phase 5 Enhancements (January 24, 2026)

### Additional Features Beyond Original Spec

| Enhancement | Status | Description |
|-------------|--------|-------------|
| Automatic Regeneration Loop | ✅ COMPLETE | Up to 5 retries for failed scripts, achieves 100% pass rate through iterative refinement |
| DJ-Separated Audit Processing | ✅ COMPLETE | Each DJ audited separately to prevent cross-contamination |
| DJ-Separated Regeneration | ✅ COMPLETE | Failed scripts regenerated per-DJ to maintain voice consistency |
| Raised Quality Threshold | ✅ COMPLETE | Increased from 6.0 to 7.5 for better quality control |
| Improved Sanitization | ✅ COMPLETE | Fixed missing spaces after punctuation, UTF-8 mojibake handling |
| Early Exit Optimization | ✅ COMPLETE | Regeneration loop exits early when all scripts pass |

**Test Results:**
- Initial audit: 50% pass rate (10/20 scripts)
- After 3 regeneration retries: 100% pass rate (20/20 scripts)
- Julie: 70% initial → 100% after 2 retries
- Mr. New Vegas: 30% initial → 100% after 3 retries

**Git Commits:**
- `feat: add automatic regeneration loop with DJ-separated processing` (6013bca)
- `fix: improve sanitize_script to add spaces after punctuation and handle mojibake` (e79634e)
- `fix: raise audit pass threshold from 6.0 to 7.5` (196b98e)

---

## Phase 5 Gate: Pipeline Complete

### All Criteria Must Pass

| Criterion | Validation Method | Status |
|-----------|-------------------|--------|
| Pipeline architecture documented | `PIPELINE_ARCHITECTURE.md` exists | ✅ PASS |
| Generate stage works | `--stage generate` completes | ✅ PASS |
| Audit stage works | `--stage audit` completes | ✅ PASS |
| Audio stage works | `--stage audio` completes | ✅ PASS |
| Full pipeline works | Full run with `--limit 10` | ✅ PASS |
| Resume works | Interrupt and resume successfully | ✅ PASS |
| GPU memory managed | No OOM errors, models unload properly | ✅ PASS |
| Test mode works | `--test --same-set` reproduces results | ✅ PASS |

### Required Artifacts

1. `docs/script_improvement/PIPELINE_ARCHITECTURE.md`
2. `scripts/generate_with_audit.py`
3. `data/audit/summary.json` (sample from test run)
4. `data/pipeline_state.json` (checkpoint file)

### Integration Test

Run complete pipeline with 10 songs:
```bash
python scripts/generate_with_audit.py --intros --dj all --test --limit 10
```

Expected outcome:
- 20 scripts generated (10 each DJ)
- 16-20 scripts pass audit (80%+ pass rate)
- 16-20 audio files generated

**Git Commit:** `8f1a5b8 - feat(generation): complete Phase 5 batch pipeline with checkpoint system` ✅

**Git Tag:** `v0.9.5-pipeline` ✅

**Audit Report:** [Phase 5 Audit Report](../../docs/audits/Phase_5_Audit_Report.md) ✅

**Phase Status:** ✅ **COMPLETE - ALL GATES PASSED**

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Phase 5 specification created |
| 2026-01-24 | Phase 5 enhancements implemented (regeneration loop, raised threshold) |
| 2026-01-24 | Phase 5 audit completed - ALL CHECKPOINTS VERIFIED |

---
---
---
