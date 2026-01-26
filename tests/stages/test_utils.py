"""Tests for stage utilities."""
import pytest
import json
from pathlib import Path
from src.ai_radio.stages.utils import (
    load_catalog_songs,
    get_lyrics_for_song,
    FakeAuditorClient,
)


class TestLoadCatalogSongs:
    """Test catalog song loading."""
    
    def test_loads_songs_from_catalog(self, tmp_path):
        """Should load songs from catalog.json."""
        catalog = {
            "songs": [
                {"id": 1, "artist": "Artist 1", "title": "Song 1", "extra": "field"},
                {"id": 2, "artist": "Artist 2", "title": "Song 2", "extra": "field"},
            ]
        }
        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text(json.dumps(catalog))
        
        songs = load_catalog_songs(catalog_path)
        
        assert len(songs) == 2
        assert songs[0]["id"] == 1
        assert songs[0]["artist"] == "Artist 1"
        assert songs[0]["title"] == "Song 1"
        # Should not include extra fields
        assert "extra" not in songs[0]
    
    def test_applies_limit(self, tmp_path):
        """Should limit number of songs loaded."""
        catalog = {
            "songs": [{"id": i, "artist": f"Artist {i}", "title": f"Song {i}"} for i in range(10)]
        }
        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text(json.dumps(catalog))
        
        songs = load_catalog_songs(catalog_path, limit=5)
        
        assert len(songs) == 5
    
    def test_random_sample(self, tmp_path):
        """Should randomly sample songs when requested."""
        catalog = {
            "songs": [{"id": i, "artist": f"Artist {i}", "title": f"Song {i}"} for i in range(10)]
        }
        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text(json.dumps(catalog))
        
        songs = load_catalog_songs(catalog_path, limit=3, random_sample=True)
        
        assert len(songs) == 3
        # IDs may not be sequential due to random sampling
    
    def test_handles_empty_catalog(self, tmp_path):
        """Should handle empty catalog."""
        catalog = {"songs": []}
        catalog_path = tmp_path / "catalog.json"
        catalog_path.write_text(json.dumps(catalog))
        
        songs = load_catalog_songs(catalog_path)
        
        assert len(songs) == 0


class TestGetLyricsForSong:
    """Test lyrics retrieval."""
    
    def test_returns_none_when_dir_missing(self):
        """Should return None when lyrics directory doesn't exist."""
        # Assuming music_with_lyrics doesn't exist in test env
        lyrics = get_lyrics_for_song("Artist", "Song")
        assert lyrics is None
    
    def test_finds_lyrics_by_pattern(self, tmp_path, monkeypatch):
        """Should find lyrics using various filename patterns."""
        lyrics_dir = tmp_path / "music_with_lyrics"
        lyrics_dir.mkdir()
        
        # Create a lyrics file
        lyrics_file = lyrics_dir / "Test Song by Test Artist.txt"
        lyrics_file.write_text("Test lyrics content")
        
        # Temporarily use this directory
        monkeypatch.chdir(tmp_path)
        
        lyrics = get_lyrics_for_song("Test Artist", "Test Song")
        
        assert lyrics == "Test lyrics content"
    
    def test_tries_multiple_patterns(self, tmp_path, monkeypatch):
        """Should try multiple filename patterns."""
        lyrics_dir = tmp_path / "music_with_lyrics"
        lyrics_dir.mkdir()
        
        # Create with alternative pattern
        lyrics_file = lyrics_dir / "Test Artist - Test Song.txt"
        lyrics_file.write_text("Alternative pattern lyrics")
        
        monkeypatch.chdir(tmp_path)
        
        lyrics = get_lyrics_for_song("Test Artist", "Test Song")
        
        assert lyrics == "Alternative pattern lyrics"


class TestFakeAuditorClient:
    """Test fake auditor client for test mode."""
    
    def test_generates_json_response(self):
        """Should return valid JSON."""
        client = FakeAuditorClient()
        
        result = client.generate("Test script")
        
        # Should be valid JSON
        data = json.loads(result)
        assert "criteria_scores" in data
        assert "issues" in data
        assert "notes" in data
    
    def test_fails_modern_slang(self):
        """Should fail scripts with modern slang."""
        client = FakeAuditorClient()
        
        result = client.generate("This is awesome!")
        data = json.loads(result)
        
        # Should have low scores
        assert any(score < 7 for score in data["criteria_scores"].values())
        assert len(data["issues"]) > 0
    
    def test_passes_good_script(self):
        """Should pass scripts without issues."""
        client = FakeAuditorClient()
        
        result = client.generate("This is a good script")
        data = json.loads(result)
        
        # Should have high scores
        assert all(score >= 8 for score in data["criteria_scores"].values())
        assert len(data["issues"]) == 0
    
    def test_borderline_case(self):
        """Should handle borderline scripts."""
        client = FakeAuditorClient()
        
        result = client.generate("This is borderline acceptable")
        data = json.loads(result)
        
        # Should have moderate scores
        assert 5 <= data["criteria_scores"]["character_voice"] <= 7
        assert len(data["issues"]) > 0
    
    def test_extracts_script_from_prompt(self):
        """Should extract script from audit prompt format."""
        client = FakeAuditorClient()
        
        # Simulate audit prompt with --- separator
        prompt = "Audit instructions\n---\nScript content awesome"
        result = client.generate(prompt)
        data = json.loads(result)
        
        # Should detect "awesome" in script part
        assert any(score < 7 for score in data["criteria_scores"].values())
