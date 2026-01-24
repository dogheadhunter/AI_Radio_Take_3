"""Convert review CSV to readable Markdown format."""
import csv
from pathlib import Path
import argparse


def csv_to_markdown(csv_path: Path, md_path: Path):
    """Convert review CSV to Markdown with readable formatting."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    md_lines = [
        "# Script Review for Human Validation",
        "",
        f"**Total Scripts:** {len(rows)}",
        "",
        "## Instructions",
        "",
        "For each script below:",
        "1. Read the script text carefully",
        "2. Decide if it passes quality standards (True/False)",
        "3. Add your decision and notes to the CSV file",
        "",
        "**Quality Criteria:**",
        "- ✅ Julie: Casual, rambling, questioning (\"I'm curious...\", \"y'all\", \"folks\")",
        "- ✅ Mr. New Vegas: Smooth, romantic, formal (\"Ladies and gentlemen\", \"allow me to introduce\")",
        "- ❌ Emojis, modern slang (\"awesome\", \"lit\"), generic clichés (\"welcome back to the show\")",
        "",
        "---",
        "",
    ]
    
    for i, row in enumerate(rows, 1):
        script_id = row.get('script_id', 'unknown')
        auditor_passed = row.get('auditor_passed', 'unknown')
        script_text = row.get('script_text', '[No text]')
        
        # Determine DJ from script_id
        dj = 'Unknown'
        if 'julie' in script_id.lower():
            dj = 'Julie'
        elif 'vegas' in script_id.lower() or 'mr_new_vegas' in script_id.lower():
            dj = 'Mr. New Vegas'
        
        md_lines.extend([
            f"## Script {i}: `{script_id}`",
            "",
            f"**DJ:** {dj}  ",
            f"**Auditor Decision:** {auditor_passed}  ",
            f"**Your Decision:** _(Fill in CSV: True/False)_  ",
            f"**Your Notes:** _(Fill in CSV)_",
            "",
            "**Script Text:**",
            "",
            f"> {script_text}",
            "",
            "---",
            "",
        ])
    
    md_lines.append(f"\n**After reviewing all {len(rows)} scripts, update the CSV file with your decisions.**")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"Created readable review document: {md_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='data/manual_validation/review.csv', help='Input CSV path')
    parser.add_argument('--out', default='data/manual_validation/REVIEW.md', help='Output Markdown path')
    args = parser.parse_args()
    
    csv_to_markdown(Path(args.csv), Path(args.out))


if __name__ == '__main__':
    main()
