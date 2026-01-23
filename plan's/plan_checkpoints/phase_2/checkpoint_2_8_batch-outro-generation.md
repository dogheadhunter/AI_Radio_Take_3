# Checkpoint 2.8: Batch Outro Generation

#### Checkpoint 2.8: Batch Song Outro Generation
**Generate DJ outro audio for all songs in catalog (similar to batch intro generation).**

## Overview
Generate outro commentary for each song in the catalog for each DJ personality. Outros play after the song finishes and provide closing commentary, teases for next song, or artist information.

## Tasks

### Task 1: Add Outro Prompt Template
- [x] Add `build_song_outro_prompt()` to `src/ai_radio/generation/prompts.py`
- [x] Include song metadata (title, artist, year, genre)
- [x] Add DJ personality context
- [x] Support variation templates for variety
- [x] Test prompt generation with different songs

### Task 2: Implement Single Outro Generation
- [x] Create `generate_song_outro()` function
- [x] Accept song_id, dj, song_metadata
- [x] Call LLM with outro prompt
- [x] Generate audio via TTS with DJ voice
- [x] Save to `data/generated/outros/<dj>/<song_id>/outro_<hash>.mp3`
- [x] Save metadata JSON (prompt, timestamp, song info)

### Task 3: Implement Batch Outro Generation
- [x] Create `generate_batch_outros()` function
- [x] Load catalog of all songs
- [x] Generate outros for each song × each DJ
- [x] Support `--resume` flag to skip existing files
- [x] Show progress bar (e.g., "Generated 342/700 outros")
- [x] Save generation log with errors

### Task 4: Add CLI Script
- [x] Extend `scripts/generate_content.py` with `--outros` flag
- [x] Support `--dj <name>` to generate for specific DJ
- [x] Support `--song <id>` to generate for specific song
- [x] Support `--resume` to continue interrupted generation
- [x] Support `--dry-run` to preview without generating

### Task 5: Testing
- [x] Unit test `build_song_outro_prompt()` with various songs
- [x] Unit test `generate_song_outro()` with mocked LLM/TTS
- [x] Integration test batch generation (small catalog)
- [x] Verify outro files exist and are valid audio
- [x] Test resume functionality

## Implementation Details

**File: `src/ai_radio/generation/prompts.py`**

Add outro prompt builder:

```python
def build_song_outro_prompt(song_metadata: dict, dj: str, variation: int = 0) -> str:
    """Build prompt for song outro commentary.
    
    Args:
        song_metadata: Dict with title, artist, year, genre, etc.
        dj: DJ personality name
        variation: Variation number for multiple outros per song
        
    Returns:
        Prompt string for LLM
    """
    title = song_metadata.get("title", "this song")
    artist = song_metadata.get("artist", "the artist")
    year = song_metadata.get("year", "")
    genre = song_metadata.get("genre", "")
    
    year_text = f" from {year}" if year else ""
    genre_text = f" {genre}" if genre else ""
    
    if dj == "julie":
        style = "warm, friendly, and enthusiastic"
        templates = [
            f"You just heard '{title}' by {artist}{year_text}. Comment briefly on what you loved about it.",
            f"That was {artist} with '{title}'{year_text}. Share a quick personal thought or fun fact.",
            f"Wrapping up '{title}' by {artist}. Give a warm closing and tease what's coming next.",
        ]
    elif dj == "mr_new_vegas":
        style = "smooth, romantic, and suave"
        templates = [
            f"And that, my friends, was '{title}' by the one and only {artist}{year_text}. A smooth transition commentary.",
            f"{artist}'s '{title}'{year_text}. Share an elegant observation about the performance.",
            f"As '{title}' by {artist} fades away, offer a romantic closing thought.",
        ]
    else:
        style = "professional"
        templates = [
            f"That was '{title}' by {artist}{year_text}.",
        ]
    
    template = templates[variation % len(templates)]
    
    prompt = (
        f"You are a {style} radio DJ. {template} "
        f"Keep it very brief (1-2 sentences max). Sound natural and conversational."
    )
    
    return prompt
```

**File: `src/ai_radio/generation/batch_outros.py`**

Create batch outro generation:

```python
"""Batch generation of song outros."""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from src.ai_radio.generation.llm import generate_text
from src.ai_radio.generation.tts import generate_audio
from src.ai_radio.generation.prompts import build_song_outro_prompt
from src.ai_radio.library.catalog import load_catalog

logger = logging.getLogger(__name__)


def generate_song_outro(
    song_id: str,
    song_metadata: Dict[str, Any],
    dj: str,
    output_dir: Path,
    variation: int = 0
) -> Optional[Path]:
    """Generate single outro for a song.
    
    Args:
        song_id: Song identifier
        song_metadata: Dict with song info
        dj: DJ personality name
        output_dir: Base directory for generated content
        variation: Variation number (for multiple outros)
        
    Returns:
        Path to generated audio file, or None on error
    """
    # Build prompt
    prompt = build_song_outro_prompt(song_metadata, dj, variation)
    
    # Generate text
    try:
        outro_text = generate_text(prompt)
    except Exception as e:
        logger.error(f"LLM error for {song_id}/{dj}: {e}")
        return None
    
    # Create unique filename from prompt hash
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
    
    # Determine voice based on DJ
    voice = "female" if dj == "julie" else "male"
    
    # Create output directory: data/generated/outros/<dj>/<song_id>/
    song_dir = output_dir / dj / song_id
    song_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate audio
    audio_path = song_dir / f"outro_{prompt_hash}.mp3"
    try:
        generate_audio(outro_text, audio_path, voice=voice)
    except Exception as e:
        logger.error(f"TTS error for {song_id}/{dj}: {e}")
        return None
    
    # Save metadata
    metadata = {
        "song_id": song_id,
        "dj": dj,
        "variation": variation,
        "prompt": prompt,
        "text": outro_text,
        "song_metadata": song_metadata,
        "generated_at": str(datetime.now()),
    }
    
    metadata_path = song_dir / f"outro_{prompt_hash}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Generated outro: {audio_path}")
    return audio_path


def generate_batch_outros(
    djs: list[str],
    catalog_path: Path,
    output_dir: Path,
    resume: bool = False,
    song_filter: Optional[str] = None
) -> Dict[str, int]:
    """Generate outros for all songs in catalog.
    
    Args:
        djs: List of DJ names to generate for
        catalog_path: Path to song catalog JSON
        output_dir: Base directory for generated content
        resume: Skip existing files
        song_filter: Optional song_id to generate only one song
        
    Returns:
        Dict with generation stats
    """
    catalog = load_catalog(catalog_path)
    songs = catalog.songs
    
    if song_filter:
        songs = [s for s in songs if s.id == song_filter]
    
    total = len(songs) * len(djs)
    generated = 0
    skipped = 0
    errors = 0
    
    logger.info(f"Generating {total} outros ({len(songs)} songs × {len(djs)} DJs)")
    
    for song in songs:
        song_metadata = {
            "title": song.title,
            "artist": song.artist,
            "year": getattr(song, "year", None),
            "genre": getattr(song, "genre", None),
        }
        
        for dj in djs:
            # Check if outro already exists
            song_dir = output_dir / dj / song.id
            if resume and song_dir.exists() and list(song_dir.glob("outro_*.mp3")):
                logger.debug(f"Skipping existing: {song.id}/{dj}")
                skipped += 1
                continue
            
            # Generate outro
            result = generate_song_outro(
                song_id=song.id,
                song_metadata=song_metadata,
                dj=dj,
                output_dir=output_dir,
                variation=0  # TODO: support multiple variations
            )
            
            if result:
                generated += 1
            else:
                errors += 1
            
            # Progress
            done = generated + skipped + errors
            pct = (done / total) * 100
            print(f"Progress: {done}/{total} ({pct:.1f}%) - Generated: {generated}, Skipped: {skipped}, Errors: {errors}", end="\r")
    
    print()  # New line after progress
    
    stats = {
        "total": total,
        "generated": generated,
        "skipped": skipped,
        "errors": errors,
    }
    
    logger.info(f"Batch outro generation complete: {stats}")
    return stats
```

**File: `scripts/generate_content.py`**

Add outro generation option:

```python
# Add to argument parser
parser.add_argument("--outros", action="store_true", help="Generate song outros")
parser.add_argument("--song", type=str, help="Generate for specific song ID only")

# Add to main logic
if args.outros:
    from src.ai_radio.generation.batch_outros import generate_batch_outros
    
    djs = ["julie", "mr_new_vegas"] if args.dj == "all" else [args.dj]
    output_dir = Path("data/generated/outros")
    catalog_path = Path("data/catalog.json")
    
    stats = generate_batch_outros(
        djs=djs,
        catalog_path=catalog_path,
        output_dir=output_dir,
        resume=args.resume,
        song_filter=args.song
    )
    
    print(f"\nOutro generation complete:")
    print(f"  Generated: {stats['generated']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
```

## Success Criteria

### Functionality
- [x] `build_song_outro_prompt()` produces DJ-appropriate prompts
- [x] `generate_song_outro()` creates audio + metadata files
- [x] `generate_batch_outros()` processes entire catalog
- [x] Resume mode skips existing files correctly
- [x] Progress tracking displays current status
- [x] Errors are logged but don't stop batch generation

### Quality
- [ ] Outro text is natural and on-brand for each DJ
- [ ] Audio quality matches intro quality
- [ ] File naming is consistent and includes variation support
- [ ] Metadata includes all relevant information

### Testing
- [ ] Unit tests pass for prompt generation
- [ ] Integration tests pass for single outro generation
- [ ] Batch generation completes without crashes
- [ ] Resume functionality verified
- [ ] Generated files are valid MP3s

## Validation Commands

```bash
# Generate outros for one song (test)
python scripts/generate_content.py --outros --song "Artie_Shaw-A_Room_With_a_View" --dj julie

# Generate all outros for Julie
python scripts/generate_content.py --outros --dj julie

# Generate for all DJs
python scripts/generate_content.py --outros --dj all

# Resume interrupted generation
python scripts/generate_content.py --outros --dj all --resume

# Dry run (test without generating)
python scripts/generate_content.py --outros --dj julie --dry-run

# Verify generated files
python -c "
from pathlib import Path
outro_dir = Path('data/generated/outros')
julie_outros = list(outro_dir.glob('julie/*/outro_*.mp3'))
print(f'Julie outros: {len(julie_outros)}')
vegas_outros = list(outro_dir.glob('mr_new_vegas/*/outro_*.mp3'))
print(f'Mr. New Vegas outros: {len(vegas_outros)}')
"

# Run unit tests
.venv/Scripts/pytest tests/test_generation_outros.py -v
```

## Anti-Regression Tests

```python
# tests/test_generation_outros.py

import pytest
from pathlib import Path
from src.ai_radio.generation.prompts import build_song_outro_prompt
from src.ai_radio.generation.batch_outros import generate_song_outro


def test_outro_prompt_includes_song_info():
    """Outro prompt should include song and artist."""
    song_meta = {"title": "Test Song", "artist": "Test Artist", "year": "1940"}
    prompt = build_song_outro_prompt(song_meta, "julie")
    
    assert "Test Song" in prompt
    assert "Test Artist" in prompt


def test_outro_prompt_varies_by_dj():
    """Different DJs should have different prompt styles."""
    song_meta = {"title": "Test Song", "artist": "Test Artist"}
    
    julie_prompt = build_song_outro_prompt(song_meta, "julie")
    vegas_prompt = build_song_outro_prompt(song_meta, "mr_new_vegas")
    
    assert julie_prompt != vegas_prompt


def test_generate_outro_creates_files(tmp_path, mock_llm, mock_tts):
    """Should create audio and metadata files."""
    song_meta = {"title": "Test", "artist": "Artist"}
    
    result = generate_song_outro(
        song_id="test_song",
        song_metadata=song_meta,
        dj="julie",
        output_dir=tmp_path,
        variation=0
    )
    
    assert result is not None
    assert result.exists()
    assert result.suffix == ".mp3"
    
    # Metadata should also exist
    metadata_file = result.with_suffix(".json")
    assert metadata_file.exists()


def test_batch_generation_resume_skips_existing(tmp_path, mock_llm, mock_tts):
    """Resume mode should skip existing files."""
    from src.ai_radio.generation.batch_outros import generate_batch_outros
    
    # Create fake catalog
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text('{"songs": [{"id": "song1", "title": "Test", "artist": "Artist"}]}')
    
    # First run
    stats1 = generate_batch_outros(
        djs=["julie"],
        catalog_path=catalog_path,
        output_dir=tmp_path / "outros",
        resume=False
    )
    
    # Second run with resume
    stats2 = generate_batch_outros(
        djs=["julie"],
        catalog_path=catalog_path,
        output_dir=tmp_path / "outros",
        resume=True
    )
    
    assert stats1["generated"] == 1
    assert stats2["generated"] == 0
    assert stats2["skipped"] == 1
```

## Git Commit

```bash
git add src/ai_radio/generation/prompts.py
git add src/ai_radio/generation/batch_outros.py
git add scripts/generate_content.py
git add tests/test_generation_outros.py
git commit -m "feat(generation): add batch song outro generation

- Add build_song_outro_prompt() with DJ-specific templates
- Implement generate_song_outro() for single outro generation
- Add generate_batch_outros() for full catalog processing
- Support resume mode to skip existing files
- Add CLI flags to generate_content.py script
- Include progress tracking and error handling
- Add comprehensive tests for outro generation
"
```

## Dependencies
- **Requires**: Checkpoint 2.1 (LLM Client), 2.3 (TTS Client), 2.4 (Generation Pipeline)
- **Enhances**: Checkpoint 4.3 (Content Selector) will use generated outros
- **Similar to**: Checkpoint 2.1 (Batch Intro Generation) - same pattern

## Notes
- Outros are typically shorter than intros (1-2 sentences vs 2-3)
- File structure: `data/generated/outros/<dj>/<song_id>/outro_<hash>.mp3`
- Variation support allows multiple outros per song (set variation=0,1,2...)
- Metadata JSON includes prompt hash for reproducibility
- Consider generating 2-3 variations per song for variety
- Fallback: if LLM/TTS fails, log error but continue batch generation
