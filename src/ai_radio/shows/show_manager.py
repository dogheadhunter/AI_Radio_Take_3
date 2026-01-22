from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re


SUPPORTED_EPISODE_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}


@dataclass
class Episode:
    episode_number: int
    path: Path
    played: bool = False


@dataclass
class Show:
    name: str
    episodes: List[Episode] = field(default_factory=list)
    intro_path: Optional[Path] = None


class ShowManager:
    """Manage show library and playback state."""

    def __init__(self) -> None:
        self._shows: Dict[str, Show] = {}

    def add_show(self, show: Show) -> None:
        self._shows[show.name] = show

    def get_show(self, name: str) -> Optional[Show]:
        return self._shows.get(name)

    def all_shows(self) -> List[Show]:
        return list(self._shows.values())


# Helpers

_episode_re = re.compile(r"episode[_\- ]?(\d+)", re.I)
_number_re = re.compile(r"(\d+)")


def _parse_episode_number(name: str, fallback_index: int) -> int:
    m = _episode_re.search(name)
    if m:
        return int(m.group(1))
    m2 = _number_re.search(name)
    if m2:
        return int(m2.group(1))
    return fallback_index


def scan_shows(manager: ShowManager, shows_dir: Path) -> List[Show]:
    """Scan the directory for shows and return list of Show objects."""
    shows: List[Show] = []

    if not shows_dir.exists():
        return shows

    for child in sorted(shows_dir.iterdir()):
        if not child.is_dir():
            continue

        show_name = child.name
        show = Show(name=show_name)

        # find intro file if present
        for f in child.iterdir():
            if f.is_file() and f.suffix.lower() in SUPPORTED_EPISODE_EXTS and "intro" in f.stem.lower():
                show.intro_path = f
                break

        # episodes
        eps = []
        idx = 1
        for f in sorted(child.iterdir()):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED_EPISODE_EXTS:
                continue
            # skip intro (already handled)
            if show.intro_path and f == show.intro_path:
                continue

            num = _parse_episode_number(f.stem, idx)
            eps.append(Episode(episode_number=num, path=f))
            idx += 1

        # sort episodes by episode_number
        eps_sorted = sorted(eps, key=lambda e: e.episode_number)
        show.episodes = eps_sorted

        manager.add_show(show)
        shows.append(show)

    return shows


def get_next_episode(manager: ShowManager, show_name: str) -> Optional[Episode]:
    show = manager.get_show(show_name)
    if not show:
        return None

    # find first unplayed
    unplayed = [e for e in show.episodes if not e.played]
    if unplayed:
        return sorted(unplayed, key=lambda e: e.episode_number)[0]

    # if all played, reset and return first
    for e in show.episodes:
        e.played = False
    if show.episodes:
        return sorted(show.episodes, key=lambda e: e.episode_number)[0]

    return None


def mark_episode_played(manager: ShowManager, episode: Episode) -> None:
    episode.played = True
