# Checkpoint 5.1: Pipeline Architecture

## Status
**NOT STARTED** ⬜

## Goal
Design the complete pipeline with GPU memory management, stage coordination, and checkpoint/resume capability.

## Tasks

### 1. Document Pipeline Stages
- [ ] Define all three stages (generate, audit, audio)
- [ ] Document GPU memory requirements per stage
- [ ] Plan model loading/unloading sequence
- [ ] Design data flow between stages

### 2. Design Checkpoint System
- [ ] Define checkpoint file format
- [ ] Determine what state to save
- [ ] Plan resume logic
- [ ] Handle partial completion

### 3. Plan Error Handling
- [ ] Stage-level error handling
- [ ] Item-level error handling (single song fails)
- [ ] Recovery strategies
- [ ] Logging and diagnostics

### 4. Design Progress Tracking
- [ ] Progress indicators per stage
- [ ] ETA calculation
- [ ] Statistics collection
- [ ] Real-time feedback

## Pipeline Architecture

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
│   ├── Run rule-based validation
│   ├── Run character validation
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

## Checkpoint File Format

```json
{
  "timestamp": "2026-01-23T12:00:00",
  "stages_completed": ["generate", "audit"],
  "current_stage": "audio",
  "generation": {
    "total": 100,
    "completed": 100,
    "failed": 2
  },
  "audit": {
    "total": 100,
    "passed": 85,
    "failed": 15
  },
  "audio": {
    "total": 85,
    "completed": 40,
    "remaining": 45
  }
}
```

## GPU Memory Management

| Stage | Model | GPU Memory | Duration (est) |
|-------|-------|------------|----------------|
| Generate | Stheno 8B | ~8GB | 2-3 hours |
| Audit | Dolphin-Llama3 | ~6GB | 1-2 hours |
| Audio | Chatterbox | ~4GB | 1-2 hours |

**Strategy:** Sequential loading ensures only one model in GPU at a time.

## Output Artifacts

- [ ] `docs/script_improvement/PIPELINE_ARCHITECTURE.md`
- [ ] Architecture diagrams
- [ ] Checkpoint format specification
- [ ] Error handling strategies

## Success Criteria

| Criterion | Status |
|-----------|--------|
| All stages documented | ⬜ |
| GPU memory transitions clear | ⬜ |
| Checkpoint/resume strategy defined | ⬜ |
| Error handling planned for each stage | ⬜ |

## Next Steps
Proceed to Checkpoint 5.2 to implement the script generation stage.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 5 specification |
