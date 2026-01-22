"""Integration tests for generation pipeline (skipped unless services available)."""
import pytest
from pathlib import Path
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.llm_client import check_ollama_available
from src.ai_radio.generation.tts_client import check_tts_available


@pytest.mark.integration
@pytest.mark.slow
def test_pipeline_integration(tmp_path):
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
