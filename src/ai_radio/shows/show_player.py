from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.ai_radio.playback.queue import QueueItem


@dataclass
class ShowBlockResult:
    duration_seconds: float


@dataclass
class ShowPlayer:
    playback: Optional[object] = None


def play_show_block(player: ShowPlayer, show: object) -> ShowBlockResult:
    """Play a show block: intro -> show -> outro.

    This function simulates callbacks to the playback controller's
    `on_item_started` hook. It does not perform real audio playback.
    """

    played_count = 0

    # intro
    if getattr(show, "intro_path", None):
        intro_item = QueueItem(path=show.intro_path, item_type="show_intro")
        if getattr(player.playback, "on_item_started", None):
            player.playback.on_item_started(intro_item)
        played_count += 1

    # main show (play each episode sequentially)
    for ep in getattr(show, "episodes", []):
        show_item = QueueItem(path=ep.path, item_type="show")
        if getattr(player.playback, "on_item_started", None):
            player.playback.on_item_started(show_item)
        played_count += 1

    # outro (DJ commentary)
    outro_item = QueueItem(path=Path(""), item_type="show_outro")
    if getattr(player.playback, "on_item_started", None):
        player.playback.on_item_started(outro_item)
    played_count += 1

    # If playback has a resume hook, call it to return control to music
    if getattr(player.playback, "resume_music", None):
        try:
            player.playback.resume_music()
        except Exception:
            pass

    # Return a result with a positive duration (1s per item)
    return ShowBlockResult(duration_seconds=float(max(1, played_count)))
