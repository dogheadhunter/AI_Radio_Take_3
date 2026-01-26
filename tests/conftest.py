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
from tests.test_modes import is_mock_mode, is_integration_mode


# ============================================================
# Test Mode Configuration Hook
# ============================================================
def pytest_configure(config):
    """Configure pytest based on TEST_MODE environment variable."""
    from tests.test_modes import get_test_mode
    mode = get_test_mode()
    
    if mode == "mock":
        # In mock mode, skip integration tests by default
        if not config.getoption("-m"):
            config.option.markexpr = "not integration and not requires_services"
    elif mode == "integration":
        # In integration mode, run all tests including integration
        pass


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests based on TEST_MODE."""
    from tests.test_modes import is_mock_mode, is_integration_mode
    
    for item in items:
        # Skip integration/requires_services tests in mock mode
        if is_mock_mode():
            if "integration" in item.keywords or "requires_services" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Skipped in mock mode (TEST_MODE=mock)"))
        
        # Ensure mock tests are marked
        if "mock" in item.keywords and is_integration_mode():
            # Mock tests can still run in integration mode as smoke tests
            pass


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
from unittest.mock import patch, MagicMock
import wave


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
def mock_llm_realistic(monkeypatch):
    """Realistic LLM mock that generates contextual responses."""
    def _generate(client, prompt, banned_phrases=None):
        # Parse prompt to provide contextual responses
        if "song intro" in prompt.lower() or "introduce" in prompt.lower():
            return "Hey there, listeners! You're tuned in to Radio New Vegas, and I've got something special for you."
        elif "weather" in prompt.lower():
            return "Looking out over the Mojave, it's a clear night at 65 degrees."
        elif "time" in prompt.lower():
            return "It's 6 o'clock in the morning, time to rise and shine!"
        elif "outro" in prompt.lower() or "sign off" in prompt.lower():
            return "That was a great one, wasn't it? Stay tuned for more."
        else:
            return "This is your DJ speaking from Radio New Vegas."
    
    # Mock the generate_text function in BOTH the source module AND where it's imported
    monkeypatch.setattr('src.ai_radio.generation.llm_client.generate_text', _generate)
    monkeypatch.setattr('src.ai_radio.generation.pipeline.generate_text', _generate)
    
    # Also mock check functions to avoid service calls
    monkeypatch.setattr('src.ai_radio.generation.llm_client.check_ollama_available', lambda *args: True)
    
    yield _generate


@pytest.fixture
def mock_llm_auditor(monkeypatch):
    """Mock LLM that returns a valid auditor JSON response."""
    import json as json_module
    def _generate(client, prompt):
        return json_module.dumps({
            "criteria_scores": {"character_voice": 8, "era_appropriateness": 7, "forbidden_elements": 10, "natural_flow": 6, "length": 8},
            "issues": [],
            "notes": "Good overall"
        })
    monkeypatch.setattr('src.ai_radio.generation.llm_client.generate_text', _generate)
    yield _generate


@pytest.fixture
def mock_llm_auditor_mixed(monkeypatch):
    """Mock auditor LLM that inspects script content and returns pass/fail for tests."""
    import json as json_module
    import re
    from src.ai_radio.generation import llm_client as llm_client_module
    from src.ai_radio.generation import auditor as auditor_module

    def _generate(client, prompt, banned_phrases=None):
        # Extract script content from between quotes in 'SCRIPT TO EVALUATE: "..."'
        match = re.search(r'SCRIPT TO EVALUATE:\s*"([^"]*)"', prompt)
        if match:
            script_text = match.group(1).lower()
        else:
            # Fallback: just use whole prompt (shouldn't happen)
            script_text = prompt.lower()

        # Bad: modern slang or emojis in the actual SCRIPT content
        if "awesome" in script_text or "emoji" in script_text or "😀" in script_text or "👍" in script_text:
            return json_module.dumps({
                "criteria_scores": {"character_voice": 4, "era_appropriateness": 2, "forbidden_elements": 1, "natural_flow": 4, "length": 6},
                "issues": ["Uses modern slang or emoji"],
                "notes": "Contains modern slang or emojis"
            })
        # Bad: wrong character signifiers
        if "sounds like generic dj" in script_text or "not julie" in script_text:
            return json_module.dumps({
                "criteria_scores": {"character_voice": 2, "era_appropriateness": 6, "forbidden_elements": 10, "natural_flow": 5, "length": 6},
                "issues": ["Not in character"],
                "notes": "Sounds like generic DJ rather than the target character"
            })
        # Borderline
        if "borderline" in script_text:
            return json_module.dumps({
                "criteria_scores": {"character_voice": 7, "era_appropriateness": 7, "forbidden_elements": 10, "natural_flow": 7, "length": 7},
                "issues": ["Slight character drift"],
                "notes": "Borderline but acceptable"
            })
        # Default: good
        return json_module.dumps({
            "criteria_scores": {"character_voice": 8, "era_appropriateness": 8, "forbidden_elements": 10, "natural_flow": 8, "length": 8},
            "issues": [],
            "notes": "Good overall"
        })

    # Mock in BOTH modules using the imported module objects
    monkeypatch.setattr(llm_client_module, 'generate_text', _generate)
    # The auditor imports llm_client as a module, so we need to patch on that reference
    monkeypatch.setattr(auditor_module.llm_client, 'generate_text', _generate)
    yield _generate


@pytest.fixture
def mock_llm_bad_json(monkeypatch):
    """Mock LLM that returns malformed JSON."""
    def _generate(client, prompt):
        return "NOT A JSON"
    monkeypatch.setattr('src.ai_radio.generation.llm_client.generate_text', _generate)
    yield _generate


@pytest.fixture
def mock_tts_realistic(monkeypatch):
    """Realistic TTS mock that creates proper WAV files without loading model."""
    def _generate(client, text, output_path, voice_reference=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a realistic silent WAV file (proper format)
        with wave.open(str(output_path), "wb") as wavf:
            wavf.setnchannels(1)  # Mono
            wavf.setsampwidth(2)  # 16-bit
            wavf.setframerate(22050)  # 22.05kHz
            # Length proportional to text length (simulate real TTS)
            duration_seconds = len(text) / 150  # ~150 chars per second
            num_frames = int(22050 * duration_seconds)
            frames = b"\x00\x00" * max(num_frames, 100)  # At least 100 frames
            wavf.writeframes(frames)
    
    # Mock the generate_audio function in BOTH the source module AND where it's imported
    monkeypatch.setattr('src.ai_radio.generation.tts_client.generate_audio', _generate)
    monkeypatch.setattr('src.ai_radio.generation.pipeline.generate_audio', _generate)
    
    # Mock the model getter to prevent loading
    monkeypatch.setattr('src.ai_radio.generation.tts_client._get_model', lambda: None)
    monkeypatch.setattr('src.ai_radio.generation.tts_client.check_tts_available', lambda *args: True)
    
    yield _generate


@pytest.fixture
def mock_services(mock_llm_realistic, mock_tts_realistic):
    """Combined fixture for both LLM and TTS mocking with realistic behavior.
    
    Also creates placeholder voice reference files if they don't exist, since
    the pipeline checks for their existence before generating audio.
    """
    from src.ai_radio.config import VOICE_REFERENCES_DIR
    
    # Create placeholder voice reference files for tests
    for dj_folder, dj_name in [("Julie", "julie"), ("Mister_New_Vegas", "mr_new_vegas")]:
        voice_dir = VOICE_REFERENCES_DIR / dj_folder
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        # Create placeholder WAV files (minimal valid WAV header)
        for suffix in ["", "_30sec"]:
            voice_file = voice_dir / f"{dj_name}{suffix}.wav"
            if not voice_file.exists():
                with wave.open(str(voice_file), "wb") as wavf:
                    wavf.setnchannels(1)
                    wavf.setsampwidth(2)
                    wavf.setframerate(22050)
                    wavf.writeframes(b"\x00\x00" * 100)
    
    return {"llm": mock_llm_realistic, "tts": mock_tts_realistic}


@pytest.fixture
def mock_service_checks(monkeypatch):
    """Mock service availability checks to return True."""
    monkeypatch.setattr('src.ai_radio.generation.llm_client.check_ollama_available', lambda: True)
    monkeypatch.setattr('src.ai_radio.generation.tts_client.check_tts_available', lambda: True)
    yield


@pytest.fixture
def sample_song_list():
    return [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]
