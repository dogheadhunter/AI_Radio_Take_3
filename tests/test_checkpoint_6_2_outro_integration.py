"""
Tests for Checkpoint 6.2: Outro Pipeline Integration

Validates that:
1. --outros flag is accepted
2. Outro scripts are generated to data/generated/outros/{dj}/{song_folder}/
3. Outro scripts are audited to data/audit/{dj}/passed|failed/
4. Checkpoint state tracks outros correctly
5. Resume works with outros
"""
import pytest
import json
from pathlib import Path
import subprocess
import sys

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"
AUDIT_DIR = DATA_DIR / "audit"
CHECKPOINT_FILE = DATA_DIR / "pipeline_state.json"


@pytest.fixture(scope="function")
def clean_outro_data():
    """Clean outro-related data before each test."""
    # Clean generated outros
    outros_dir = GENERATED_DIR / "outros"
    if outros_dir.exists():
        import shutil
        shutil.rmtree(outros_dir)
    
    # Clean audit files
    if AUDIT_DIR.exists():
        import shutil
        shutil.rmtree(AUDIT_DIR)
    
    # Clean checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
    
    yield
    
    # Cleanup after test (optional - comment out if you want to inspect outputs)
    # if outros_dir.exists():
    #     import shutil
    #     shutil.rmtree(outros_dir)
    # if AUDIT_DIR.exists():
    #     import shutil
    #     shutil.rmtree(AUDIT_DIR)
    # if CHECKPOINT_FILE.exists():
    #     CHECKPOINT_FILE.unlink()


def test_outros_flag_accepted(clean_outro_data):
    """Test that --outros flag is accepted without error."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--outros", "--dj", "julie", "--limit", "1", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    
    # Should not error
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    
    # Should not contain the blocking error message
    assert "Currently only --intros is supported" not in result.stderr
    assert "Currently only --intros is supported" not in result.stdout


def test_outro_scripts_generated(clean_outro_data):
    """Test that outro scripts are generated to correct location."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--outros", "--dj", "julie", "--limit", "1", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    
    # Check that outro directory exists
    outros_dir = GENERATED_DIR / "outros" / "julie"
    assert outros_dir.exists(), "Outros directory not created"
    
    # Check that at least one outro file exists
    outro_files = list(outros_dir.glob("**/*_outro.txt"))
    assert len(outro_files) > 0, "No outro text files generated"
    
    # Verify file structure: data/generated/outros/{dj}/{song_folder}/{dj}_outro.txt
    outro_file = outro_files[0]
    assert outro_file.name == "julie_outro.txt", f"Expected julie_outro.txt, got {outro_file.name}"
    assert outro_file.parent.parent.name == "julie", "Outro not in correct DJ folder"


def test_outro_scripts_audited(clean_outro_data):
    """Test that outro scripts are audited and results saved."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--outros", "--dj", "julie", "--limit", "1", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    
    # Check audit directory exists
    audit_dir = AUDIT_DIR / "julie"
    assert audit_dir.exists(), "Audit directory not created"
    
    # Check for passed or failed outro audits
    passed_dir = audit_dir / "passed"
    failed_dir = audit_dir / "failed"
    
    outro_audits = []
    if passed_dir.exists():
        outro_audits.extend(list(passed_dir.glob("*_song_outro_audit.json")))
    if failed_dir.exists():
        outro_audits.extend(list(failed_dir.glob("*_song_outro_audit.json")))
    
    assert len(outro_audits) > 0, "No outro audit files found"
    
    # Verify audit file content
    audit_file = outro_audits[0]
    with open(audit_file, 'r', encoding='utf-8') as f:
        audit_data = json.load(f)
    
    assert audit_data["content_type"] == "song_outro", "Audit content_type should be 'song_outro'"
    assert "score" in audit_data, "Audit should contain score"
    assert "passed" in audit_data, "Audit should contain passed status"


def test_checkpoint_tracks_outros(clean_outro_data):
    """Test that checkpoint state correctly tracks outros."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--outros", "--dj", "julie", "--limit", "2", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    assert CHECKPOINT_FILE.exists(), "Checkpoint file not created"
    
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
    
    # Verify outros is in content_types
    assert "outros" in checkpoint["config"]["content_types"], "Checkpoint should track 'outros'"
    
    # Verify scripts were generated (should be 2 outro scripts for 2 songs)
    assert checkpoint["stages"]["generate"]["scripts_generated"] == 2, "Should have generated 2 outro scripts"


def test_intros_and_outros_together(clean_outro_data):
    """Test that both --intros and --outros work together."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--intros", "--outros", "--dj", "julie", "--limit", "1", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    
    # Check both intro and outro files exist
    intros_dir = GENERATED_DIR / "intros" / "julie"
    outros_dir = GENERATED_DIR / "outros" / "julie"
    
    assert intros_dir.exists(), "Intros directory not created"
    assert outros_dir.exists(), "Outros directory not created"
    
    intro_files = list(intros_dir.glob("**/*_0.txt"))
    outro_files = list(outros_dir.glob("**/*_outro.txt"))
    
    assert len(intro_files) > 0, "No intro files generated"
    assert len(outro_files) > 0, "No outro files generated"
    
    # Verify checkpoint
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
    
    assert "intros" in checkpoint["config"]["content_types"], "Checkpoint should track 'intros'"
    assert "outros" in checkpoint["config"]["content_types"], "Checkpoint should track 'outros'"
    
    # Should have 2 scripts (1 intro + 1 outro)
    assert checkpoint["stages"]["generate"]["scripts_generated"] == 2


def test_resume_with_outros(clean_outro_data):
    """Test that resume works with outros."""
    # First run: generate and audit outros
    result1 = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--outros", "--dj", "julie", "--limit", "1", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result1.returncode == 0, f"First run failed: {result1.stderr}"
    
    # Second run: resume (should skip completed stages)
    result2 = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--resume", "--skip-audio"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result2.returncode == 0, f"Resume run failed: {result2.stderr}"
    
    # Should indicate stages were skipped (output goes to stderr with logging)
    output = result2.stdout + result2.stderr
    assert "RESUME MODE" in output, "Should show RESUME MODE"
    assert ("Skipping completed stages" in output or "All stages already completed" in output), \
        f"Should indicate stages were skipped. Output: {output}"


def test_time_and_weather_still_blocked():
    """Test that --time and --weather are still blocked."""
    # Test --time
    result_time = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--time", "--dj", "julie"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result_time.returncode != 0, "--time should be blocked"
    assert "only --intros and --outros are supported" in result_time.stderr
    
    # Test --weather
    result_weather = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--weather", "--dj", "julie"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result_weather.returncode != 0, "--weather should be blocked"
    assert "only --intros and --outros are supported" in result_weather.stderr
    
    # Test --all-content
    result_all = subprocess.run(
        [sys.executable, "scripts/generate_with_audit.py", "--all-content", "--dj", "julie"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result_all.returncode != 0, "--all-content should be blocked"
    assert "only --intros and --outros are supported" in result_all.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
