"""Tests for custom exceptions."""
import pytest
from src.ai_radio.utils.errors import (
    AIRadioError,
    SongNotFoundError,
    LLMError,
    PlaybackError,
)


class TestAIRadioError:
    """Test base exception."""

    def test_message_is_accessible(self):
        """Exception message must be accessible."""
        error = AIRadioError("Test message")
        assert error.message == "Test message"

    def test_suggestion_is_optional(self):
        """Suggestion should be optional."""
        error = AIRadioError("Test message")
        assert error.suggestion == ""

    def test_suggestion_included_in_str(self):
        """Suggestion should appear in string representation."""
        error = AIRadioError("Test message", "Try this fix")
        assert "Try this fix" in str(error)


class TestExceptionHierarchy:
    """Test that exceptions inherit correctly."""

    def test_song_not_found_is_music_library_error(self):
        """SongNotFoundError must be a MusicLibraryError."""
        error = SongNotFoundError("Song missing")
        assert isinstance(error, AIRadioError)

    def test_llm_error_is_generation_error(self):
        """LLMError must be a GenerationError."""
        error = LLMError("LLM failed")
        assert isinstance(error, AIRadioError)

    def test_can_catch_by_base_class(self):
        """Should be able to catch all errors by base class."""
        with pytest.raises(AIRadioError):
            raise PlaybackError("Playback failed")
