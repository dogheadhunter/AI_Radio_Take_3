# Checkpoint 1.5: Library Integration Script

#### Checkpoint 1.5: Library Integration Script
**Create a script to scan your actual music library.**

**Tasks:**
1. Create `scripts/scan_library. py`
2. Scan your music directory
3. Build and save the catalog
4. Report statistics

**File: `scripts/scan_library.py`**
```python
"""
Scan music library and build catalog. 

Usage: python scripts/scan_library. py /path/to/music
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent. parent / "src"))

from ai_radio.library.scanner import scan_library
from ai_radio. library.catalog import SongCatalog, add_song, save_catalog
from ai_radio. config import CATALOG_FILE


def main():
    parser = argparse.ArgumentParser(description="Scan music library")
    parser.add_argument("music_path", type=Path, help="Path to music directory")
    args = parser.parse_args()
    
    print(f"Scanning:  {args.music_path}")
    print("-" * 50)
    
    result = scan_library(args.music_path)
    
    print(f"Total files found: {result.total_files}")
    print(f"Successfully read: {len(result.songs)}")
    print(f"Failed:  {len(result. failed_files)}")
    
    if result.failed_files:
        print("\nFailed files:")
        for path, error in result. failed_files[: 10]: 
            print(f"  {path}: {error}")
        if len(result. failed_files) > 10:
            print(f"  ... and {len(result.failed_files) - 10} more")
    
    # Build catalog
    catalog = SongCatalog()
    for song in result.songs:
        add_song(catalog, song)
    
    # Save
    save_catalog(catalog, CATALOG_FILE)
    print(f"\nCatalog saved to:  {CATALOG_FILE}")
    print(f"Total songs in catalog: {len(catalog)}")


if __name__ == "__main__":
    main()
```

**Success Criteria:**
- [ ] Script runs on your actual music directory
- [ ] `data/catalog.json` is created with your songs
- [ ] Report shows reasonable success/failure counts

**Validation:**
```bash
# Human runs:
python scripts/scan_library. py "C:/path/to/your/music"

# Human verifies: 
cat data/catalog.json | python -m json.tool | head -50
# Should see your actual songs
```

**Git Commit:** `feat(scripts): add library scan script`
