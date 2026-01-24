from pathlib import Path
import json
from scripts.collect_audit_samples import collect_samples


def make_fake_audit_dir(tmp_path):
    d = tmp_path / 'audit'
    passed = d / 'passed'
    failed = d / 'failed'
    passed.mkdir(parents=True)
    failed.mkdir(parents=True)
    for i in range(3):
        (passed / f'p{i}.json').write_text(json.dumps({"script_id": f"p{i}", "score": 8, "passed": True}), encoding='utf-8')
    for i in range(2):
        (failed / f'f{i}.json').write_text(json.dumps({"script_id": f"f{i}", "score": 3, "passed": False}), encoding='utf-8')
    return d


def test_collect_samples(tmp_path):
    d = make_fake_audit_dir(tmp_path)
    out = tmp_path / 'manual'
    s_passed, s_failed = collect_samples(d, out, passed_n=2, failed_n=2)
    assert len(s_passed) == 2
    assert len(s_failed) == 2
    assert (out / 'samples_passed.json').exists()
    assert (out / 'samples_failed.json').exists()
