from pathlib import Path
from scripts.generate_with_audit import generate_and_audit


def test_generate_with_audit_creates_files(tmp_path):
    out = generate_and_audit(intros=True, dj='all', limit=4, test=True, output_base=tmp_path)
    # Check out dir exists
    assert out.exists()
    # Check audit files exist
    assert (out / 'AUDIT_SUMMARY.json').exists()
    assert (out / 'AUDITOR_VALIDATION.md').exists()
    # Check passed folder exists; failed may not exist if no failures
    assert (out / 'passed').exists()
    # failed may be absent when everything passes; that's acceptable
    assert True
