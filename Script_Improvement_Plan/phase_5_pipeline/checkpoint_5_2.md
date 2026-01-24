# Checkpoint 5.2: Script Generation Stage

## Status
**NOT STARTED** ⬜

## Goal
Implement Stage 1 with batching, progress tracking, and checkpoint saving.

## Tasks

### 1. Create Main Pipeline Script
- [ ] Create `scripts/generate_with_audit.py`
- [ ] Implement command-line argument parsing
- [ ] Add stage selection logic
- [ ] Implement main execution flow

### 2. Implement Writer Model Loading
- [ ] Load Stheno 8B model
- [ ] Verify model loaded successfully
- [ ] Implement proper model unloading
- [ ] Handle loading errors

### 3. Implement Batch Script Generation
- [ ] Load song catalog
- [ ] Load lyrics data (if available)
- [ ] Batch generate by DJ (prevent character bleed)
- [ ] Save scripts to `data/generated/scripts/`

### 4. Implement Progress Tracking
- [ ] Display current song being processed
- [ ] Show completion percentage
- [ ] Estimate time remaining
- [ ] Log statistics

### 5. Implement Checkpoint Saving
- [ ] Save state after generation complete
- [ ] Include statistics in checkpoint
- [ ] Enable resume from this stage
- [ ] Handle checkpoint errors

## Implementation

### File: `scripts/generate_with_audit.py`

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

## Success Criteria

| Criterion | Status |
|-----------|--------|
| Script generation works in batch | ⬜ |
| Progress displayed during generation | ⬜ |
| Checkpoint saved after completion | ⬜ |
| Writer model properly unloaded | ⬜ |
| `--limit` flag works for testing | ⬜ |

## Next Steps
Proceed to Checkpoint 5.3 to implement the audit stage.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 5 specification |
