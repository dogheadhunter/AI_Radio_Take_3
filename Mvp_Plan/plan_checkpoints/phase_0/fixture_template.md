### Fixture Template (conftest.py)
```python
# tests/conftest. py
"""
Shared test fixtures. 

Fixtures provide reusable test data and mocks.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock


# ============================================================
# Path Fixtures
# ============================================================

@pytest.fixture
def tmp_music_dir(tmp_path):
    """Create a temporary music directory."""
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    return music_dir


@pytest.fixture
def sample_mp3_path(tmp_music_dir):
    """Create a sample MP3 file (minimal valid MP3)."""
    mp3_path = tmp_music_dir / "sample.mp3"
    # Minimal MP3 header
    mp3_path.write_bytes(b'\xff\xfb\x90\x00' + b'\x00' * 100)
    return mp3_path


# ============================================================
# Mock Fixtures
# ============================================================

@pytest.fixture
def mock_ollama():
    """Mock Ollama LLM responses."""
    with patch('src.ai_radio. generation.llm_client.ollama') as mock:
        mock.generate.return_value = {"response": "Generated text"}
        yield mock


@pytest.fixture
def mock_pygame():
    """Mock pygame for audio tests."""
    with patch('src.ai_radio.playback.player.pygame') as mock:
        yield mock


# ============================================================
# Data Fixtures
# ============================================================

@pytest.fixture
def sample_song_metadata():
    """Create sample song metadata."""
    from src.ai_radio.library.metadata import SongMetadata
    return SongMetadata(
        file_path=Path("/music/test.mp3"),
        artist="Test Artist",
        title="Test Song",
        album="Test Album",
        year=1945,
        duration_seconds=180. 0,
    )


@pytest.fixture
def sample_catalog(sample_song_metadata):
    """Create a sample catalog with one song."""
    from src.ai_radio.library.catalog import SongCatalog, add_song
    catalog = SongCatalog()
    add_song(catalog, sample_song_metadata)
    return catalog
```
