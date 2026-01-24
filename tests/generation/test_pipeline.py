"""Tests for generation pipeline."""
import pytest
from pathlib import Path
from src.ai_radio.generation.pipeline import GenerationPipeline, generate_song_intro as _gs, GenerationResult


@pytest.fixture
def sample_song_list():
    return [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]


def test_returns_generation_result(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class Dummy:
        def generate(self, prompt):
            return "Generated text"

    monkeypatch.setattr(pipeline, "_llm", Dummy())

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    result = pipeline.generate_song_intro(song_id="test_song", artist="Test Artist", title="Test Song", dj="julie")
    assert isinstance(result, GenerationResult)


def test_result_contains_text(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class Dummy:
        def generate(self, prompt, banned_phrases=None):
            return "Here's a great song!"

    monkeypatch.setattr(pipeline, "_llm", Dummy())

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    result = pipeline.generate_song_intro(song_id="test_song", artist="Test Artist", title="Test Song", dj="julie")
    assert result.text is not None
    assert len(result.text) > 0


def test_result_contains_audio_path(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class Dummy:
        def generate(self, prompt, banned_phrases=None):
            return "Some text"

    monkeypatch.setattr(pipeline, "_llm", Dummy())

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    result = pipeline.generate_song_intro(song_id="test_song", artist="Test Artist", title="Test Song", dj="julie")
    assert result.audio_path is not None
    assert result.audio_path.exists()


def test_llm_called_before_tts(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)
    call_order = []

    class MockLLM:
        def generate(self, prompt, banned_phrases=None):
            call_order.append("llm")
            return "Generated text"

    class MockTTS:
        def synthesize(self, *a, **k):
            call_order.append("tts")
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_llm", MockLLM())
    monkeypatch.setattr(pipeline, "_tts", MockTTS())

    pipeline.generate_song_intro("id", "Artist", "Title", "julie")
    assert call_order == ["llm", "tts"]


def test_processes_all_songs(monkeypatch, tmp_path, sample_song_list):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class DummyLLM:
        def generate(self, prompt):
            return "Generated"

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    results = list(pipeline.generate_batch_intros(sample_song_list))
    assert len(results) == len(sample_song_list)


def test_continues_on_single_failure(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class FlakyLLM:
        def __init__(self):
            self.count = 0

        def generate(self, prompt):
            self.count += 1
            if self.count == 3:
                raise Exception("boom")
            return "Generated"

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_llm", FlakyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    songs = [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]
    results = list(pipeline.generate_batch_intros(songs))
    assert len(results) == 5


def test_tracks_progress(monkeypatch, tmp_path, sample_song_list):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class DummyLLM:
        def generate(self, prompt, banned_phrases=None):
            return "Generated"

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    progress_updates = []
    for result in pipeline.generate_batch_intros(sample_song_list, progress_callback=lambda p: progress_updates.append(p)):
        pass

    assert len(progress_updates) > 0
    assert progress_updates[-1].completed == len(sample_song_list)


def test_can_resume_from_checkpoint(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)

    class DummyLLM:
        def generate(self, prompt):
            return "Generated"

    class DummyTTS:
        def synthesize(self, *a, **k):
            return b"\x00\x00"

    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", DummyTTS())

    songs = [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(10)]

    # create files for first 5 in new DJ-organized structure
    for i in range(5):
        safe_artist = "Test"
        safe_title = f"Song_{i}"
        folder_name = f"{safe_artist}-{safe_title}"
        p = tmp_path / "intros" / "julie" / folder_name / "julie_0.wav"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\x00\x00")

    results = list(pipeline.generate_batch_intros(songs, resume=True))
    new_generations = [r for r in results if not r.skipped]
    assert len(new_generations) == 5


def test_unloads_llm_before_tts(monkeypatch, tmp_path):
    pipeline = GenerationPipeline(output_dir=tmp_path)
    llm_loaded_during_tts = []

    class TrackingTTS:
        def synthesize(self, *a, **k):
            llm_loaded_during_tts.append(pipeline._llm_loaded)
            return b"\x00\x00"

    class DummyLLM:
        def generate(self, prompt):
            return "Generated"

    monkeypatch.setattr(pipeline, "_llm", DummyLLM())
    monkeypatch.setattr(pipeline, "_tts", TrackingTTS())

    pipeline.generate_song_intro("id", "Artist", "Title", "julie")
    assert not any(llm_loaded_during_tts)
