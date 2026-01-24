# Auditor Human Review Instructions

This document explains how to perform human validation for the auditor and how to record results.

## Goal
Collect human judgements for a representative set of scripts so we can compute agreement metrics and decide whether the auditor meets quality thresholds.

## Files
- `data/manual_validation/samples_passed.json` — JSON array of passed-script audit results selected for review.
- `data/manual_validation/samples_failed.json` — JSON array of failed-script audit results selected for review.
- `data/manual_validation/review.csv` — CSV template for reviewers. Columns: `script_id`, `auditor_passed`, `human_passed`, `notes`.

## How to review
1. Open `data/manual_validation/review.csv` in Excel, Google Sheets, or your editor.
2. For each row, listen to the script or read the script under `data/audit/<timestamp>/passed` or `failed` as appropriate.
3. Set `human_passed` to `True` if you agree the script should be accepted, `False` if you think it should be rejected.
4. Add brief `notes` explaining your decision (one sentence is fine).

## Example CSV rows
script_id,auditor_passed,human_passed,notes
song_1_julie,True,True,Good voice and era-appropriate
song_2_mr_new_vegas,False,True,Too strict on era; acceptable language

## After review
- Save the CSV back to `data/manual_validation/review.csv`.
- Run the metric script to compute agreement and optionally auto-mark the phase:

```
python -m scripts.compute_audit_metrics --review data/manual_validation/review.csv --auto-mark
```

If the thresholds are met, the script will update `Script_Improvment_Plan/Phase/Phase_three.md` and commit/push the change.

## Thresholds
- Agreement rate > 80% (0.8)
- False positives < 10% (0.1)
- False negatives < 20% (0.2)

## Notes
- If there are too few failed samples (e.g., zero), consider running a non-test audit run with `scripts/generate_with_audit.py` in non-test mode to surface real failures, or create additional purposely-bad scripts to evaluate auditor sensitivity.
