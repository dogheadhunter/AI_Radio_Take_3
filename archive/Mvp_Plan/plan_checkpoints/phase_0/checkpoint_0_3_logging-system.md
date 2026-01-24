# Checkpoint 0.3: Logging System

#### Checkpoint 0.3: Logging System
**Create the logging infrastructure.**

**Tasks:**
1. Create `src/ai_radio/utils/logging.py`
2. Implement dual-format logging (plain English + technical)
3. Create logging tests

**File: `src/ai_radio/utils/logging.py`**
```python
"""
Logging configuration for AI Radio Station. 

Provides structured logging with: 
- Plain English descriptions
- Technical details
- Fix suggestions for errors
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from src.ai_radio. config import LOGS_DIR, LOG_FORMAT, LOG_LEVEL


def setup_logging(name: str = "ai_radio") -> logging.Logger:
    """
    Set up and return a configured logger.
    
    Args:
        name: Logger name (usually module name)
        
    Returns: 
        Configured logger instance
    """
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # File handler (daily rotation)
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(
        LOGS_DIR / f"ai_radio_{today}. log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def log_error_with_context(
    logger: logging. Logger,
    what_happened: str,
    technical_error: str,
    suggestion: str,
    action_taken: str = "None"
) -> None:
    """
    Log an error with full context for debugging.
    
    Args:
        logger: Logger instance
        what_happened:  Plain English description
        technical_error: Technical error message
        suggestion: How to fix it
        action_taken: What the system did in response
    """
    message = f"""
ERROR DETAILS:
  What happened: {what_happened}
  Technical:  {technical_error}
  Suggestion:  {suggestion}
  Action taken: {action_taken}
"""
    logger.error(message)
```

**File: `tests/utils/test_logging. py`**
```python
"""Tests for logging module."""
import pytest
import logging
from pathlib import Path
from src.ai_radio. utils.logging import setup_logging, log_error_with_context
from src.ai_radio.config import LOGS_DIR


class TestSetupLogging: 
    """Test logger setup."""
    
    def test_returns_logger_instance(self):
        """setup_logging must return a Logger."""
        logger = setup_logging("test_logger")
        assert isinstance(logger, logging. Logger)
    
    def test_logger_has_handlers(self):
        """Logger must have at least one handler."""
        logger = setup_logging("test_logger_handlers")
        assert len(logger.handlers) > 0
    
    def test_creates_logs_directory(self):
        """Logs directory must be created if it doesn't exist."""
        setup_logging("test_logger_dir")
        assert LOGS_DIR. exists()


class TestLogErrorWithContext:
    """Test contextual error logging."""
    
    def test_logs_all_fields(self, caplog):
        """Error log must contain all context fields."""
        logger = setup_logging("test_error_context")
        
        with caplog.at_level(logging.ERROR):
            log_error_with_context(
                logger,
                what_happened="Test error occurred",
                technical_error="TestError:  This is a test",
                suggestion="This is just a test, ignore it",
                action_taken="Logged for testing"
            )
        
        assert "Test error occurred" in caplog.text
        assert "TestError" in caplog.text
        assert "just a test" in caplog.text
        assert "Logged for testing" in caplog.text
```

**Success Criteria:**
- [x] `pytest tests/utils/test_logging. py` passes all tests
- [x] Log file is created in `logs/` directory
- [x] Console output is readable

**Status:** Completed on 2026-01-22 — tests passed and logging files are created as expected.

**Validation:**
```bash
# Human runs:
pytest tests/utils/test_logging.py -v

# Human verifies log file exists: 
ls logs/
# Expected: ai_radio_YYYY-MM-DD. log file
```

**Git Commit:** `feat(logging): add structured logging system`
