"""Integration tests for generation pipeline (skipped unless services available).

These tests require real external services:
- Ollama LLM (http://localhost:11434)
- Chatterbox TTS (local model or Docker)

To run these tests:
    TEST_MODE=integration pytest tests/generation/test_pipeline_integration.py

To skip these tests (default):
    pytest  # or TEST_MODE=mock pytest
"""
import pytest
from pathlib import Path
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.llm_client import check_ollama_available
from src.ai_radio.generation.tts_client import check_tts_available
import wave


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_services
def test_pipeline_integration_full(tmp_path):
    """Integration test: Full pipeline with real LLM and TTS services."""
    if not (check_ollama_available() and check_tts_available()):
        pytest.skip("Required services not available")

    pipeline = GenerationPipeline(output_dir=tmp_path)

    songs = [{"id": "int_test", "artist": "Test", "title": "Integration Song"}]
    results = list(pipeline.generate_batch_intros(songs))

    assert len(results) == 1
    res = results[0]
    assert res.success
    assert res.audio_path is not None
    assert res.audio_path.exists()
    
    # Verify it's a valid audio file
    with wave.open(str(res.audio_path), "rb") as wav:
        assert wav.getnchannels() > 0
        assert wav.getsampwidth() > 0
        assert wav.getframerate() > 0


@pytest.mark.integration
@pytest.mark.requires_services
def test_pipeline_integration_text_only(tmp_path):
    """Integration test: Text generation only (faster, requires Ollama only)."""
    if not check_ollama_available():
        pytest.skip("Ollama not available")
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_song_intro(
        song_id="text_test",
        artist="Integration Artist",
        title="Integration Song",
        dj="julie",
        text_only=True
    )
    
    assert result.success
    assert result.text is not None
    assert len(result.text) > 0
    # Verify it's actual generated content, not a mock
    assert "Test" not in result.text or "fake" not in result.text.lower()


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_services
def test_pipeline_integration_weather(tmp_path):
    """Integration test: Weather announcement with real services."""
    if not (check_ollama_available() and check_tts_available()):
        pytest.skip("Required services not available")
    
    from src.ai_radio.services.weather import WeatherData
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    weather = WeatherData(
        temperature=72,
        conditions="Sunny",
        humidity=30,
        wind_speed=8,
        wind_direction="SW",
        timestamp="2026-01-23T12:00:00"
    )
    
    result = pipeline.generate_weather_announcement(
        hour=12,
        minute=0,
        dj="mr_new_vegas",
        weather_data=weather
    )
    
    assert result.success
    assert result.text is not None
    assert result.audio_path is not None
    assert result.audio_path.exists()

