"""Tests for song catalog."""
import json
from pathlib import Path

import pytest

from src.ai_radio.library.catalog import (
    SongCatalog,
    add_song,
    get_song,
    save_catalog,
    load_catalog,
)
from src.ai_radio.library.metadata import SongMetadata


def mock_song_metadata():
    return SongMetadata(file_path=Path("/tmp/test.mp3"), artist="A", title="T", album="Al", year=1999, duration_seconds=3.5)


class TestSongCatalog:
    """Test catalog operations."""

    def test_add_song_increases_count(self):
        """Adding a song must increase catalog size."""
        catalog = SongCatalog()
        assert len(catalog) == 0
        add_song(catalog, mock_song_metadata())
        assert len(catalog) == 1

    def test_get_song_by_id(self):
        """Must be able to retrieve song by ID."""
        catalog = SongCatalog()
        song = mock_song_metadata()
        song_id = add_song(catalog, song)
        retrieved = get_song(catalog, song_id)
        assert retrieved.title == song.title

    def test_save_creates_file(self, tmp_path):
        """Saving must create a JSON file."""
        catalog = SongCatalog()
        add_song(catalog, mock_song_metadata())
        file_path = tmp_path / "catalog.json"
        save_catalog(catalog, file_path)
        assert file_path.exists()

    def test_load_restores_catalog(self, tmp_path):
        """Loading must restore saved catalog."""
        catalog = SongCatalog()
        song = mock_song_metadata()
        add_song(catalog, song)
        file_path = tmp_path / "catalog.json"
        save_catalog(catalog, file_path)

        loaded = load_catalog(file_path)
        assert len(loaded) == 1

    def test_catalog_is_json_serializable(self, tmp_path):
        """Catalog file must be valid JSON."""
        catalog = SongCatalog()
        add_song(catalog, mock_song_metadata())
        file_path = tmp_path / "catalog.json"
        save_catalog(catalog, file_path)

        # This should not raise
        with open(file_path) as f:
            data = json.load(f)
        assert "songs" in data
