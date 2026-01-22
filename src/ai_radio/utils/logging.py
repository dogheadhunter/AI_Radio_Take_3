"""Logging configuration for AI Radio Station.

Provides structured logging with:
- Plain English descriptions
- Technical details
- Fix suggestions for errors
"""
import logging
import sys
from datetime import datetime

from src.ai_radio.config import LOGS_DIR, LOG_FORMAT, LOG_LEVEL


def setup_logging(name: str = "ai_radio") -> logging.Logger:
    """Set up and return a configured logger.

    Args:
        name: Logger name (usually module name)

    Returns:
        Configured logger instance
    """
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # File handler (daily file)
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = LOGS_DIR / f"ai_radio_{today}.log"
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_error_with_context(
    logger: logging.Logger,
    what_happened: str,
    technical_error: str,
    suggestion: str,
    action_taken: str = "None",
) -> None:
    """Log an error with full context for debugging.

    Args:
        logger: Logger instance
        what_happened: Plain English description
        technical_error: Technical error message
        suggestion: How to fix it
        action_taken: What the system did in response
    """
    message = (
        "ERROR DETAILS:\n"
        f"  What happened: {what_happened}\n"
        f"  Technical:  {technical_error}\n"
        f"  Suggestion:  {suggestion}\n"
        f"  Action taken: {action_taken}"
    )
    logger.error(message)
