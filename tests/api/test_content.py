"""Tests for Content API."""
import pytest
import json
from pathlib import Path

from src.ai_radio.api.content import ContentAPI
from src.ai_radio.api.schemas import ContentType, DJ, SongInfo


@pytest.fixture
def sample_catalog(tmp_path):
    """Create a sample catalog.json for testing."""
    catalog = {
        "songs": [
            {"id": "1", "artist": "Test Artist 1", "title": "Test Song 1"},
            {"id": "2", "artist": "Test Artist 2", "title": "Test Song 2"},
            {"id": "3", "artist": "Test Artist 3", "title": "Test Song 3"},
        ]
    }
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, 'w') as f:
        json.dump(catalog, f)
    return catalog_path


@pytest.fixture
def content_api(tmp_path, sample_catalog, monkeypatch):
    """Create a ContentAPI with test directories."""
    from src.ai_radio import config
    
    data_dir = tmp_path
    generated_dir = tmp_path / "generated"
    generated_dir.mkdir()
    
    # Patch config to use tmp directories
    monkeypatch.setattr(config, 'DATA_DIR', data_dir)
    monkeypatch.setattr(config, 'GENERATED_DIR', generated_dir)
    
    return ContentAPI(data_dir=data_dir, generated_dir=generated_dir)


class TestLoadCatalog:
    """Test catalog loading functionality."""
    
    def test_load_catalog_returns_songs(self, content_api, sample_catalog):
        """load_catalog should return SongInfo objects."""
        songs = content_api.load_catalog()
        
        assert len(songs) == 3
        assert all(isinstance(s, SongInfo) for s in songs)
        assert songs[0].artist == "Test Artist 1"
        assert songs[0].title == "Test Song 1"
    
    def test_load_catalog_caching(self, content_api):
        """Catalog should be cached after first load."""
        songs1 = content_api.load_catalog()
        songs2 = content_api.load_catalog()
        
        # Should be the same object (cached)
        assert songs1 is songs2
    
    def test_load_catalog_force_reload(self, content_api):
        """force_reload should bypass cache."""
        songs1 = content_api.load_catalog()
        songs2 = content_api.load_catalog(force_reload=True)
        
        # Should be different objects
        assert songs1 is not songs2
        # But same content
        assert len(songs1) == len(songs2)
    
    def test_load_catalog_missing_file(self, tmp_path):
        """Missing catalog should return empty list."""
        api = ContentAPI(data_dir=tmp_path)
        songs = api.load_catalog()
        
        assert songs == []


class TestListScripts:
    """Test script listing functionality."""
    
    def test_list_scripts_with_intro(self, content_api):
        """Should find intro scripts."""
        from src.ai_radio.core.paths import get_script_path
        
        # Get a song from catalog and create script using proper path
        songs = content_api.load_catalog()
        song = songs[0]
        script_path = get_script_path(song.to_dict(), "julie", content_type="intros")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Hello listeners!")
        
        scripts = content_api.list_scripts(content_type=ContentType.INTRO)
        
        # Should find at least our new script
        assert len(scripts) >= 1
        julie_scripts = [s for s in scripts if s.dj == DJ.JULIE and s.content_type == ContentType.INTRO]
        assert len(julie_scripts) >= 1
    
    def test_list_scripts_filter_by_dj(self, content_api):
        """Should filter by DJ."""
        from src.ai_radio.core.paths import get_script_path
        
        songs = content_api.load_catalog()
        song = songs[0]
        
        # Create scripts for both DJs
        for dj in ["julie", "mr_new_vegas"]:
            script_path = get_script_path(song.to_dict(), dj, content_type="intros")
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text(f"Hello from {dj}!")
        
        scripts = content_api.list_scripts(dj=DJ.JULIE, content_type=ContentType.INTRO)
        
        # All returned scripts should be for Julie
        assert all(s.dj == DJ.JULIE for s in scripts)
    
    def test_list_scripts_include_text(self, content_api):
        """include_text should load script content."""
        from src.ai_radio.core.paths import get_script_path
        
        songs = content_api.load_catalog()
        song = songs[0]
        script_path = get_script_path(song.to_dict(), "julie", content_type="intros")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Hello listeners!")
        
        scripts = content_api.list_scripts(content_type=ContentType.INTRO, include_text=True)
        
        # Find our specific script
        our_script = next((s for s in scripts if s.script_path == script_path), None)
        assert our_script is not None
        assert our_script.script_text == "Hello listeners!"
    
    def test_list_time_scripts(self, content_api):
        """Should find time announcement scripts."""
        from src.ai_radio.core.paths import get_time_script_path
        
        # Create a unique time slot
        script_path = get_time_script_path(23, 30, "julie")  # Use unusual time
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("It's almost midnight!")
        
        scripts = content_api.list_scripts(content_type=ContentType.TIME, dj=DJ.JULIE)
        
        # Should find our script
        our_script = next((s for s in scripts if s.hour == 23 and s.minute == 30), None)
        assert our_script is not None
        assert our_script.content_type == ContentType.TIME
    
    def test_list_weather_scripts(self, content_api):
        """Should find weather announcement scripts."""
        from src.ai_radio.core.paths import get_weather_script_path
        
        script_path = get_weather_script_path(12, "julie")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Clear skies today!")
        
        scripts = content_api.list_scripts(content_type=ContentType.WEATHER, dj=DJ.JULIE)
        
        # Should find our script
        our_script = next((s for s in scripts if s.weather_hour == 12), None)
        assert our_script is not None
        assert our_script.content_type == ContentType.WEATHER


class TestGetScript:
    """Test getting specific scripts."""
    
    def test_get_script_intro(self, content_api):
        """Should get a specific intro script."""
        from src.ai_radio.core.paths import get_script_path
        
        song = SongInfo(id="1", artist="Test Artist 1", title="Test Song 1")
        
        # Create script using proper path function
        script_path = get_script_path(song.to_dict(), "julie", content_type="intros")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Hello!")
        
        result = content_api.get_script(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=song,
        )
        
        assert result is not None
        assert result.script_text == "Hello!"
    
    def test_get_script_not_found(self, content_api):
        """Should return None for missing script."""
        song = SongInfo(id="999", artist="Missing", title="Song")
        
        result = content_api.get_script(
            content_type=ContentType.INTRO,
            dj=DJ.JULIE,
            song=song,
        )
        
        assert result is None
    
    def test_get_script_time(self, content_api):
        """Should get a specific time script."""
        from src.ai_radio.core.paths import get_time_script_path
        
        script_path = get_time_script_path(8, 0, "julie")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text("Good morning!")
        
        result = content_api.get_script(
            content_type=ContentType.TIME,
            dj=DJ.JULIE,
            hour=8,
            minute=0,
        )
        
        assert result is not None
        assert result.script_text == "Good morning!"


class TestGetPipelineStatus:
    """Test pipeline status retrieval."""
    
    def test_empty_status(self, content_api, tmp_path):
        """Should return default status when no checkpoint exists."""
        status = content_api.get_pipeline_status()
        
        assert not status.generate_completed
        assert not status.audit_completed
        assert status.scripts_generated == 0
    
    def test_with_checkpoint(self, content_api, tmp_path):
        """Should read status from checkpoint file."""
        checkpoint = {
            "timestamp": "2024-01-01T00:00:00",
            "run_id": "test_run",
            "stages": {
                "generate": {"status": "completed", "scripts_generated": 50},
                "audit": {"status": "completed", "passed": 45, "failed": 5},
                "audio": {"status": "in_progress", "audio_files_generated": 20},
            }
        }
        checkpoint_path = tmp_path / "pipeline_state.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f)
        
        status = content_api.get_pipeline_status()
        
        assert status.generate_completed
        assert status.audit_completed
        assert not status.audio_completed
        assert status.scripts_generated == 50
        assert status.scripts_passed == 45


class TestCountContent:
    """Test content counting."""
    
    def test_count_returns_expected_structure(self, content_api):
        """Count should return expected structure."""
        counts = content_api.count_content()
        
        assert "scripts" in counts
        assert "audio_files" in counts
        assert "songs_in_catalog" in counts
        
        assert counts["scripts"] >= 0
        assert counts["audio_files"] >= 0
        assert counts["songs_in_catalog"] == 3  # From our fixture
