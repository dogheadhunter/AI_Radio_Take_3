# Checkpoint 4.1: Lyrics File Parser

## Status
**NOT STARTED** ⬜

## Goal
Parse the lyrics files into usable data structures with proper metadata extraction and error handling.

## Tasks

### 1. Understand Lyrics File Format
- [ ] Review existing lyrics files in `music_with_lyrics/`
- [ ] Document the format structure
- [ ] Identify edge cases (instrumental, missing metadata, etc.)
- [ ] Note any format variations

### 2. Design Data Structure
- [ ] Define `LyricsData` dataclass
- [ ] Include title, artist, lyrics text
- [ ] Include metadata flags (instrumental, synced, etc.)
- [ ] Add file path reference

### 3. Implement Parser
- [ ] Create `parse_lyrics_file()` function
- [ ] Extract metadata from header
- [ ] Extract lyrics text
- [ ] Handle separator line
- [ ] Return structured data

### 4. Handle Edge Cases
- [ ] Instrumental songs (no lyrics text)
- [ ] Missing metadata fields
- [ ] Malformed files
- [ ] Encoding issues
- [ ] Empty or corrupt files

### 5. Implement Matching
- [ ] Create `match_lyrics_to_catalog()` function
- [ ] Match by title and artist
- [ ] Handle case variations
- [ ] Handle artist name variations
- [ ] Handle "feat." and other artist modifiers

### 6. Write Tests
- [ ] Test normal lyrics file parsing
- [ ] Test instrumental file handling
- [ ] Test malformed file handling
- [ ] Test matching to catalog
- [ ] Test edge cases

## Lyrics File Format

### Example Format
```
Title: A Good Man Is Hard to Find
Artist: Cass Daley
Provider: lrclib
Synced: False
Instrumental: False
--------------------------------------------------------------------------------

[Verse 1]
A good man is hard to find
You always get the other kind...
```

### Metadata Fields
- **Title** - Song title (required)
- **Artist** - Artist name (required)
- **Provider** - Lyrics source (optional)
- **Synced** - Whether lyrics are time-synced (optional)
- **Instrumental** - Whether song is instrumental (optional)

### Separator
- 80 dashes: `--------------------------------------------------------------------------------`
- Separates metadata from lyrics text

## Code Structure

### File: `src/ai_radio/generation/lyrics_parser.py`

```python
"""
Lyrics file parser for AI Radio.

Parses lyrics files from music_with_lyrics/ directory and matches them
to songs in the catalog.
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
    is_instrumental: bool = False
    is_synced: bool = False
    provider: Optional[str] = None
    file_path: Optional[Path] = None
    
    def has_lyrics(self) -> bool:
        """Check if lyrics text is available."""
        return bool(self.lyrics) and not self.is_instrumental


def parse_lyrics_file(file_path: Path) -> Optional[LyricsData]:
    """
    Parse a lyrics file into structured data.
    
    Args:
        file_path: Path to the lyrics file
        
    Returns:
        LyricsData object if successful, None if parsing fails
        
    Raises:
        None - errors are logged and None is returned
    """
    try:
        # Read file
        content = file_path.read_text(encoding='utf-8')
        
        # Split metadata and lyrics
        parts = content.split('---', 1)
        if len(parts) != 2:
            return None
            
        metadata_text, lyrics_text = parts
        
        # Parse metadata
        metadata = {}
        for line in metadata_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        # Extract required fields
        title = metadata.get('Title')
        artist = metadata.get('Artist')
        
        if not title or not artist:
            return None
        
        # Extract optional fields
        provider = metadata.get('Provider')
        is_synced = metadata.get('Synced', 'False').lower() == 'true'
        is_instrumental = metadata.get('Instrumental', 'False').lower() == 'true'
        
        # Clean lyrics text
        lyrics = lyrics_text.strip()
        
        return LyricsData(
            title=title,
            artist=artist,
            lyrics=lyrics,
            is_instrumental=is_instrumental,
            is_synced=is_synced,
            provider=provider,
            file_path=file_path,
        )
        
    except Exception as e:
        # Log error but don't raise
        print(f"Error parsing {file_path}: {e}")
        return None


def normalize_string(s: str) -> str:
    """Normalize string for matching (lowercase, remove punctuation)."""
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def match_artist(lyrics_artist: str, catalog_artist: str) -> bool:
    """
    Check if artist names match.
    
    Handles variations like:
    - Case differences
    - "feat.", "ft.", "featuring"
    - "The" prefix
    - Punctuation differences
    """
    # Normalize both
    lyrics_norm = normalize_string(lyrics_artist)
    catalog_norm = normalize_string(catalog_artist)
    
    # Direct match
    if lyrics_norm == catalog_norm:
        return True
    
    # Remove "the" prefix
    lyrics_no_the = lyrics_norm.replace('the ', '')
    catalog_no_the = catalog_norm.replace('the ', '')
    if lyrics_no_the == catalog_no_the:
        return True
    
    # Check if one contains the other (for feat./ft. cases)
    if lyrics_norm in catalog_norm or catalog_norm in lyrics_norm:
        return True
    
    return False


def match_lyrics_to_catalog(
    lyrics_dir: Path,
    catalog: 'SongCatalog',
) -> Dict[str, LyricsData]:
    """
    Match lyrics files to songs in the catalog.
    
    Args:
        lyrics_dir: Directory containing lyrics files
        catalog: Song catalog to match against
        
    Returns:
        Dictionary mapping song_id -> LyricsData
    """
    matches = {}
    unmatched = []
    
    # Parse all lyrics files
    lyrics_files = list(lyrics_dir.glob('*.txt'))
    
    for lyrics_file in lyrics_files:
        lyrics_data = parse_lyrics_file(lyrics_file)
        
        if not lyrics_data:
            continue
        
        # Try to find matching song in catalog
        matched = False
        
        for song in catalog.songs:
            # Normalize titles for comparison
            song_title_norm = normalize_string(song.title)
            lyrics_title_norm = normalize_string(lyrics_data.title)
            
            # Check title match
            title_match = song_title_norm == lyrics_title_norm
            
            # Check artist match
            artist_match = match_artist(lyrics_data.artist, song.artist)
            
            if title_match and artist_match:
                matches[song.id] = lyrics_data
                matched = True
                break
        
        if not matched:
            unmatched.append(lyrics_data)
    
    # Log statistics
    print(f"Matched {len(matches)} lyrics to catalog")
    print(f"Unmatched: {len(unmatched)} lyrics files")
    
    return matches
```

## Edge Cases to Handle

### 1. Instrumental Songs
- `Instrumental: True` in metadata
- Lyrics text may be empty or contain "Instrumental"
- Should not generate context from non-existent lyrics

### 2. Missing Metadata
- Some files may have incomplete metadata
- Parser should handle missing optional fields gracefully
- Required fields (title, artist) must be present

### 3. Malformed Files
- Separator line missing or wrong format
- Metadata format variations
- Encoding issues (UTF-8)
- File corruption

### 4. Matching Challenges
- Artist name variations ("The Beatles" vs "Beatles")
- Featured artists ("Song feat. Artist")
- Compilation albums (various artists)
- Punctuation differences ("Don't" vs "Dont")

## Test Cases

### Test File: `tests/generation/test_lyrics_parser.py`

```python
"""Tests for lyrics parser."""
import pytest
from pathlib import Path
from ai_radio.generation.lyrics_parser import (
    parse_lyrics_file,
    match_lyrics_to_catalog,
    normalize_string,
    match_artist,
)


def test_parse_normal_lyrics(tmp_path):
    """Test parsing a normal lyrics file."""
    lyrics_file = tmp_path / "test.txt"
    lyrics_file.write_text("""Title: Test Song
Artist: Test Artist
Provider: test
Synced: False
Instrumental: False
--------------------------------------------------------------------------------

[Verse 1]
Test lyrics here
More lyrics
""")
    
    result = parse_lyrics_file(lyrics_file)
    
    assert result is not None
    assert result.title == "Test Song"
    assert result.artist == "Test Artist"
    assert "Test lyrics here" in result.lyrics
    assert not result.is_instrumental


def test_parse_instrumental(tmp_path):
    """Test parsing instrumental file."""
    lyrics_file = tmp_path / "instrumental.txt"
    lyrics_file.write_text("""Title: Instrumental Song
Artist: Test Artist
Instrumental: True
--------------------------------------------------------------------------------

""")
    
    result = parse_lyrics_file(lyrics_file)
    
    assert result is not None
    assert result.is_instrumental
    assert not result.has_lyrics()


def test_parse_malformed_file(tmp_path):
    """Test handling malformed file."""
    lyrics_file = tmp_path / "malformed.txt"
    lyrics_file.write_text("Not a valid lyrics file")
    
    result = parse_lyrics_file(lyrics_file)
    
    assert result is None


def test_normalize_string():
    """Test string normalization."""
    assert normalize_string("The Beatles") == "the beatles"
    assert normalize_string("Don't Stop") == "dont stop"
    assert normalize_string("  Extra   Spaces  ") == "extra spaces"


def test_match_artist():
    """Test artist matching."""
    assert match_artist("The Beatles", "Beatles")
    assert match_artist("Artist feat. Someone", "Artist")
    assert match_artist("ARTIST", "artist")
    assert not match_artist("Completely Different", "Artist")
```

## Success Criteria

| Criterion | Validation Method | Status |
|-----------|-------------------|--------|
| Parser extracts title, artist, lyrics correctly | Unit tests | ⬜ |
| Handles instrumental files (no lyrics text) | Unit tests | ⬜ |
| Handles malformed files gracefully | Unit tests | ⬜ |
| Matches to catalog by title/artist | Integration test | ⬜ |
| Tests pass | `pytest tests/generation/test_lyrics_parser.py` | ⬜ |
| >90% of lyrics files parse successfully | Manual verification | ⬜ |
| >85% match to catalog | Manual verification | ⬜ |

## Next Steps
Once complete, proceed to Checkpoint 4.2 to implement lyrics context extraction.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 4 specification |
