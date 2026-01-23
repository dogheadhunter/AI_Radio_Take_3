# 📋 PHASE 4: Lyrics Integration

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Parse lyrics files and integrate them into script generation |
| **Duration** | 1-2 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 2 complete (prompts support lyrics context) |
| **Outputs** | `lyrics_parser.py`, lyrics integration in pipeline |

---

## Why This Phase Matters

Lyrics provide rich context that can make intros more meaningful:
- Reference specific themes or emotions
- Connect songs to listener experiences
- Provide interesting facts about the song content

---

## Checkpoints

### Checkpoint 4.1: Lyrics File Parser

**Goal:** Parse the lyrics files into usable data

**Lyrics File Format (from your example):**
```
Title: A Good Man Is Hard to Find
Artist: Cass Daley
Provider: lrclib
Synced: False
Instrumental: False
--------------------------------------------------------------------------------

[lyrics text]
```

**Tasks:**
1. Create parser for this format
2. Extract metadata (title, artist)
3. Extract lyrics text
4. Handle edge cases (instrumental, missing lyrics)
5. Match lyrics files to songs in catalog

**File: `src/ai_radio/generation/lyrics_parser.py`**

```python
"""
Lyrics file parser for AI Radio.

Parses lyrics files and matches them to songs in the catalog.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict
import re


@dataclass
class LyricsData:
    """Parsed lyrics data."""
    title: str
    artist: str
    lyrics: str
    is_instrumental: bool
    provider: Optional[str] = None
    file_path: Optional[Path] = None


def parse_lyrics_file(file_path: Path) -> Optional[LyricsData]:
    """
    Parse a lyrics file into structured data.
    
    Returns None if file cannot be parsed.
    """
    pass


def extract_lyrics_context(lyrics: LyricsData, max_length: int = 200) -> str:
    """
    Extract a brief context summary from lyrics.
    
    This is what gets passed to the prompt - not the full lyrics,
    but a summary of themes, mood, or notable lines.
    """
    pass


def match_lyrics_to_catalog(
    lyrics_dir: Path,
    catalog: 'SongCatalog',
) -> Dict[str, LyricsData]:
    """
    Match lyrics files to songs in the catalog.
    
    Returns dict mapping song_id -> LyricsData
    """
    pass
```

**Test File:** `tests/generation/test_lyrics_parser.py`

**Success Criteria:**
- [ ] Parser extracts title, artist, lyrics correctly
- [ ] Handles instrumental files (no lyrics text)
- [ ] Handles malformed files gracefully
- [ ] Matches to catalog by title/artist
- [ ] Tests pass

---

### Checkpoint 4.2: Lyrics Context Extraction

**Goal:** Create meaningful context summaries from lyrics

**Tasks:**
1. Identify themes/mood from lyrics
2. Extract notable/quotable lines (without reproducing full lyrics)
3. Create brief summaries for prompt context
4. Handle instrumental songs

**Context Types:**

| Type | Description | Example |
|------|-------------|---------|
| Mood | Overall emotional tone | "A melancholic love ballad" |
| Theme | What the song is about | "About finding true love" |
| Notable Element | Something interesting | "Features a memorable chorus about..." |

**Context Format for Prompt:**
```
This song is about [theme]. The mood is [mood]. [Optional: Notable element].
```

**Example:**
```
This song is about the difficulty of finding a good romantic partner. 
The mood is playful and humorous despite the serious topic.
```

**Success Criteria:**
- [ ] Context summaries are 1-3 sentences
- [ ] Summaries capture essence without reproducing lyrics
- [ ] Instrumental songs get appropriate context ("An instrumental piece")
- [ ] Context is usable in prompts

---

### Checkpoint 4.3: Pipeline Integration

**Goal:** Integrate lyrics into the generation pipeline

**Tasks:**
1. Load lyrics data when starting generation
2. Match lyrics to each song before generating
3. Pass lyrics context to prompt builder
4. Handle missing lyrics gracefully

**Integration Point:**
```python
# In generation pipeline
def generate_intro_with_lyrics(song, dj, lyrics_data):
    lyrics_context = None
    if song.id in lyrics_data:
        lyrics_context = extract_lyrics_context(lyrics_data[song.id])
    
    prompt = build_song_intro_prompt_v2(
        dj=dj,
        artist=song.artist,
        title=song.title,
        lyrics_context=lyrics_context,  # NEW
    )
    
    return generate_text(prompt)
```

**Success Criteria:**
- [ ] Lyrics loaded at pipeline start
- [ ] Matching works for most songs
- [ ] Missing lyrics don't break generation
- [ ] Generated intros reference lyrics when appropriate

---

## Phase 4 Gate: Lyrics Integration Complete

### All Criteria Must Pass

| Criterion | Validation Method |
|-----------|-------------------|
| Parser works | Tests pass |
| Context extraction works | Manual review of 10 summaries |
| Pipeline integration complete | Generation uses lyrics when available |
| Graceful degradation | Songs without lyrics still generate |

### Required Artifacts

1. `src/ai_radio/generation/lyrics_parser.py`
2. `tests/generation/test_lyrics_parser.py`
3. Updated `prompts_v2.py` (lyrics_context parameter)

**Git Commit:** `feat(generation): add lyrics integration`

**Git Tag:** `v0.9.4-lyrics`

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Phase 4 specification created |

---
---
---