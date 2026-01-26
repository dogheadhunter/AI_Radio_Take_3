"""Tests for Audit API."""
import pytest
import json
from pathlib import Path

from src.ai_radio.api.audit import AuditAPI
from src.ai_radio.api.schemas import AuditResult, ContentType, DJ, SongInfo


@pytest.fixture
def audit_api(tmp_path, monkeypatch):
    """Create an AuditAPI with test directories."""
    from src.ai_radio import config
    monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(config, 'GENERATED_DIR', tmp_path / "generated")
    return AuditAPI(data_dir=tmp_path, test_mode=True)


@pytest.fixture
def sample_song():
    """Create a sample SongInfo."""
    return SongInfo(id="1", artist="Test Artist", title="Test Song")


@pytest.fixture
def sample_script_file(audit_api, sample_song):
    """Create a sample script file for auditing."""
    from src.ai_radio.core.paths import get_script_path
    
    script_path = get_script_path(sample_song.to_dict(), "julie", content_type="intros")
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("Hey there, listeners! You're tuned in to Radio New Vegas.")
    
    return script_path


class TestAuditScript:
    """Test script auditing functionality."""
    
    def test_audit_script_passes_in_test_mode(self, audit_api, sample_song, sample_script_file):
        """Good script should pass in test mode."""
        result = audit_api.audit_script(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=sample_song,
        )
        
        assert isinstance(result, AuditResult)
        assert result.passed
        assert result.score >= 7.0
    
    def test_audit_script_with_explicit_text(self, audit_api, sample_song):
        """Should audit explicit script text."""
        result = audit_api.audit_script(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=sample_song,
            script_text="Hey there, listeners! It's a beautiful day.",
            save_result=False,
        )
        
        assert isinstance(result, AuditResult)
        assert result.passed  # Good script in test mode
    
    def test_audit_script_saves_result(self, audit_api, sample_song, sample_script_file):
        """Audit should save result to disk when save_result=True."""
        result = audit_api.audit_script(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=sample_song,
            save_result=True,
        )
        
        # Check that file was created
        assert result.audit_path is not None
        assert result.audit_path.exists()
        
        # Verify content
        with open(result.audit_path, 'r') as f:
            data = json.load(f)
        assert data["passed"] == result.passed
    
    def test_audit_script_missing_file(self, audit_api, sample_song):
        """Should raise FileNotFoundError for missing script.
        
        Note: This uses a different song so there's no script file.
        """
        missing_song = SongInfo(id="999", artist="Missing", title="Song")
        with pytest.raises(FileNotFoundError):
            audit_api.audit_script(
                content_type=ContentType.INTRO,
                dj=DJ.JULIE,
                song=missing_song,
            )
    
    def test_audit_script_missing_song_for_intro(self, audit_api):
        """Should raise ValueError when song is missing for INTRO."""
        with pytest.raises(ValueError, match="song is required"):
            audit_api.audit_script(
                content_type=ContentType.INTRO,
                dj=DJ.JULIE,
            )
    
    def test_audit_script_missing_time_params(self, audit_api):
        """Should raise ValueError when hour/minute missing for TIME."""
        with pytest.raises(ValueError, match="hour and minute are required"):
            audit_api.audit_script(
                content_type=ContentType.TIME,
                dj=DJ.JULIE,
            )


class TestListAuditResults:
    """Test audit result listing."""
    
    def test_list_empty(self, audit_api):
        """Should return empty list when no audits exist."""
        results = audit_api.list_audit_results()
        assert results == []
    
    def test_list_passed_results(self, audit_api, tmp_path):
        """Should list passed audit results."""
        # Create passed audit file
        passed_dir = tmp_path / "audit" / "julie" / "passed"
        passed_dir.mkdir(parents=True)
        
        audit_data = {
            "script_id": "1_julie_intro",
            "dj": "julie",
            "content_type": "song_intro",
            "passed": True,
            "score": 8.5,
            "criteria_scores": {},
            "issues": [],
            "notes": "Good",
        }
        with open(passed_dir / "test_audit.json", 'w') as f:
            json.dump(audit_data, f)
        
        results = audit_api.list_audit_results(passed=True)
        
        assert len(results) == 1
        assert results[0].passed
        assert results[0].dj == DJ.JULIE
    
    def test_list_failed_results(self, audit_api, tmp_path):
        """Should list failed audit results."""
        # Create failed audit file
        failed_dir = tmp_path / "audit" / "mr_new_vegas" / "failed"
        failed_dir.mkdir(parents=True)
        
        audit_data = {
            "script_id": "1_mr_new_vegas_intro",
            "dj": "mr_new_vegas",
            "content_type": "song_intro",
            "passed": False,
            "score": 4.0,
            "issues": ["Wrong voice"],
            "notes": "Bad",
        }
        with open(failed_dir / "test_audit.json", 'w') as f:
            json.dump(audit_data, f)
        
        results = audit_api.list_audit_results(passed=False)
        
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].dj == DJ.MR_NEW_VEGAS
    
    def test_list_filter_by_dj(self, audit_api, tmp_path):
        """Should filter by DJ."""
        # Create audits for both DJs
        for dj in ["julie", "mr_new_vegas"]:
            passed_dir = tmp_path / "audit" / dj / "passed"
            passed_dir.mkdir(parents=True)
            
            audit_data = {
                "script_id": f"1_{dj}_intro",
                "dj": dj,
                "content_type": "song_intro",
                "passed": True,
                "score": 8.0,
            }
            with open(passed_dir / f"{dj}_audit.json", 'w') as f:
                json.dump(audit_data, f)
        
        results = audit_api.list_audit_results(dj=DJ.JULIE)
        
        assert len(results) == 1
        assert results[0].dj == DJ.JULIE


class TestGetAuditResult:
    """Test getting specific audit results."""
    
    def test_get_result_not_found(self, audit_api, sample_song):
        """Should return None when audit doesn't exist."""
        missing_song = SongInfo(id="999", artist="Missing", title="Song")
        result = audit_api.get_audit_result(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=missing_song,
        )
        assert result is None
    
    def test_get_result_passed(self, audit_api, sample_song):
        """Should find passed audit result."""
        from src.ai_radio.core.paths import get_audit_path
        
        audit_path = get_audit_path(sample_song.to_dict(), "julie", passed=True, content_type='song_intro')
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        
        audit_data = {
            "script_id": "1_julie_intro",
            "dj": "julie",
            "content_type": "song_intro",
            "passed": True,
            "score": 8.5,
        }
        with open(audit_path, 'w') as f:
            json.dump(audit_data, f)
        
        result = audit_api.get_audit_result(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=sample_song,
        )
        
        assert result is not None
        assert result.passed


class TestGetAuditSummary:
    """Test audit summary statistics."""
    
    def test_empty_summary(self, audit_api):
        """Empty audit directory should return zero counts."""
        summary = audit_api.get_audit_summary()
        
        assert summary["total"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["pass_rate"] == 0.0
    
    def test_summary_with_results(self, audit_api, tmp_path):
        """Should calculate correct statistics."""
        # Create passed and failed audits
        for status, count in [("passed", 8), ("failed", 2)]:
            status_dir = tmp_path / "audit" / "julie" / status
            status_dir.mkdir(parents=True)
            
            for i in range(count):
                audit_data = {
                    "script_id": f"{i}_julie_intro",
                    "dj": "julie",
                    "content_type": "song_intro",
                    "passed": status == "passed",
                    "score": 8.0 if status == "passed" else 4.0,
                }
                with open(status_dir / f"audit_{i}.json", 'w') as f:
                    json.dump(audit_data, f)
        
        summary = audit_api.get_audit_summary()
        
        assert summary["total"] == 10
        assert summary["passed"] == 8
        assert summary["failed"] == 2
        assert summary["pass_rate"] == 0.8


class TestDeleteAuditResult:
    """Test audit result deletion."""
    
    def test_delete_nonexistent(self, audit_api, sample_song):
        """Should return False for nonexistent audit."""
        missing_song = SongInfo(id="999", artist="Missing", title="Song")
        result = audit_api.delete_audit_result(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=missing_song,
        )
        assert not result
    
    def test_delete_existing(self, audit_api, sample_song):
        """Should delete existing audit and return True."""
        from src.ai_radio.core.paths import get_audit_path
        
        audit_path = get_audit_path(sample_song.to_dict(), "julie", passed=True, content_type='song_intro')
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text("{}")
        
        assert audit_path.exists()
        
        result = audit_api.delete_audit_result(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=sample_song,
        )
        
        assert result
        assert not audit_path.exists()
