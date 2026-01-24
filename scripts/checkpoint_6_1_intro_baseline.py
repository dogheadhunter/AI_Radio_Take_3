"""Run Checkpoint 6.1: Intro Baseline Validation

This script automates the steps in
`Script_Improvment_Plan/Phase/phase_6_testing/checkpoint_6_1_intro-baseline.md`.

It supports two modes:
- test (default): runs the pipeline in test mode (fast, uses fake auditor)
- integration: runs the pipeline in integration mode (uses real services)

The script performs:
- Clean generated intros, audit results, and pipeline state
- Run Julie only (limit 10)
- Run Mr. New Vegas only (limit 10)
- Run both DJs at scale (--limit 25 per DJ)
- Check initial and final pass rates and report success/fail

Usage:
    python scripts/checkpoint_6_1_intro_baseline.py --mode test
"""
from pathlib import Path
import subprocess
import argparse
import json
import sys
import shutil
import os

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
GENERATED_DIR = REPO_ROOT / "data" / "generated"
AUDIT_DIR = DATA_DIR / "audit"
PIPELINE_STATE = DATA_DIR / "pipeline_state.json"
SCRIPT = REPO_ROOT / "scripts" / "generate_with_audit.py"


def clean_state():
    # Remove generated intros, audit results, and pipeline state
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)
    if AUDIT_DIR.exists():
        shutil.rmtree(AUDIT_DIR)
    if PIPELINE_STATE.exists():
        PIPELINE_STATE.unlink()


def run_pipeline(dj: str, limit: int, mode: str, skip_audio: bool = True) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--intros", "--dj", dj, "--limit", str(limit), "--skip-audio"]
    if mode == "test":
        cmd.append("--test")
    env = os.environ.copy()
    if mode == "integration":
        env["TEST_MODE"] = "integration"
    else:
        env["TEST_MODE"] = "mock"

    print(f"Running: {' '.join(cmd)} (TEST_MODE={env['TEST_MODE']})")
    return subprocess.run(cmd, env=env, cwd=REPO_ROOT, capture_output=True, text=True)


def load_summary() -> dict:
    summary_path = DATA_DIR / "audit" / "summary.json"
    if not summary_path.exists():
        return {}
    return json.loads(summary_path.read_text(encoding='utf-8'))


def compute_final_pass_rate(djs: list) -> float:
    total = 0
    passed = 0
    for dj in djs:
        passed_dir = DATA_DIR / "audit" / dj / "passed"
        failed_dir = DATA_DIR / "audit" / dj / "failed"
        p = len(list(passed_dir.glob("*.json"))) if passed_dir.exists() else 0
        f = len(list(failed_dir.glob("*.json"))) if failed_dir.exists() else 0
        total += p + f
        passed += p
    return (passed / total) if total else 0.0


def run_check(mode: str = "test") -> int:
    # 1. Clean state
    print("\n[STEP] Clean state")
    clean_state()

    failures = []

    # Task 1: Julie only
    print("\n[STEP] Julie only (10)")
    res = run_pipeline("julie", 10, mode)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        failures.append("Julie run failed")
    summary = load_summary()
    initial_pass_rate = summary.get("pass_rate", 0)
    final_pass_rate = compute_final_pass_rate(["julie"])
    print(f"Julie initial pass rate: {initial_pass_rate:.1%}; final pass rate: {final_pass_rate:.1%}")
    if initial_pass_rate < 0.5:
        failures.append("Julie initial pass rate < 50%")
    if final_pass_rate < 0.95:
        failures.append("Julie final pass rate < 95% after regen")

    # Task 2: Mr. New Vegas only
    print("\n[STEP] Mr. New Vegas only (10)")
    # Clean only generated/audit for safety
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)
    if AUDIT_DIR.exists():
        shutil.rmtree(AUDIT_DIR)
    if PIPELINE_STATE.exists():
        PIPELINE_STATE.unlink()

    res = run_pipeline("mr_new_vegas", 10, mode)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        failures.append("Mr. NV run failed")
    summary = load_summary()
    initial_pass_rate = summary.get("pass_rate", 0)
    final_pass_rate = compute_final_pass_rate(["mr_new_vegas"])
    print(f"Mr. NV initial pass rate: {initial_pass_rate:.1%}; final pass rate: {final_pass_rate:.1%}")
    if initial_pass_rate < 0.5:
        failures.append("Mr. NV initial pass rate < 50%")
    if final_pass_rate < 0.95:
        failures.append("Mr. NV final pass rate < 95% after regen")

    # Task 3: Scale verification (both DJs)
    print("\n[STEP] Scale verification (both DJs, limit=25 each -> 50 scripts)")
    # Clean state
    clean_state()

    res = run_pipeline("all", 25, mode)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        failures.append("Combined run failed")
    summary = load_summary()
    initial_pass_rate = summary.get("pass_rate", 0)
    final_pass_rate = compute_final_pass_rate(["julie", "mr_new_vegas"])
    print(f"Combined initial pass rate: {initial_pass_rate:.1%}; final pass rate: {final_pass_rate:.1%}")
    if initial_pass_rate < 0.5:
        failures.append("Combined initial pass rate < 50%")
    if final_pass_rate < 0.95:
        failures.append("Combined final pass rate < 95% after regen")

    print("\n--- CHECKPOINT 6.1 RESULTS ---")
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f" - {f}")
        return 2
    else:
        print("All checks passed ✅")
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['test', 'integration'], default='test')
    args = parser.parse_args()
    sys.exit(run_check(mode=args.mode))
