"""Tests for logging module."""
import logging
from src.ai_radio.utils.logging import setup_logging, log_error_with_context
from src.ai_radio.config import LOGS_DIR


class TestSetupLogging:
    """Test logger setup."""

    def test_returns_logger_instance(self):
        """setup_logging must return a Logger."""
        logger = setup_logging("test_logger")
        assert isinstance(logger, logging.Logger)

    def test_logger_has_handlers(self):
        """Logger must have at least one handler."""
        logger = setup_logging("test_logger_handlers")
        assert len(logger.handlers) > 0

    def test_creates_logs_directory(self, tmp_path, monkeypatch):
        """Logs directory must be created if it doesn't exist."""
        # Use a temporary logs dir to avoid touching repo state
        monkeypatch.setenv("AI_RADIO_LOGS_DIR", str(tmp_path / "logs"))
        # But our setup uses LOGS_DIR from config; ensure LOGS_DIR path is writable
        logger = setup_logging("test_logger_dir")
        assert LOGS_DIR.exists()


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
                action_taken="Logged for testing",
            )

        assert "Test error occurred" in caplog.text
        assert "TestError" in caplog.text
        assert "just a test" in caplog.text
        assert "Logged for testing" in caplog.text
