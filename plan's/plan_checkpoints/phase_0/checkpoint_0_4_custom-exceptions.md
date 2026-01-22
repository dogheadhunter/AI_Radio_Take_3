# Checkpoint 0.4: Custom Exceptions

#### Checkpoint 0.4: Custom Exceptions
**Create custom exception classes for clear error handling.**

**Tasks:**
1. Create `src/ai_radio/utils/errors.py`
2. Define exception hierarchy
3. Create exception tests

**File: `src/ai_radio/utils/errors.py`**
```python
"""
Custom exceptions for AI Radio Station. 

Clear, descriptive exceptions make debugging easier.
Each exception includes context for logging.
"""


class AIRadioError(Exception):
    """Base exception for all AI Radio errors."""
    
    def __init__(self, message: str, suggestion: str = ""):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def __str__(self):
        if self.suggestion:
            return f"{self.message}\nSuggestion:  {self.suggestion}"
        return self. message


# Library Errors
class MusicLibraryError(AIRadioError):
    """Errors related to music library operations."""
    pass


class SongNotFoundError(MusicLibraryError):
    """A specific song could not be found."""
    pass


class MetadataError(MusicLibraryError):
    """Error reading or writing song metadata."""
    pass


# Generation Errors
class GenerationError(AIRadioError):
    """Errors during content generation."""
    pass


class LLMError(GenerationError):
    """Error communicating with Ollama/LLM."""
    pass


class TTSError(GenerationError):
    """Error during text-to-speech generation."""
    pass


# Playback Errors
class PlaybackError(AIRadioError):
    """Errors during audio playback."""
    pass


class AudioFileError(PlaybackError):
    """Error with an audio file (corrupt, missing, wrong format)."""
    pass


# Service Errors
class ServiceError(AIRadioError):
    """Errors with external services."""
    pass


class WeatherAPIError(ServiceError):
    """Error fetching weather data."""
    pass
```

**File: `tests/utils/test_errors.py`**
```python
"""Tests for custom exceptions."""
import pytest
from src.ai_radio.utils. errors import (
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
        assert error. suggestion == ""
    
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
```

**Success Criteria:**
- [ ] `pytest tests/utils/test_errors.py` passes all tests
- [ ] All exceptions can be caught by `AIRadioError`
- [ ] Exception strings include suggestions when provided

**Validation:**
```bash
# Human runs: 
pytest tests/utils/test_errors. py -v
```

**Git Commit:** `feat(errors): add custom exception hierarchy`
