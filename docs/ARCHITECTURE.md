# AI Radio Architecture

This document describes the refactored architecture of the AI Radio generation pipeline after the modular refactoring completed in January 2026.

## Overview

The AI Radio system generates DJ scripts and audio for a 24/7 radio station with two distinct DJ personalities. The pipeline has been refactored from a monolithic ~1,400 line script into a modular, testable architecture.

## Architecture Principles

1. **Separation of Concerns**: Core utilities, pipeline stages, and CLI are cleanly separated
2. **Testability**: All modules have comprehensive mock tests (390+ tests)
3. **Maintainability**: Small, focused modules instead of one large file
4. **Reusability**: Core utilities can be used across different contexts

## Directory Structure

```
src/ai_radio/
├── core/                    # Core utilities (NEW)
│   ├── __init__.py
│   ├── checkpoint.py       # Pipeline state management
│   ├── paths.py           # Path construction utilities
│   └── sanitizer.py       # Text sanitization & validation
│
├── stages/                  # Pipeline stages (NEW)
│   ├── __init__.py
│   ├── generate.py        # Stage 1: Generate scripts
│   ├── audit.py           # Stage 2: Audit quality
│   ├── regenerate.py      # Stage 3: Fix failed scripts
│   ├── audio.py           # Stage 4: Generate audio files
│   └── utils.py           # Shared stage utilities
│
├── generation/             # Generation backend (existing)
│   ├── pipeline.py
│   ├── auditor.py
│   ├── llm_client.py
│   ├── tts_client.py
│   └── prompts_v2.py
│
└── ... (other modules)

scripts/
└── generate_with_audit.py  # CLI dispatcher (292 lines, was 1,449)

tests/
├── core/                   # Core module tests (NEW)
│   ├── test_checkpoint.py  # 11 tests
│   ├── test_paths.py       # 15 tests
│   └── test_sanitizer.py   # 27 tests
│
├── stages/                 # Stage tests (NEW)
│   └── test_utils.py       # 12 tests
│
└── scripts/
    └── test_generate_with_audit.py  # 2 tests (updated)
```

## Module Responsibilities

### Core Modules (`src/ai_radio/core/`)

#### `checkpoint.py`
- **Purpose**: Manages pipeline state for resume capability
- **Key Class**: `PipelineCheckpoint`
- **Responsibilities**:
  - Save/load pipeline state to JSON
  - Track stage completion status
  - Enable resume from interruption
  - Store progress metrics

#### `paths.py`
- **Purpose**: Centralized path construction for all content types
- **Key Functions**:
  - `get_script_path()` - Script file paths
  - `get_audio_path()` - Audio file paths
  - `get_audit_path()` - Audit result paths
  - Variants for time/weather announcements
- **Responsibilities**:
  - Consistent filename sanitization
  - Directory structure enforcement
  - Path generation for all content types

#### `sanitizer.py`
- **Purpose**: Text sanitization and validation for TTS
- **Key Functions**:
  - `sanitize_script()` - Remove meta-commentary, fix encoding
  - `truncate_after_song_intro()` - Prevent rambling intros
  - `validate_time_announcement()` - Rule-based validation
  - `validate_weather_announcement()` - Rule-based validation
- **Responsibilities**:
  - Clean text for TTS compatibility
  - Remove forbidden content (years, meta-text, etc.)
  - Validate script appropriateness

### Stage Modules (`src/ai_radio/stages/`)

#### `generate.py`
- **Purpose**: Stage 1 - Generate text scripts
- **Key Function**: `stage_generate()`
- **Responsibilities**:
  - Generate intros, outros, time announcements, weather
  - Apply sanitization and validation
  - Save scripts to disk
  - Skip existing scripts
  - Track progress in checkpoint

#### `audit.py`
- **Purpose**: Stage 2 - Audit script quality
- **Key Function**: `stage_audit()`
- **Responsibilities**:
  - Audit all generated scripts with LLM auditor
  - Save audit results (passed/failed)
  - Track pass/fail statistics
  - Support test mode with fake auditor

#### `regenerate.py`
- **Purpose**: Stage 3 - Fix failed scripts with feedback
- **Key Function**: `stage_regenerate()`
- **Responsibilities**:
  - Find all failed audit results
  - Regenerate with audit feedback
  - Re-audit regenerated scripts
  - Move successful regenerations to passed
  - Retry with escalating feedback (up to 5 attempts)

#### `audio.py`
- **Purpose**: Stage 4 - Generate audio from passed scripts
- **Key Function**: `stage_audio()`
- **Responsibilities**:
  - Generate WAV files from all passed scripts
  - Use appropriate voice for each DJ
  - Skip existing audio files
  - Track audio generation progress

#### `utils.py`
- **Purpose**: Shared utilities for stages
- **Key Functions/Classes**:
  - `load_catalog_songs()` - Load and filter song catalog
  - `get_lyrics_for_song()` - Retrieve lyrics if available
  - `FakeAuditorClient` - Mock auditor for testing
- **Responsibilities**:
  - Catalog data loading
  - Test mode support
  - Shared helper functions

### CLI Dispatcher (`scripts/generate_with_audit.py`)

- **Size**: 292 lines (reduced from 1,449 lines - 80% reduction)
- **Purpose**: Command-line interface and pipeline orchestration
- **Responsibilities**:
  - Parse command-line arguments
  - Initialize pipeline and checkpoint
  - Orchestrate stage execution
  - Handle resume mode
  - Manage test mode
- **Does NOT contain**: Stage logic, path utilities, sanitization (all extracted)

## Pipeline Flow

```
1. CLI Parsing (generate_with_audit.py)
   ↓
2. Checkpoint Initialization (core/checkpoint.py)
   ↓
3. Stage 1: Generate (stages/generate.py)
   - Uses: core/paths, core/sanitizer
   - Generates: Text scripts
   ↓
4. Stage 2: Audit (stages/audit.py)
   - Uses: core/paths
   - Generates: Audit results (passed/failed)
   ↓
5. Stage 3: Regenerate (stages/regenerate.py)
   - Uses: core/paths, core/sanitizer
   - Fixes: Failed scripts with feedback loop
   ↓
6. Stage 4: Audio (stages/audio.py)
   - Uses: core/paths
   - Generates: WAV audio files
```

## Content Types

The pipeline handles four content types:

1. **Song Intros** - DJ introductions for songs
2. **Song Outros** - DJ outros after songs
3. **Time Announcements** - Time checks (every 30 minutes, 48 slots/day)
4. **Weather Announcements** - Weather updates (6 AM, 12 PM, 5 PM)

## DJ Personalities

1. **Julie** - Warm, personal, Appalachian style (Fallout 76)
2. **Mr. New Vegas** - Smooth, romantic, polished (Fallout New Vegas)

## Testing Strategy

### Mock Tests (Primary)
- **Location**: `tests/core/`, `tests/stages/`
- **Coverage**: 390+ tests
- **Purpose**: Fast, deterministic testing without external services
- **No Requirements**: Ollama, TTS, or other services
- **Run with**: `pytest` or `TEST_MODE=mock pytest`

### Integration Tests (Secondary)
- **Purpose**: End-to-end validation with real services
- **Requirements**: Ollama + TTS services running
- **Run with**: `TEST_MODE=integration pytest`
- **Note**: Ask user before running

## Key Design Decisions

### Why Modular Stages?
1. **Testability**: Each stage can be tested in isolation
2. **Maintainability**: ~200-400 lines per module vs 1,400 line monolith
3. **Reusability**: Stages can be used independently
4. **Debuggability**: Easier to locate and fix issues
5. **Future API**: Clean interfaces for REST API wrapper

### Why Core Utilities?
1. **DRY Principle**: Path logic used by all stages
2. **Consistency**: Single source of truth for paths/sanitization
3. **Testing**: Core logic tested independently
4. **Migration Path**: Easy to extend for GUI/API

### Why Checkpoint System?
1. **Long-Running Tasks**: Pipeline can take hours for 600+ scripts
2. **Reliability**: Resume from interruption without losing work
3. **Observability**: Track progress metrics
4. **Debugging**: Know exactly which stage failed

## Future Extensions

With this modular architecture, future extensions are easier:

1. **REST API** - Wrap stages in API endpoints
2. **GUI** - Import stages into web interface
3. **Batch Processing** - Parallel execution of stages
4. **Alternative Backends** - Swap LLM/TTS providers
5. **Additional Content Types** - New stages for news, ads, etc.

## Migration Notes

### For Developers
- Old imports: `from scripts.generate_with_audit import PipelineCheckpoint`
- New imports: `from src.ai_radio.core.checkpoint import PipelineCheckpoint`

### For Scripts
- Main script still works with same CLI arguments
- All functionality preserved
- Resume capability unchanged
- Test mode still supported

## Performance

- **No Performance Impact**: Same execution time
- **Faster Development**: Smaller files easier to navigate
- **Faster Tests**: Mock tests run in <1 second

## Security

- No new security considerations
- Same audit process as before
- CodeQL validation recommended

## References

- Original issue: "Refactor: Split Generation Pipeline Script into Modular Stages"
- Baseline tag: `v1.0.0-phase6-baseline`
- Completion: January 2026
