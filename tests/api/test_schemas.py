"""Tests for API schemas."""
import pytest
from pathlib import Path
from datetime import datetime

from src.ai_radio.api.schemas import (
    ContentType,
    DJ,
    ReviewStatus,
    AuditStatus,
    SongInfo,
    ContentItem,
    GenerationResult,
    AuditResult,
    ReviewItem,
    ContentFilter,
    AuditFilter,
    PipelineStatus,
)


class TestEnums:
    """Test enum definitions."""
    
    def test_content_type_values(self):
        """Content types should have expected values."""
        assert ContentType.INTRO.value == "intro"
        assert ContentType.OUTRO.value == "outro"
        assert ContentType.TIME.value == "time"
        assert ContentType.WEATHER.value == "weather"
    
    def test_dj_values(self):
        """DJ enum should have expected values."""
        assert DJ.JULIE.value == "julie"
        assert DJ.MR_NEW_VEGAS.value == "mr_new_vegas"
    
    def test_review_status_values(self):
        """ReviewStatus should have expected values."""
        assert ReviewStatus.PENDING.value == "pending"
        assert ReviewStatus.APPROVED.value == "approved"
        assert ReviewStatus.REJECTED.value == "rejected"
        assert ReviewStatus.REGENERATING.value == "regenerating"
    
    def test_audit_status_values(self):
        """AuditStatus should have expected values."""
        assert AuditStatus.PASSED.value == "passed"
        assert AuditStatus.FAILED.value == "failed"
        assert AuditStatus.NOT_AUDITED.value == "not_audited"


class TestSongInfo:
    """Test SongInfo dataclass."""
    
    def test_creation(self):
        """SongInfo should be created with expected fields."""
        song = SongInfo(id="1", artist="Test Artist", title="Test Song")
        assert song.id == "1"
        assert song.artist == "Test Artist"
        assert song.title == "Test Song"
    
    def test_to_dict(self):
        """to_dict should return compatible dictionary."""
        song = SongInfo(id="1", artist="Test Artist", title="Test Song")
        d = song.to_dict()
        assert d["id"] == "1"
        assert d["artist"] == "Test Artist"
        assert d["title"] == "Test Song"


class TestContentItem:
    """Test ContentItem dataclass."""
    
    def test_creation_with_song(self):
        """ContentItem should be created with song info."""
        song = SongInfo(id="1", artist="Artist", title="Song")
        item = ContentItem(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=song,
        )
        assert item.content_type == ContentType.INTRO
        assert item.dj == DJ.JULIE
        assert item.song == song
    
    def test_display_name_song(self):
        """display_name should work for song content."""
        song = SongInfo(id="1", artist="Artist", title="Song")
        
        intro = ContentItem(content_type=ContentType.INTRO, dj=DJ.JULIE, song=song)
        assert "Artist" in intro.display_name
        assert "Song" in intro.display_name
        assert "Intro" in intro.display_name
        
        outro = ContentItem(content_type=ContentType.OUTRO, dj=DJ.JULIE, song=song)
        assert "Outro" in outro.display_name
    
    def test_display_name_time(self):
        """display_name should work for time announcements."""
        item = ContentItem(
            content_type=ContentType.TIME,
            dj=DJ.JULIE,
            hour=14,
            minute=30,
        )
        assert "14:30" in item.display_name
        assert "Time" in item.display_name
    
    def test_display_name_weather(self):
        """display_name should work for weather announcements."""
        item = ContentItem(
            content_type=ContentType.WEATHER,
            dj=DJ.JULIE,
            weather_hour=12,
        )
        assert "12:00" in item.display_name
        assert "Weather" in item.display_name
    
    def test_has_script_without_path(self):
        """has_script should return False without path."""
        item = ContentItem(content_type=ContentType.INTRO, dj=DJ.JULIE)
        assert not item.has_script
    
    def test_has_script_with_nonexistent_path(self, tmp_path):
        """has_script should return False for nonexistent path."""
        item = ContentItem(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            script_path=tmp_path / "nonexistent.txt",
        )
        assert not item.has_script
    
    def test_has_script_with_existing_path(self, tmp_path):
        """has_script should return True for existing path."""
        script_file = tmp_path / "script.txt"
        script_file.write_text("Hello")
        
        item = ContentItem(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            script_path=script_file,
        )
        assert item.has_script


class TestGenerationResult:
    """Test GenerationResult dataclass."""
    
    def test_success_result(self):
        """GenerationResult should capture success."""
        result = GenerationResult(
            success=True,
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            text="Generated text",
        )
        assert result.success
        assert result.text == "Generated text"
        assert result.error is None
    
    def test_failure_result(self):
        """GenerationResult should capture failure."""
        result = GenerationResult(
            success=False,
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            error="Generation failed",
        )
        assert not result.success
        assert result.error == "Generation failed"


class TestAuditResult:
    """Test AuditResult dataclass."""
    
    def test_creation(self):
        """AuditResult should be created with expected fields."""
        result = AuditResult(
            script_id="test_script",
            dj=DJ.JULIE,
            content_type=ContentType.INTRO,
            passed=True,
            score=8.5,
            criteria_scores={"character_voice": 9, "era_appropriateness": 8},
            issues=[],
            notes="Good script",
        )
        assert result.script_id == "test_script"
        assert result.passed
        assert result.score == 8.5
    
    def test_from_dict_intro(self):
        """from_dict should parse intro audit data."""
        data = {
            "script_id": "1_julie_intro",
            "dj": "julie",
            "content_type": "song_intro",
            "passed": True,
            "score": 8.5,
            "criteria_scores": {"character_voice": 8},
            "issues": [],
            "notes": "Good",
        }
        result = AuditResult.from_dict(data)
        
        assert result.script_id == "1_julie_intro"
        assert result.dj == DJ.JULIE
        assert result.content_type == ContentType.INTRO
        assert result.passed
    
    def test_from_dict_time(self):
        """from_dict should parse time audit data."""
        data = {
            "script_id": "12-30_julie_time",
            "dj": "julie",
            "content_type": "time_announcement",
            "passed": False,
            "score": 5.0,
        }
        result = AuditResult.from_dict(data)
        
        assert result.content_type == ContentType.TIME
        assert not result.passed
    
    def test_from_dict_mr_new_vegas(self):
        """from_dict should parse mr_new_vegas DJ."""
        data = {
            "script_id": "1_mr_new_vegas_intro",
            "dj": "mr_new_vegas",
            "content_type": "song_intro",
            "passed": True,
            "score": 9.0,
        }
        result = AuditResult.from_dict(data)
        
        assert result.dj == DJ.MR_NEW_VEGAS


class TestReviewItem:
    """Test ReviewItem dataclass."""
    
    def test_needs_review_pending(self):
        """needs_review should return True for pending items."""
        content = ContentItem(content_type=ContentType.INTRO, dj=DJ.JULIE)
        item = ReviewItem(content=content, status=ReviewStatus.PENDING)
        assert item.needs_review
    
    def test_needs_review_approved(self):
        """needs_review should return False for approved items."""
        content = ContentItem(content_type=ContentType.INTRO, dj=DJ.JULIE)
        item = ReviewItem(content=content, status=ReviewStatus.APPROVED)
        assert not item.needs_review


class TestPipelineStatus:
    """Test PipelineStatus dataclass."""
    
    def test_default_values(self):
        """PipelineStatus should have sensible defaults."""
        status = PipelineStatus()
        assert not status.generate_completed
        assert not status.audit_completed
        assert not status.audio_completed
        assert status.scripts_generated == 0
    
    def test_with_values(self):
        """PipelineStatus should accept values."""
        status = PipelineStatus(
            generate_completed=True,
            scripts_generated=100,
            scripts_passed=95,
        )
        assert status.generate_completed
        assert status.scripts_generated == 100
        assert status.scripts_passed == 95
