# Phase 1 Overview

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
