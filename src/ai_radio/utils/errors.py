"""Custom exceptions for AI Radio Station.

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
        return self.message


# Library Errors
class MusicLibraryError(AIRadioError):
    """Errors related to music library operations."""


class SongNotFoundError(MusicLibraryError):
    """A specific song could not be found."""


class MetadataError(MusicLibraryError):
    """Error reading or writing song metadata."""


# Generation Errors
class GenerationError(AIRadioError):
    """Errors during content generation."""


class LLMError(GenerationError):
    """Error communicating with Ollama/LLM."""


class TTSError(GenerationError):
    """Error during text-to-speech generation."""


# Playback Errors
class PlaybackError(AIRadioError):
    """Errors during audio playback."""


class AudioFileError(PlaybackError):
    """Error with an audio file (corrupt, missing, wrong format)."""


# Service Errors
class ServiceError(AIRadioError):
    """Errors with external services."""


class WeatherAPIError(ServiceError):
    """Error fetching weather data."""
