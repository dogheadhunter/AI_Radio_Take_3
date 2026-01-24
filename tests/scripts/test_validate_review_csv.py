from pathlib import Path
from scripts.validate_review_csv import validate
import csv


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['script_id', 'auditor_passed', 'human_passed', 'notes'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def test_validate_insufficient(tmp_path):
    p = tmp_path / 'review.csv'
    rows = [
        {'script_id': 'a', 'auditor_passed': 'True', 'human_passed': 'True'},
        {'script_id': 'b', 'auditor_passed': 'True', 'human_passed': ''},
    ]
    write_csv(p, rows)
    reviewed, total = validate(p)
    assert reviewed == 1
    assert total == 2
