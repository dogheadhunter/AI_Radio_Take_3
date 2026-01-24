# Checkpoint 6.4: Extended Test Run

## Status
**NOT STARTED** ⬜

## Goal
Validate system at larger scale before full generation.

## Tasks

### 1. Run Pipeline on 50 Songs
- [ ] Random selection from catalog
- [ ] Both DJs represented
- [ ] Full pipeline execution
- [ ] Collect all statistics

### 2. Review Audit Results
- [ ] Check pass rate (>80% target)
- [ ] Review audit summary
- [ ] Identify any new issue patterns
- [ ] Verify consistency with smaller tests

### 3. Spot-Check Quality
- [ ] Randomly select 10 scripts
- [ ] Manual review for quality
- [ ] All should be acceptable
- [ ] Note any remaining issues

### 4. Verify System Performance
- [ ] GPU memory managed correctly
- [ ] No crashes or errors
- [ ] Reasonable execution time
- [ ] Resume capability works

## Test Command

```bash
python scripts/generate_with_audit.py --intros --dj all --limit 50
```

## Expected Results
- ~100 scripts generated (50 each DJ)
- >80 scripts pass audit
- <20 scripts in failed folder
- Audio generated for passed scripts

## Spot-Check Protocol
1. Randomly select 5 passed Julie scripts
2. Randomly select 5 passed Mr. NV scripts
3. Review each for quality
4. All should be acceptable (minor issues OK)

## Success Criteria

| Criterion | Status |
|-----------|--------|
| 50 songs processed successfully | ⬜ |
| Pass rate >80% | ⬜ |
| Spot-check: 8/10 acceptable or better | ⬜ |
| No new systematic issues discovered | ⬜ |
| GPU memory managed correctly throughout | ⬜ |

## Next Steps
Proceed to Checkpoint 6.5 for full content generation.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 6 specification |
