"""Tests for core path utilities."""
import pytest
from pathlib import Path
from src.ai_radio.core.paths import (
    get_script_path,
    get_audio_path,
    get_audit_path,
    get_time_script_path,
    get_time_audio_path,
    get_time_audit_path,
    get_weather_script_path,
    get_weather_audio_path,
    get_weather_audit_path,
)


class TestSongPaths:
    """Test path generation for song-based content (intros/outros)."""
    
    def test_get_script_path_intro(self):
        """Script path for intro should follow expected pattern."""
        song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
        path = get_script_path(song, "julie", content_type="intros")
        
        assert "Test_Artist-Test_Song" in str(path)
        assert path.name == "julie_0.txt"
        assert "intros" in str(path)
        assert "julie" in str(path)
    
    def test_get_script_path_outro(self):
        """Script path for outro should use outro directory and filename."""
        song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
        path = get_script_path(song, "julie", content_type="outros")
        
        assert "Test_Artist-Test_Song" in str(path)
        assert path.name == "julie_outro.txt"
        assert "outros" in str(path)
    
    def test_get_audio_path_intro(self):
        """Audio path for intro should use .wav extension."""
        song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
        path = get_audio_path(song, "julie", content_type="intros")
        
        assert "Test_Artist-Test_Song" in str(path)
        assert path.name == "julie_0.wav"
        assert path.suffix == ".wav"
    
    def test_get_audio_path_outro(self):
        """Audio path for outro should use outro naming."""
        song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
        path = get_audio_path(song, "julie", content_type="outros")
        
        assert "Test_Artist-Test_Song" in str(path)
        assert path.name == "julie_outro.wav"
        assert "outros" in str(path)
    
    def test_get_audit_path_passed(self):
        """Audit path for passed script should use passed folder."""
        song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
        path = get_audit_path(song, "julie", passed=True, content_type="song_intro")
        
        assert "passed" in str(path)
        assert "Test_Artist-Test_Song_song_intro_audit.json" == path.name
    
    def test_get_audit_path_failed(self):
        """Audit path for failed script should use failed folder."""
        song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
        path = get_audit_path(song, "julie", passed=False, content_type="song_outro")
        
        assert "failed" in str(path)
        assert "Test_Artist-Test_Song_song_outro_audit.json" == path.name
    
    def test_sanitizes_special_characters(self):
        """Special characters should be sanitized to underscores."""
        song = {"id": 1, "artist": "AC/DC", "title": "Back in Black!"}
        path = get_script_path(song, "julie")
        
        assert "AC_DC" in str(path)
        assert "Back_in_Black_" in str(path)
        # Should not contain special chars
        assert "/" not in path.name
        assert "!" not in path.name


class TestTimePaths:
    """Test path generation for time announcements."""
    
    def test_get_time_script_path(self):
        """Time script path should use hour-minute format."""
        path = get_time_script_path(hour=14, minute=30, dj="julie")
        
        assert "14-30" in str(path)
        assert path.name == "julie_0.txt"
        assert "time" in str(path)
    
    def test_get_time_audio_path(self):
        """Time audio path should use .wav extension."""
        path = get_time_audio_path(hour=8, minute=0, dj="mr_new_vegas")
        
        assert "08-00" in str(path)
        assert path.name == "mr_new_vegas_0.wav"
        assert path.suffix == ".wav"
    
    def test_get_time_audit_path_passed(self):
        """Time audit path should include passed/failed status."""
        path = get_time_audit_path(hour=12, minute=30, dj="julie", passed=True)
        
        assert "passed" in str(path)
        assert "12-30_time_announcement_audit.json" == path.name
    
    def test_get_time_audit_path_failed(self):
        """Time audit failed path should use failed folder."""
        path = get_time_audit_path(hour=18, minute=0, dj="julie", passed=False)
        
        assert "failed" in str(path)
        assert "18-00_time_announcement_audit.json" == path.name


class TestWeatherPaths:
    """Test path generation for weather announcements."""
    
    def test_get_weather_script_path(self):
        """Weather script path should use hour-00 format."""
        path = get_weather_script_path(hour=6, dj="julie")
        
        assert "06-00" in str(path)
        assert path.name == "julie_0.txt"
        assert "weather" in str(path)
    
    def test_get_weather_audio_path(self):
        """Weather audio path should use .wav extension."""
        path = get_weather_audio_path(hour=12, dj="mr_new_vegas")
        
        assert "12-00" in str(path)
        assert path.name == "mr_new_vegas_0.wav"
        assert "weather" in str(path)
    
    def test_get_weather_audit_path_passed(self):
        """Weather audit path should include status folder."""
        path = get_weather_audit_path(hour=17, dj="julie", passed=True)
        
        assert "passed" in str(path)
        assert "17-00_weather_announcement_audit.json" == path.name
    
    def test_get_weather_audit_path_failed(self):
        """Weather audit failed path should use failed folder."""
        path = get_weather_audit_path(hour=6, dj="julie", passed=False)
        
        assert "failed" in str(path)
        assert "06-00_weather_announcement_audit.json" == path.name
