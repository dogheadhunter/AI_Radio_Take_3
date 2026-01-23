"""Tests for TTS client."""
import pytest
from pathlib import Path
from src.ai_radio.generation.tts_client import TTSClient, generate_audio, check_tts_available
from src.ai_radio.utils.errors import TTSError


def test_generate_creates_file(tmp_path):
    client = TTSClient()
    output_path = tmp_path / "output.wav"
    generate_audio(client, text="Hello world", output_path=output_path)
    assert output_path.exists()


def test_generate_with_voice_reference(tmp_path, tmp_path_factory):
    client = TTSClient()
    output_path = tmp_path / "output_with_ref.wav"
    # voice sample: just make a small file path
    voice_sample = tmp_path / "voice.wav"
    voice_sample.write_bytes(b"dummy")
    generate_audio(client, text="Hello", output_path=output_path, voice_reference=voice_sample)
    assert output_path.exists()


def test_fallback_on_tts_error(monkeypatch, tmp_path):
    """When TTS fails, generate_audio creates a silent placeholder instead of raising."""
    class BrokenClient:
        def synthesize(self, *args, **kwargs):
            raise TTSError("boom")  # Must raise TTSError for fallback to catch

    client = BrokenClient()
    output_path = tmp_path / "out.wav"
    # Should NOT raise - instead creates silent fallback
    generate_audio(client, text="Hello", output_path=output_path)
    assert output_path.exists()  # Silent WAV was created


def test_synthesize_raises_on_error():
    """TTSClient.synthesize should raise TTSError when model fails."""
    client = TTSClient()
    # Force model to None to simulate failure
    client._model = None  
    # Monkeypatch to prevent model loading
    import src.ai_radio.generation.tts_client as tts_module
    original = tts_module._model_load_attempted
    tts_module._model_load_attempted = True
    tts_module._model = None
    try:
        with pytest.raises(TTSError):
            client.synthesize("Hello")
    finally:
        tts_module._model_load_attempted = original


def test_check_tts_available():
    assert isinstance(check_tts_available(), bool)


import pytest

@pytest.mark.integration
@pytest.mark.slow
def test_real_generation_integration(tmp_path):
    """Call Chatterbox if available and generate audio file.

    If the synthesize endpoint returns 404 or otherwise indicates missing
    functionality, skip the test to avoid failing CI when the service is
    partially present.
    """
    if not check_tts_available():
        pytest.skip("Chatterbox not available")

    client = TTSClient()
    output_path = tmp_path / "test_output.wav"
    try:
        generate_audio(client, text="Hello, this is a test.", output_path=output_path)
    except Exception as exc:
        msg = str(exc).lower()
        if "404" in msg or "not found" in msg:
            pytest.skip("Chatterbox synthesize endpoint not available (404)")
        raise

    assert output_path.exists()
    assert output_path.stat().st_size > 0
