# Checkpoint 2.4: Generation Pipeline (Continued)

## Phase 2: Content Generation Pipeline (Continued)

#### Checkpoint 2.4: Generation Pipeline (Continued)
**Orchestrate the full generation process.**

**Tasks:**
1. Create `src/ai_radio/generation/pipeline. py`
2. Combine LLM and TTS for complete content generation
3. Handle sequential processing (LLM first, then TTS — never simultaneous due to VRAM limits)
4. Implement progress tracking and resumability

**Tests First:**
```python
# tests/generation/test_pipeline.py
"""Tests for generation pipeline."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.ai_radio. generation.pipeline import (
    GenerationPipeline,
    generate_song_intro,
    generate_batch_intros,
    GenerationResult,
    BatchProgress,
)


class TestGenerateSongIntro: 
    """Test single song intro generation."""
    
    def test_returns_generation_result(self, mock_llm, mock_tts):
        """Must return a GenerationResult object."""
        pipeline = GenerationPipeline()
        result = generate_song_intro(
            pipeline,
            song_id="test_song",
            artist="Test Artist",
            title="Test Song",
            dj="julie",
        )
        assert isinstance(result, GenerationResult)
    
    def test_result_contains_text(self, mock_llm, mock_tts):
        """Result must contain generated text."""
        mock_llm.return_value = "Here's a great song!"
        pipeline = GenerationPipeline()
        result = generate_song_intro(
            pipeline,
            song_id="test_song",
            artist="Test Artist",
            title="Test Song",
            dj="julie",
        )
        assert result.text is not None
        assert len(result.text) > 0
    
    def test_result_contains_audio_path(self, mock_llm, mock_tts, tmp_path):
        """Result must contain path to generated audio."""
        pipeline = GenerationPipeline(output_dir=tmp_path)
        result = generate_song_intro(
            pipeline,
            song_id="test_song",
            artist="Test Artist",
            title="Test Song",
            dj="julie",
        )
        assert result.audio_path is not None
        assert result.audio_path.exists()
    
    def test_llm_called_before_tts(self, mock_llm, mock_tts):
        """LLM must be called before TTS (sequential processing)."""
        call_order = []
        mock_llm.side_effect = lambda *args:  call_order.append("llm") or "Generated text"
        mock_tts.side_effect = lambda *args: call_order.append("tts")
        
        pipeline = GenerationPipeline()
        generate_song_intro(pipeline, "id", "Artist", "Title", "julie")
        
        assert call_order == ["llm", "tts"]


class TestBatchGeneration: 
    """Test batch intro generation."""
    
    def test_processes_all_songs(self, mock_llm, mock_tts, sample_song_list):
        """Must process all songs in the list."""
        pipeline = GenerationPipeline()
        results = list(generate_batch_intros(pipeline, sample_song_list))
        assert len(results) == len(sample_song_list)
    
    def test_continues_on_single_failure(self, mock_llm_sometimes_fails, mock_tts):
        """Must continue processing if one song fails."""
        pipeline = GenerationPipeline()
        songs = [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]
        
        results = list(generate_batch_intros(pipeline, songs))
        
        # Should have results for all songs (some may be failures)
        assert len(results) == 5
    
    def test_tracks_progress(self, mock_llm, mock_tts, sample_song_list):
        """Must yield progress updates."""
        pipeline = GenerationPipeline()
        
        progress_updates = []
        for result in generate_batch_intros(
            pipeline, 
            sample_song_list,
            progress_callback=lambda p: progress_updates.append(p)
        ):
            pass
        
        assert len(progress_updates) > 0
        assert progress_updates[-1].completed == len(sample_song_list)
    
    def test_can_resume_from_checkpoint(self, mock_llm, mock_tts, tmp_path):
        """Must be able to resume interrupted batch."""
        pipeline = GenerationPipeline(output_dir=tmp_path)
        songs = [{"id":  f"song_{i}", "artist": "Test", "title":  f"Song {i}"} for i in range(10)]
        
        # Simulate partial completion
        for i in range(5):
            (tmp_path / "intros" / f"song_{i}_julie_0.wav").parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / "intros" / f"song_{i}_julie_0.wav").touch()
        
        # Resume should skip completed
        results = list(generate_batch_intros(pipeline, songs, resume=True))
        
        # Should only generate for remaining 5
        new_generations = [r for r in results if not r.skipped]
        assert len(new_generations) == 5


class TestSequentialProcessing: 
    """Test that LLM and TTS never run simultaneously."""
    
    def test_unloads_llm_before_tts(self, mock_llm, mock_tts):
        """Must unload LLM before starting TTS."""
        pipeline = GenerationPipeline()
        
        # Track if LLM is "loaded" when TTS runs
        llm_loaded_during_tts = []
        
        def track_tts(*args, **kwargs):
            llm_loaded_during_tts.append(pipeline._llm_loaded)
        
        mock_tts.side_effect = track_tts
        
        generate_song_intro(pipeline, "id", "Artist", "Title", "julie")
        
        # LLM should not be loaded when TTS runs
        assert not any(llm_loaded_during_tts)
```

**Implementation Specification:**
```python
# src/ai_radio/generation/pipeline.py
"""
Content generation pipeline. 

Orchestrates LLM and TTS for generating radio content. 
Handles sequential processing to respect VRAM limits. 
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Callable, Optional, List, Dict, Any
from src.ai_radio. generation.llm_client import LLMClient, generate_text
from src.ai_radio.generation. tts_client import TTSClient, generate_audio
from src.ai_radio. generation.prompts import build_song_intro_prompt, DJ
from src.ai_radio.utils.logging import setup_logging, log_error_with_context
from src.ai_radio. utils.errors import GenerationError


@dataclass
class GenerationResult:
    """Result of a single content generation."""
    song_id: str
    dj: str
    text: str
    audio_path: Optional[Path]
    success: bool
    error: Optional[str] = None
    skipped: bool = False


@dataclass
class BatchProgress:
    """Progress of batch generation."""
    total: int
    completed: int
    failed: int
    current_song: str
    
    @property
    def percent(self) -> float:
        return (self.completed / self.total) * 100 if self.total > 0 else 0


class GenerationPipeline:
    """
    Orchestrates content generation. 
    
    Ensures LLM and TTS never run simultaneously.
    Supports batch processing with progress tracking. 
    Supports resuming interrupted batches. 
    """
    
    def __init__(self, output_dir:  Path = None):
        self.output_dir = output_dir or Path("data/generated")
        self. logger = setup_logging("generation. pipeline")
        self._llm_loaded = False
        self._tts_loaded = False
    
    # Implementation details...
```

**Success Criteria:**
- [x] All pipeline tests pass
- [x] Single song generation works end-to-end
- [x] Batch generation processes all songs
- [x] Failed songs don't stop the batch
- [x] Can resume interrupted batches
- [x] LLM and TTS never run simultaneously

**Validation:**
```bash
# Human runs: 
pytest tests/generation/test_pipeline.py -v

# Human runs integration test (requires Ollama + Chatterbox):
pytest tests/generation/test_pipeline. py -v -m integration
```

**Git Commit:** `feat(generation): add generation pipeline`
