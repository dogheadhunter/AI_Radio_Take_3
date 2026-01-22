"""
Scan music library and build catalog.

Usage: python scripts/scan_library.py /path/to/music
"""
import argparse
from pathlib import Path
import sys

# allow running from repository root (add repo root so `src` package is importable)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_radio.library.scanner import scan_library
from src.ai_radio.library.catalog import SongCatalog, add_song, save_catalog
from src.ai_radio.config import CATALOG_FILE


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan music library")
    parser.add_argument("music_path", type=Path, help="Path to music directory")
    args = parser.parse_args()

    print(f"Scanning: {args.music_path}")
    print("-" * 50)

    result = scan_library(args.music_path)

    print(f"Total files found: {result.total_files}")
    print(f"Successfully read: {len(result.songs)}")
    print(f"Failed: {len(result.failed_files)}")

    if result.failed_files:
        print("\nFailed files:")
        for path, error in result.failed_files[:10]:
            print(f"  {path}: {error}")
        if len(result.failed_files) > 10:
            print(f"  ... and {len(result.failed_files) - 10} more")

    # Build catalog
    catalog = SongCatalog()
    for song in result.songs:
        add_song(catalog, song)

    # Save
    save_catalog(catalog, CATALOG_FILE)
    print(f"\nCatalog saved to: {CATALOG_FILE}")
    print(f"Total songs in catalog: {len(catalog)}")


if __name__ == "__main__":
    main()
