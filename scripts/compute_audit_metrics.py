"""Compute human/auditor agreement metrics from a review CSV.

Usage:
  python -m scripts.compute_audit_metrics --review data/manual_validation/review.csv --auto-mark

If --auto-mark is provided and thresholds are met, this script will update
`Script_Improvment_Plan/Phase/Phase_three.md` to mark the Checkpoint 3.4 boxes as complete
and commit & push the change.
"""
import argparse
from pathlib import Path
import csv
import subprocess


def compute_metrics(csv_path: Path):
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Normalize boolean fields
            a = r.get('auditor_passed', '').strip().lower()
            h = r.get('human_passed', '').strip().lower()
            if h == 'true' or h == '1' or h == 'yes':
                human = True
            elif h == 'false' or h == '0' or h == 'no' or h == '':
                # empty treated as None
                human = None if h == '' else False
            else:
                human = None

            auditor = True if a in ('true', '1', 'yes') else False
            rows.append({'script_id': r.get('script_id'), 'auditor': auditor, 'human': human})

    # Filter to only rows where human decision exists
    validated = [r for r in rows if r['human'] is not None]
    total_reviewed = len(validated)

    if total_reviewed == 0:
        return {'total_reviewed': 0, 'agreement_rate': 0.0, 'false_positive_rate': 0.0, 'false_negative_rate': 0.0}

    agreements = sum(1 for r in validated if r['auditor'] == r['human'])
    agreement_rate = agreements / total_reviewed

    false_positives = sum(1 for r in validated if r['auditor'] and not r['human'])
    false_negatives = sum(1 for r in validated if not r['auditor'] and r['human'])

    false_positive_rate = false_positives / total_reviewed
    false_negative_rate = false_negatives / total_reviewed

    return {
        'total_reviewed': total_reviewed,
        'agreement_rate': agreement_rate,
        'false_positive_rate': false_positive_rate,
        'false_negative_rate': false_negative_rate,
        'agreements': agreements,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
    }


def auto_mark_phase(metrics: dict, md_path: Path, thresholds: dict):
    # Check thresholds
    ok = True
    if metrics['agreement_rate'] < thresholds['agreement_rate']:
        ok = False
    if metrics['false_positive_rate'] > thresholds['false_positive_rate']:
        ok = False
    if metrics['false_negative_rate'] > thresholds['false_negative_rate']:
        ok = False

    if not ok:
        print('Metrics did not meet thresholds; not updating phase file.')
        return False

    # Update Phase_three.md: mark the remaining 3 checkboxes as done
    text = md_path.read_text(encoding='utf-8')
    text = text.replace('- [ ] Human/auditor agreement >80%', '- [x] Human/auditor agreement >80%')
    text = text.replace('- [ ] False positives (passed but bad) <10%', '- [x] False positives (passed but bad) <10%')
    text = text.replace('- [ ] False negatives (failed but good) <20%', '- [x] False negatives (failed but good) <20%')
    md_path.write_text(text, encoding='utf-8')

    # Commit & push
    subprocess.check_call(['git', 'add', str(md_path)])
    subprocess.check_call(['git', 'commit', '-m', 'test(audit): mark Checkpoint 3.4 complete after successful human validation'])
    subprocess.check_call(['git', 'push'])
    print('Phase file updated and pushed.')
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--review', required=True, help='Path to review CSV')
    parser.add_argument('--auto-mark', action='store_true', help='Auto-mark Phase 3 as complete if thresholds met')
    parser.add_argument('--md-path', default='Script_Improvment_Plan/Phase/Phase_three.md')
    parser.add_argument('--agree-threshold', type=float, default=0.8)
    parser.add_argument('--fp-threshold', type=float, default=0.1)
    parser.add_argument('--fn-threshold', type=float, default=0.2)
    args = parser.parse_args()

    metrics = compute_metrics(Path(args.review))
    print('Metrics:', metrics)

    if args.auto_mark:
        thresholds = {'agreement_rate': args.agree_threshold, 'false_positive_rate': args.fp_threshold, 'false_negative_rate': args.fn_threshold}
        auto_mark_phase(metrics, Path(args.md_path), thresholds)


if __name__ == '__main__':
    main()
