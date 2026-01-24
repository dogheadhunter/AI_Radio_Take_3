# Checkpoint 6.3: Auditor Calibration

## Status
**NOT STARTED** ⬜

## Goal
Ensure auditor is accurately identifying quality issues through calibration.

## Calibration Process

1. Review all auditor decisions from test runs
2. Identify false positives (passed but bad)
3. Identify false negatives (failed but good)
4. Adjust auditor prompt if needed

## Analysis Tables

### False Positive Analysis
- Scripts that passed audit but you'd reject
- Why did auditor miss the issue?
- What should auditor look for?

### False Negative Analysis
- Scripts that failed audit but are actually fine
- Why did auditor flag it incorrectly?
- Is the auditor too strict on certain criteria?

## Calibration Adjustments

| Problem | Adjustment |
|---------|------------|
| Too many false positives | Add specific issues to check for |
| Too many false negatives | Relax overly strict criteria |
| Wrong scoring weights | Adjust criteria weights |
| Inconsistent scores | Add more examples to auditor prompt |

## Success Criteria

| Criterion | Status |
|-----------|--------|
| False positive rate < 10% | ⬜ |
| False negative rate < 20% | ⬜ |
| Auditor prompt refined if needed | ⬜ |
| Calibration documented | ⬜ |

## Next Steps
Proceed to Checkpoint 6.4 for extended test run.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 6 specification |
