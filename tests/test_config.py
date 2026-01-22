"""Tests for the canonical src.ai_radio.config module (checkpoint 0.2)."""
import pytest
from pathlib import Path
from src.ai_radio.config import (
    PROJECT_ROOT,
    DATA_DIR,
    DJ_JULIE_SHIFT_START,
    DJ_JULIE_SHIFT_END,
    CORE_PLAYLIST_RATIO,
)


class TestConfigPaths:
    """Test that configuration paths are valid."""

    def test_project_root_exists(self):
        """Project root directory must exist."""
        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.is_dir()

    def test_data_dir_is_under_project_root(self):
        """Data directory must be under project root."""
        assert str(DATA_DIR).startswith(str(PROJECT_ROOT))


class TestConfigValues:
    """Test that configuration values are sensible."""

    def test_julie_shift_is_valid_hours(self):
        """Julie's shift must be valid 24-hour times."""
        assert 0 <= DJ_JULIE_SHIFT_START <= 23
        assert 0 <= DJ_JULIE_SHIFT_END <= 23

    def test_julie_shift_start_before_end(self):
        """Julie's shift must start before it ends."""
        assert DJ_JULIE_SHIFT_START < DJ_JULIE_SHIFT_END

    def test_core_playlist_ratio_is_valid(self):
        """Core playlist ratio must be between 0 and 1."""
        assert 0 < CORE_PLAYLIST_RATIO < 1

    def test_core_playlist_ratio_is_majority(self):
        """Core playlist should be the majority."""
        assert CORE_PLAYLIST_RATIO >= 0.5
