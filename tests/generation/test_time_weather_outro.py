"""Tests for time/weather/outro generation pipeline."""
import pytest
from pathlib import Path
from src.ai_radio.generation.pipeline import GenerationPipeline, generate_batch_time_announcements, generate_batch_weather_announcements, generate_batch_outros


class DummyLLM:
    def generate(self, prompt):
        # Return prompt back for easy assertions
        return f"LLM: {prompt}"


class DummyTTS:
    def synthesize(self, *a, **k):
        return b"\x00\x00"


@pytest.fixture
def pipeline(tmp_path):
    return GenerationPipeline(output_dir=tmp_path)


def test_generate_time_announcement_creates_files(monkeypatch, pipeline):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    res = pipeline.generate_time_announcement(14, 30, "julie")
    assert res.success
    assert res.text is not None
    assert res.audio_path is not None
    assert res.audio_path.exists()


def test_batch_time_announcements_count(monkeypatch, pipeline):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    results = list(generate_batch_time_announcements(pipeline, dj="julie", resume=False))
    # 24 hours * 2 (00/30) = 48
    assert len(results) == 48
    assert all(r.success for r in results)


def test_batch_time_announcements_resume_skips(monkeypatch, pipeline, tmp_path):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    # Create a couple of existing files to be skipped
    slot_dir = tmp_path / "time" / "julie" / "14-30"
    slot_dir.mkdir(parents=True, exist_ok=True)
    (slot_dir / "julie_0.wav").write_bytes(b"\x00\x00")

    results = list(generate_batch_time_announcements(pipeline, dj="julie", resume=True))
    skipped = [r for r in results if r.skipped]
    assert len(skipped) >= 1


def test_generate_weather_announcement_creates_files(monkeypatch, pipeline):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    weather = {"summary": "Sunny", "temp": 72}
    res = pipeline.generate_weather_announcement(6, 0, "julie", weather_data=weather)
    assert res.success
    assert res.text is not None
    assert res.audio_path.exists()
    # metadata exists
    md = res.audio_path.parent / "weather_data.json"
    assert md.exists()


def test_batch_weather_announcements_uses_weather_service(monkeypatch, pipeline):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    class FakeWeatherService:
        def __init__(self, location=None):
            pass

        def get_current_weather(self):
            # Return an object compatible with WeatherData (simple dict allowed by pipeline usage)
            return {"summary": "Cloudy", "temp": 60}

        def get_forecast_for_hour(self, hour):
            return {"summary": "Cloudy", "temp": 60, "hour": hour}

    monkeypatch.setattr('src.ai_radio.services.weather.WeatherService', FakeWeatherService)

    results = list(generate_batch_weather_announcements(pipeline, dj="julie", resume=False))
    assert len(results) > 0
    assert all(isinstance(r.success, bool) for r in results)


def test_batch_weather_announcements_count(monkeypatch, pipeline):
    """Batch generation should produce one result for each configured weather time."""
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    class FakeWeatherService:
        def __init__(self, location=None):
            pass

        def get_current_weather(self):
            return {"summary": "Cloudy", "temp": 60}

        def get_forecast_for_hour(self, hour):
            return {"summary": "Cloudy", "temp": 60, "hour": hour}

    monkeypatch.setattr('src.ai_radio.services.weather.WeatherService', FakeWeatherService)

    from src.ai_radio.config import WEATHER_TIMES
    results = list(generate_batch_weather_announcements(pipeline, dj="julie", resume=False))
    assert len(results) == len(WEATHER_TIMES)


def test_weather_announcement_resume(monkeypatch, pipeline, tmp_path):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    # Create existing files for each configured weather time
    from src.ai_radio.config import WEATHER_TIMES
    for hour in WEATHER_TIMES:
        slot_dir = tmp_path / "weather" / "julie" / f"{hour:02d}-00"
        slot_dir.mkdir(parents=True, exist_ok=True)
        (slot_dir / "julie_0.wav").write_bytes(b"\x00\x00")

    monkeypatch.setattr('src.ai_radio.services.weather.WeatherService', lambda location=None: None)

    results = list(generate_batch_weather_announcements(pipeline, dj="julie", resume=True))
    skipped = [r for r in results if r.skipped]
    assert len(skipped) == len(WEATHER_TIMES)


def test_generate_song_outro_creates_files(monkeypatch, pipeline):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    res = pipeline.generate_song_outro("song_1", "Artist", "Title", "julie", next_song="Other Song")
    assert res.success
    assert res.text is not None
    assert res.audio_path.exists()


def test_batch_outros_resume(monkeypatch, pipeline, tmp_path):
    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    songs = [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]

    # create existing outro file for first song
    safe_artist = "Test"
    safe_title = "Song_0"
    folder_name = f"{safe_artist}-{safe_title}"
    p = tmp_path / "outros" / "julie" / folder_name / "julie_outro.wav"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\x00\x00")

    results = list(generate_batch_outros(pipeline, songs, dj="julie", resume=True))
    skipped = [r for r in results if r.skipped]
    assert len(skipped) == 1
