"""Tests for Generation API."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.ai_radio.api.generation import GenerationAPI
from src.ai_radio.api.schemas import ContentType, DJ, GenerationResult, SongInfo


@pytest.fixture
def sample_song():
    """Create a sample SongInfo."""
    return SongInfo(id="1", artist="Test Artist", title="Test Song")


@pytest.fixture
def mock_pipeline():
    """Create a mock generation pipeline."""
    pipeline = MagicMock()
    
    # Mock successful result
    result = MagicMock()
    result.success = True
    result.text = "Hey there, listeners! Here's a great song coming up for you on this fine day."
    
    pipeline.generate_song_intro.return_value = result
    pipeline.generate_song_outro.return_value = result
    pipeline.generate_time_announcement.return_value = result
    pipeline.generate_weather_announcement.return_value = result
    
    return pipeline


@pytest.fixture
def generation_api(tmp_path, mock_pipeline, monkeypatch):
    """Create a GenerationAPI with mock pipeline."""
    from src.ai_radio import config
    monkeypatch.setattr(config, 'GENERATED_DIR', tmp_path / "generated")
    monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
    
    return GenerationAPI(
        output_dir=tmp_path / "generated",
        test_mode=True,
        pipeline=mock_pipeline,
    )


class TestGenerateIntro:
    """Test intro generation."""
    
    def test_generate_intro_success(self, generation_api, sample_song):
        """Successful generation should return result with text."""
        result = generation_api.generate_intro(song=sample_song, dj=DJ.JULIE, overwrite=True)
        
        assert result.success
        assert result.content_type == ContentType.INTRO
        assert result.dj == DJ.JULIE
        assert result.text is not None
    
    def test_generate_intro_saves_file(self, generation_api, sample_song):
        """Generation should save script file."""
        result = generation_api.generate_intro(song=sample_song, dj=DJ.JULIE, overwrite=True)
        
        assert result.script_path is not None
        assert result.script_path.exists()
    
    def test_generate_intro_skip_existing(self, generation_api):
        """Should skip generation if script exists and overwrite=False."""
        # Use a unique song to avoid pollution from other tests
        unique_song = SongInfo(id="unique_skip", artist="Skip Artist", title="Skip Song")
        
        # Generate first time
        result1 = generation_api.generate_intro(song=unique_song, dj=DJ.JULIE, overwrite=True)
        call_count_after_first = generation_api.pipeline.generate_song_intro.call_count
        
        # Generate second time - should return existing (skip pipeline call)
        result2 = generation_api.generate_intro(song=unique_song, dj=DJ.JULIE, overwrite=False)
        
        assert result2.success
        assert result1.script_path == result2.script_path
        # Pipeline should not be called again
        assert generation_api.pipeline.generate_song_intro.call_count == call_count_after_first
    
    def test_generate_intro_overwrite(self, generation_api):
        """Should regenerate if overwrite=True."""
        # Use a unique song
        unique_song = SongInfo(id="unique_overwrite", artist="Overwrite Artist", title="Overwrite Song")
        
        # Generate first time
        generation_api.generate_intro(song=unique_song, dj=DJ.JULIE, overwrite=True)
        call_count_after_first = generation_api.pipeline.generate_song_intro.call_count
        
        # Generate with overwrite - should call pipeline again
        generation_api.generate_intro(song=unique_song, dj=DJ.JULIE, overwrite=True)
        
        # Pipeline should be called again
        assert generation_api.pipeline.generate_song_intro.call_count == call_count_after_first + 1
    
    def test_generate_intro_with_feedback(self, generation_api):
        """Should pass audit feedback to pipeline."""
        unique_song = SongInfo(id="unique_feedback", artist="Feedback Artist", title="Feedback Song")
        
        generation_api.generate_intro(
            song=unique_song,
            dj=DJ.JULIE,
            audit_feedback="Wrong character voice",
            overwrite=True,
        )
        
        # Verify feedback was passed
        call_kwargs = generation_api.pipeline.generate_song_intro.call_args[1]
        assert call_kwargs.get('audit_feedback') == "Wrong character voice"


class TestGenerateOutro:
    """Test outro generation."""
    
    def test_generate_outro_success(self, generation_api, sample_song):
        """Successful outro generation."""
        result = generation_api.generate_outro(song=sample_song, dj=DJ.MR_NEW_VEGAS, overwrite=True)
        
        assert result.success
        assert result.content_type == ContentType.OUTRO
        assert result.dj == DJ.MR_NEW_VEGAS


class TestGenerateTimeAnnouncement:
    """Test time announcement generation."""
    
    def test_generate_time_success(self, generation_api):
        """Successful time generation."""
        result = generation_api.generate_time_announcement(
            hour=14,
            minute=30,
            dj=DJ.JULIE,
            overwrite=True,
        )
        
        assert result.success
        assert result.content_type == ContentType.TIME
        assert result.hour == 14
        assert result.minute == 30
    
    def test_generate_time_saves_file(self, generation_api):
        """Time announcement should save script file."""
        result = generation_api.generate_time_announcement(
            hour=21,  # Use less common hour
            minute=0,
            dj=DJ.JULIE,
            overwrite=True,
        )
        
        assert result.script_path is not None
        assert result.script_path.exists()
        assert "21-00" in str(result.script_path)


class TestGenerateWeatherAnnouncement:
    """Test weather announcement generation."""
    
    def test_generate_weather_success(self, generation_api):
        """Successful weather generation."""
        result = generation_api.generate_weather_announcement(
            hour=12,
            dj=DJ.MR_NEW_VEGAS,
            weather_summary="Clear skies, temperature around 75 degrees today in the Mojave.",
            overwrite=True,
        )
        
        assert result.success
        assert result.content_type == ContentType.WEATHER
        assert result.hour == 12


class TestGenerationFailures:
    """Test handling of generation failures."""
    
    def test_pipeline_failure(self, tmp_path, monkeypatch):
        """Should handle pipeline failures gracefully."""
        from src.ai_radio import config
        monkeypatch.setattr(config, 'GENERATED_DIR', tmp_path / "gen_fail")
        
        # Use unique song that doesn't exist
        unique_song = SongInfo(id="fail_test", artist="Fail Artist", title="Fail Song")
        
        failed_pipeline = MagicMock()
        failed_result = MagicMock()
        failed_result.success = False
        failed_result.text = None
        failed_result.error = "LLM service unavailable"
        failed_pipeline.generate_song_intro.return_value = failed_result
        
        api = GenerationAPI(
            output_dir=tmp_path / "gen_fail",
            pipeline=failed_pipeline,
        )
        
        result = api.generate_intro(song=unique_song, dj=DJ.JULIE)
        
        assert not result.success
        assert result.error is not None
    
    def test_exception_handling(self, tmp_path, monkeypatch):
        """Should handle exceptions gracefully."""
        from src.ai_radio import config
        monkeypatch.setattr(config, 'GENERATED_DIR', tmp_path / "gen_exc")
        
        # Use unique song that doesn't exist
        unique_song = SongInfo(id="exc_test", artist="Exc Artist", title="Exc Song")
        
        error_pipeline = MagicMock()
        error_pipeline.generate_song_intro.side_effect = Exception("Connection failed")
        
        api = GenerationAPI(
            output_dir=tmp_path / "gen_exc",
            pipeline=error_pipeline,
        )
        
        result = api.generate_intro(song=unique_song, dj=DJ.JULIE)
        
        assert not result.success
        assert "Connection failed" in result.error


class TestBatchGeneration:
    """Test batch generation functionality."""
    
    def test_generate_batch(self, generation_api):
        """Should generate batch of content."""
        songs = [
            SongInfo(id="batch1", artist="Batch Artist 1", title="Batch Song 1"),
            SongInfo(id="batch2", artist="Batch Artist 2", title="Batch Song 2"),
        ]
        
        results = generation_api.generate_batch(
            songs=songs,
            djs=[DJ.JULIE],
            content_types=[ContentType.INTRO],
        )
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    def test_generate_batch_multiple_types(self, generation_api):
        """Should generate multiple content types."""
        songs = [SongInfo(id="batch_multi", artist="Multi Artist", title="Multi Song")]
        
        results = generation_api.generate_batch(
            songs=songs,
            djs=[DJ.JULIE],
            content_types=[ContentType.INTRO, ContentType.OUTRO],
        )
        
        assert len(results) == 2
        types = {r.content_type for r in results}
        assert ContentType.INTRO in types
        assert ContentType.OUTRO in types
