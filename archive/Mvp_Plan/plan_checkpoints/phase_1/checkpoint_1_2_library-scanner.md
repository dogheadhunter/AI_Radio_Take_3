# Checkpoint 1.2: Library Scanner

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
- [x] All `test_scanner.py` tests pass
- [x] Can scan your actual music directory
- [x] Reports count of successful and failed files

**Status:** Completed on 2026-01-22 — scanner implemented, tested, and validated against the local `music/` directory.


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
