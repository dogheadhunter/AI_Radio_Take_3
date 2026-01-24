# Checkpoint 5.3: Audit Stage

## Status
**NOT STARTED** ⬜

## Goal
Implement Stage 2 with result organization, summary generation, and checkpoint update.

## Tasks

### 1. Implement Auditor Model Loading
- [ ] Load Dolphin-Llama3 model
- [ ] Verify model loaded successfully
- [ ] Implement proper model unloading
- [ ] Handle loading errors

### 2. Implement Batch Auditing
- [ ] Load generated scripts
- [ ] Run rule-based validation
- [ ] Run character validation
- [ ] Track pass/fail results

### 3. Organize Results
- [ ] Create `data/audit/{dj}/passed/` folders
- [ ] Create `data/audit/{dj}/failed/` folders
- [ ] Save audit results to appropriate folders
- [ ] Maintain file naming consistency

### 4. Generate Audit Summary
- [ ] Calculate overall statistics
- [ ] Calculate per-DJ statistics
- [ ] Identify common failure patterns
- [ ] Save to `data/audit/summary.json`

### 5. Update Checkpoint
- [ ] Update pipeline state
- [ ] Include audit statistics
- [ ] Mark audit stage complete
- [ ] Enable resume from audio stage

## Audit Output Structure

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
└── summary.json
```

## Summary Format

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
    {"issue": "flowery language", "count": 5},
    {"issue": "character bleed", "count": 4}
  ]
}
```

## Success Criteria

| Criterion | Status |
|-----------|--------|
| Auditor model properly loaded/unloaded | ⬜ |
| Results saved to correct folders | ⬜ |
| Summary generated with statistics | ⬜ |
| Common issues identified | ⬜ |
| Checkpoint updated after completion | ⬜ |

## Next Steps
Proceed to Checkpoint 5.4 to implement the audio generation stage.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 5 specification |
