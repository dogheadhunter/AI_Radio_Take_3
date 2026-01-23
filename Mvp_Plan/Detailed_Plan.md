# 🎙️ AI Radio Station — Implementation Roadmap

## Document Purpose
This roadmap provides a **step-by-step implementation plan** designed for LLM-assisted development.  Every phase has explicit success criteria, validation checkpoints, and anti-regression safeguards. 

---

## 📋 Table of Contents
1. [Development Philosophy](#development-philosophy)
2. [Anti-Corruption Safeguards](#anti-corruption-safeguards)
3. [Project Scaffold Strategy](#project-scaffold-strategy)
4. [Phase Overview](#phase-overview)
5. [Phase 0: Foundation](#phase-0-foundation)
6. [Phase 1: Music Library](#phase-1-music-library)
7. [Phase 2: Content Generation Pipeline](#phase-2-content-generation-pipeline)
8. [Phase 3: Audio Playback Engine](#phase-3-audio-playback-engine)
9. [Phase 4: DJ System](#phase-4-dj-system)
10. [Phase 5: Radio Shows](#phase-5-radio-shows)
11. [Phase 6: Information Services](#phase-6-information-services)
12. [Phase 7: Integration](#phase-7-integration)
13. [Phase 8: 24-Hour Validation](#phase-8-24-hour-validation)
14. [Refactoring Guidelines](#refactoring-guidelines)
15. [Context Management](#context-management)
16. [Appendix:  Test Templates](#appendix-test-templates)

---

## Development Philosophy

### Core Principles

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT CYCLE                         │
│                                                              │
│    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐ │
│    │ PLAN │ ─▶ │ CODE │ ─▶ │ TEST │ ─▶ │DEBUG │ ─▶ │COMMIT│ │
│    └──────┘    └──────┘    └──────┘    └──────┘    └──────┘ │
│        ▲                                    │                │
│        └────────────────────────────────────┘                │
│                    ITERATE                                   │
└─────────────────────────────────────────────────────────────┘
```

### The Rules

1. **No code without a test plan**:  Every function has tests defined BEFORE implementation
2. **No commit without passing tests**: All tests must pass before GitHub push
3. **No phase advancement without gate validation**: Success criteria are non-negotiable
4. **Small, atomic commits**: Each commit does ONE thing
5. **Human validates, LLM implements**: You run tests and confirm behavior
6. **Tests are sacred**: Tests are NEVER modified to pass — code is modified to pass tests

### Complexity Management

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each file does ONE thing |
| **Shallow Modules** | No function longer than 50 lines |
| **Explicit over Implicit** | No magic, everything is obvious |
| **Fail Fast** | Errors surface immediately |
| **Log Everything** | Every action is traceable |

---

## Anti-Corruption Safeguards

### The Problem with LLM-Generated Code
LLMs can: 
- Generate code that looks correct but doesn't work
- Modify tests to make them pass instead of fixing code
- Lose context mid-conversation and generate inconsistent code
- Create subtle bugs that surface later
- Over-engineer simple solutions

### Safeguard System

#### 1. Test Immutability Rule
```
┌─────────────────────────────────────────────────────────────┐
│                    TEST IMMUTABILITY                         │
│                                                              │
│  Once a test is written and committed:                        │
│                                                              │
│  ✅ ALLOWED: Add new tests                                   │
│  ✅ ALLOWED: Add more assertions to existing tests           │
│  ❌ FORBIDDEN: Weaken assertions                             │
│  ❌ FORBIDDEN: Remove tests                                  │
│  ❌ FORBIDDEN: Change expected values to match wrong output  │
│                                                              │
│  Exception: Bug in test logic (requires human approval)      │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Human Validation Checkpoints
At every checkpoint, YOU (the human) must:
1. Run all tests yourself:  `pytest -v`
2. Manually verify ONE behavior works as expected
3. Review the git diff before committing
4. Confirm the output makes sense

#### 3. Regression Prevention
```
┌───────────────────────────────────��─────────────────────────┐
│                 REGRESSION PREVENTION                        │
│                                                              │
│  Before EVERY commit:                                        │
│                                                              │
│  1. Run: pytest --tb=short                                   │
│  2. ALL tests must pass (not just new ones)                  │
│  3. No warnings in test output                               │
│  4. Coverage must not decrease                               │
│                                                              │
│  If any test fails:                                           │
│  → DO NOT COMMIT                                             │
│  → Fix the code (not the test)                               │
│  → Re-run all tests                                          │
└─────────────────────────────────────────────────────────────┘
```

#### 4. Context Anchoring
Every coding session starts with: 
1. Read this roadmap document
2. Read the current phase's specification
3. Run all existing tests to confirm baseline
4. Review the last 3 commits to understand recent changes

#### 5. Validation Artifacts
Each checkpoint produces artifacts that prove success:
- Screenshot of passing tests
- Log file showing expected behavior
- Manual test result documentation

---

## Project Scaffold Strategy

### Directory Structure

```
AI_Radio_Take_3/
│
├── . github/
│   └── copilot-instructions. md
│
├── docs/
│   ├── PROJECT_SPEC.md          # Complete specification (previous document)
│   ├── ROADMAP.md               # This document
│   ├── CHANGELOG.md             # What changed and when
│   └── decisions/               # Architecture Decision Records
│       └── ADR-001-audio-library.md
│
├── src/
│   └── ai_radio/
│       ├── __init__.py
│       ├── config.py            # All configuration in one place
│       │
│       ├── library/             # Phase 1: Music library management
│       │   ├── __init__.py
│       │   ├── scanner.py       # Scan music files
│       │   ├── metadata.py      # Read/write metadata
│       │   ├── catalog.py       # Song database
│       │   └── rotation.py      # Core/Discovery/Banished logic
│       │
│       ├── generation/          # Phase 2: Content generation
│       │   ├── __init__. py
│       │   ├── llm_client.py    # Ollama interface
│       │   ├── tts_client.py    # Chatterbox interface
│       │   ├── prompts.py       # All prompt templates
│       │   └── pipeline.py      # Generation orchestration
│       │
│       ├── playback/            # Phase 3: Audio playback
│       │   ├── __init__.py
│       │   ├── player.py        # Audio player
│       │   ├── queue.py         # Playback queue
│       │   └── mixer.py         # Volume, crossfade
│       │
│       ├── dj/                  # Phase 4: DJ system
│       │   ├── __init__.py
│       │   ├── personality.py   # Julie, Mr. New Vegas
│       │   ├── scheduler.py     # Time-based DJ switching
│       │   └── content. py       # Intro/outro selection
│       │
│       ├── shows/               # Phase 5: Radio shows
│       │   ├── __init__. py
│       │   ├── show_manager.py  # Show scheduling
│       │   └── show_player.py   # Show playback
│       │
│       ├── services/            # Phase 6: Weather, time
│       │   ├── __init__. py
│       │   ├── weather.py       # Weather API
│       │   ├── clock.py         # Time announcements
│       │   └── cache.py         # Service caching
│       │
│       ├── station/             # Phase 7: Integration
│       │   ├── __init__.py
│       │   ├── controller.py    # Main station controller
│       │   ├── display.py       # Terminal display
│       │   └── commands.py      # User input handling
│       │
│       └── utils/               # Shared utilities
│           ├── __init__. py
│           ├── logging.py       # Logging configuration
│           ├── errors.py        # Custom exceptions
│           └── validators.py    # Input validation
│
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_config.py
│   │
│   ├── library/
│   │   ├── test_scanner.py
│   │   ├── test_metadata.py
│   │   ├── test_catalog.py
│   │   └── test_rotation.py
│   │
│   ├── generation/
│   │   ├── test_llm_client.py
│   │   ├── test_tts_client. py
│   │   ├── test_prompts.py
│   │   └── test_pipeline.py
│   │
│   ├── playback/
│   │   ├── test_player. py
│   │   ├── test_queue.py
│   │   └── test_mixer. py
│   │
│   ├── dj/
│   │   ├── test_personality.py
│   │   ├── test_scheduler.py
│   │   └── test_content.py
│   │
│   ├── shows/
│   │   ├── test_show_manager.py
���   │   └── test_show_player.py
│   │
│   ├── services/
│   │   ├── test_weather.py
│   │   ├── test_clock. py
│   │   └── test_cache.py
│   │
│   ├── station/
│   │   ├── test_controller.py
│   │   ├── test_display.py
│   │   └── test_commands.py
│   │
│   └── integration/
│       ├── test_music_to_playback.py
│       ├── test_generation_pipeline.py
│       └── test_full_station.py
│
├── data/                        # Runtime data (gitignored except structure)
│   ├── . gitkeep
│   ├── catalog.json             # Song database
│   ├── banished_songs.txt       # Banished list
│   ├── flagged_intros.txt       # Flagged for regeneration
│   └── generated/               # Generated audio content
│       ├── intros/
│       ├── outros/
│       ├── time/
│       └── weather/
│
├── logs/                        # Log files (gitignored)
│   └── . gitkeep
│
├── assets/                      # Voice samples, etc.
│   ├── voices/
│   │   ├── julie/
│   │   └── mr_new_vegas/
│   └── . gitkeep
│
├── scripts/                     # Utility scripts
│   ├── scan_library.py          # One-off library scan
│   ├── generate_content. py      # Batch content generation
│   └── validate_setup.py        # Environment validation
│
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project configuration
├── pytest.ini                   # Pytest configuration
├── . gitignore
└── README.md
```

### Why This Structure?

| Decision | Rationale |
|----------|-----------|
| **Separate `src/` and `tests/`** | Clear separation, standard Python practice |
| **One module per concern** | Easy to test, easy to understand |
| **Flat-ish hierarchy** | No more than 2 levels deep — prevents getting lost |
| **`data/` for runtime** | Keep generated content separate from code |
| **`scripts/` for utilities** | One-off tasks separate from core logic |
| **`docs/decisions/`** | Record why we made choices (ADRs) |

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PHASE PROGRESSION                        │
│                                                              │
│  Phase 0: Foundation ──────────────────────────────────────▶│
│    └── Environment, structure, validation tools              │
│                                                              │
│  Phase 1: Music Library ───────────────────────────────────▶│
│    └── Scan, catalog, rotation logic                         │
│                                                              │
│  Phase 2: Content Generation ──────────────────────────────▶│
│    └── LLM client, TTS client, pipeline                      │
│                                                              │
│  Phase 3: Audio Playback ──────────────────────────────────▶│
│    └── Player, queue, basic controls                         │
│                                                              │
│  Phase 4: DJ System ───────────────────────────────────────▶│
│    └── Personalities, scheduling, content selection          │
│                                                              │
│  Phase 5: Radio Shows ─────────────────────────────────────▶│
│    └── Show management, DJ integration                       │
│                                                              │
│  Phase 6: Information Services ────────────────────────────▶│
│    └── Weather, time announcements                           │
│                                                              │
│  Phase 7: Integration ─────────────────────────────────────▶│
│    └── Station controller, display, commands                 │
│                                                              │
│  Phase 8: 24-Hour Validation ──────────────────────────────▶│
│    └── Stress test, bug fixes, polish                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase Dependencies

```
Phase 0 ─┬─▶ Phase 1 ─┬─▶ Phase 3 ────────────┐
         │            │                        │
         │            └─▶ Phase 2 ─────────────┤
         │                                     │
         └─▶ Phase 4 (can start after P1) ────┤
                                               │
         Phase 5 (needs P3, P4) ◀──────────────┤
                                               │
         Phase 6 (needs P2, P4) ◀──────────────┤
                                               │
         Phase 7 (needs all above) ◀───────────┘
                        │
                        ▼
                    Phase 8
```

---

## Phase 0: Foundation

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Project structure, environment, validation tools |
| **Duration** | 1-2 sessions |
| **Complexity** | Low |
| **Dependencies** | None |

### Checkpoints

#### Checkpoint 0. 1: Project Structure
**Create the directory structure and initial files.**

**Tasks:**
1. Create all directories as specified in scaffold
2. Create empty `__init__.py` files
3. Create `.gitkeep` files for empty directories
4. Create initial `requirements.txt`
5. Create `pytest.ini` configuration
6. Create `.gitignore`

**Files to Create:**
```python
# requirements.txt
pytest>=7.0.0
pytest-cov>=4.0.0
mutagen>=1.47.0  # Metadata reading
```

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*. py
python_functions = test_*
addopts = -v --tb=short
```

**Success Criteria:**
- [ ] All directories exist
- [ ] `pytest` runs without error (even with no tests)
- [ ] `.gitignore` prevents `data/`, `logs/`, `__pycache__/` from being tracked

**Validation:**
```bash
# Human runs: 
pytest
# Expected: "no tests ran" or similar (not an error)

ls src/ai_radio/
# Expected: All module directories visible
```

**Git Commit:** `feat(scaffold): initialize project structure`

---

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
- [ ] `pytest tests/test_config.py` passes all tests
- [ ] Configuration can be imported:  `from src.ai_radio.config import PROJECT_ROOT`
- [ ] No hardcoded values outside config. py

**Validation:**
```bash
# Human runs:
pytest tests/test_config. py -v

# Human verifies:
python -c "from src.ai_radio. config import PROJECT_ROOT; print(PROJECT_ROOT)"
# Expected:  Prints the actual project path
```

**Git Commit:** `feat(config): add central configuration module`

---

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
- [ ] `pytest tests/utils/test_logging. py` passes all tests
- [ ] Log file is created in `logs/` directory
- [ ] Console output is readable

**Validation:**
```bash
# Human runs:
pytest tests/utils/test_logging.py -v

# Human verifies log file exists: 
ls logs/
# Expected: ai_radio_YYYY-MM-DD. log file
```

**Git Commit:** `feat(logging): add structured logging system`

---

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

---

#### Checkpoint 0.5: Environment Validation Script
**Create a script to verify the development environment is correctly set up.**

**Tasks:**
1. Create `scripts/validate_setup.py`
2. Check all dependencies and external tools
3. Provide clear pass/fail output

**File: `scripts/validate_setup.py`**
```python
"""
Environment validation script. 

Run this to verify your setup is ready for AI Radio development.
Usage:  python scripts/validate_setup. py
"""
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def check_python_version():
    """Check Python version is 3.8+."""
    print("Checking Python version.. .", end=" ")
    version = sys. version_info
    if version. major >= 3 and version.minor >= 8:
        print(f"✅ Python {version. major}.{version. minor}. {version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (need 3.8+)")
        return False


def check_import(module_name:  str, package_name: str = None):
    """Check if a Python module can be imported."""
    package_name = package_name or module_name
    print(f"Checking {package_name}...", end=" ")
    try: 
        __import__(module_name)
        print("✅ Installed")
        return True
    except ImportError: 
        print(f"❌ Not installed (pip install {package_name})")
        return False


def check_ollama():
    """Check if Ollama is installed and running."""
    print("Checking Ollama...", end=" ")
    try: 
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result. returncode == 0:
            print("✅ Installed and running")
            return True
        else: 
            print("❌ Installed but not responding")
            return False
    except FileNotFoundError: 
        print("❌ Not installed")
        return False
    except subprocess.TimeoutExpired: 
        print("❌ Timeout (is Ollama running? )")
        return False


def check_directory_structure():
    """Check that project directories exist."""
    print("Checking directory structure...", end=" ")
    project_root = Path(__file__).parent.parent
    required_dirs = [
        "src/ai_radio",
        "tests",
        "data",
        "logs",
        "assets",
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Missing:  {', '.join(missing)}")
        return False
    else:
        print("✅ All directories present")
        return True


def check_config_import():
    """Check that config module can be imported."""
    print("Checking config module...", end=" ")
    try: 
        from ai_radio.config import PROJECT_ROOT
        print("✅ Importable")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def main():
    """Run all validation checks."""
    print("=" * 50)
    print("AI Radio Station - Environment Validation")
    print("=" * 50)
    print()
    
    checks = [
        check_python_version,
        lambda: check_import("pytest"),
        lambda: check_import("mutagen"),
        check_ollama,
        check_directory_structure,
        check_config_import,
    ]
    
    results = [check() for check in checks]
    
    print()
    print("=" * 50)
    if all(results):
        print("✅ All checks passed! Environment is ready.")
        return 0
    else:
        print("❌ Some checks failed.  Fix issues above and re-run.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Success Criteria:**
- [ ] Script runs without error
- [ ] All checks pass on your machine
- [ ] Clear output shows what's missing if something fails

**Validation:**
```bash
# Human runs: 
python scripts/validate_setup.py

# Expected: All checks show ✅
```

**Git Commit:** `feat(scripts): add environment validation script`

---

### Phase 0 Gate: Foundation Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| Project structure matches scaffold | Visual inspection |
| `pytest` runs without error | `pytest --collect-only` |
| Config module imports correctly | `python -c "from src.ai_radio. config import PROJECT_ROOT"` |
| Logging creates files | Check `logs/` directory |
| All Phase 0 tests pass | `pytest tests/ -v` |
| Validation script passes | `python scripts/validate_setup.py` |

**Human Validation Required:**
1. Run `pytest -v` — all tests pass
2. Run `python scripts/validate_setup.py` — all checks pass
3. Review git log — commits are clean and atomic

**Git Tag:** `v0.1.0-foundation`

---

## Phase 1: Music Library

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Scan, catalog, and manage music library |
| **Duration** | 2-3 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 0 complete |

### Checkpoints

#### Checkpoint 1.1: Metadata Reader
**Read metadata from MP3 files.**

**Tasks:**
1. Create `src/ai_radio/library/metadata. py`
2. Read artist, title, album, year from MP3 files
3. Handle missing metadata gracefully

**Tests First (Write Before Implementation):**
```python
# tests/library/test_metadata.py
"""Tests for metadata reading."""
import pytest
from pathlib import Path
from src.ai_radio.library.metadata import read_metadata, SongMetadata


class TestReadMetadata:
    """Test metadata reading from files."""
    
    def test_returns_song_metadata_object(self, sample_mp3_path):
        """Must return a SongMetadata dataclass."""
        result = read_metadata(sample_mp3_path)
        assert isinstance(result, SongMetadata)
    
    def test_extracts_artist(self, sample_mp3_with_tags):
        """Must extract artist from tags."""
        result = read_metadata(sample_mp3_with_tags)
        assert result.artist is not None
        assert len(result.artist) > 0
    
    def test_extracts_title(self, sample_mp3_with_tags):
        """Must extract title from tags."""
        result = read_metadata(sample_mp3_with_tags)
        assert result.title is not None
        assert len(result.title) > 0
    
    def test_handles_missing_metadata(self, sample_mp3_no_tags):
        """Must handle files with no metadata gracefully."""
        result = read_metadata(sample_mp3_no_tags)
        # Should use filename as fallback
        assert result.title is not None
    
    def test_raises_for_nonexistent_file(self):
        """Must raise SongNotFoundError for missing files."""
        from src.ai_radio.utils.errors import SongNotFoundError
        with pytest.raises(SongNotFoundError):
            read_metadata(Path("/nonexistent/file. mp3"))
    
    def test_raises_for_non_audio_file(self, tmp_path):
        """Must raise MetadataError for non-audio files."""
        from src.ai_radio.utils.errors import MetadataError
        fake_file = tmp_path / "not_audio. txt"
        fake_file.write_text("This is not audio")
        with pytest.raises(MetadataError):
            read_metadata(fake_file)
```

**Implementation Specification:**
```python
# src/ai_radio/library/metadata. py
"""
Music file metadata reading. 

Uses mutagen library to extract ID3 tags from MP3 files. 
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import mutagen
from mutagen.easyid3 import EasyID3
from src.ai_radio. utils.errors import SongNotFoundError, MetadataError


@dataclass
class SongMetadata: 
    """Metadata extracted from a song file."""
    file_path: Path
    artist: str
    title: str
    album: Optional[str] = None
    year: Optional[int] = None
    duration_seconds: Optional[float] = None
    
    @property
    def display_name(self) -> str:
        """Return 'Artist - Title' format."""
        return f"{self.artist} - {self.title}"


def read_metadata(file_path: Path) -> SongMetadata:
    """
    Read metadata from an audio file.
    
    Args:
        file_path: Path to the audio file
        
    Returns: 
        SongMetadata with extracted information
        
    Raises: 
        SongNotFoundError: If file doesn't exist
        MetadataError:  If file can't be read as audio
    """
    # Implementation here
    pass
```

**Success Criteria:**
- [ ] All `test_metadata.py` tests pass
- [ ] Can read metadata from your actual music files
- [ ] Missing metadata handled gracefully (no crashes)

**Validation:**
```bash
# Human runs:
pytest tests/library/test_metadata.py -v

# Human tests with real file:
python -c "
from pathlib import Path
from src.ai_radio. library.metadata import read_metadata
result = read_metadata(Path('path/to/your/song.mp3'))
print(f'Artist: {result.artist}')
print(f'Title: {result.title}')
"
```

**Git Commit:** `feat(library): add metadata reader`

---

#### Checkpoint 1.2: Library Scanner
**Scan a directory for all music files.**

**Tasks:**
1. Create `src/ai_radio/library/scanner.py`
2. Recursively find all MP3 files
3. Read metadata for each file
4. Report progress and errors

**Tests First:**
```python
# tests/library/test_scanner.py
"""Tests for library scanning."""
import pytest
from pathlib import Path
from src.ai_radio.library. scanner import scan_library, ScanResult


class TestScanLibrary: 
    """Test library scanning."""
    
    def test_returns_scan_result(self, music_directory):
        """Must return a ScanResult object."""
        result = scan_library(music_directory)
        assert isinstance(result, ScanResult)
    
    def test_finds_mp3_files(self, music_directory_with_files):
        """Must find all MP3 files in directory."""
        result = scan_library(music_directory_with_files)
        assert result.total_files > 0
    
    def test_returns_song_metadata_list(self, music_directory_with_files):
        """Must return list of SongMetadata objects."""
        result = scan_library(music_directory_with_files)
        assert len(result.songs) > 0
        from src.ai_radio.library.metadata import SongMetadata
        assert all(isinstance(s, SongMetadata) for s in result.songs)
    
    def test_tracks_failed_files(self, music_directory_with_bad_files):
        """Must track files that failed to read."""
        result = scan_library(music_directory_with_bad_files)
        assert len(result.failed_files) > 0
    
    def test_raises_for_nonexistent_directory(self):
        """Must raise MusicLibraryError for missing directory."""
        from src.ai_radio.utils.errors import MusicLibraryError
        with pytest.raises(MusicLibraryError):
            scan_library(Path("/nonexistent/directory"))
    
    def test_handles_empty_directory(self, tmp_path):
        """Must handle empty directories gracefully."""
        result = scan_library(tmp_path)
        assert result. total_files == 0
        assert len(result.songs) == 0
```

**Success Criteria:**
- [ ] All `test_scanner.py` tests pass
- [ ] Can scan your actual music directory
- [ ] Reports count of successful and failed files

**Validation:**
```bash
# Human runs:
pytest tests/library/test_scanner.py -v

# Human tests with real directory: 
python -c "
from pathlib import Path
from src.ai_radio.library. scanner import scan_library
result = scan_library(Path('path/to/your/music'))
print(f'Found:  {result.total_files} files')
print(f'Successfully read:  {len(result. songs)}')
print(f'Failed:  {len(result. failed_files)}')
"
```

**Git Commit:** `feat(library): add library scanner`

---

#### Checkpoint 1.3: Song Catalog
**Persistent storage for song database.**

**Tasks:**
1. Create `src/ai_radio/library/catalog. py`
2. Save/load catalog to JSON
3. Query songs by various criteria

**Tests First:**
```python
# tests/library/test_catalog.py
"""Tests for song catalog."""
import pytest
import json
from pathlib import Path
from src.ai_radio. library.catalog import (
    SongCatalog,
    add_song,
    get_song,
    save_catalog,
    load_catalog,
)


class TestSongCatalog: 
    """Test catalog operations."""
    
    def test_add_song_increases_count(self):
        """Adding a song must increase catalog size."""
        catalog = SongCatalog()
        assert len(catalog) == 0
        add_song(catalog, mock_song_metadata())
        assert len(catalog) == 1
    
    def test_get_song_by_id(self):
        """Must be able to retrieve song by ID."""
        catalog = SongCatalog()
        song = mock_song_metadata()
        song_id = add_song(catalog, song)
        retrieved = get_song(catalog, song_id)
        assert retrieved.title == song.title
    
    def test_save_creates_file(self, tmp_path):
        """Saving must create a JSON file."""
        catalog = SongCatalog()
        add_song(catalog, mock_song_metadata())
        file_path = tmp_path / "catalog. json"
        save_catalog(catalog, file_path)
        assert file_path.exists()
    
    def test_load_restores_catalog(self, tmp_path):
        """Loading must restore saved catalog."""
        catalog = SongCatalog()
        song = mock_song_metadata()
        add_song(catalog, song)
        file_path = tmp_path / "catalog.json"
        save_catalog(catalog, file_path)
        
        loaded = load_catalog(file_path)
        assert len(loaded) == 1
    
    def test_catalog_is_json_serializable(self, tmp_path):
        """Catalog file must be valid JSON."""
        catalog = SongCatalog()
        add_song(catalog, mock_song_metadata())
        file_path = tmp_path / "catalog.json"
        save_catalog(catalog, file_path)
        
        # This should not raise
        with open(file_path) as f:
            data = json.load(f)
        assert "songs" in data
```

**Success Criteria:**
- [ ] All `test_catalog.py` tests pass
- [ ] Catalog persists between sessions
- [ ] JSON file is human-readable

**Validation:**
```bash
# Human runs:
pytest tests/library/test_catalog.py -v

# Human verifies JSON is readable:
cat data/catalog.json | python -m json.tool | head -20
```

**Git Commit:** `feat(library): add song catalog storage`

---

#### Checkpoint 1.4: Rotation System
**Core/Discovery/Banished playlist management.**

**Tasks:**
1. Create `src/ai_radio/library/rotation.py`
2. Implement tier assignment logic
3. Implement graduation and banishment
4. Implement song selection with proper ratios

**Tests First:**
```python
# tests/library/test_rotation.py
"""Tests for rotation system."""
import pytest
from src.ai_radio. library.rotation import (
    RotationManager,
    SongTier,
    get_next_song,
    banish_song,
    promote_song,
    record_play,
)


class TestSongTiers:
    """Test tier assignment."""
    
    def test_new_songs_are_discovery(self, rotation_manager):
        """New songs must start in Discovery tier."""
        song = mock_song()
        tier = rotation_manager.get_tier(song. id)
        assert tier == SongTier.DISCOVERY
    
    def test_promoted_songs_are_core(self, rotation_manager):
        """Promoted songs must be in Core tier."""
        song = mock_song()
        promote_song(rotation_manager, song. id)
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.CORE
    
    def test_banished_songs_are_banished(self, rotation_manager):
        """Banished songs must be in Banished tier."""
        song = mock_song()
        banish_song(rotation_manager, song.id)
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier. BANISHED


class TestAutomaticGraduation:
    """Test automatic promotion after plays."""
    
    def test_graduates_after_threshold(self, rotation_manager):
        """Song must graduate to Core after enough plays."""
        from src.ai_radio.config import DISCOVERY_GRADUATION_PLAYS
        song = mock_song()
        
        for _ in range(DISCOVERY_GRADUATION_PLAYS):
            record_play(rotation_manager, song. id)
        
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier. CORE
    
    def test_does_not_graduate_early(self, rotation_manager):
        """Song must not graduate before threshold."""
        from src.ai_radio.config import DISCOVERY_GRADUATION_PLAYS
        song = mock_song()
        
        for _ in range(DISCOVERY_GRADUATION_PLAYS - 1):
            record_play(rotation_manager, song. id)
        
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier. DISCOVERY


class TestSongSelection:
    """Test song selection respects ratios."""
    
    def test_never_selects_banished(self, rotation_manager_with_songs):
        """Banished songs must never be selected."""
        banished_id = "banished_song"
        banish_song(rotation_manager_with_songs, banished_id)
        
        # Select 100 songs, none should be banished
        selected = [get_next_song(rotation_manager_with_songs) for _ in range(100)]
        assert banished_id not in [s.id for s in selected]
    
    def test_respects_core_ratio_approximately(self, rotation_manager_with_mixed_tiers):
        """Core songs should be selected ~70% of the time."""
        from src.ai_radio.config import CORE_PLAYLIST_RATIO
        
        selections = [get_next_song(rotation_manager_with_mixed_tiers) for _ in range(1000)]
        core_count = sum(1 for s in selections if s.tier == SongTier. CORE)
        
        # Allow 10% margin of error
        expected = CORE_PLAYLIST_RATIO * 1000
        assert abs(core_count - expected) < 100
```

**Success Criteria:**
- [ ] All `test_rotation.py` tests pass
- [ ] Banished songs never play
- [ ] Core/Discovery ratio is approximately correct
- [ ] Auto-graduation works after threshold plays

**Validation:**
```bash
# Human runs:
pytest tests/library/test_rotation.py -v
```

**Git Commit:** `feat(library): add rotation system`

---

#### Checkpoint 1.5: Library Integration Script
**Create a script to scan your actual music library.**

**Tasks:**
1. Create `scripts/scan_library. py`
2. Scan your music directory
3. Build and save the catalog
4. Report statistics

**File: `scripts/scan_library.py`**
```python
"""
Scan music library and build catalog. 

Usage: python scripts/scan_library. py /path/to/music
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent. parent / "src"))

from ai_radio.library.scanner import scan_library
from ai_radio. library.catalog import SongCatalog, add_song, save_catalog
from ai_radio. config import CATALOG_FILE


def main():
    parser = argparse.ArgumentParser(description="Scan music library")
    parser.add_argument("music_path", type=Path, help="Path to music directory")
    args = parser.parse_args()
    
    print(f"Scanning:  {args.music_path}")
    print("-" * 50)
    
    result = scan_library(args.music_path)
    
    print(f"Total files found: {result.total_files}")
    print(f"Successfully read: {len(result.songs)}")
    print(f"Failed:  {len(result. failed_files)}")
    
    if result.failed_files:
        print("\nFailed files:")
        for path, error in result. failed_files[: 10]: 
            print(f"  {path}: {error}")
        if len(result. failed_files) > 10:
            print(f"  ... and {len(result.failed_files) - 10} more")
    
    # Build catalog
    catalog = SongCatalog()
    for song in result.songs:
        add_song(catalog, song)
    
    # Save
    save_catalog(catalog, CATALOG_FILE)
    print(f"\nCatalog saved to:  {CATALOG_FILE}")
    print(f"Total songs in catalog: {len(catalog)}")


if __name__ == "__main__":
    main()
```

**Success Criteria:**
- [ ] Script runs on your actual music directory
- [ ] `data/catalog.json` is created with your songs
- [ ] Report shows reasonable success/failure counts

**Validation:**
```bash
# Human runs:
python scripts/scan_library. py "C:/path/to/your/music"

# Human verifies: 
cat data/catalog.json | python -m json.tool | head -50
# Should see your actual songs
```

**Git Commit:** `feat(scripts): add library scan script`

---

### Phase 1 Gate: Music Library Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All library tests pass | `pytest tests/library/ -v` |
| Can scan your music folder | `python scripts/scan_library.py <path>` |
| Catalog contains your songs | Check `data/catalog.json` |
| Rotation logic works | Unit tests pass |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass (not just library)
2. Run scan script on your music — catalog created
3. Manually check catalog. json — songs look correct
4. Check a few songs have correct metadata

**Artifact:** Screenshot of passing tests + first 5 songs from catalog

**Git Tag:** `v0.2.0-library`

---

## Phase 2: Content Generation Pipeline

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | LLM and TTS integration for generating DJ content |
| **Duration** | 3-4 sessions |
| **Complexity** | High |
| **Dependencies** | Phase 0 complete, Phase 1 helpful but not required |

### Important Note on Testing
LLM and TTS are external services.  Tests must: 
- Use mocking for unit tests
- Have separate integration tests that call real services
- Never depend on specific LLM output (it's non-deterministic)

---

#### Checkpoint 2.1: LLM Client
**Interface with Ollama for text generation.**

**Tasks:**
1. Create `src/ai_radio/generation/llm_client.py`
2. Create synchronous interface to Ollama
3. Handle errors and timeouts

**Tests First (With Mocking):**
```python
# tests/generation/test_llm_client.py
"""Tests for LLM client."""
import pytest
from unittest. mock import Mock, patch
from src.ai_radio.generation.llm_client import (
    LLMClient,
    generate_text,
    check_ollama_available,
)


class TestLLMClient:
    """Test LLM client operations."""
    
    def test_generate_returns_string(self, mock_ollama):
        """Generate must return a string."""
        client = LLMClient()
        result = generate_text(client, "Test prompt")
        assert isinstance(result, str)
    
    def test_generate_returns_nonempty(self, mock_ollama):
        """Generate must return non-empty string."""
        mock_ollama.return_value = "Generated response"
        client = LLMClient()
        result = generate_text(client, "Test prompt")
        assert len(result) > 0
    
    def test_raises_on_ollama_error(self, mock_ollama_error):
        """Must raise LLMError when Ollama fails."""
        from src.ai_radio.utils.errors import LLMError
        client = LLMClient()
        with pytest.raises(LLMError):
            generate_text(client, "Test prompt")
    
    def test_check_available_returns_bool(self):
        """Availability check must return boolean."""
        result = check_ollama_available()
        assert isinstance(result, bool)


class TestLLMClientIntegration:
    """Integration tests that call real Ollama. 
    
    These tests are marked slow and require Ollama running.
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_generation(self):
        """Actually call Ollama and get a response."""
        if not check_ollama_available():
            pytest.skip("Ollama not available")
        
        client = LLMClient()
        result = generate_text(client, "Say 'hello' and nothing else.")
        assert len(result) > 0
```

**Success Criteria:**
- [ ] Unit tests pass with mocking
- [ ] Integration test passes when Ollama is running
- [ ] Errors are caught and wrapped in `LLMError`

**Git Commit:** `feat(generation): add LLM client`

---

#### Checkpoint 2.2:  Prompt Templates
**Create prompt templates for DJ personalities.**

**Tasks:**
1. Create `src/ai_radio/generation/prompts.py`
2. Define templates for Julie and Mr. New Vegas
3. Templates for intros, outros, time, weather

**Tests First:**
```python
# tests/generation/test_prompts.py
"""Tests for prompt templates."""
import pytest
from src.ai_radio.generation. prompts import (
    build_song_intro_prompt,
    build_time_announcement_prompt,
    build_weather_prompt,
    DJ,
)


class TestSongIntroPrompt:
    """Test song intro prompt generation."""
    
    def test_includes_song_title(self):
        """Prompt must include the song title."""
        prompt = build_song_intro_prompt(
            dj=DJ. JULIE,
            artist="Bing Crosby",
            title="White Christmas",
            year=1942,
        )
        assert "White Christmas" in prompt
    
    def test_includes_artist(self):
        """Prompt must include the artist name."""
        prompt = build_song_intro_prompt(
            dj=DJ. JULIE,
            artist="Bing Crosby",
            title="White Christmas",
            year=1942,
        )
        assert "Bing Crosby" in prompt
    
    def test_julie_prompt_has_julie_traits(self):
        """Julie prompt must include her personality traits."""
        prompt = build_song_intro_prompt(
            dj=DJ.JULIE,
            artist="Test",
            title="Test",
        )
        # Should mention filler words, friendly tone, etc.
        assert "friend" in prompt. lower() or "earnest" in prompt.lower()
    
    def test_mr_vegas_prompt_has_his_traits(self):
        """Mr.  New Vegas prompt must include his personality traits."""
        prompt = build_song_intro_prompt(
            dj=DJ.MR_NEW_VEGAS,
            artist="Test",
            title="Test",
        )
        # Should mention suave, romantic, etc.
        assert "suave" in prompt.lower() or "romantic" in prompt.lower()
    
    def test_different_djs_produce_different_prompts(self):
        """Julie and Mr. New Vegas prompts must be different."""
        julie_prompt = build_song_intro_prompt(DJ.JULIE, "Test", "Test")
        vegas_prompt = build_song_intro_prompt(DJ.MR_NEW_VEGAS, "Test", "Test")
        assert julie_prompt != vegas_prompt
```

**Success Criteria:**
- [ ] All prompt tests pass
- [ ] Prompts capture DJ personality from character cards
- [ ] Prompts are complete and self-contained

**Git Commit:** `feat(generation): add prompt templates`

---

#### Checkpoint 2.3: TTS Client
**Interface with Chatterbox for voice synthesis.**

**Tasks:**
1. Create `src/ai_radio/generation/tts_client.py`
2. Generate audio from text
3. Support voice cloning with reference audio

**Tests First:**
```python
# tests/generation/test_tts_client.py
"""Tests for TTS client."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.ai_radio. generation.tts_client import (
    TTSClient,
    generate_audio,
    check_tts_available,
)


class TestTTSClient: 
    """Test TTS client operations."""
    
    def test_generate_creates_file(self, mock_chatterbox, tmp_path):
        """Generate must create an audio file."""
        client = TTSClient()
        output_path = tmp_path / "output. wav"
        generate_audio(
            client,
            text="Hello world",
            output_path=output_path,
        )
        assert output_path.exists()
    
    def test_generate_with_voice_reference(self, mock_chatterbox, tmp_path, voice_sample):
        """Generate must accept voice reference for cloning."""
        client = TTSClient()
        output_path = tmp_path / "output.wav"
        # Should not raise
        generate_audio(
            client,
            text="Hello world",
            output_path=output_path,
            voice_reference=voice_sample,
        )
    
    def test_raises_on_tts_error(self, mock_chatterbox_error, tmp_path):
        """Must raise TTSError when TTS fails."""
        from src.ai_radio.utils.errors import TTSError
        client = TTSClient()
        with pytest.raises(TTSError):
            generate_audio(
                client,
                text="Hello world",
                output_path=tmp_path / "output.wav",
            )


class TestTTSClientIntegration: 
    """Integration tests that call real Chatterbox. 
    
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_generation(self, tmp_path):
        """Actually call Chatterbox and generate audio."""
        if not check_tts_available():
            pytest.skip("Chatterbox not available")
        
        client = TTSClient()
        output_path = tmp_path / "test_output.wav"
        generate_audio(client, "Hello, this is a test.", output_path)
        
        assert output_path.exists()
        assert output_path. stat().st_size > 0
```

**Success Criteria:**
- [ ] Unit tests pass with mocking
- [ ] Integration test generates actual audio file
- [ ] Voice cloning with reference audio works

**Git Commit:** `feat(generation): add TTS client`

---

## Phase 2: Content Generation Pipeline (Continued)

#### Checkpoint 2.4: Generation Pipeline (Continued)
**Orchestrate the full generation process.**

**Tasks:**
1. Create `src/ai_radio/generation/pipeline. py`
2. Combine LLM and TTS for complete content generation
3. Handle sequential processing (LLM first, then TTS — never simultaneous due to VRAM limits)
4. Implement progress tracking and resumability

**Tests First:**
```python
# tests/generation/test_pipeline.py
"""Tests for generation pipeline."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.ai_radio. generation.pipeline import (
    GenerationPipeline,
    generate_song_intro,
    generate_batch_intros,
    GenerationResult,
    BatchProgress,
)


class TestGenerateSongIntro: 
    """Test single song intro generation."""
    
    def test_returns_generation_result(self, mock_llm, mock_tts):
        """Must return a GenerationResult object."""
        pipeline = GenerationPipeline()
        result = generate_song_intro(
            pipeline,
            song_id="test_song",
            artist="Test Artist",
            title="Test Song",
            dj="julie",
        )
        assert isinstance(result, GenerationResult)
    
    def test_result_contains_text(self, mock_llm, mock_tts):
        """Result must contain generated text."""
        mock_llm.return_value = "Here's a great song!"
        pipeline = GenerationPipeline()
        result = generate_song_intro(
            pipeline,
            song_id="test_song",
            artist="Test Artist",
            title="Test Song",
            dj="julie",
        )
        assert result.text is not None
        assert len(result.text) > 0
    
    def test_result_contains_audio_path(self, mock_llm, mock_tts, tmp_path):
        """Result must contain path to generated audio."""
        pipeline = GenerationPipeline(output_dir=tmp_path)
        result = generate_song_intro(
            pipeline,
            song_id="test_song",
            artist="Test Artist",
            title="Test Song",
            dj="julie",
        )
        assert result.audio_path is not None
        assert result.audio_path.exists()
    
    def test_llm_called_before_tts(self, mock_llm, mock_tts):
        """LLM must be called before TTS (sequential processing)."""
        call_order = []
        mock_llm.side_effect = lambda *args:  call_order.append("llm") or "Generated text"
        mock_tts.side_effect = lambda *args: call_order.append("tts")
        
        pipeline = GenerationPipeline()
        generate_song_intro(pipeline, "id", "Artist", "Title", "julie")
        
        assert call_order == ["llm", "tts"]


class TestBatchGeneration: 
    """Test batch intro generation."""
    
    def test_processes_all_songs(self, mock_llm, mock_tts, sample_song_list):
        """Must process all songs in the list."""
        pipeline = GenerationPipeline()
        results = list(generate_batch_intros(pipeline, sample_song_list))
        assert len(results) == len(sample_song_list)
    
    def test_continues_on_single_failure(self, mock_llm_sometimes_fails, mock_tts):
        """Must continue processing if one song fails."""
        pipeline = GenerationPipeline()
        songs = [{"id": f"song_{i}", "artist": "Test", "title": f"Song {i}"} for i in range(5)]
        
        results = list(generate_batch_intros(pipeline, songs))
        
        # Should have results for all songs (some may be failures)
        assert len(results) == 5
    
    def test_tracks_progress(self, mock_llm, mock_tts, sample_song_list):
        """Must yield progress updates."""
        pipeline = GenerationPipeline()
        
        progress_updates = []
        for result in generate_batch_intros(
            pipeline, 
            sample_song_list,
            progress_callback=lambda p: progress_updates.append(p)
        ):
            pass
        
        assert len(progress_updates) > 0
        assert progress_updates[-1].completed == len(sample_song_list)
    
    def test_can_resume_from_checkpoint(self, mock_llm, mock_tts, tmp_path):
        """Must be able to resume interrupted batch."""
        pipeline = GenerationPipeline(output_dir=tmp_path)
        songs = [{"id":  f"song_{i}", "artist": "Test", "title":  f"Song {i}"} for i in range(10)]
        
        # Simulate partial completion
        for i in range(5):
            (tmp_path / "intros" / f"song_{i}_julie_0.wav").parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / "intros" / f"song_{i}_julie_0.wav").touch()
        
        # Resume should skip completed
        results = list(generate_batch_intros(pipeline, songs, resume=True))
        
        # Should only generate for remaining 5
        new_generations = [r for r in results if not r.skipped]
        assert len(new_generations) == 5


class TestSequentialProcessing: 
    """Test that LLM and TTS never run simultaneously."""
    
    def test_unloads_llm_before_tts(self, mock_llm, mock_tts):
        """Must unload LLM before starting TTS."""
        pipeline = GenerationPipeline()
        
        # Track if LLM is "loaded" when TTS runs
        llm_loaded_during_tts = []
        
        def track_tts(*args, **kwargs):
            llm_loaded_during_tts.append(pipeline._llm_loaded)
        
        mock_tts.side_effect = track_tts
        
        generate_song_intro(pipeline, "id", "Artist", "Title", "julie")
        
        # LLM should not be loaded when TTS runs
        assert not any(llm_loaded_during_tts)
```

**Implementation Specification:**
```python
# src/ai_radio/generation/pipeline.py
"""
Content generation pipeline. 

Orchestrates LLM and TTS for generating radio content. 
Handles sequential processing to respect VRAM limits. 
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Callable, Optional, List, Dict, Any
from src.ai_radio. generation.llm_client import LLMClient, generate_text
from src.ai_radio.generation. tts_client import TTSClient, generate_audio
from src.ai_radio. generation.prompts import build_song_intro_prompt, DJ
from src.ai_radio.utils.logging import setup_logging, log_error_with_context
from src.ai_radio. utils.errors import GenerationError


@dataclass
class GenerationResult:
    """Result of a single content generation."""
    song_id: str
    dj: str
    text: str
    audio_path: Optional[Path]
    success: bool
    error: Optional[str] = None
    skipped: bool = False


@dataclass
class BatchProgress:
    """Progress of batch generation."""
    total: int
    completed: int
    failed: int
    current_song: str
    
    @property
    def percent(self) -> float:
        return (self.completed / self.total) * 100 if self.total > 0 else 0


class GenerationPipeline:
    """
    Orchestrates content generation. 
    
    Ensures LLM and TTS never run simultaneously.
    Supports batch processing with progress tracking. 
    Supports resuming interrupted batches. 
    """
    
    def __init__(self, output_dir:  Path = None):
        self.output_dir = output_dir or Path("data/generated")
        self. logger = setup_logging("generation. pipeline")
        self._llm_loaded = False
        self._tts_loaded = False
    
    # Implementation details...
```

**Success Criteria:**
- [ ] All pipeline tests pass
- [ ] Single song generation works end-to-end
- [ ] Batch generation processes all songs
- [ ] Failed songs don't stop the batch
- [ ] Can resume interrupted batches
- [ ] LLM and TTS never run simultaneously

**Validation:**
```bash
# Human runs: 
pytest tests/generation/test_pipeline.py -v

# Human runs integration test (requires Ollama + Chatterbox):
pytest tests/generation/test_pipeline. py -v -m integration
```

**Git Commit:** `feat(generation): add generation pipeline`

---

#### Checkpoint 2.5: Generation Script
**Create a script for batch content generation.**

**Tasks:**
1. Create `scripts/generate_content.py`
2. Generate intros for all songs in catalog
3. Show progress and save checkpoints

**File:  `scripts/generate_content.py`**
```python
"""
Batch content generation script. 

Usage:  
    python scripts/generate_content. py --intros --dj julie
    python scripts/generate_content.py --intros --dj mr_new_vegas
    python scripts/generate_content.py --intros --all
    python scripts/generate_content.py --time-announcements
    python scripts/generate_content.py --resume

Options:
    --intros            Generate song intros
    --time-announcements Generate time announcements
    --dj <name>         Specify DJ (julie, mr_new_vegas, or all)
    --limit <n>         Only process first n songs (for testing)
    --resume            Resume interrupted generation
    --dry-run           Show what would be generated without doing it
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent. parent / "src"))

from ai_radio.library.catalog import load_catalog
from ai_radio.generation. pipeline import GenerationPipeline, generate_batch_intros
from ai_radio.config import CATALOG_FILE, GENERATED_DIR
from ai_radio. utils.logging import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Generate radio content")
    parser.add_argument("--intros", action="store_true", help="Generate song intros")
    parser.add_argument("--time-announcements", action="store_true", help="Generate time announcements")
    parser.add_argument("--dj", choices=["julie", "mr_new_vegas", "all"], default="all")
    parser.add_argument("--limit", type=int, help="Limit number of songs")
    parser.add_argument("--resume", action="store_true", help="Resume interrupted generation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    args = parser.parse_args()
    
    logger = setup_logging("generate_content")
    
    if not CATALOG_FILE.exists():
        print(f"Error:  Catalog not found at {CATALOG_FILE}")
        print("Run 'python scripts/scan_library.py' first.")
        return 1
    
    catalog = load_catalog(CATALOG_FILE)
    songs = list(catalog. songs. values())
    
    if args.limit:
        songs = songs[:args.limit]
        print(f"Limited to {args.limit} songs for testing")
    
    if args.dry_run:
        print(f"Would generate content for {len(songs)} songs")
        print(f"DJs: {args. dj}")
        print(f"Output directory: {GENERATED_DIR}")
        return 0
    
    if args.intros:
        print(f"Generating intros for {len(songs)} songs...")
        print(f"DJ: {args. dj}")
        print(f"Resume mode: {args.resume}")
        print("-" * 50)
        
        pipeline = GenerationPipeline(output_dir=GENERATED_DIR)
        
        djs = ["julie", "mr_new_vegas"] if args.dj == "all" else [args.dj]
        
        for dj in djs: 
            print(f"\n=== Generating {dj. upper()} intros ===\n")
            
            start_time = datetime. now()
            success_count = 0
            fail_count = 0
            
            def progress_callback(progress):
                elapsed = datetime.now() - start_time
                print(f"\r[{progress.percent:.1f}%] {progress.completed}/{progress.total} "
                      f"({progress.failed} failed) - {progress.current_song[: 40]}...", 
                      end="", flush=True)
            
            for result in generate_batch_intros(
                pipeline,
                [{"id": s. id, "artist":  s.artist, "title": s.title} for s in songs],
                dj=dj,
                resume=args.resume,
                progress_callback=progress_callback,
            ):
                if result.success:
                    success_count += 1
                else:
                    fail_count += 1
                    logger.warning(f"Failed:  {result.song_id} - {result.error}")
            
            elapsed = datetime.now() - start_time
            print(f"\n\nCompleted in {elapsed}")
            print(f"Success: {success_count}, Failed: {fail_count}")
    
    if args.time_announcements:
        print("Generating time announcements...")
        # Implementation for time announcements
        pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Success Criteria:**
- [ ] Script runs without error
- [ ] `--dry-run` shows what would be generated
- [ ] `--limit 5` generates only 5 intros
- [ ] Progress is displayed during generation
- [ ] `--resume` skips already-generated content

**Validation:**
```bash
# Human runs dry-run first:
python scripts/generate_content.py --intros --dj julie --dry-run

# Human runs small test:
python scripts/generate_content.py --intros --dj julie --limit 3

# Human verifies files created:
ls data/generated/intros/
```

**Git Commit:** `feat(scripts): add content generation script`

---

### Phase 2 Gate: Content Generation Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All generation tests pass | `pytest tests/generation/ -v` |
| LLM client works with Ollama | Integration test |
| TTS client works with Chatterbox | Integration test |
| Pipeline generates complete intros | Integration test |
| Batch generation handles failures | Unit tests |
| Resume functionality works | Unit tests |
| Generation script runs | Manual test with `--limit 5` |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass
2. Run generation script with `--limit 3` — hear the audio
3. Listen to generated intros — do they sound like Julie?
4. Check that audio files are reasonable size (not empty, not huge)

**Quality Check:**
- [ ] Generated text sounds like the DJ personality
- [ ] Audio is clear and understandable
- [ ] No obvious errors or hallucinations
- [ ] Intros are appropriate length (10-30 seconds)

**Artifact:** 
- 3 sample intro audio files
- Screenshot of passing tests

**Git Tag:** `v0.3.0-generation`

---

## Phase 3: Audio Playback Engine

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Play audio files with queue management |
| **Duration** | 2-3 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 0 complete |

### Technology Decision
Before implementing, we need to choose an audio library.  This is an **Architecture Decision Record (ADR)**.

**File:  `docs/decisions/ADR-001-audio-library.md`**
```markdown
# ADR-001: Audio Playback Library

## Status
Proposed

## Context
We need to play MP3 and WAV files for the radio station. 
Requirements:
- Play audio files sequentially
- Control volume
- Know when a file finishes playing
- Work on Windows 11
- Be reliable for 24-hour operation

## Options Considered

### Option A: pygame. mixer
- Pros: Well-documented, cross-platform, easy to use
- Cons: Requires pygame installation, may be overkill

### Option B: playsound
- Pros: Very simple, minimal dependencies
- Cons: Limited features, no callbacks for completion

### Option C:  python-vlc
- Pros: Powerful, uses VLC backend
- Cons:  Requires VLC installation, complex

### Option D: pydub + simpleaudio
- Pros: Good audio manipulation, lightweight playback
- Cons: Two libraries to manage

## Decision
**Option A:  pygame.mixer**

Rationale:
- Most documented for this use case
- Provides completion callbacks
- Handles common audio formats
- Cross-platform

## Consequences
- Must add pygame to requirements. txt
- Initialize pygame.mixer at startup
- Use pygame.mixer.music for longer files (songs)
- Use pygame.mixer.Sound for short files (intros, time announcements)
```

---

#### Checkpoint 3.1: Basic Audio Player
**Play a single audio file.**

**Tasks:**
1. Create `src/ai_radio/playback/player.py`
2. Play MP3 and WAV files
3. Provide callbacks for play completion
4. Handle errors gracefully

**Tests First:**
```python
# tests/playback/test_player.py
"""Tests for audio player."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.ai_radio.playback.player import (
    AudioPlayer,
    play_file,
    stop_playback,
    is_playing,
    get_current_position,
    PlayerState,
)


class TestAudioPlayer: 
    """Test basic player operations."""
    
    def test_play_changes_state_to_playing(self, mock_pygame, sample_audio):
        """Playing must change state to PLAYING."""
        player = AudioPlayer()
        play_file(player, sample_audio)
        assert player.state == PlayerState. PLAYING
    
    def test_stop_changes_state_to_stopped(self, mock_pygame, sample_audio):
        """Stopping must change state to STOPPED."""
        player = AudioPlayer()
        play_file(player, sample_audio)
        stop_playback(player)
        assert player.state == PlayerState.STOPPED
    
    def test_is_playing_returns_correct_state(self, mock_pygame, sample_audio):
        """is_playing must reflect actual state."""
        player = AudioPlayer()
        assert not is_playing(player)
        play_file(player, sample_audio)
        assert is_playing(player)
    
    def test_raises_for_nonexistent_file(self, mock_pygame):
        """Must raise AudioFileError for missing files."""
        from src.ai_radio.utils.errors import AudioFileError
        player = AudioPlayer()
        with pytest.raises(AudioFileError):
            play_file(player, Path("/nonexistent/file.mp3"))
    
    def test_calls_completion_callback(self, mock_pygame, sample_audio):
        """Must call callback when playback completes."""
        player = AudioPlayer()
        callback = Mock()
        play_file(player, sample_audio, on_complete=callback)
        
        # Simulate playback completion
        player._simulate_complete()
        
        callback.assert_called_once()


class TestPlayerIntegration:
    """Integration tests with real audio. 
    
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    def test_plays_real_audio(self, real_audio_file):
        """Actually play an audio file."""
        player = AudioPlayer()
        play_file(player, real_audio_file)
        
        # Wait a moment
        import time
        time.sleep(0.5)
        
        assert is_playing(player) or player.state == PlayerState.COMPLETED
        stop_playback(player)
```

**Success Criteria:**
- [ ] All player tests pass
- [ ] Can play an actual MP3 file
- [ ] Completion callback fires when file ends
- [ ] Errors are handled gracefully

**Git Commit:** `feat(playback): add basic audio player`

---

#### Checkpoint 3.2: Playback Queue
**Manage a queue of audio files to play.**

**Tasks:**
1. Create `src/ai_radio/playback/queue.py`
2. Queue multiple files
3. Auto-advance to next file
4. Support insert (for intros before songs)

**Tests First:**
```python
# tests/playback/test_queue.py
"""Tests for playback queue."""
import pytest
from pathlib import Path
from src.ai_radio. playback.queue import (
    PlaybackQueue,
    add_to_queue,
    insert_next,
    get_next,
    peek_next,
    clear_queue,
    get_queue_length,
    QueueItem,
)


class TestQueueOperations:
    """Test queue management."""
    
    def test_add_increases_length(self):
        """Adding to queue must increase length."""
        queue = PlaybackQueue()
        assert get_queue_length(queue) == 0
        add_to_queue(queue, QueueItem(Path("song. mp3"), "song"))
        assert get_queue_length(queue) == 1
    
    def test_get_next_returns_and_removes(self):
        """get_next must return item and remove from queue."""
        queue = PlaybackQueue()
        item = QueueItem(Path("song.mp3"), "song")
        add_to_queue(queue, item)
        
        returned = get_next(queue)
        assert returned == item
        assert get_queue_length(queue) == 0
    
    def test_peek_does_not_remove(self):
        """peek_next must not remove from queue."""
        queue = PlaybackQueue()
        item = QueueItem(Path("song.mp3"), "song")
        add_to_queue(queue, item)
        
        peek_next(queue)
        assert get_queue_length(queue) == 1
    
    def test_insert_next_goes_to_front(self):
        """insert_next must place item at front of queue."""
        queue = PlaybackQueue()
        add_to_queue(queue, QueueItem(Path("song1.mp3"), "song"))
        add_to_queue(queue, QueueItem(Path("song2.mp3"), "song"))
        
        intro = QueueItem(Path("intro.wav"), "intro")
        insert_next(queue, intro)
        
        next_item = get_next(queue)
        assert next_item == intro
    
    def test_fifo_order(self):
        """Queue must be first-in-first-out."""
        queue = PlaybackQueue()
        items = [QueueItem(Path(f"song{i}.mp3"), "song") for i in range(3)]
        for item in items: 
            add_to_queue(queue, item)
        
        for expected in items:
            actual = get_next(queue)
            assert actual == expected
    
    def test_clear_empties_queue(self):
        """clear_queue must empty the queue."""
        queue = PlaybackQueue()
        for i in range(5):
            add_to_queue(queue, QueueItem(Path(f"song{i}.mp3"), "song"))
        
        clear_queue(queue)
        assert get_queue_length(queue) == 0


class TestQueueWithIntros:
    """Test queue behavior with song intros."""
    
    def test_intro_plays_before_song(self):
        """When song is queued, intro should be insertable before it."""
        queue = PlaybackQueue()
        
        song = QueueItem(Path("song.mp3"), "song", song_id="song_1")
        intro = QueueItem(Path("intro.wav"), "intro", song_id="song_1")
        
        add_to_queue(queue, song)
        insert_next(queue, intro)
        
        first = get_next(queue)
        second = get_next(queue)
        
        assert first. item_type == "intro"
        assert second.item_type == "song"
```

**Success Criteria:**
- [ ] All queue tests pass
- [ ] FIFO ordering works correctly
- [ ] insert_next places items at front
- [ ] Queue can be cleared

**Git Commit:** `feat(playback): add playback queue`

---

#### Checkpoint 3.3: Playback Controller
**Combine player and queue for continuous playback.**

**Tasks:**
1. Create `src/ai_radio/playback/controller.py`
2. Automatically advance through queue
3. Emit events for song changes
4. Handle empty queue gracefully

**Tests First:**
```python
# tests/playback/test_controller. py
"""Tests for playback controller."""
import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path
from src. ai_radio.playback.controller import (
    PlaybackController,
    start_playback,
    pause_playback,
    resume_playback,
    skip_current,
    add_song_with_intro,
)


class TestPlaybackController:
    """Test playback controller operations."""
    
    def test_start_begins_playing(self, mock_player, mock_queue_with_items):
        """start_playback must begin playing first item."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        assert controller.is_playing
    
    def test_auto_advances_to_next(self, mock_player, mock_queue_with_items):
        """Must automatically play next item when current finishes."""
        controller = PlaybackController(queue=mock_queue_with_items)
        
        items_played = []
        controller.on_item_started = lambda item: items_played.append(item)
        
        start_playback(controller)
        
        # Simulate first item completing
        controller._on_playback_complete()
        
        assert len(items_played) == 2
    
    def test_skip_advances_to_next(self, mock_player, mock_queue_with_items):
        """skip_current must stop current and play next."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        
        first_item = controller.current_item
        skip_current(controller)
        
        assert controller.current_item != first_item
    
    def test_pause_stops_without_advancing(self, mock_player, mock_queue_with_items):
        """pause_playback must stop but keep current item."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        
        current = controller.current_item
        pause_playback(controller)
        
        assert not controller.is_playing
        assert controller.current_item == current
    
    def test_resume_continues_current(self, mock_player, mock_queue_with_items):
        """resume_playback must continue from pause."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        pause_playback(controller)
        resume_playback(controller)
        
        assert controller.is_playing


class TestSongWithIntro:
    """Test adding songs with their intros."""
    
    def test_adds_intro_then_song(self, mock_player):
        """add_song_with_intro must queue intro before song."""
        controller = PlaybackController()
        
        add_song_with_intro(
            controller,
            song_path=Path("song. mp3"),
            intro_path=Path("intro.wav"),
            song_id="song_1",
        )
        
        # Should have 2 items in queue
        assert controller.queue_length == 2
    
    def test_intro_plays_first(self, mock_player):
        """Intro must play before its song."""
        controller = PlaybackController()
        
        played = []
        controller. on_item_started = lambda item: played.append(item. item_type)
        
        add_song_with_intro(
            controller,
            song_path=Path("song.mp3"),
            intro_path=Path("intro. wav"),
            song_id="song_1",
        )
        
        start_playback(controller)
        controller._on_playback_complete()  # Finish intro
        
        assert played == ["intro", "song"]
```

**Success Criteria:**
- [ ] All controller tests pass
- [ ] Auto-advances through queue
- [ ] Pause/resume works correctly
- [ ] Skip advances to next item
- [ ] Songs play after their intros

**Git Commit:** `feat(playback): add playback controller`

---

### Phase 3 Gate: Audio Playback Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All playback tests pass | `pytest tests/playback/ -v` |
| Can play actual audio file | Integration test |
| Queue manages items correctly | Unit tests |
| Controller auto-advances | Unit tests |
| Pause/resume works | Integration test |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass
2. Create simple test script that plays 2 songs with intros
3. Verify songs play in correct order
4. Verify pause/resume works manually

**Artifact:** 
- Recording or description of test playback session
- Screenshot of passing tests

**Git Tag:** `v0.4.0-playback`

---

## Phase 4: DJ System

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | DJ personalities, scheduling, content selection |
| **Duration** | 2-3 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 1 (catalog), Phase 2 (generation), Phase 3 (playback) |

---

#### Checkpoint 4.1: DJ Personality Model
**Define DJ personalities as data structures.**

**Tasks:**
1. Create `src/ai_radio/dj/personality.py`
2. Load personality from JSON character cards
3. Provide personality traits for prompt generation

**Tests First:**
```python
# tests/dj/test_personality.py
"""Tests for DJ personality."""
import pytest
from pathlib import Path
from src.ai_radio.dj. personality import (
    DJPersonality,
    load_personality,
    get_random_catchphrase,
    get_random_starter_phrase,
    DJ,
)


class TestLoadPersonality:
    """Test personality loading."""
    
    def test_load_returns_personality(self, julie_character_card):
        """Must return DJPersonality object."""
        personality = load_personality(julie_character_card)
        assert isinstance(personality, DJPersonality)
    
    def test_personality_has_name(self, julie_character_card):
        """Personality must have a name."""
        personality = load_personality(julie_character_card)
        assert personality.name is not None
        assert "Julie" in personality.name
    
    def test_personality_has_tone(self, julie_character_card):
        """Personality must have a tone description."""
        personality = load_personality(julie_character_card)
        assert personality. tone is not None
    
    def test_personality_has_catchphrases(self, julie_character_card):
        """Personality must have catchphrases."""
        personality = load_personality(julie_character_card)
        assert len(personality.catchphrases) > 0


class TestDJTraits:
    """Test DJ-specific traits."""
    
    def test_julie_has_filler_words(self):
        """Julie must have filler words defined."""
        personality = load_personality(DJ. JULIE)
        assert "um" in personality.speech_patterns. filler_words or \
               "like" in personality.speech_patterns.filler_words
    
    def test_mr_vegas_has_no_filler_words(self):
        """Mr. New Vegas must have no filler words."""
        personality = load_personality(DJ.MR_NEW_VEGAS)
        assert len(personality.speech_patterns.filler_words) == 0
    
    def test_random_catchphrase_from_list(self):
        """Random catchphrase must be from defined list."""
        personality = load_personality(DJ.JULIE)
        catchphrase = get_random_catchphrase(personality)
        assert catchphrase in personality.catchphrases
```

**Success Criteria:**
- [ ] All personality tests pass
- [ ] Can load Julie and Mr. New Vegas personalities
- [ ] Personality traits match character cards

**Git Commit:** `feat(dj): add personality model`

---

#### Checkpoint 4.2: DJ Scheduler
**Switch DJs based on time of day.**

**Tasks:**
1. Create `src/ai_radio/dj/scheduler. py`
2. Determine current DJ based on time
3. Handle DJ transitions
4. Emit events for DJ changes

**Tests First:**
```python
# tests/dj/test_scheduler. py
"""Tests for DJ scheduler."""
import pytest
from datetime import datetime, time
from src.ai_radio. dj.scheduler import (
    DJScheduler,
    get_current_dj,
    get_next_transition,
    is_transition_time,
    DJ,
)


class TestGetCurrentDJ: 
    """Test current DJ determination."""
    
    def test_julie_in_morning(self):
        """Julie must be active at 8 AM."""
        scheduler = DJScheduler()
        morning = datetime(2026, 1, 22, 8, 0)
        assert get_current_dj(scheduler, morning) == DJ.JULIE
    
    def test_julie_in_afternoon(self):
        """Julie must be active at 2 PM."""
        scheduler = DJScheduler()
        afternoon = datetime(2026, 1, 22, 14, 0)
        assert get_current_dj(scheduler, afternoon) == DJ.JULIE
    
    def test_mr_vegas_in_evening(self):
        """Mr. New Vegas must be active at 8 PM."""
        scheduler = DJScheduler()
        evening = datetime(2026, 1, 22, 20, 0)
        assert get_current_dj(scheduler, evening) == DJ.MR_NEW_VEGAS
    
    def test_mr_vegas_at_midnight(self):
        """Mr. New Vegas must be active at midnight."""
        scheduler = DJScheduler()
        midnight = datetime(2026, 1, 22, 0, 0)
        assert get_current_dj(scheduler, midnight) == DJ.MR_NEW_VEGAS
    
    def test_mr_vegas_at_5am(self):
        """Mr. New Vegas must be active at 5 AM."""
        scheduler = DJScheduler()
        early = datetime(2026, 1, 22, 5, 0)
        assert get_current_dj(scheduler, early) == DJ.MR_NEW_VEGAS
    
    def test_julie_at_6am(self):
        """Julie must take over at 6 AM."""
        scheduler = DJScheduler()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert get_current_dj(scheduler, six_am) == DJ.JULIE


class TestTransitions:
    """Test DJ transition detection."""
    
    def test_transition_at_7pm(self):
        """7 PM must be a transition time."""
        scheduler = DJScheduler()
        seven_pm = datetime(2026, 1, 22, 19, 0)
        assert is_transition_time(scheduler, seven_pm)
    
    def test_transition_at_6am(self):
        """6 AM must be a transition time."""
        scheduler = DJScheduler()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert is_transition_time(scheduler, six_am)
    
    def test_not_transition_at_noon(self):
        """Noon must not be a transition time."""
        scheduler = DJScheduler()
        noon = datetime(2026, 1, 22, 12, 0)
        assert not is_transition_time(scheduler, noon)
    
    def test_get_next_transition_from_morning(self):
        """Next transition from morning must be 7 PM."""
        scheduler = DJScheduler()
        morning = datetime(2026, 1, 22, 10, 0)
        next_trans = get_next_transition(scheduler, morning)
        assert next_trans. hour == 19
```

**Success Criteria:**
- [ ] All scheduler tests pass
- [ ] Correct DJ returned for all times
- [ ] Transition times detected correctly

**Git Commit:** `feat(dj): add DJ scheduler`

---

#### Checkpoint 4.3: Content Selector
**Select appropriate intro/outro for current context.**

**Tasks:**
1. Create `src/ai_radio/dj/content. py`
2. Select intro based on DJ and song
3. Handle multiple intro variations
4. Track which intros have been used (variety)

**Tests First:**
```python
# tests/dj/test_content. py
"""Tests for DJ content selection."""
import pytest
from pathlib import Path
from src.ai_radio. dj.content import (
    ContentSelector,
    get_intro_for_song,
    get_time_announcement,
    get_weather_announcement,
    mark_intro_used,
)


class TestIntroSelection:
    """Test intro selection."""
    
    def test_returns_path_to_audio(self, content_with_intros):
        """Must return path to intro audio file."""
        selector = ContentSelector(content_dir=content_with_intros)
        intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
        assert isinstance(intro, Path)
        assert intro.exists()
    
    def test_returns_none_if_no_intro(self, empty_content_dir):
        """Must return None if no intro exists."""
        selector = ContentSelector(content_dir=empty_content_dir)
        intro = get_intro_for_song(selector, song_id="nonexistent", dj="julie")
        assert intro is None
    
    def test_selects_different_intro_each_time(self, content_with_multiple_intros):
        """Should select different intros for variety."""
        selector = ContentSelector(content_dir=content_with_multiple_intros)
        
        intros = []
        for _ in range(10):
            intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
            mark_intro_used(selector, intro)
            intros.append(intro)
        
        # Should have used multiple different intros
        unique_intros = set(intros)
        assert len(unique_intros) > 1
    
    def test_selects_correct_dj_intro(self, content_with_both_djs):
        """Must select intro for the specified DJ."""
        selector = ContentSelector(content_dir=content_with_both_djs)
        
        julie_intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
        vegas_intro = get_intro_for_song(selector, song_id="song_1", dj="mr_new_vegas")
        
        assert "julie" in str(julie_intro).lower()
        assert "vegas" in str(vegas_intro).lower() or "mr_new" in str(vegas_intro).lower()


class TestTimeAnnouncements:
    """Test time announcement selection."""
    
    def test_returns_audio_path(self, content_with_time):
        """Must return path to time announcement audio."""
        selector = ContentSelector(content_dir=content_with_time)
        from datetime import datetime
        
        announcement = get_time_announcement(
            selector, 
            dj="julie", 
            time=datetime(2026, 1, 22, 14, 30)
        )
        assert isinstance(announcement, Path)
    
    def test_different_for_different_times(self, content_with_time):
        """Different times should have different announcements."""
        selector = ContentSelector(content_dir=content_with_time)
        from datetime import datetime
        
        two_pm = get_time_announcement(selector, "julie", datetime(2026, 1, 22, 14, 0))
        three_pm = get_time_announcement(selector, "julie", datetime(2026, 1, 22, 15, 0))
        
        assert two_pm != three_pm
```

**Success Criteria:**
- [ ] All content tests pass
- [ ] Correct intros selected for DJ and song
- [ ] Variety in intro selection works
- [ ] Time announcements match time of day

**Git Commit:** `feat(dj): add content selector`

---

### Phase 4 Gate: DJ System Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All DJ tests pass | `pytest tests/dj/ -v` |
| Personalities load correctly | Unit tests |
| Scheduler returns correct DJ | Unit tests for all time slots |
| Content selection works | Unit tests |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass
2.  Verify Julie is selected between 6 AM - 7 PM
3. Verify Mr. New Vegas is selected 7 PM - 6 AM
4. Verify content selector finds generated intros

**Git Tag:** `v0.5.0-dj`

---

## Phase 5: Radio Shows

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Play radio dramas with DJ integration |
| **Duration** | 1-2 sessions |
| **Complexity** | Low-Medium |
| **Dependencies** | Phase 3 (playback), Phase 4 (DJ) |

---

#### Checkpoint 5.1: Show Manager
**Manage radio show library and scheduling.**

**Tasks:**
1. Create `src/ai_radio/shows/show_manager.py`
2. Scan show library
3. Track which episodes have been played
4. Select next episode (sequential)

**Tests First:**
```python
# tests/shows/test_show_manager.py
"""Tests for show manager."""
import pytest
from pathlib import Path
from src. ai_radio.shows.show_manager import (
    ShowManager,
    scan_shows,
    get_next_episode,
    mark_episode_played,
    Show,
    Episode,
)


class TestScanShows:
    """Test show scanning."""
    
    def test_finds_show_directories(self, shows_directory):
        """Must find show directories."""
        manager = ShowManager()
        shows = scan_shows(manager, shows_directory)
        assert len(shows) > 0
    
    def test_finds_episodes_in_show(self, shows_directory):
        """Must find episode files in each show."""
        manager = ShowManager()
        shows = scan_shows(manager, shows_directory)
        
        for show in shows:
            assert len(show.episodes) > 0


class TestEpisodeSelection: 
    """Test episode selection."""
    
    def test_returns_first_unplayed(self, manager_with_shows):
        """Must return first unplayed episode."""
        episode = get_next_episode(manager_with_shows, show_name="The Shadow")
        assert episode.episode_number == 1
    
    def test_advances_after_played(self, manager_with_shows):
        """Must return next episode after marking played."""
        ep1 = get_next_episode(manager_with_shows, show_name="The Shadow")
        mark_episode_played(manager_with_shows, ep1)
        
        ep2 = get_next_episode(manager_with_shows, show_name="The Shadow")
        assert ep2.episode_number == 2
    
    def test_loops_after_all_played(self, manager_with_shows):
        """Must loop back to episode 1 after all played."""
        show = manager_with_shows.get_show("The Shadow")
        
        # Play all episodes
        for ep in show.episodes:
            mark_episode_played(manager_with_shows, ep)
        
        # Next should be episode 1 again
        next_ep = get_next_episode(manager_with_shows, show_name="The Shadow")
        assert next_ep.episode_number == 1
```

**Success Criteria:**
- [ ] All show manager tests pass
- [ ] Scans show directories correctly
- [ ] Sequential episode selection works
- [ ] Loops after all episodes played

**Git Commit:** `feat(shows): add show manager`

---

#### Checkpoint 5.2: Show Player Integration
**Integrate shows with DJ and playback.**

**Tasks:**
1. Create `src/ai_radio/shows/show_player.py`
2. Generate DJ intro for shows (if not pre-generated)
3. Play intro → show → DJ commentary
4. Return to music after show

**Tests First:**
```python
# tests/shows/test_show_player.py
"""Tests for show player."""
import pytest
from unittest.mock import Mock
from src.ai_radio. shows.show_player import (
    ShowPlayer,
    play_show_block,
    ShowBlockResult,
)


class TestShowBlock:
    """Test show block playback."""
    
    def test_plays_intro_before_show(self, mock_playback, show_with_intro):
        """DJ intro must play before show."""
        player = ShowPlayer(playback=mock_playback)
        
        played_items = []
        mock_playback.on_item_started = lambda item: played_items.append(item.item_type)
        
        play_show_block(player, show_with_intro)
        
        assert played_items[0] == "show_intro"
        assert played_items[1] == "show"
    
    def test_plays_outro_after_show(self, mock_playback, show_with_intro):
        """DJ commentary must play after show."""
        player = ShowPlayer(playback=mock_playback)
        
        played_items = []
        mock_playback.on_item_started = lambda item:  played_items.append(item.item_type)
        
        play_show_block(player, show_with_intro)
        
        assert played_items[-1] == "show_outro"
    
    def test_returns_result_with_duration(self, mock_playback, show_with_intro):
        """Must return result with total duration."""
        player = ShowPlayer(playback=mock_playback)
        result = play_show_block(player, show_with_intro)
        
        assert isinstance(result, ShowBlockResult)
        assert result.duration_seconds > 0
```

**Success Criteria:**
- [ ] All show player tests pass
- [ ] Shows play with DJ intro and outro
- [ ] Control returns to music after show

**Git Commit:** `feat(shows): add show player integration`

---

### Phase 5 Gate: Radio Shows Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All show tests pass | `pytest tests/shows/ -v` |
| Show scanning works | Unit tests |
| Sequential play works | Unit tests |
| DJ integration works | Unit tests |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass
2. Place The Shadow episode in shows folder
3. Verify show is detected by scanner
4. Manual test:  play show with DJ intro/outro

**Git Tag:** `v0.6.0-shows`

---

## Phase 6: Information Services

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Weather and time announcement services |
| **Duration** | 2-3 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 2 (generation), Phase 4 (DJ) |

---

#### Checkpoint 6.1: Clock Service
**Time tracking and announcement scheduling.**

**Tasks:**
1. Create `src/ai_radio/services/clock. py`
2. Track current time
3. Determine when to announce time
4. Get appropriate time announcement

**Tests First:**
```python
# tests/services/test_clock. py
"""Tests for clock service."""
import pytest
from datetime import datetime, timedelta
from src.ai_radio.services.clock import (
    ClockService,
    is_announcement_time,
    get_next_announcement_time,
    format_time_for_dj,
)


class TestAnnouncementTiming:
    """Test time announcement scheduling."""
    
    def test_announces_on_hour(self):
        """Must announce on the hour."""
        clock = ClockService()
        on_hour = datetime(2026, 1, 22, 14, 0, 0)
        assert is_announcement_time(clock, on_hour)
    
    def test_announces_on_half_hour(self):
        """Must announce on the half hour."""
        clock = ClockService()
        half_hour = datetime(2026, 1, 22, 14, 30, 0)
        assert is_announcement_time(clock, half_hour)
    
    def test_no_announce_at_quarter(self):
        """Must not announce at quarter hour."""
        clock = ClockService()
        quarter = datetime(2026, 1, 22, 14, 15, 0)
        assert not is_announcement_time(clock, quarter)
    
    def test_next_announcement_from_10_past(self):
        """Next announcement from : 10 should be : 30."""
        clock = ClockService()
        ten_past = datetime(2026, 1, 22, 14, 10, 0)
        next_time = get_next_announcement_time(clock, ten_past)
        assert next_time.minute == 30
    
    def test_next_announcement_from_40_past(self):
        """Next announcement from :40 should be next hour."""
        clock = ClockService()
        forty_past = datetime(2026, 1, 22, 14, 40, 0)
        next_time = get_next_announcement_time(clock, forty_past)
        assert next_time.hour == 15
        assert next_time. minute == 0


class TestTimeFormatting:
    """Test DJ-style time formatting."""
    
    def test_format_includes_hour(self):
        """Formatted time must include hour."""
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 30))
        assert "2" in formatted or "two" in formatted. lower() or "14" in formatted
    
    def test_format_on_hour_says_oclock(self):
        """On-the-hour times should say 'o'clock' or similar."""
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 0))
        assert "o'clock" in formatted.lower() or "00" in formatted
```

**Success Criteria:**
- [ ] All clock tests pass
- [ ] Announcement times detected correctly
- [ ] Time formatting is natural

**Git Commit:** `feat(services): add clock service`

---

#### Checkpoint 6.2: Weather Service
**Fetch and cache weather data.**

**Tasks:**
1. Create `src/ai_radio/services/weather.py`
2. Fetch weather from API
3. Cache results
4. Format for DJ announcement

**Tests First:**
```python
# tests/services/test_weather.py
"""Tests for weather service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.ai_radio. services.weather import (
    WeatherService,
    get_current_weather,
    is_weather_time,
    format_weather_for_dj,
    WeatherData,
)


class TestWeatherFetch:
    """Test weather data fetching."""
    
    def test_returns_weather_data(self, mock_weather_api):
        """Must return WeatherData object."""
        service = WeatherService()
        weather = get_current_weather(service)
        assert isinstance(weather, WeatherData)
    
    def test_weather_has_temperature(self, mock_weather_api):
        """Weather must include temperature."""
        service = WeatherService()
        weather = get_current_weather(service)
        assert weather.temperature is not None
    
    def test_weather_has_conditions(self, mock_weather_api):
        """Weather must include conditions description."""
        service = WeatherService()
        weather = get_current_weather(service)
        assert weather.conditions is not None
    
    def test_caches_results(self, mock_weather_api):
        """Must cache results to avoid API spam."""
        service = WeatherService()
        
        get_current_weather(service)
        get_current_weather(service)
        
        # API should only be called once
        assert mock_weather_api.call_count == 1
    
    def test_cache_expires(self, mock_weather_api):
        """Cache must expire after timeout."""
        service = WeatherService(cache_minutes=1)
        
        get_current_weather(service)
        
        # Simulate time passing
        service._cache_time = datetime.now() - timedelta(minutes=2)
        
        get_current_weather(service)
        
        # API should be called twice
        assert mock_weather_api.call_count == 2


class TestWeatherTiming:
    """Test weather announcement timing."""
    
    def test_weather_at_6am(self):
        """Must announce weather at 6 AM."""
        service = WeatherService()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert is_weather_time(service, six_am)
    
    def test_weather_at_noon(self):
        """Must announce weather at 12 PM."""
        service = WeatherService()
        noon = datetime(2026, 1, 22, 12, 0)
        assert is_weather_time(service, noon)
    
    def test_weather_at_5pm(self):
        """Must announce weather at 5 PM."""
        service = WeatherService()
        five_pm = datetime(2026, 1, 22, 17, 0)
        assert is_weather_time(service, five_pm)
    
    def test_no_weather_at_3pm(self):
        """Must not announce weather at 3 PM."""
        service = WeatherService()
        three_pm = datetime(2026, 1, 22, 15, 0)
        assert not is_weather_time(service, three_pm)


class TestWeatherFormatting:
    """Test period-style weather formatting."""
    
    def test_format_includes_temperature(self):
        """Formatted weather must include temperature."""
        weather = WeatherData(temperature=45, conditions="cloudy")
        formatted = format_weather_for_dj(weather)
        assert "45" in formatted
    
    def test_format_is_period_style(self):
        """Format should be period-flavored, not clinical."""
        weather = WeatherData(temperature=25, conditions="snow")
        formatted = format_weather_for_dj(weather)
        # Should use colorful language, not just "25 degrees snow"
        assert len(formatted) > 20  # More than minimal
```

**Success Criteria:**
- [ ] All weather tests pass
- [ ] API fetch works (with mock)
- [ ] Caching prevents API spam
- [ ] Formatting is period-appropriate

**Git Commit:** `feat(services): add weather service`

---

#### Checkpoint 6.3: Service Cache System
**Generic caching for all services.**

**Tasks:**
1. Create `src/ai_radio/services/cache.py`
2. Generic cache with expiration
3. Used by weather and other services

**Tests First:**
```python
# tests/services/test_cache.py
"""Tests for service cache."""
import pytest
from datetime import datetime, timedelta
from src.ai_radio. services.cache import (
    ServiceCache,
    cache_get,
    cache_set,
    cache_invalidate,
    is_cache_valid,
)


class TestServiceCache:
    """Test generic caching."""
    
    def test_set_and_get(self):
        """Must be able to set and get values."""
        cache = ServiceCache()
        cache_set(cache, "key", "value")
        assert cache_get(cache, "key") == "value"
    
    def test_get_missing_returns_none(self):
        """Getting missing key must return None."""
        cache = ServiceCache()
        assert cache_get(cache, "nonexistent") is None
    
    def test_cache_expires(self):
        """Cached values must expire."""
        cache = ServiceCache(default_ttl_seconds=60)
        cache_set(cache, "key", "value")
        
        # Simulate time passing
        cache._entries["key"]. created = datetime.now() - timedelta(seconds=120)
        
        assert cache_get(cache, "key") is None
    
    def test_invalidate_removes_entry(self):
        """Invalidating must remove entry."""
        cache = ServiceCache()
        cache_set(cache, "key", "value")
        cache_invalidate(cache, "key")
        assert cache_get(cache, "key") is None
```

**Success Criteria:**
- [ ] All cache tests pass
- [ ] Generic cache works for any data
- [ ] Expiration works correctly

**Git Commit:** `feat(services): add service cache`

---

### Phase 6 Gate: Information Services Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All service tests pass | `pytest tests/services/ -v` |
| Clock timing is correct | Unit tests |
| Weather caching works | Unit tests |
| Integration with real API | Integration test (manual) |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass
2. Run weather service with real API key (if configured)
3. Verify time announcements at correct intervals
4. Verify weather formatting sounds natural

**Git Tag:** `v0.7.0-services`

---

# 🎙️ AI Radio Station — Implementation Roadmap (Continued)

---

## Phase 7: Integration (Continued)

#### Checkpoint 7.1: Station Controller (Continued)

**Tests First (Continued):**
```python
# tests/station/test_controller.py (continued)

    def test_uses_correct_dj(self, controller_with_content):
        """Must use correct DJ for time of day."""
        controller = controller_with_content
        
        with patch_current_time(datetime(2026, 1, 22, 10, 0)):
            current_dj = controller.get_current_dj()
            assert current_dj. name == "julie"
        
        with patch_current_time(datetime(2026, 1, 22, 22, 0)):
            current_dj = controller.get_current_dj()
            assert current_dj.name == "mr_new_vegas"
    
    def test_handles_dj_handoff(self, controller_with_content):
        """Must handle DJ transition at 7 PM."""
        controller = controller_with_content
        
        with patch_current_time(datetime(2026, 1, 22, 19, 0)):
            items = controller._get_next_items()
        
        types = [item.item_type for item in items]
        assert "dj_handoff" in types


class TestStationRecovery:
    """Test error recovery."""
    
    def test_continues_on_song_error(self, controller_with_content, corrupt_song):
        """Must skip corrupt songs and continue."""
        controller = controller_with_content
        controller.queue_song(corrupt_song)
        
        # Should not raise
        controller._play_next()
        
        # Should have moved on
        assert controller. current_item != corrupt_song
    
    def test_logs_errors(self, controller_with_content, corrupt_song, caplog):
        """Must log errors for review."""
        controller = controller_with_content
        controller.queue_song(corrupt_song)
        
        controller._play_next()
        
        assert "error" in caplog. text. lower()
    
    def test_plays_recovery_line(self, controller_with_content, corrupt_song):
        """Must play DJ recovery line on error."""
        controller = controller_with_content
        
        played = []
        controller.on_item_started = lambda item: played.append(item. item_type)
        
        controller.queue_song(corrupt_song)
        controller._play_next()
        
        assert "error_recovery" in played
```

**Implementation Specification:**
```python
# src/ai_radio/station/controller.py
"""
Station controller - the brain of the radio station. 

Orchestrates all subsystems: 
- Music library and rotation
- Content playback
- DJ scheduling
- Information services (weather, time)
- Radio shows
- Error recovery

This is the main entry point for running the station.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Callable
from pathlib import Path

from src.ai_radio.library.catalog import SongCatalog, load_catalog
from src.ai_radio.library. rotation import RotationManager, get_next_song
from src.ai_radio.playback. controller import PlaybackController
from src.ai_radio. dj.scheduler import DJScheduler, get_current_dj
from src.ai_radio. dj.content import ContentSelector, get_intro_for_song
from src.ai_radio.services. clock import ClockService, is_announcement_time
from src.ai_radio. services.weather import WeatherService, is_weather_time
from src.ai_radio.shows.show_manager import ShowManager, get_next_episode
from src.ai_radio.utils.logging import setup_logging, log_error_with_context
from src.ai_radio. utils.errors import AIRadioError, PlaybackError
from src.ai_radio. config import (
    CATALOG_FILE,
    RADIO_SHOW_HOUR,
    DJ_HANDOFF_HOUR,
)


class StationState(Enum):
    """Station operational states."""
    INITIALIZING = auto()
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass
class StationStatus:
    """Current station status for display."""
    state: StationState
    current_song: Optional[str]
    current_dj: str
    next_up: Optional[str]
    uptime_seconds: float
    songs_played: int
    errors_count: int


class StationController: 
    """
    Master controller for the AI Radio Station. 
    
    Coordinates all subsystems and makes decisions about
    what to play next based on time, DJ, and programming.
    """
    
    def __init__(self, config_overrides: dict = None):
        self.logger = setup_logging("station. controller")
        self.state = StationState. INITIALIZING
        
        # Subsystems (initialized in start())
        self.catalog:  Optional[SongCatalog] = None
        self.rotation: Optional[RotationManager] = None
        self.playback: Optional[PlaybackController] = None
        self. dj_scheduler: Optional[DJScheduler] = None
        self.content: Optional[ContentSelector] = None
        self.clock: Optional[ClockService] = None
        self.weather: Optional[WeatherService] = None
        self.shows: Optional[ShowManager] = None
        
        # Statistics
        self.start_time:  Optional[datetime] = None
        self. songs_played: int = 0
        self.errors_count: int = 0
        
        # Callbacks
        self.on_song_change: Optional[Callable] = None
        self.on_dj_change: Optional[Callable] = None
        self. on_error: Optional[Callable] = None
    
    def _initialize_subsystems(self) -> None:
        """Initialize all subsystems."""
        self. logger.info("Initializing subsystems...")
        
        # Load catalog
        self. catalog = load_catalog(CATALOG_FILE)
        self.logger.info(f"Loaded {len(self.catalog)} songs")
        
        # Initialize rotation
        self.rotation = RotationManager(self.catalog)
        
        # Initialize playback
        self.playback = PlaybackController()
        self.playback.on_item_complete = self._on_playback_complete
        
        # Initialize DJ system
        self. dj_scheduler = DJScheduler()
        self.content = ContentSelector()
        
        # Initialize services
        self.clock = ClockService()
        self.weather = WeatherService()
        
        # Initialize shows
        self.shows = ShowManager()
        
        self.logger.info("All subsystems initialized")
    
    def _decide_next_content(self) -> List['QueueItem']:
        """
        Decide what to play next based on current time and state.
        
        Priority order:
        1. DJ Handoff (if transition time)
        2. Radio Show (if 8 PM)
        3. Weather (if weather time)
        4. Time announcement (if announcement time)
        5. Next song with intro
        """
        now = datetime.now()
        items = []
        current_dj = get_current_dj(self.dj_scheduler, now)
        
        # Check for DJ handoff
        if now.hour == DJ_HANDOFF_HOUR and now.minute < 5:
            handoff = self._get_handoff_content()
            if handoff:
                items. extend(handoff)
        
        # Check for radio show time
        if now.hour == RADIO_SHOW_HOUR and not self._show_played_today():
            show_items = self._get_show_content()
            if show_items:
                items.extend(show_items)
                return items  # Show takes priority
        
        # Check for weather
        if is_weather_time(self.weather, now):
            weather_item = self._get_weather_content(current_dj)
            if weather_item:
                items. append(weather_item)
        
        # Check for time announcement
        if is_announcement_time(self.clock, now):
            time_item = self._get_time_content(current_dj, now)
            if time_item: 
                items.append(time_item)
        
        # Always queue next song
        song_items = self._get_next_song_content(current_dj)
        items.extend(song_items)
        
        return items
    
    # Additional implementation methods...
```

**Success Criteria:**
- [ ] All controller tests pass
- [ ] Station starts and initializes all subsystems
- [ ] Correct content decisions based on time
- [ ] DJ handoff works at 7 PM
- [ ] Radio shows play at 8 PM
- [ ] Weather plays at scheduled times
- [ ] Time announcements play every 30 minutes
- [ ] Errors are caught and recovered from

**Validation:**
```bash
# Human runs: 
pytest tests/station/test_controller. py -v
```

**Git Commit:** `feat(station): add station controller`

---

#### Checkpoint 7.2: Terminal Display
**Show current station status in terminal.**

**Tasks:**
1. Create `src/ai_radio/station/display.py`
2. Simple text-based status display
3. Update without flickering
4. Show key information

**Tests First:**
```python
# tests/station/test_display.py
"""Tests for terminal display."""
import pytest
from src.ai_radio. station.display import (
    StationDisplay,
    format_status,
    format_now_playing,
    format_next_up,
    clear_and_draw,
)
from src.ai_radio.station.controller import StationStatus, StationState


class TestFormatStatus:
    """Test status formatting."""
    
    def test_includes_state(self):
        """Formatted status must include state."""
        status = StationStatus(
            state=StationState. PLAYING,
            current_song="Test Song",
            current_dj="Julie",
            next_up="Next Song",
            uptime_seconds=3600,
            songs_played=10,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "PLAYING" in formatted or "Playing" in formatted
    
    def test_includes_current_song(self):
        """Formatted status must include current song."""
        status = StationStatus(
            state=StationState. PLAYING,
            current_song="Bing Crosby - White Christmas",
            current_dj="Julie",
            next_up=None,
            uptime_seconds=0,
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "Bing Crosby" in formatted
        assert "White Christmas" in formatted
    
    def test_includes_dj_name(self):
        """Formatted status must include DJ name."""
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Test",
            current_dj="Mr. New Vegas",
            next_up=None,
            uptime_seconds=0,
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "Mr. New Vegas" in formatted or "Vegas" in formatted
    
    def test_includes_uptime(self):
        """Formatted status must include uptime."""
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Test",
            current_dj="Julie",
            next_up=None,
            uptime_seconds=7200,  # 2 hours
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "2" in formatted and ("hour" in formatted. lower() or "h" in formatted)


class TestDisplayOutput:
    """Test display output."""
    
    def test_format_now_playing_shows_song(self):
        """Now playing must show song info."""
        output = format_now_playing("Bing Crosby", "White Christmas")
        assert "Bing Crosby" in output
        assert "White Christmas" in output
    
    def test_format_next_up_shows_upcoming(self):
        """Next up must show upcoming song."""
        output = format_next_up("Frank Sinatra - Fly Me to the Moon")
        assert "Frank Sinatra" in output
    
    def test_format_next_up_handles_none(self):
        """Next up must handle no upcoming song."""
        output = format_next_up(None)
        assert output is not None  # Should not crash
```

**Implementation Specification:**
```python
# src/ai_radio/station/display.py
"""
Terminal display for station status.

Provides a simple, clean terminal interface showing:
- Current song
- Current DJ
- Next up
- Station status
- Uptime and statistics
"""
import os
import sys
from datetime import timedelta
from src.ai_radio. station.controller import StationStatus, StationState


def clear_screen() -> None:
    """Clear the terminal screen."""
    os. system('cls' if os.name == 'nt' else 'clear')


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable form."""
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if td.days > 0:
        return f"{td.days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"


def format_status(status: StationStatus) -> str:
    """Format complete station status for display."""
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║           🎙️  AI RADIO STATION                           ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Status: {status.state.name: <47} ║",
        f"║  DJ: {status.current_dj:<51} ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  NOW PLAYING:                                             ║",
        f"║    {(status.current_song or 'Nothing')[:54]:<54} ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  NEXT UP:                                                ║",
        f"║    {(status.next_up or 'Unknown')[:54]:<54} ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Uptime: {format_uptime(status.uptime_seconds):<47} ║",
        f"║  Songs Played: {status. songs_played: <41} ║",
        f"║  Errors: {status.errors_count:<47} ║",
        "╠══════════════════════════════════════════════════════════╣",
        "║  Commands:  [Q]uit  [P]ause  [S]kip  [B]anish             ║",
        "╚══════════════════════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


def format_now_playing(artist: str, title: str) -> str:
    """Format now playing line."""
    return f"{artist} - {title}"


def format_next_up(song_display: str | None) -> str:
    """Format next up line."""
    if song_display is None:
        return "Queuing next song..."
    return song_display


class StationDisplay: 
    """
    Manages terminal display updates. 
    
    Updates display without excessive flickering. 
    """
    
    def __init__(self):
        self.last_status: StationStatus | None = None
    
    def update(self, status: StationStatus) -> None:
        """Update display with new status."""
        # Only clear and redraw if status changed
        if self._status_changed(status):
            clear_screen()
            print(format_status(status))
            self. last_status = status
    
    def _status_changed(self, new_status: StationStatus) -> bool:
        """Check if status has meaningfully changed."""
        if self.last_status is None:
            return True
        
        return (
            self.last_status. current_song != new_status.current_song or
            self. last_status.current_dj != new_status.current_dj or
            self.last_status.state != new_status. state or
            self.last_status. next_up != new_status.next_up
        )
```

**Success Criteria:**
- [ ] All display tests pass
- [ ] Status shows all required information
- [ ] Display is readable and clean
- [ ] Updates without excessive flickering

**Git Commit:** `feat(station): add terminal display`

---

#### Checkpoint 7.3: Command Handler
**Handle user input during playback.**

**Tasks:**
1. Create `src/ai_radio/station/commands.py`
2. Non-blocking keyboard input
3. Handle Q (quit), P (pause), S (skip), B (banish)
4. Handle flagging bad intros

**Tests First:**
```python
# tests/station/test_commands.py
"""Tests for command handler."""
import pytest
from unittest.mock import Mock
from src.ai_radio.station.commands import (
    CommandHandler,
    Command,
    parse_key,
    execute_command,
)


class TestParseKey:
    """Test key parsing."""
    
    def test_q_is_quit(self):
        """'q' key must map to QUIT command."""
        assert parse_key('q') == Command.QUIT
        assert parse_key('Q') == Command.QUIT
    
    def test_p_is_pause(self):
        """'p' key must map to PAUSE command."""
        assert parse_key('p') == Command.PAUSE
        assert parse_key('P') == Command.PAUSE
    
    def test_s_is_skip(self):
        """'s' key must map to SKIP command."""
        assert parse_key('s') == Command.SKIP
        assert parse_key('S') == Command.SKIP
    
    def test_b_is_banish(self):
        """'b' key must map to BANISH command."""
        assert parse_key('b') == Command.BANISH
        assert parse_key('B') == Command.BANISH
    
    def test_f_is_flag(self):
        """'f' key must map to FLAG command."""
        assert parse_key('f') == Command.FLAG
        assert parse_key('F') == Command.FLAG
    
    def test_unknown_key_is_none(self):
        """Unknown keys must return None."""
        assert parse_key('x') is None
        assert parse_key('1') is None


class TestExecuteCommand:
    """Test command execution."""
    
    def test_quit_stops_station(self, mock_controller):
        """QUIT must stop the station."""
        execute_command(Command. QUIT, mock_controller)
        mock_controller.stop. assert_called_once()
    
    def test_pause_pauses_playback(self, mock_controller):
        """PAUSE must pause playback."""
        execute_command(Command.PAUSE, mock_controller)
        mock_controller.pause.assert_called_once()
    
    def test_skip_advances_song(self, mock_controller):
        """SKIP must advance to next song."""
        execute_command(Command.SKIP, mock_controller)
        mock_controller.skip.assert_called_once()
    
    def test_banish_banishes_current_song(self, mock_controller):
        """BANISH must banish current song."""
        mock_controller.current_song_id = "song_123"
        execute_command(Command. BANISH, mock_controller)
        mock_controller.banish_song.assert_called_once_with("song_123")
    
    def test_flag_flags_current_intro(self, mock_controller):
        """FLAG must flag current intro for regeneration."""
        mock_controller.current_intro_path = "/path/to/intro.wav"
        execute_command(Command.FLAG, mock_controller)
        mock_controller.flag_intro. assert_called_once()
```

**Implementation Specification:**
```python
# src/ai_radio/station/commands.py
"""
Command handler for user input during playback.

Provides non-blocking keyboard input handling on Windows.
Supports: 
- Q:  Quit station
- P:  Pause/Resume
- S: Skip current song
- B:  Banish current song
- F: Flag current intro for regeneration
- +/-: Volume up/down (future)
"""
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
import sys
import threading

if TYPE_CHECKING: 
    from src. ai_radio.station.controller import StationController


class Command(Enum):
    """Available commands."""
    QUIT = auto()
    PAUSE = auto()
    RESUME = auto()
    SKIP = auto()
    BANISH = auto()
    FLAG = auto()
    PROMOTE = auto()
    VOLUME_UP = auto()
    VOLUME_DOWN = auto()


# Key mappings
KEY_MAP = {
    'q': Command. QUIT,
    'p': Command. PAUSE,
    's': Command.SKIP,
    'b': Command.BANISH,
    'f': Command.FLAG,
    'r': Command.PROMOTE,  # R for "really like this"
    '+':  Command.VOLUME_UP,
    '-': Command.VOLUME_DOWN,
}


def parse_key(key: str) -> Optional[Command]:
    """Parse a key press into a command."""
    return KEY_MAP.get(key.lower())


def execute_command(command: Command, controller: 'StationController') -> None:
    """Execute a command on the station controller."""
    from src.ai_radio.utils.logging import setup_logging
    logger = setup_logging("commands")
    
    if command == Command. QUIT:
        logger.info("Quit command received")
        controller. stop()
    
    elif command == Command.PAUSE: 
        if controller.is_playing: 
            logger.info("Pausing playback")
            controller.pause()
        else:
            logger.info("Resuming playback")
            controller.resume()
    
    elif command == Command. SKIP:
        logger.info(f"Skipping:  {controller.current_song_display}")
        controller. skip()
    
    elif command == Command.BANISH: 
        song_id = controller. current_song_id
        if song_id: 
            logger.info(f"Banishing: {controller.current_song_display}")
            controller.banish_song(song_id)
            controller.skip()
    
    elif command == Command.FLAG: 
        intro_path = controller. current_intro_path
        if intro_path:
            logger.info(f"Flagging intro for regeneration: {intro_path}")
            controller.flag_intro(intro_path)
    
    elif command == Command.PROMOTE:
        song_id = controller.current_song_id
        if song_id:
            logger. info(f"Promoting: {controller. current_song_display}")
            controller. promote_song(song_id)


class CommandHandler: 
    """
    Non-blocking keyboard input handler.
    
    Runs in a separate thread to avoid blocking playback.
    """
    
    def __init__(self, controller: 'StationController'):
        self.controller = controller
        self.running = False
        self.thread:  Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start listening for keyboard input."""
        self.running = True
        self.thread = threading.Thread(target=self._input_loop, daemon=True)
        self.thread. start()
    
    def stop(self) -> None:
        """Stop listening for keyboard input."""
        self.running = False
    
    def _input_loop(self) -> None:
        """Main input loop (runs in thread)."""
        # Windows-specific keyboard handling
        if sys.platform == 'win32': 
            import msvcrt
            while self. running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                    command = parse_key(key)
                    if command:
                        execute_command(command, self.controller)
        else:
            # Unix-like systems would need different handling
            # For MVP, focus on Windows
            pass
```

**Success Criteria:**
- [ ] All command tests pass
- [ ] Keys map to correct commands
- [ ] Commands execute correctly
- [ ] Non-blocking input works

**Git Commit:** `feat(station): add command handler`

---

#### Checkpoint 7.4: Main Entry Point
**Create the main script to run the station.**

**Tasks:**
1. Create `src/ai_radio/main.py`
2. Parse command-line arguments
3. Initialize and run station
4. Handle graceful shutdown

**File:  `src/ai_radio/main.py`**
```python
"""
AI Radio Station - Main Entry Point

Usage:
    python -m ai_radio
    python -m ai_radio --config custom_config.py
    python -m ai_radio --dry-run

Options:
    --dry-run       Show configuration and exit
    --no-weather    Disable weather announcements
    --no-shows      Disable radio shows
    --debug         Enable debug logging
"""
import sys
import signal
import argparse
from pathlib import Path

from src.ai_radio.station.controller import StationController, start_station, stop_station
from src.ai_radio.station.display import StationDisplay
from src.ai_radio. station.commands import CommandHandler
from src.ai_radio.utils.logging import setup_logging
from src.ai_radio.config import CATALOG_FILE


def parse_args():
    """Parse command line arguments."""
    parser = argparse. ArgumentParser(
        description="AI Radio Station - Your personal Golden Age radio experience"
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show configuration and exit')
    parser.add_argument('--no-weather', action='store_true',
                        help='Disable weather announcements')
    parser.add_argument('--no-shows', action='store_true',
                        help='Disable radio shows')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    logger = setup_logging("main")
    
    # Dry run - just show config
    if args. dry_run: 
        print("AI Radio Station - Configuration")
        print("=" * 50)
        print(f"Catalog: {CATALOG_FILE}")
        print(f"Catalog exists: {CATALOG_FILE.exists()}")
        if CATALOG_FILE. exists():
            from src.ai_radio.library.catalog import load_catalog
            catalog = load_catalog(CATALOG_FILE)
            print(f"Songs in catalog: {len(catalog)}")
        print(f"Weather enabled: {not args. no_weather}")
        print(f"Shows enabled: {not args.no_shows}")
        return 0
    
    # Check prerequisites
    if not CATALOG_FILE.exists():
        print(f"Error:  Catalog not found at {CATALOG_FILE}")
        print("Run 'python scripts/scan_library.py <music_path>' first.")
        return 1
    
    # Initialize station
    logger.info("Starting AI Radio Station...")
    
    controller = StationController(
        config_overrides={
            'weather_enabled': not args. no_weather,
            'shows_enabled': not args.no_shows,
        }
    )
    display = StationDisplay()
    commands = CommandHandler(controller)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        stop_station(controller)
        sys.exit(0)
    
    signal. signal(signal. SIGINT, signal_handler)
    
    # Start everything
    try: 
        start_station(controller)
        commands.start()
        
        logger.info("Station is now playing!")
        
        # Main loop
        while controller.is_running:
            status = controller.get_status()
            display.update(status)
            
            # Small sleep to prevent CPU spinning
            import time
            time.sleep(0.1)
    
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1
    
    finally:
        commands.stop()
        stop_station(controller)
        logger.info("Station stopped")
    
    return 0


if __name__ == "__main__": 
    sys.exit(main())
```

**Tests for Main:**
```python
# tests/station/test_main. py
"""Tests for main entry point."""
import pytest
from unittest.mock import Mock, patch
from src.ai_radio.main import parse_args, main


class TestParseArgs:
    """Test argument parsing."""
    
    def test_dry_run_flag(self):
        """--dry-run flag must be parsed."""
        with patch('sys.argv', ['main', '--dry-run']):
            args = parse_args()
            assert args.dry_run is True
    
    def test_no_weather_flag(self):
        """--no-weather flag must be parsed."""
        with patch('sys.argv', ['main', '--no-weather']):
            args = parse_args()
            assert args.no_weather is True
    
    def test_defaults(self):
        """Default values must be correct."""
        with patch('sys.argv', ['main']):
            args = parse_args()
            assert args.dry_run is False
            assert args.no_weather is False
            assert args.no_shows is False


class TestMain: 
    """Test main function."""
    
    def test_dry_run_exits_zero(self, mock_catalog_exists):
        """Dry run must exit with code 0."""
        with patch('sys.argv', ['main', '--dry-run']):
            result = main()
            assert result == 0
    
    def test_missing_catalog_exits_one(self, mock_catalog_missing):
        """Missing catalog must exit with code 1."""
        with patch('sys. argv', ['main']):
            result = main()
            assert result == 1
```

**Success Criteria:**
- [ ] All main tests pass
- [ ] `--dry-run` shows configuration
- [ ] Station starts with valid configuration
- [ ] Ctrl+C stops station gracefully
- [ ] Exit codes are correct

**Git Commit:** `feat(station): add main entry point`

---

#### Checkpoint 7.5: Integration Test Script
**Create a comprehensive integration test.**

**Tasks:**
1. Create `tests/integration/test_full_station.py`
2. Test complete startup → play → shutdown cycle
3. Test all subsystems working together

**File: `tests/integration/test_full_station.py`**
```python
"""
Full station integration tests. 

These tests verify the complete system works together.
They may take longer to run and require actual audio files. 

Run with:  pytest tests/integration/ -v -m integration
"""
import pytest
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


@pytest.mark.integration
class TestFullStationCycle:
    """Test complete station operation."""
    
    def test_startup_plays_first_song(self, configured_station):
        """Station must start playing within 5 seconds."""
        controller = configured_station
        
        controller.start()
        
        # Wait for first song
        timeout = 5
        start = time.time()
        while time.time() - start < timeout:
            if controller.current_song is not None:
                break
            time. sleep(0.1)
        
        assert controller.current_song is not None
        controller.stop()
    
    def test_auto_advances_to_next_song(self, configured_station, short_audio_files):
        """Station must auto-advance when song ends."""
        controller = configured_station
        
        # Use very short audio for test
        controller.start()
        
        first_song = None
        timeout = 10
        start = time.time()
        
        while time.time() - start < timeout:
            if controller.current_song is not None:
                if first_song is None:
                    first_song = controller. current_song
                elif controller.current_song != first_song: 
                    # Advanced to second song
                    break
            time.sleep(0.1)
        
        assert controller.current_song != first_song
        controller.stop()
    
    def test_dj_is_correct_for_time(self, configured_station):
        """DJ must match the current time of day."""
        controller = configured_station
        
        with patch_current_time(datetime(2026, 1, 22, 10, 0)):
            controller.start()
            assert controller.current_dj. name. lower() == "julie"
            controller. stop()
        
        with patch_current_time(datetime(2026, 1, 22, 22, 0)):
            controller.start()
            assert "vegas" in controller.current_dj.name.lower()
            controller.stop()
    
    def test_graceful_shutdown(self, configured_station):
        """Station must shut down gracefully."""
        controller = configured_station
        controller.start()
        
        # Let it run briefly
        time.sleep(1)
        
        # Should not raise
        controller.stop()
        
        assert controller.is_stopped
    
    def test_logs_all_songs_played(self, configured_station, caplog):
        """Station must log all songs played."""
        controller = configured_station
        controller.start()
        
        # Let it play a couple songs
        time. sleep(5)
        controller.stop()
        
        # Check logs contain song information
        assert any("Playing" in record.message for record in caplog.records)


@pytest.mark.integration
class TestErrorRecovery:
    """Test station error recovery."""
    
    def test_recovers_from_missing_song(self, configured_station, catalog_with_missing_file):
        """Station must skip missing songs and continue."""
        controller = configured_station
        controller.start()
        
        # Should not crash
        time.sleep(3)
        
        assert controller.is_playing
        controller.stop()
    
    def test_logs_errors(self, configured_station, catalog_with_missing_file, caplog):
        """Station must log errors."""
        controller = configured_station
        controller.start()
        time.sleep(3)
        controller. stop()
        
        # Should have logged the error
        assert any("error" in record.message. lower() for record in caplog.records)
```

**Success Criteria:**
- [ ] Integration tests pass
- [ ] Station completes full cycle
- [ ] Error recovery works
- [ ] Logging captures everything

**Git Commit:** `test(integration): add full station integration tests`

---

### Phase 7 Gate:  Integration Complete

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| All station tests pass | `pytest tests/station/ -v` |
| Integration tests pass | `pytest tests/integration/ -v -m integration` |
| Station starts and plays | Manual test |
| Commands work (Q, P, S, B, F) | Manual test |
| Display shows correct info | Visual inspection |
| Logs are comprehensive | Review log file |
| No regressions | `pytest tests/ -v` (all tests) |

**Human Validation Required:**
1. Run `pytest tests/ -v` — ALL tests pass (entire test suite)
2. Run station for 15 minutes manually
3. Test all keyboard commands
4. Verify DJ switches at transition time (or mock time)
5. Review log file for completeness
6. Verify display updates correctly

**Artifact:**
- Screenshot of station running
- Log file from 15-minute test
- Screenshot of all tests passing

**Git Tag:** `v0.8.0-integration`

---

## Phase 8: 24-Hour Validation

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Prove station runs 24 hours without intervention |
| **Duration** | 1-2 days |
| **Complexity** | Low (mostly monitoring) |
| **Dependencies** | All previous phases complete |

---

#### Checkpoint 8.1: Pre-Flight Checklist
**Verify everything is ready for 24-hour test.**

**Checklist:**
```markdown
## 24-Hour Test Pre-Flight Checklist

### Content Verification
- [ ] Catalog contains all songs
- [ ] All songs have at least one generated intro (Julie and Mr. New Vegas)
- [ ] Time announcements generated for all 48 slots (every 30 min × 2 DJs)
- [ ] Weather templates generated
- [ ] At least one radio show episode ready
- [ ] DJ handoff audio generated

### System Verification
- [ ] All tests pass:  `pytest tests/ -v`
- [ ] Station starts without errors:  `python -m ai_radio --dry-run`
- [ ] Ollama is not needed during playback (all content pre-generated)
- [ ] Chatterbox is not needed during playback (all content pre-generated)
- [ ] Log directory has write permissions
- [ ] Adequate disk space for 24 hours of logs

### Configuration Verification
- [ ] Music library path is correct
- [ ] Weather API key is configured (or weather disabled)
- [ ] Shows directory contains episode(s)

### Environmental Verification
- [ ] Computer will not sleep during test
- [ ] Screen saver won't interfere
- [ ] No scheduled restarts or updates
- [ ] Audio output is configured correctly
```

**Git Commit:** `docs:  add 24-hour test checklist`

---

#### Checkpoint 8.2: 24-Hour Test Execution
**Run the station for 24 hours.**

**Protocol:**
1. Start station at a memorable time (e.g., 8:00 AM)
2. Let it run unattended for 24 hours
3. Check in briefly at key times:
   - +1 hour:  Still running? 
   - +4 hours: Still running?  Any errors in log?
   - +8 hours: Check log size, any issues? 
   - +12 hours:  Midpoint check
   - +24 hours: Final validation

**Success Log Template:**
```markdown
## 24-Hour Test Log

### Start
- Start time: ___________
- Initial song: ___________
- Initial DJ: ___________
- Start conditions: ___________

### +1 Hour Check
- Time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played: ___________
- Errors in log: ___________

### +4 Hour Check
- Time:  ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played: ___________
- Errors in log: ___________

### +8 Hour Check
- Time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played: ___________
- Log file size: ___________

### +12 Hour Check
- Time:  ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- DJ handoff observed: [ ] Yes [ ] No
- Radio show played: [ ] Yes [ ] No

### +24 Hour Final
- End time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Total songs played: ___________
- Total errors: ___________
- Final DJ: ___________

### Issues Observed
(List any issues)

### Overall Result
[ ] PASS - Ran 24 hours without manual intervention
[ ] FAIL - Reason: ___________
```

---

#### Checkpoint 8.3: Post-Test Analysis
**Analyze logs and fix any issues.**

**Tasks:**
1. Review complete log file
2. Count and categorize errors
3. Identify any patterns
4. Fix critical issues
5. Document non-critical issues for future

**Analysis Template:**
```markdown
## 24-Hour Test Analysis

### Summary Statistics
- Total runtime: ___ hours ___ minutes
- Songs played: ___
- Time announcements: ___
- Weather announcements: ___
- Radio shows played: ___
- DJ handoffs: ___
- Errors: ___

### Error Analysis
| Error Type | Count | Severity | Action |
|------------|-------|----------|--------|
| | | | |

### Performance Observations
- Memory usage stable?  ___
- CPU usage reasonable? ___
- Log file size: ___
- Any audio glitches? ___

### Recommendations
(List recommendations for improvement)
```

---

#### Checkpoint 8.4: Bug Fixes
**Fix any issues discovered during 24-hour test.**

**For each bug:**
1. Create a failing test that reproduces the bug
2. Fix the bug
3. Verify test now passes
4. Run full test suite to check for regressions

**Git Commit Pattern:**
```
fix(component): brief description of fix

Discovered during 24-hour test. 
- Root cause: ... 
- Solution: ... 

Fixes #XX (if tracking issues)
```

---

### Phase 8 Gate: MVP Complete!  🎉

**All Criteria Must Pass:**

| Criterion | Validation Method |
|-----------|-------------------|
| Station ran 24 hours | Test log documentation |
| No crashes | Log file review |
| All major features worked | Test log checkboxes |
| Errors were recoverable | Station continued running |
| All tests still pass | `pytest tests/ -v` |

**Human Validation Required:**
1. Complete 24-hour test log
2. Run `pytest tests/ -v` — ALL tests still pass
3. Review log file for any concerning patterns
4. Confirm you're happy with the experience

**Celebration Criteria:**
- ✅ Pressed start
- ✅ Walked away
- ✅ Came back 24 hours later
- ✅ Still playing
- ✅ Logs captured everything

**Git Tag:** `v1.0.0-mvp`

---

## Refactoring Guidelines

### When to Refactor

| Signal | Action |
|--------|--------|
| Same code in 3+ places | Extract to shared function |
| Function > 50 lines | Break into smaller functions |
| File > 300 lines | Split into modules |
| Test is hard to write | Simplify the code |
| You can't explain what code does | Rewrite for clarity |

### How to Refactor Safely

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFE REFACTORING                          │
│                                                              │
│  1. All tests pass BEFORE refactoring                        │
│  2. Make ONE change at a time                                │
│  3. Run tests after EACH change                              │
│  4. If tests fail, UNDO the change                           │
│  5. Commit after each successful change                      │
│  6. Never refactor and add features simultaneously           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Refactoring Commit Pattern
```
refactor(component): description of change

- What was changed
- Why it was changed
- No behavior changes

All tests pass. 
```

---

## Context Management

### Preventing Context Rot

**For LLM-Assisted Development:**

#### 1. Session Start Protocol
Every coding session begins with:
```markdown
1. Read ROADMAP.md (this document)
2. Read current phase specification
3. Run:  pytest tests/ -v (establish baseline)
4. Review last 3 git commits
5. Read any flagged issues/TODOs
```

#### 2. Session End Protocol
Every coding session ends with: 
```markdown
1. Run: pytest tests/ -v (all must pass)
2. Commit all changes with clear messages
3. Update CHANGELOG.md if significant
4. Note any incomplete work in TODO
5. Push to GitHub
```

#### 3. Context Anchors
Key files that maintain context:
- `ROADMAP.md` — Overall plan (this document)
- `PROJECT_SPEC.md` — What we're building
- `CHANGELOG.md` — What's been done
- `data/catalog.json` — Current music state
- `logs/` — Recent activity

#### 4. Conversation Boundaries
When starting a new conversation with an LLM: 
```markdown
## Context for New Session

### Current Phase:  [X]
### Last Completed Checkpoint: [X. Y]
### Current Checkpoint: [X.Z]

### Recent Changes:
- [commit 1]
- [commit 2]
- [commit 3]

### Known Issues:
- [issue 1]

### Today's Goal:
[specific goal]
```

#### 5. Test-Driven Context
Tests serve as executable documentation:
- If unsure what code should do, read the tests
- Tests define the contract
- Tests don't lie (code might)

---

## Appendix:  Test Templates

### Fixture Template (conftest.py)
```python
# tests/conftest. py
"""
Shared test fixtures. 

Fixtures provide reusable test data and mocks.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock


# ============================================================
# Path Fixtures
# ============================================================

@pytest.fixture
def tmp_music_dir(tmp_path):
    """Create a temporary music directory."""
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    return music_dir


@pytest.fixture
def sample_mp3_path(tmp_music_dir):
    """Create a sample MP3 file (minimal valid MP3)."""
    mp3_path = tmp_music_dir / "sample.mp3"
    # Minimal MP3 header
    mp3_path.write_bytes(b'\xff\xfb\x90\x00' + b'\x00' * 100)
    return mp3_path


# ============================================================
# Mock Fixtures
# ============================================================

@pytest.fixture
def mock_ollama():
    """Mock Ollama LLM responses."""
    with patch('src.ai_radio. generation.llm_client.ollama') as mock:
        mock.generate.return_value = {"response": "Generated text"}
        yield mock


@pytest.fixture
def mock_pygame():
    """Mock pygame for audio tests."""
    with patch('src.ai_radio.playback.player.pygame') as mock:
        yield mock


# ============================================================
# Data Fixtures
# ============================================================

@pytest.fixture
def sample_song_metadata():
    """Create sample song metadata."""
    from src.ai_radio.library.metadata import SongMetadata
    return SongMetadata(
        file_path=Path("/music/test.mp3"),
        artist="Test Artist",
        title="Test Song",
        album="Test Album",
        year=1945,
        duration_seconds=180. 0,
    )


@pytest.fixture
def sample_catalog(sample_song_metadata):
    """Create a sample catalog with one song."""
    from src.ai_radio.library.catalog import SongCatalog, add_song
    catalog = SongCatalog()
    add_song(catalog, sample_song_metadata)
    return catalog
```

### Unit Test Template
```python
# tests/module/test_component.py
"""
Tests for [component]. 

Test naming convention:
    test_[method]_[scenario]_[expected_result]
    
Example:
    test_add_song_valid_input_increases_count
"""
import pytest
from src.ai_radio. module.component import function_to_test


class TestFunctionName:
    """Tests for function_name."""
    
    def test_returns_expected_type(self):
        """Function must return the expected type."""
        result = function_to_test()
        assert isinstance(result, ExpectedType)
    
    def test_handles_edge_case(self):
        """Function must handle edge case correctly."""
        result = function_to_test(edge_input)
        assert result == expected_output
    
    def test_raises_on_invalid_input(self):
        """Function must raise appropriate error on invalid input."""
        with pytest. raises(ExpectedError):
            function_to_test(invalid_input)


class TestAnotherScenario:
    """Tests for another scenario."""
    
    @pytest.fixture
    def setup_data(self):
        """Set up data for these tests."""
        return create_test_data()
    
    def test_with_setup(self, setup_data):
        """Test using the setup fixture."""
        result = function_to_test(setup_data)
        assert result is not None
```

### Integration Test Template
```python
# tests/integration/test_feature.py
"""
Integration tests for [feature].

These tests verify multiple components working together. 
They may require external services and take longer to run. 

Run with: pytest -m integration
"""
import pytest


@pytest.mark. integration
class TestFeatureIntegration: 
    """Integration tests for feature."""
    
    @pytest.fixture
    def configured_system(self):
        """Set up a fully configured system."""
        system = create_system()
        yield system
        system. cleanup()
    
    def test_end_to_end_flow(self, configured_system):
        """Test complete flow from input to output."""
        input_data = create_input()
        result = configured_system.process(input_data)
        assert result. is_valid
    
    @pytest.mark.slow
    def test_performance_under_load(self, configured_system):
        """Test system handles load correctly."""
        # This test may take a while
        for _ in range(100):
            configured_system.process(create_input())
        assert configured_system. is_healthy
```

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-22 | Initial comprehensive roadmap created |

---

## Quick Reference

### Command Cheat Sheet
```bash
# Run all tests
pytest tests/ -v

# Run specific phase tests
pytest tests/library/ -v
pytest tests/generation/ -v
pytest tests/playback/ -v

# Run integration tests
pytest tests/integration/ -v -m integration

# Run with coverage
pytest tests/ --cov=src/ai_radio --cov-report=html

# Scan music library
python scripts/scan_library. py /path/to/music

# Generate content (test)
python scripts/generate_content.py --intros --dj julie --limit 5

# Run station (dry run)
python -m ai_radio --dry-run

# Run station
python -m ai_radio
```

### Git Tag Summary
| Tag | Milestone |
|-----|-----------|
| `v0.1.0-foundation` | Phase 0 complete |
| `v0.2.0-library` | Phase 1 complete |
| `v0.3.0-generation` | Phase 2 complete |
| `v0.4.0-playback` | Phase 3 complete |
| `v0.5.0-dj` | Phase 4 complete |
| `v0.6.0-shows` | Phase 5 complete |
| `v0.7.0-services` | Phase 6 complete |
| `v0.8.0-integration` | Phase 7 complete |
| `v1.0.0-mvp` | MVP complete!  🎉 |

*This roadmap is your guide.  Follow it step by step, validate each checkpoint, and you will have a working AI Radio Station.*