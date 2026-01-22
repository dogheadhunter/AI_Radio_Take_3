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


def test_raises_on_tts_error(monkeypatch, tmp_path):
    class BrokenClient:
        def synthesize(self, *args, **kwargs):
            raise Exception("boom")

    client = BrokenClient()
    with pytest.raises(TTSError):
        generate_audio(client, text="Hello", output_path=tmp_path / "out.wav")


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
