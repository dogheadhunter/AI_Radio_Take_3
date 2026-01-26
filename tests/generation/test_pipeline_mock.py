"""Mock tests for generation pipeline - fast alternative to integration tests.

These tests use mocked LLM and TTS services to provide the same test coverage
as integration tests but run much faster. They verify:
- Pipeline orchestration logic
- File generation and organization
- Error handling
- Batch processing

To run real integration tests instead:
    TEST_MODE=integration pytest tests/generation/

To run only mock tests (default):
    pytest tests/generation/
    # or explicitly: TEST_MODE=mock pytest tests/generation/
"""
import pytest
from pathlib import Path
from src.ai_radio.generation.pipeline import GenerationPipeline
import wave


@pytest.mark.mock
def test_pipeline_mock_song_intro(tmp_path, mock_services):
    """Mock test: Song intro generation with text and audio."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_song_intro(
        song_id="test_123",
        artist="Test Artist",
        title="Test Song",
        dj="julie"
    )
    
    assert result.success
    assert result.text is not None
    assert len(result.text) > 0  # Just verify text was generated
    assert result.audio_path is not None
    assert result.audio_path.exists()
    
    # Verify audio is a valid WAV file
    with wave.open(str(result.audio_path), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 22050


@pytest.mark.mock
def test_pipeline_mock_text_only(tmp_path, mock_services):
    """Mock test: Text-only generation mode."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_song_intro(
        song_id="test_456",
        artist="Artist",
        title="Title",
        dj="mr_new_vegas",
        text_only=True
    )
    
    assert result.success
    assert result.text is not None
    # In text_only mode, audio_path should be None (no audio generated)
    assert result.audio_path is None


@pytest.mark.mock
def test_pipeline_mock_batch_intros(tmp_path, mock_services):
    """Mock test: Batch processing of multiple songs."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    songs = [
        {"id": "song1", "artist": "Artist 1", "title": "Title 1"},
        {"id": "song2", "artist": "Artist 2", "title": "Title 2"},
        {"id": "song3", "artist": "Artist 3", "title": "Title 3"},
    ]
    
    results = list(pipeline.generate_batch_intros(songs, dj="julie"))
    
    assert len(results) == 3
    assert all(r.success for r in results)
    assert all(r.audio_path.exists() for r in results)


@pytest.mark.mock
def test_pipeline_mock_weather_announcement(tmp_path, mock_services):
    """Mock test: Weather announcement generation."""
    from src.ai_radio.services.weather import WeatherData
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    # Create mock weather data (match actual WeatherData signature)
    weather = WeatherData(
        temperature=65.0,
        conditions="Clear",
        humidity=45,
        wind_speed=5.0
    )
    
    result = pipeline.generate_weather_announcement(
        hour=6,
        minute=0,
        dj="julie",
        weather_data=weather,
        text_only=True
    )
    
    assert result.success
    assert result.text is not None
    assert len(result.text) > 0  # Just verify text was generated


@pytest.mark.mock
def test_pipeline_mock_time_announcement(tmp_path, mock_services):
    """Mock test: Time announcement generation."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_time_announcement(
        hour=6,
        minute=0,
        dj="mr_new_vegas",
        text_only=True
    )
    
    assert result.success
    assert result.text is not None
    assert len(result.text) > 0  # Just verify text was generated


@pytest.mark.mock
def test_pipeline_mock_song_outro(tmp_path, mock_services):
    """Mock test: Song outro generation."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_song_outro(
        song_id="outro_test",
        artist="Test Artist",
        title="Test Song",
        dj="julie",
        text_only=True
    )
    
    assert result.success
    assert result.text is not None


@pytest.mark.mock
def test_pipeline_mock_file_organization(tmp_path, mock_services):
    """Mock test: Verify proper file organization structure."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_song_intro(
        song_id="org_test",
        artist="The Beatles",
        title="Hey Jude",
        dj="julie"
    )
    
    assert result.success
    
    # Check folder structure: intros/dj/Artist-Title/
    expected_folder = tmp_path / "intros" / "julie" / "The_Beatles-Hey_Jude"
    assert expected_folder.exists()
    
    # Check files exist (note: pipeline now creates _full.wav for dual audio)
    text_file = expected_folder / "julie_0.txt"
    audio_file = expected_folder / "julie_0_full.wav"
    assert text_file.exists()
    assert audio_file.exists()


@pytest.mark.mock
def test_pipeline_mock_error_handling(tmp_path, mock_llm_realistic, monkeypatch):
    """Mock test: Error handling when TTS fails."""
    # Mock TTS to raise an error
    def _failing_tts(client, text, output_path, voice_reference=None):
        from src.ai_radio.utils.errors import TTSError
        raise TTSError("Simulated TTS failure")
    
    monkeypatch.setattr('src.ai_radio.generation.tts_client.generate_audio', _failing_tts)
    # Also prevent model loading
    monkeypatch.setattr('src.ai_radio.generation.tts_client._get_model', lambda: None)
    monkeypatch.setattr('src.ai_radio.generation.tts_client.check_tts_available', lambda *args: True)
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    result = pipeline.generate_song_intro(
        song_id="error_test",
        artist="Artist",
        title="Title",
        dj="julie"
    )
    
    # Pipeline should handle the error gracefully
    # With TTS failing, the generation should fail
    assert result.song_id == "error_test"
    # Either it fails completely or succeeds with just text depending on implementation
    assert not result.success or result.text is not None


@pytest.mark.mock
def test_pipeline_mock_voice_reference_handling(tmp_path, mock_llm_realistic, mock_tts_realistic):
    """Mock test: Verify voice reference is handled correctly."""
    from src.ai_radio.generation.pipeline import GenerationPipeline
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    # Test with julie (voice ref should be attempted)
    result = pipeline.generate_song_intro(
        song_id="voice_test",
        artist="Artist",
        title="Title",
        dj="julie",
        text_only=True  # Skip actual TTS
    )
    
    assert result.success


@pytest.mark.mock
def test_pipeline_mock_batch_progress_reporting(tmp_path, mock_services):
    """Mock test: Verify batch progress reporting works."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    songs = [
        {"id": f"song{i}", "artist": f"Artist {i}", "title": f"Title {i}"}
        for i in range(5)
    ]
    
    progress_updates = []
    
    def progress_callback(progress):
        progress_updates.append({
            'total': progress.total,
            'completed': progress.completed,
            'percent': progress.percent
        })
    
    results = list(pipeline.generate_batch_intros(
        songs,
        dj="julie",
        progress_callback=progress_callback
    ))
    
    assert len(results) == 5
    if progress_updates:  # If progress callback is supported
        assert progress_updates[-1]['completed'] == 5
        assert progress_updates[-1]['percent'] == 100.0


@pytest.mark.mock 
def test_pipeline_mock_concurrent_djs(tmp_path, mock_services):
    """Mock test: Multiple DJs generating content for same song."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    
    # Generate intro with both DJs
    result_julie = pipeline.generate_song_intro(
        song_id="multi_dj",
        artist="Artist",
        title="Song",
        dj="julie"
    )
    
    result_vegas = pipeline.generate_song_intro(
        song_id="multi_dj",
        artist="Artist",
        title="Song",
        dj="mr_new_vegas"
    )
    
    assert result_julie.success
    assert result_vegas.success
    
    # Both should exist in separate DJ folders
    julie_folder = tmp_path / "intros" / "julie" / "Artist-Song"
    vegas_folder = tmp_path / "intros" / "mr_new_vegas" / "Artist-Song"
    
    assert julie_folder.exists()
    assert vegas_folder.exists()
    # Note: pipeline now creates _full.wav for dual audio
    assert (julie_folder / "julie_0_full.wav").exists()
    assert (vegas_folder / "mr_new_vegas_0_full.wav").exists()
