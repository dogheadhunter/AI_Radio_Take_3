# AI Radio

A modular Python pipeline for generating DJ scripts and audio for a 24/7 AI-powered radio station with distinct DJ personalities. Features LLM-powered script generation, TTS audio synthesis, and quality auditing with feedback loops.

> 📖 **For detailed architecture documentation, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)**

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Required Services

AI Radio requires two external services for content generation:

| Service | Port | Purpose |
|---------|------|---------|
| **Ollama** | 11434 | LLM for script generation |
| **Chatterbox** | 3000 | TTS for audio synthesis |

```bash
# Start Ollama
ollama serve

# Start Chatterbox TTS
python dev/chatterbox_server.py
```

### 3. Generate Content

```bash
# Generate with full pipeline (generate → audit → regenerate → audio)
python scripts/generate_with_audit.py --intros --dj all

# Generate scripts only (skip audio)
python scripts/generate_with_audit.py --intros --dj julie --skip-audio

# Resume interrupted pipeline
python scripts/generate_with_audit.py --intros --dj all --resume
```

## Project Architecture

The pipeline uses a modular architecture with clean separation of concerns:

```
src/ai_radio/
├── core/               # Core utilities
│   ├── checkpoint.py   # Pipeline state management
│   ├── paths.py        # Path construction
│   └── sanitizer.py    # Text sanitization & validation
│
├── stages/             # Pipeline stages
│   ├── generate.py     # Stage 1: Generate scripts
│   ├── audit.py        # Stage 2: Audit quality
│   ├── regenerate.py   # Stage 3: Fix failed scripts
│   └── audio.py        # Stage 4: Generate audio
│
├── cherry_picker.py    # 🆕 Script batch selection (standalone)
│
└── generation/         # Backend services
    ├── pipeline.py     # Generation orchestration
    ├── llm_client.py   # Ollama client
    ├── tts_client.py   # TTS client
    └── prompts_v2.py   # Prompt templates
```

**Full architecture details**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## CLI Reference

### Main Generation Script

```bash
python scripts/generate_with_audit.py [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--intros` | Generate song introduction scripts |
| `--outros` | Generate song outro scripts |
| `--time` | Generate time announcements (48 slots/day) |
| `--weather` | Generate weather announcements |
| `--dj {julie,mr_new_vegas,all}` | Select DJ personality |
| `--skip-audio` | Skip TTS audio generation |
| `--resume` | Resume from checkpoint |
| `--test` | Use mock services for testing (no Ollama/TTS required) |

### Examples

```bash
# Full pipeline for all DJs
python scripts/generate_with_audit.py --intros --outros --dj all

# Quick test with mock services
python scripts/generate_with_audit.py --intros --dj julie --test --skip-audio

# Generate specific content type
python scripts/generate_with_audit.py --time --dj all --skip-audio
python scripts/generate_with_audit.py --weather --dj all --skip-audio
```

## DJ Personalities

| DJ | Style | Era |
|----|-------|-----|
| **Julie** | Warm, personal, Appalachian | Fallout 76 aesthetic |
| **Mr. New Vegas** | Smooth, romantic, polished | Fallout New Vegas aesthetic |

## Content Types

| Type | Count | Description |
|------|-------|-------------|
| Song Intros | 264 | 132 songs × 2 DJs |
| Song Outros | 264 | 132 songs × 2 DJs |
| Time Announcements | 96 | 48 time slots × 2 DJs |
| Weather Reports | 6 | 3 conditions × 2 DJs |
| **Total** | **630** | |

## Cherry Picker (NEW)

The **Cherry Picker** module provides intelligent script selection from multiple versions (e.g., original + regenerations). Instead of using "last-pass-wins" logic, it evaluates candidates using configurable guidelines to select the best broadcast-appropriate script.

### Features

- **Guideline-based selection**: Clarity, era/style compliance, creativity, conciseness, TTS safety, novelty
- **Configurable weights**: Adjust importance of each criterion
- **Audit integration**: Uses existing audit results as baseline
- **Forced picks**: Support for manual overrides
- **Detailed rankings**: Full rationale for each candidate's score

### Usage Example

```python
from pathlib import Path
from src.ai_radio.cherry_picker import CherryPicker, SelectionGuidelines

# Setup
picker = CherryPicker()
guidelines = SelectionGuidelines(
    require_audit_pass=True,
    style_weight=2.0,          # Emphasize DJ personality
    tts_safety_weight=1.5      # Prioritize pronunciation
)

# Select best from batch
result = picker.pick_best(
    script_paths=[
        Path("data/generated/intros/julie/song_123/julie_0.txt"),  # Original
        Path("data/generated/intros/julie/song_123/julie_1.txt"),  # Regen v1
        Path("data/generated/intros/julie/song_123/julie_2.txt"),  # Regen v2
    ],
    audit_results={...},  # Audit results dict
    guidelines=guidelines,
    dj="julie"
)

print(f"Winner: {result.winner_path}")
print(f"Rationale: {result.selection_rationale}")

# View full rankings
for ranking in result.rankings:
    print(f"  Rank {ranking.rank}: {ranking.path.name} - Score {ranking.overall_score:.2f}")
    print(f"    {ranking.rationale}")
```

### Design Notes

- **Standalone module**: Not yet integrated into pipeline stages (future extension point)
- **Extensible**: Add new scoring criteria by extending `_score_*` methods
- **Replaces "last-pass-wins"**: Alternative to simple "use latest regeneration" logic
- **27 comprehensive tests**: Full test coverage for all features and edge cases

**Architecture**: The module follows the same patterns as `core/` utilities, designed for eventual integration into `stages/regenerate.py` or as a new pipeline stage.

## Testing

This project uses a **dual testing approach** for reliability:

```bash
# Fast mock tests (default, no services needed)
pytest                           # or: make test

# Integration tests (requires Ollama + TTS)
TEST_MODE=integration pytest     # or: make test-integration

# Test just cherry picker
pytest tests/cherry_picker/      # 27 tests, <1 second
```

**Testing documentation**: [`tests/TESTING_MODES.md`](tests/TESTING_MODES.md)

## Documentation Index

| Document | Description |
|----------|-------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **System architecture and design** |
| [`docs/LLM_CONTEXT.md`](docs/LLM_CONTEXT.md) | LLM-optimized context document |
| [`tests/TESTING_MODES.md`](tests/TESTING_MODES.md) | Testing strategy and modes |
| [`docs/gui/REVIEW_GUI.md`](docs/gui/REVIEW_GUI.md) | Review GUI (optional, Streamlit) |

## Directory Structure

```
AI_Radio_Take_3/
├── src/ai_radio/       # Main package (modular architecture)
│   ├── core/           # Core utilities (checkpoint, paths, sanitizer)
│   ├── stages/         # Pipeline stages (generate, audit, regen, audio)
│   └── generation/     # LLM/TTS clients and prompts
├── scripts/            # CLI entry points
├── tests/              # Test suite (390+ tests)
├── data/               # Generated content and audit results
├── docs/               # Documentation
└── archive/            # Historical documentation
```

## Development

### VS Code Debug

Open the workspace in VS Code. Use the `Run and Debug` view and pick `Python: Debug Tests` to run pytest with the debugger attached.

### Services Check

```bash
# Check Ollama (LLM)
curl http://localhost:11434/api/tags

# Check Chatterbox (TTS)  
curl http://localhost:3000/health
```

### Key Source Files

| File | Purpose |
|------|---------|
| `scripts/generate_with_audit.py` | Main CLI dispatcher (292 lines) |
| `src/ai_radio/core/checkpoint.py` | Pipeline state management |
| `src/ai_radio/stages/generate.py` | Script generation stage |
| `src/ai_radio/generation/prompts_v2.py` | Prompt templates for DJs |

## License

Part of the AI Radio Take 3 project.
