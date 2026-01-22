# Checkpoint 1.1: Metadata Reader

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
