"""Music file metadata reading.

Uses mutagen library to extract ID3 tags from MP3 files.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from src.ai_radio.utils.errors import SongNotFoundError, MetadataError


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
    """Read metadata from an audio file.

    Args:
        file_path: Path to the audio file

    Returns:
        SongMetadata with extracted information

    Raises:
        SongNotFoundError: If file doesn't exist
        MetadataError:  If file can't be read as audio
    """
    if not file_path.exists():
        raise SongNotFoundError(f"File not found: {file_path}")

    # attempt to read tags first (ID3 tags can exist without valid MPEG frames)
    artist = None
    title = None
    album = None
    year = None
    duration = None

    try:
        tags = EasyID3(file_path)
    except ID3NoHeaderError:
        tags = {}
    except Exception:
        tags = {}

    if tags:
        artist = tags.get("artist", [None])[0]
        title = tags.get("title", [None])[0]
        album = tags.get("album", [None])[0]
        # year may be in 'date' or 'year' depending on tags
        year_raw = tags.get("date", tags.get("year", [None]))
        year = int(year_raw[0]) if year_raw and year_raw[0] and str(year_raw[0]).isdigit() else None

    # attempt to read audio info (duration), but don't fail if audio frames are absent
    try:
        audio = mutagen.File(file_path)
        if audio is not None and hasattr(audio, "info") and getattr(audio.info, "length", None) is not None:
            duration = float(audio.info.length)
    except Exception:
        # couldn't parse audio frames; it's okay if we have tags
        audio = None

    # If we have neither tags nor audio info, decide based on file extension.
    # Accept common audio extensions (e.g., .mp3) in general, but reject suspiciously small files
    if (not tags) and (audio is None):
        if file_path.suffix.lower() not in {".mp3", ".wav", ".flac", ".m4a"}:
            raise MetadataError(f"File is not a recognized audio file and has no tags: {file_path}")
        # If the file is very small, it's likely not a valid audio file
        try:
            size = file_path.stat().st_size
        except Exception:
            size = 0
        if size < 512:
            raise MetadataError(f"File appears too small to be valid audio: {file_path}")
        # else: allow and continue with fallbacks



    # Fallbacks for missing crucial tags
    if not title or title.strip() == "":
        title = file_path.stem
    if not artist or artist.strip() == "":
        artist = "Unknown"

    return SongMetadata(
        file_path=file_path,
        artist=artist,
        title=title,
        album=album,
        year=year,
        duration_seconds=duration,
    )
