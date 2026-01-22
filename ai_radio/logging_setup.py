import logging
from typing import Optional

# Use canonical config values from src.ai_radio.config
from src.ai_radio.config import LOG_FORMAT as _LOG_FORMAT, LOG_LEVEL as _LOG_LEVEL


def setup_logging(level: Optional[str] = None) -> None:
    """Configure root logging using project defaults from config."""
    if level is None:
        level = _LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO) if isinstance(level, str) else logging.INFO
    logging.basicConfig(level=numeric_level, format=_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with the project's default formatting."""
    # Ensure basic configuration is set (idempotent)
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
