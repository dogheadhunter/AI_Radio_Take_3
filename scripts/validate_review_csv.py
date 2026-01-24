"""Validate that a review CSV has human decisions filled for a minimum number of samples.

Usage:
  python -m scripts.validate_review_csv --review data/manual_validation/review.csv --min-reviewed 8
"""
import argparse
from pathlib import Path
import csv


def validate(review_path: Path, min_reviewed: int = 8):
    with open(review_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    reviewed = [r for r in rows if r.get('human_passed', '').strip() != '']
    return len(reviewed), len(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--review', required=True)
    parser.add_argument('--min-reviewed', type=int, default=8)
    args = parser.parse_args()

    reviewed, total = validate(Path(args.review), args.min_reviewed)
    print(f"Total rows: {total}, reviewed: {reviewed}")
    if reviewed < args.min_reviewed:
        print('Not enough reviews yet.')
        return 1
    print('Sufficient reviews present.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())