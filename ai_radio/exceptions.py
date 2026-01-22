class AIRadioError(Exception):
    """Base class for AI Radio errors."""


class ConfigError(AIRadioError):
    """Raised when configuration is invalid or missing."""


class EnvironmentValidationError(AIRadioError):
    """Raised when environment validation fails."""
