"""Transfer human review decisions from Markdown back to CSV."""
import re
from pathlib import Path
import csv
import argparse


def parse_markdown_reviews(md_path: Path):
    """Extract decisions and notes from REVIEW.md."""
    content = md_path.read_text(encoding='utf-8')
    
    # Pattern to match each script section
    pattern = r'## Script \d+: `([^`]+)`.*?\*\*Your Decision:\*\* _([^_]+)_.*?\*\*Your Notes:\*\* _([^_]+)_'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    reviews = {}
    for script_id, decision, notes in matches:
        # Normalize decision to True/False
        decision_clean = decision.strip().lower()
        passed = decision_clean in ['pass', 'true', 'yes']
        
        reviews[script_id] = {
            'human_passed': passed,
            'notes': notes.strip()
        }
    
    return reviews


def update_csv_with_reviews(csv_path: Path, reviews: dict):
    """Update CSV with human review decisions."""
    # Read existing CSV
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    # Update rows with review data
    for row in rows:
        script_id = row['script_id']
        if script_id in reviews:
            row['human_passed'] = reviews[script_id]['human_passed']
            row['notes'] = reviews[script_id]['notes']
    
    # Write updated CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Updated {len(reviews)} reviews in {csv_path}")
    return len(reviews)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--md', default='data/manual_validation/REVIEW.md', help='Markdown file with reviews')
    parser.add_argument('--csv', default='data/manual_validation/review.csv', help='CSV file to update')
    args = parser.parse_args()
    
    reviews = parse_markdown_reviews(Path(args.md))
    
    if not reviews:
        print("⚠️  No reviews found in Markdown file")
        return 1
    
    print(f"Found {len(reviews)} reviews in Markdown")
    for script_id, data in reviews.items():
        status = "✅ PASS" if data['human_passed'] else "❌ FAIL"
        print(f"  {script_id}: {status} - {data['notes'][:50]}...")
    
    update_csv_with_reviews(Path(args.csv), reviews)
    print("\n✅ CSV updated successfully!")


if __name__ == '__main__':
    main()
