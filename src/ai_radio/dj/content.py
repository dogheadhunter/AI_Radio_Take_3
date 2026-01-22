from pathlib import Path
from typing import Optional, List
from random import choice


class ContentSelector:
    def __init__(self, content_dir: Path):
        self.content_dir = Path(content_dir)
        self._used = {}  # song_id -> set(paths)

    def _find_intros(self, song_id: str, dj: str) -> List[Path]:
        candidates = []
        if not self.content_dir.exists():
            return candidates

        # Look for files containing song_id and dj in their name (case-insensitive)
        pattern = f"*{song_id.lower()}*{dj.lower()}*"
        for p in self.content_dir.rglob("*"):
            if p.is_file():
                name = p.name.lower()
                if song_id.lower() in name and dj.lower() in name:
                    candidates.append(p)
        # Fallback: any file for DJ
        if not candidates:
            for p in self.content_dir.rglob("*"):
                if p.is_file() and dj.lower() in p.name.lower():
                    candidates.append(p)
        return candidates


def get_intro_for_song(selector: ContentSelector, song_id: str, dj: str) -> Optional[Path]:
    intros = selector._find_intros(song_id, dj)
    if not intros:
        return None

    used = selector._used.setdefault(song_id, set())
    unused = [p for p in intros if str(p) not in used]

    pick = choice(unused) if unused else choice(intros)
    return pick


def mark_intro_used(selector: ContentSelector, intro: Path):
    # Mark intro as used for its song if we can infer a song_id from the name
    # use the filename as a key to simplify tracking
    key = intro.name
    used = selector._used.setdefault(key, set())
    used.add(str(intro))


def get_time_announcement(selector: ContentSelector, dj: str, time) -> Optional[Path]:
    # Look for files with hour in name (e.g., time_14_julie.mp3)
    hour = getattr(time, "hour", None)
    if hour is None:
        return None

    for p in selector.content_dir.rglob("*"):
        if p.is_file() and dj.lower() in p.name.lower() and str(hour) in p.name:
            return p

    # Do not fallback to generic time files; if a specific hour is not present return None
    return None


def get_weather_announcement(selector: ContentSelector, dj: str) -> Optional[Path]:
    for p in selector.content_dir.rglob("*"):
        if p.is_file() and dj.lower() in p.name.lower() and "weather" in p.name.lower():
            return p
    return None