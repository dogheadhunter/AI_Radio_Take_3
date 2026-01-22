# Checkpoint 1.3: Song Catalog

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
