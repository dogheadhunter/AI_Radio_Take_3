# Auditor Validation

This document describes how to run an auditor integration test and collect human validation data.

## Steps

1. Generate scripts and run auditor:
   - python scripts/generate_with_audit.py --intros --dj all --test --limit 10
   - Output will be saved to `data/audit/<timestamp>/`
2. Collect samples for human review:
   - python scripts/collect_audit_samples.py --audit-dir data/audit/<timestamp> --out data/manual_validation --passed 5 --failed 5
   - This writes `samples_passed.json` and `samples_failed.json` to `data/manual_validation/`
3. Human review:
   - Manually review each sample and record whether you agree with the auditor's pass/fail decision and add notes.
   - Create a CSV or JSON file with fields: script_id, auditor_passed, human_passed, notes
4. Compute agreement metrics:
   - Agreement rate = (# agreements) / (total reviewed)
   - False positive = # auditor_passed but human_failed / total
   - False negative = # auditor_failed but human_passed / total

## Success thresholds

- Agreement rate > 80%
- False positives < 10%
- False negatives < 20%

## Notes

- Use the `--test` flag for automated dry-run with deterministic auditor behavior.
- When ready for real integration, omit `--test` to use the real auditor model.
