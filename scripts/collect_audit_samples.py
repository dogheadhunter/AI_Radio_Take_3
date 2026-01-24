"""Collect samples from audit results for human validation.

Usage:
  python scripts/collect_audit_samples.py --audit-dir data/audit/20260123_... --out data/manual_validation --passed 5 --failed 5
"""
import argparse
from pathlib import Path
import json
import random


def collect_samples(audit_dir: Path, out_dir: Path, passed_n: int = 5, failed_n: int = 5):
    passed = list((audit_dir / 'passed').glob('*.json')) if (audit_dir / 'passed').exists() else []
    failed = list((audit_dir / 'failed').glob('*.json')) if (audit_dir / 'failed').exists() else []

    out_dir.mkdir(parents=True, exist_ok=True)

    def load_and_sample(files, n):
        items = []
        for f in files:
            d = json.loads(f.read_text(encoding='utf-8'))
            items.append(d)
        if not items:
            return []
        return random.sample(items, min(n, len(items)))

    s_passed = load_and_sample(passed, passed_n)
    s_failed = load_and_sample(failed, failed_n)

    (out_dir / 'samples_passed.json').write_text(json.dumps(s_passed, indent=2, ensure_ascii=False), encoding='utf-8')
    (out_dir / 'samples_failed.json').write_text(json.dumps(s_failed, indent=2, ensure_ascii=False), encoding='utf-8')

    return s_passed, s_failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit-dir', required=True)
    parser.add_argument('--out', default='data/manual_validation')
    parser.add_argument('--passed', type=int, default=5)
    parser.add_argument('--failed', type=int, default=5)
    args = parser.parse_args()

    s_passed, s_failed = collect_samples(Path(args.audit_dir), Path(args.out), args.passed, args.failed)
    print(f"Collected {len(s_passed)} passed and {len(s_failed)} failed samples to {args.out}")


if __name__ == '__main__':
    main()
