import sys
from pathlib import Path

# Ensure repository root is on sys.path so tests can import `src.*` packages
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Shared test fixtures
import pytest
from pathlib import Path
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC


@pytest.fixture
def tmp_music_dir(tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    return music_dir


@pytest.fixture
def sample_mp3_path(tmp_music_dir):
    mp3_path = tmp_music_dir / "sample.mp3"
    # Minimal MPEG header (not a full MP3 but sufficient for mutagen to attach ID3)
    mp3_path.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 1024)
    return mp3_path


@pytest.fixture
def sample_mp3_with_tags(sample_mp3_path):
    # Add ID3 tags to the existing minimal MP3 file
    id3 = ID3()
    id3.add(TIT2(encoding=3, text="Test Title"))
    id3.add(TPE1(encoding=3, text="Test Artist"))
    id3.add(TALB(encoding=3, text="Test Album"))
    id3.add(TDRC(encoding=3, text="1945"))
    id3.save(sample_mp3_path)
    return sample_mp3_path


@pytest.fixture
def sample_mp3_no_tags(sample_mp3_path):
    # Ensure file has no tags
    try:
        ID3(sample_mp3_path).delete()
    except Exception:
        pass
    return sample_mp3_path


# ============================================================
# Generation & External Service Mocks
# ============================================================
from unittest.mock import patch


@pytest.fixture
def mock_ollama():
    """Mock Ollama LLM responses by patching requests in the llm client."""
    with patch('src.ai_radio.generation.llm_client.requests') as mock:
        mock.post.return_value.json.return_value = {"response": "Generated text"}
        mock.post.return_value.status_code = 200
        yield mock


@pytest.fixture
def mock_chatterbox():
    """Mock Chatterbox TTS service by patching requests in the tts client."""
    with patch('src.ai_radio.generation.tts_client.requests') as mock:
        mock.post.return_value.content = b"\x00\x00"
        mock.post.return_value.status_code = 200
        yield mock


@pytest.fixture
def mock_llm(monkeypatch):
    """Simple fixture that replaces the llm generate_text function."""
    from src.ai_radio.generation.llm_client import generate_text

    def _fake(client, prompt):
        return "Fake LLM output"

    monkeypatch.setattr('src.ai_radio.generation.llm_client.generate_text', _fake)
    yield _fake


@pytest.fixture
def mock_tts(monkeypatch):
    """Simple fixture that replaces the tts generate_audio function."""

    def _fake(client, text, output_path, voice_reference=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x00\x00")
        return

    monkeypatch.setattr('src.ai_radio.generation.tts_client.generate_audio', _fake)
    yield _fake


@pytest.fixture
def sample_song_list():
    return [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]
