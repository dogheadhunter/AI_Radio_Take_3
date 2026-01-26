# AI Radio - LLM Context Document

> **Purpose**: This document is optimized for LLM context windows. Load this at session start to understand the codebase quickly.
> **Last Updated**: January 2026 (post-modularization refactor)

## Project Summary

AI Radio is a **modular Python pipeline** for generating DJ scripts and audio. Two LLM models work together:
- **Writer Model** (Stheno 8B): Generates DJ scripts
- **Auditor Model** (Dolphin-Llama3): Validates script quality

The system generates content for two DJ personalities and four content types.

## Architecture Overview

```
Pipeline Flow:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Generate   │→ │    Audit    │→ │ Regenerate  │→ │    Audio    │
│  Scripts    │  │   Quality   │  │  w/Feedback │  │    Files    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
     Stage 1          Stage 2          Stage 3          Stage 4
```

## Key Locations

| What | Where |
|------|-------|
| **Main CLI** | `scripts/generate_with_audit.py` |
| **Core modules** | `src/ai_radio/core/` |
| **Pipeline stages** | `src/ai_radio/stages/` |
| **Generation backend** | `src/ai_radio/generation/` |
| **Prompts** | `src/ai_radio/generation/prompts_v2.py` |
| **Tests** | `tests/core/`, `tests/stages/` |
| **Generated content** | `data/generated/{type}/{dj}/` |
| **Audit results** | `data/audit/{dj}/{passed|failed}/` |

## Module Responsibilities

### Core Modules (`src/ai_radio/core/`)

| Module | Purpose |
|--------|---------|
| `checkpoint.py` | Pipeline state management, resume capability |
| `paths.py` | Centralized path construction for all content |
| `sanitizer.py` | Text sanitization and TTS validation |

### Stage Modules (`src/ai_radio/stages/`)

| Module | Purpose |
|--------|---------|
| `generate.py` | Stage 1: Generate text scripts |
| `audit.py` | Stage 2: Audit quality with LLM |
| `regenerate.py` | Stage 3: Fix failed scripts with feedback |
| `audio.py` | Stage 4: Generate WAV audio files |
| `utils.py` | Shared utilities, catalog loading |

## Two DJs

| DJ | Voice Style | Era Reference |
|----|-------------|---------------|
| Julie | Warm, personal, Appalachian | Fallout 76 |
| Mr. New Vegas | Smooth, romantic, polished | Fallout New Vegas |

## Content Types

| Type | Count | Notes |
|------|-------|-------|
| Song Intros | 264 | 132 songs × 2 DJs |
| Song Outros | 264 | 132 songs × 2 DJs |
| Time Announcements | 96 | 48 slots/day × 2 DJs |
| Weather Reports | 6 | 3 conditions × 2 DJs |
| **Total** | **630** | 99.5% audit pass rate achieved |

## Essential Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run tests (mock mode, no services)
pytest

# Generate content
python scripts/generate_with_audit.py --intros --dj all
python scripts/generate_with_audit.py --intros --dj julie --skip-audio
python scripts/generate_with_audit.py --intros --dj julie --test  # mock mode

# Resume interrupted pipeline
python scripts/generate_with_audit.py --intros --dj all --resume

# Required services (for real generation)
ollama serve                        # Port 11434
python dev/chatterbox_server.py     # Port 3000
```

## Import Patterns

```python
# Core modules
from src.ai_radio.core.checkpoint import PipelineCheckpoint
from src.ai_radio.core.paths import get_script_path, get_audio_path
from src.ai_radio.core.sanitizer import sanitize_script, validate_time_announcement

# Stage modules
from src.ai_radio.stages.generate import stage_generate
from src.ai_radio.stages.audit import stage_audit
from src.ai_radio.stages.regenerate import stage_regenerate
from src.ai_radio.stages.audio import stage_audio

# Generation backend
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.llm_client import LLMClient
from src.ai_radio.generation.tts_client import TTSClient
```

## Testing Modes

| Mode | Command | Services Needed |
|------|---------|-----------------|
| Mock (default) | `pytest` | None |
| Integration | `TEST_MODE=integration pytest` | Ollama + TTS |

## Quality Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Initial pass rate | >50% | ✅ |
| Final pass rate | >95% | 99.5% |
| Character recognition | >90% | ✅ |
| Era appropriateness | >95% | ✅ |

## File Naming Conventions

```
data/generated/{content_type}/{dj}/{item_id}/
├── {dj}_0.txt          # Original script
├── {dj}_0.wav          # Original audio
├── {dj}_1.txt          # Regenerated v1
├── {dj}_1.wav          # Regenerated v1 audio
└── review_status.json  # Review metadata
```

## Key Design Decisions

1. **Modular stages**: ~200-400 lines per module vs 1,400 line monolith
2. **Core utilities**: DRY principle for paths/sanitization
3. **Checkpoint system**: Resume from interruption (pipelines can take hours)
4. **Dual testing**: Fast mock tests + integration tests
5. **Feedback loop**: Failed scripts regenerated with audit feedback

## What NOT to Reference

These are **archived/obsolete**:
- `Script_Improvement_Plan/` (moved to `archive/`)
- Old CLI patterns using `generate_content.py` for main generation
- Monolithic pipeline references before modularization

## Session Protocol

1. Load this document
2. Check `docs/ARCHITECTURE.md` for detailed architecture
3. Run `pytest` to verify environment
4. Make changes in appropriate modules
5. Test with `pytest tests/core/` or `pytest tests/stages/`
6. Commit with descriptive messages
