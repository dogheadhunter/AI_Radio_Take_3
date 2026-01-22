"""Persistent song catalog storage.

Provides a minimal in-memory catalog and JSON persistence helpers used by the
application and tested in `tests/library/test_catalog.py`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional, List
import json

from src.ai_radio.library.metadata import SongMetadata
from src.ai_radio.utils.errors import MusicLibraryError


@dataclass
class SongRecord:
    """Serializable song record extracted from SongMetadata."""
    id: int
    file_path: str
    artist: str
    title: str
    album: Optional[str]
    year: Optional[int]
    duration_seconds: Optional[float]


class SongCatalog:
    """Simple in-memory catalog for songs.

    Songs are stored in an internal dict mapping integer IDs to SongMetadata
    representations.
    """

    def __init__(self) -> None:
        self._songs: Dict[int, SongMetadata] = {}
        self._next_id = 1

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._songs)

    def add(self, song: SongMetadata) -> int:
        """Add a song and return its assigned ID."""
        song_id = self._next_id
        self._next_id += 1
        self._songs[song_id] = song
        return song_id

    def get(self, song_id: int) -> SongMetadata:
        """Retrieve a song by ID, raise KeyError if missing."""
        return self._songs[song_id]

    def all(self) -> List[SongMetadata]:
        """Return list of all SongMetadata objects."""
        return list(self._songs.values())


# Convenience functions used by tests & application

def add_song(catalog: SongCatalog, song: SongMetadata) -> int:
    return catalog.add(song)


def get_song(catalog: SongCatalog, song_id: int) -> SongMetadata:
    return catalog.get(song_id)


def save_catalog(catalog: SongCatalog, path: Path) -> None:
    """Persist the catalog to a JSON file with human-readable formatting.

    The file structure is:
    {
      "songs": [ {song record}, ... ]
    }
    """
    try:
        payload = {
            "songs": [
                {
                    "id": song_id,
                    "file_path": str(song.file_path),
                    "artist": song.artist,
                    "title": song.title,
                    "album": song.album,
                    "year": song.year,
                    "duration_seconds": song.duration_seconds,
                }
                for song_id, song in _iter_with_ids(catalog)
            ]
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception as exc:  # pragma: no cover - defensive
        raise MusicLibraryError(f"Failed to save catalog: {exc}")


def load_catalog(path: Path) -> SongCatalog:
    """Load a catalog from a JSON file previously saved with `save_catalog`."""
    if not path.exists():
        raise MusicLibraryError(f"Catalog file does not exist: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        raise MusicLibraryError(f"Failed to load catalog: {exc}")

    catalog = SongCatalog()
    songs = data.get("songs", [])
    for rec in songs:
        # create SongMetadata instances; file_path is stored as string
        song_meta = SongMetadata(
            file_path=Path(rec.get("file_path")),
            artist=rec.get("artist", "Unknown"),
            title=rec.get("title", ""),
            album=rec.get("album"),
            year=rec.get("year"),
            duration_seconds=rec.get("duration_seconds"),
        )
        # ensure the assigned IDs are preserved by adding in order and
        # incrementing _next_id appropriately
        assigned_id = rec.get("id")
        if isinstance(assigned_id, int) and assigned_id >= catalog._next_id:
            catalog._next_id = assigned_id + 1
        # manually insert with the original id
        catalog._songs[assigned_id if isinstance(assigned_id, int) else catalog._next_id] = song_meta

    return catalog


def _iter_with_ids(catalog: SongCatalog):
    """Yield (id, SongMetadata) pairs in insertion order."""
    # The internal dict keeps insertion order in Python 3.7+
    for song_id, song in catalog._songs.items():
        yield song_id, song
