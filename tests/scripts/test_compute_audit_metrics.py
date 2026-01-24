import csv
from pathlib import Path
from scripts.compute_audit_metrics import compute_metrics


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['script_id', 'auditor_passed', 'human_passed', 'notes'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def test_compute_metrics_simple(tmp_path):
    csvp = tmp_path / 'review.csv'
    rows = [
        {'script_id': 'a', 'auditor_passed': 'True', 'human_passed': 'True'},
        {'script_id': 'b', 'auditor_passed': 'True', 'human_passed': 'False'},
        {'script_id': 'c', 'auditor_passed': 'False', 'human_passed': 'False'},
        {'script_id': 'd', 'auditor_passed': 'False', 'human_passed': 'True'},
        {'script_id': 'e', 'auditor_passed': 'True', 'human_passed': ''},  # not reviewed
    ]
    write_csv(csvp, rows)
    metrics = compute_metrics(csvp)
    assert metrics['total_reviewed'] == 4
    assert metrics['agreements'] == 2  # a and c
    assert metrics['false_positives'] == 1  # b
    assert metrics['false_negatives'] == 1  # d
    assert abs(metrics['agreement_rate'] - 0.5) < 1e-6
