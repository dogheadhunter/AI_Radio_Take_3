"""Generate a CSV template for human review from collected audit samples.

Usage:
  python -m scripts.generate_review_csv --samples data/manual_validation --out data/manual_validation/review.csv
"""
import argparse
from pathlib import Path
import json
import csv


def generate_csv(samples_dir: Path, out_path: Path):
    passed_file = samples_dir / 'samples_passed.json'
    failed_file = samples_dir / 'samples_failed.json'

    passed = json.loads(passed_file.read_text(encoding='utf-8')) if passed_file.exists() else []
    failed = json.loads(failed_file.read_text(encoding='utf-8')) if failed_file.exists() else []

    rows = []
    for p in passed:
        rows.append({
            'script_id': p.get('script_id'),
            'auditor_passed': True,
            'human_passed': '',
            'notes': ''
        })
    for f in failed:
        rows.append({
            'script_id': f.get('script_id'),
            'auditor_passed': False,
            'human_passed': '',
            'notes': ''
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['script_id', 'auditor_passed', 'human_passed', 'notes'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', default='data/manual_validation')
    parser.add_argument('--out', default='data/manual_validation/review.csv')
    args = parser.parse_args()
    out = generate_csv(Path(args.samples), Path(args.out))
    print('Wrote review CSV to', out)


if __name__ == '__main__':
    main()
