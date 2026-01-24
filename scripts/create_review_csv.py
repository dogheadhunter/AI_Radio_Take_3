"""Create review CSV from samples for human validation."""
from pathlib import Path
import csv
import json
import argparse


def create_review_csv(samples_dir: Path, output_csv: Path):
    """Create review CSV from samples_passed.json and samples_failed.json."""
    rows = []
    
    # Load passed samples
    passed_file = samples_dir / 'samples_passed.json'
    if passed_file.exists():
        samples = json.loads(passed_file.read_text(encoding='utf-8'))
        for s in samples:
            rows.append({
                'script_id': s.get('script_id', ''),
                'auditor_passed': True,
                'human_passed': '',
                'notes': '',
                'script_text': s.get('script_content', ''),
            })
    
    # Load failed samples
    failed_file = samples_dir / 'samples_failed.json'
    if failed_file.exists():
        samples = json.loads(failed_file.read_text(encoding='utf-8'))
        for s in samples:
            rows.append({
                'script_id': s.get('script_id', ''),
                'auditor_passed': False,
                'human_passed': '',
                'notes': '',
                'script_text': s.get('script_content', ''),
            })
    
    # Write CSV
    if rows:
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['script_id', 'auditor_passed', 'human_passed', 'notes', 'script_text'])
            writer.writeheader()
            writer.writerows(rows)
        print(f"Created review CSV with {len(rows)} scripts: {output_csv}")
    else:
        print("No samples found to create review CSV")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples-dir', default='data/manual_validation', help='Directory with samples JSONs')
    parser.add_argument('--out', default='data/manual_validation/review.csv', help='Output CSV path')
    args = parser.parse_args()
    
    create_review_csv(Path(args.samples_dir), Path(args.out))


if __name__ == '__main__':
    main()
