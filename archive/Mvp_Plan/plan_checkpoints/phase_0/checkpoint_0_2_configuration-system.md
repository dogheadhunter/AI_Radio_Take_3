# Checkpoint 0.2: Configuration System

#### Checkpoint 0.2: Configuration System
**Create the central configuration module.**

**Tasks:**
1. Create `src/ai_radio/config.py`
2. Define all paths and settings
3. Create configuration tests

**File:  `src/ai_radio/config.py`**
```python
"""
Central configuration for AI Radio Station. 

All paths, settings, and constants defined here.
No magic values anywhere else in the codebase. 
"""
from pathlib import Path

# Project root (where this repo lives)
PROJECT_ROOT = Path(__file__).parent.parent. parent

# Directory paths
MUSIC_LIBRARY_PATH = Path("SET_THIS_TO_YOUR_MUSIC_FOLDER")
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
ASSETS_DIR = PROJECT_ROOT / "assets"
GENERATED_DIR = DATA_DIR / "generated"

# Catalog files
CATALOG_FILE = DATA_DIR / "catalog.json"
BANISHED_FILE = DATA_DIR / "banished_songs.txt"
FLAGGED_FILE = DATA_DIR / "flagged_intros.txt"

# DJ Settings
DJ_JULIE_SHIFT_START = 6   # 6 AM
DJ_JULIE_SHIFT_END = 19    # 7 PM
DJ_HANDOFF_HOUR = 19       # 7 PM

# Rotation settings
CORE_PLAYLIST_RATIO = 0.70  # 70% core, 30% discovery
DISCOVERY_GRADUATION_PLAYS = 5  # Plays before auto-promotion

# Time announcement settings
TIME_ANNOUNCE_INTERVAL_MINUTES = 30

# Weather settings
WEATHER_TIMES = [6, 12, 17]  # 6 AM, 12 PM, 5 PM
WEATHER_CACHE_MINUTES = 30

# Radio show settings
RADIO_SHOW_HOUR = 20  # 8 PM

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
```

**File: `tests/test_config. py`**
```python
"""Tests for configuration module."""
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
```

**Success Criteria:**
- [x] `pytest tests/test_config.py` passes all tests
- [x] Configuration can be imported:  `from src.ai_radio.config import PROJECT_ROOT`
- [x] No hardcoded values outside `config.py` (all runtime defaults and env names centralized in `src.ai_radio.config`)

**Status:** Completed on 2026-01-22 — all checks passed and constants centralized.

**Validation:**
```bash
# Human runs:
pytest tests/test_config. py -v

# Human verifies:
python -c "from src.ai_radio. config import PROJECT_ROOT; print(PROJECT_ROOT)"
# Expected:  Prints the actual project path
```

**Git Commit:** `feat(config): add central configuration module`
