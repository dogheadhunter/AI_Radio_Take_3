"""Tests for script auditor."""
import pytest
from pathlib import Path
from src.ai_radio.generation.auditor import (
    audit_script,
    AuditResult,
    audit_batch,
    save_audit_result,
    load_audit_results,
)


class TestAuditScript:
    """Test single script auditing."""

    def test_returns_audit_result(self, mock_llm_auditor):
        """Must return an AuditResult object."""
        result = audit_script(
            client=None,
            script_content="Test script",
            script_id="test_1",
            dj="julie",
        )
        assert isinstance(result, AuditResult)

    def test_score_in_range(self, mock_llm_auditor):
        """Score must be between 1 and 10."""
        result = audit_script(
            client=None,
            script_content="Test script",
            script_id="test_1",
            dj="julie",
        )
        assert 1 <= result.score <= 10

    def test_passed_reflects_threshold(self, mock_llm_auditor):
        """passed=True if score >= 6."""
        result = audit_script(
            client=None,
            script_content="Test script",
            script_id="test_1",
            dj="julie",
        )
        assert result.passed == (result.score >= 6)

    def test_handles_malformed_json(self, mock_llm_bad_json):
        """Must handle non-JSON response gracefully."""
        result = audit_script(
            client=None,
            script_content="Bad script",
            script_id="test_bad",
            dj="julie",
        )
        assert result.passed == False
        assert "parse error" in result.notes.lower()


def test_batch_and_save_load(tmp_path, mock_llm_auditor):
    scripts = [
        {"script_id": "s1", "script_content": "One", "dj": "julie"},
        {"script_id": "s2", "script_content": "Two", "dj": "julie"},
    ]
    out = tmp_path / "audit_out"
    summary = audit_batch(scripts, out, client=None)
    assert summary["total"] == 2

    # Ensure files saved
    passed = list((out / "passed").glob("*.json"))
    failed = list((out / "failed").glob("*.json"))
    assert (len(passed) + len(failed)) == 2

    # Load results
    results = load_audit_results(out)
    assert len(results) == 2


def test_auditor_on_sample_scripts(tmp_path, mock_llm_auditor_mixed):
    """Run auditor on 5 sample scripts (good/bad/borderline) and verify outcomes."""
    scripts = [
        {"script_id": "good_julie", "script_content": "Hey there, you know, this is Julie. Lovely tune ahead.", "dj": "julie"},
        {"script_id": "bad_julie_slang", "script_content": "Hey, awesome track! 😀", "dj": "julie"},
        {"script_id": "bad_mrnv", "script_content": "Yo, that was awesome, totally rad.", "dj": "mr_new_vegas"},
        {"script_id": "borderline_julie", "script_content": "This is a borderline script with slight drift.", "dj": "julie"},
        {"script_id": "good_mrnv", "script_content": "A smooth evening, the lights shimmer over the lounge.", "dj": "mr_new_vegas"},
    ]

    out = tmp_path / "audit_mixed"
    summary = audit_batch(scripts, out, client=None)

    # Expect: 3 pass (good_julie, borderline_julie, good_mrnv), 2 fail
    assert summary["total"] == 5
    assert summary["passed"] == 3
    assert summary["failed"] == 2

    # Ensure issues are recorded for failures
    results = load_audit_results(out)
    failed_ids = [r.script_id for r in results if not r.passed]
    assert "bad_julie_slang" in failed_ids
    assert "bad_mrnv" in failed_ids
