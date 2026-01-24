# Checkpoint 6.2: Prompt Refinement Cycle

## Status
**NOT STARTED** ⬜

## Goal
Improve prompts based on test results through iterative refinement cycles.

## Refinement Process

```
1. IDENTIFY ISSUES
   └── Review failed scripts and low-scoring passes

2. DIAGNOSE ROOT CAUSE
   ├── Prompt too vague?
   ├── Examples not representative?
   ├── Missing constraints?
   └── Wrong emphasis?

3. MODIFY PROMPT
   └── Make ONE change at a time

4. TEST WITH SAME SONGS
   └── Use --same-set to compare directly

5. COMPARE RESULTS
   ├── Did quality improve?
   ├── Any regressions?
   └── Keep or revert change?

6. REPEAT until quality target met
```

## Common Issues and Fixes

| Issue | Possible Cause | Fix to Try |
|-------|----------------|------------|
| Too generic | Not enough examples | Add 2-3 more examples |
| Wrong vocabulary | Era constraints too weak | Add specific forbidden words |
| Forced catchphrases | Examples overweight catchphrases | Replace with varied examples |
| Too long | No length guidance | Add explicit length constraint |
| Wrong character | Examples not distinct enough | Add differentiation instructions |

## Refinement Log Template

```markdown
## Refinement Log

### Iteration 1
**Date:**
**Issue identified:** 
**Root cause hypothesis:** 
**Change made:** 
**Test results:** 
- Before: X/10 average
- After: Y/10 average
**Decision:** Keep / Revert

### Iteration 2
...
```

## Success Criteria

| Criterion | Status |
|-----------|--------|
| At least 2 refinement cycles completed | ⬜ |
| Each change tested with `--same-set` | ⬜ |
| Refinement log maintained | ⬜ |
| Quality improving or stable | ⬜ |

## Next Steps
Proceed to Checkpoint 6.3 for auditor calibration.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 6 specification |
