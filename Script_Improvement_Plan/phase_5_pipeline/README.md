# Phase 5: Batch Pipeline

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Create the complete generation→audit→audio pipeline with GPU memory management |
| **Duration** | 2-3 sessions |
| **Complexity** | High |
| **Dependencies** | Phases 2, 3, 4 complete |
| **Outputs** | `generate_with_audit.py`, complete workflow, pipeline architecture docs |
| **Status** | ⬜ Not Started |

---

## Why This Phase Matters

This phase combines all previous work into a cohesive, production-ready pipeline that:

1. **Generates scripts** with improved prompts and lyrics context
2. **Audits scripts** with multi-stage validation
3. **Generates audio** only for passed scripts
4. **Manages GPU memory** by sequential model loading/unloading
5. **Supports batch processing** with checkpoints and resume capability

### Current State
- Individual components work in isolation
- Manual process to run each stage
- No coordination between stages
- GPU memory conflicts possible
- No checkpoint/resume capability

### Target State
- Fully automated pipeline
- Coordinated stage execution
- Proper GPU memory management
- Checkpoint/resume on interruption
- Comprehensive CLI interface

---

## Checkpoints

- [ ] **Checkpoint 5.1** - Pipeline Architecture Design
- [ ] **Checkpoint 5.2** - Script Generation Stage
- [ ] **Checkpoint 5.3** - Audit Stage
- [ ] **Checkpoint 5.4** - Audio Generation Stage
- [ ] **Checkpoint 5.5** - CLI and Options

---

## Pipeline Stages

### Stage 1: Generate Scripts
- Load writer model (Stheno 8B)
- Load lyrics data
- Generate all scripts
- Unload writer model
- Save checkpoint

### Stage 2: Audit Scripts
- Load auditor model (Dolphin-Llama3)
- Run validation on all scripts
- Organize into passed/failed
- Unload auditor model
- Generate summary report

### Stage 3: Generate Audio
- Load TTS model (Chatterbox)
- Generate audio for passed scripts only
- Unload TTS model
- Complete

---

## Deliverables

### Code
- `scripts/generate_with_audit.py` - Main pipeline script
- `docs/script_improvement/PIPELINE_ARCHITECTURE.md` - Architecture doc
- Updated pipeline classes with checkpoint support

### Data
- `data/pipeline_state.json` - Checkpoint file
- `data/audit/summary.json` - Audit statistics

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Pipeline completes without errors | 100% |
| GPU memory managed correctly | No OOM errors |
| Resume works after interruption | 100% |
| Full run (10 songs) | <30 minutes |
| Pass rate | >80% |

---

## Dependencies

### Input
- Validated generation pipeline (Phase 3)
- Lyrics integration (Phase 4)
- Updated prompts (Phase 2)

### Output
- Complete batch pipeline
- CLI interface
- Checkpoint system

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GPU OOM errors | Medium | High | Sequential model loading |
| Long generation times | High | Medium | Batch optimization, caching |
| Pipeline interruptions | Medium | Medium | Checkpoint/resume system |
| Failed audits | Medium | Low | Regeneration capability |

---

## Timeline Estimate

| Checkpoint | Estimated Time |
|------------|----------------|
| 5.1 - Architecture | 2 hours |
| 5.2 - Script Generation | 3-4 hours |
| 5.3 - Audit Stage | 2-3 hours |
| 5.4 - Audio Stage | 2-3 hours |
| 5.5 - CLI | 2 hours |
| **Total** | **11-14 hours (2-3 sessions)** |

---

## Phase Status

**Current Status:** ⬜ Not Started

**Blockers:** None (Phases 2, 3, 4 complete)

**Next Action:** Begin Checkpoint 5.1 - Pipeline Architecture Design

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Phase 5 README created from Phase 5 specification |
