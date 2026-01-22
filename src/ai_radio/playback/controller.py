from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from src.ai_radio.playback.player import AudioPlayer, play_file, stop_playback
from src.ai_radio.playback.queue import (
    PlaybackQueue,
    QueueItem,
    add_to_queue,
    insert_next,
    get_next,
    get_queue_length,
)


@dataclass
class PlaybackController:
    queue: PlaybackQueue = None
    player: AudioPlayer = None
    is_playing: bool = False
    current_item: Optional[QueueItem] = None

    # Hooks that callers can set
    on_item_started: Optional[Callable[[QueueItem], None]] = None
    on_item_finished: Optional[Callable[[QueueItem], None]] = None

    def __post_init__(self):
        if self.queue is None:
            self.queue = PlaybackQueue()
        if self.player is None:
            self.player = AudioPlayer()

    @property
    def queue_length(self) -> int:
        return get_queue_length(self.queue)

    def _play_item(self, item: QueueItem):
        self.current_item = item
        if self.on_item_started:
            try:
                self.on_item_started(item)
            except Exception:
                pass

        # Start playback and set completion callback
        play_file(self.player, item.path, on_complete=self._on_playback_complete)
        self.is_playing = True

    def _on_playback_complete(self):
        finished = self.current_item
        if self.on_item_finished and finished is not None:
            try:
                self.on_item_finished(finished)
            except Exception:
                pass

        self.is_playing = False
        self.current_item = None

        # Auto-advance
        next_item = get_next(self.queue)
        if next_item:
            self._play_item(next_item)


# Top-level controller functions

def start_playback(controller: PlaybackController):
    if controller.is_playing:
        return
    next_item = get_next(controller.queue)
    if not next_item:
        return
    controller._play_item(next_item)


def pause_playback(controller: PlaybackController):
    # Stop playback but keep current_item so resume can continue it
    stop_playback(controller.player)
    controller.is_playing = False


def resume_playback(controller: PlaybackController):
    # Resume the current item if present
    if controller.current_item:
        controller._play_item(controller.current_item)


def skip_current(controller: PlaybackController):
    # Stop current and immediately play next
    stop_playback(controller.player)
    controller.is_playing = False
    next_item = get_next(controller.queue)
    if next_item:
        controller._play_item(next_item)


def add_song_with_intro(controller: PlaybackController, song_path: Path, intro_path: Path, song_id: str):
    song = QueueItem(path=song_path, item_type="song", song_id=song_id)
    intro = QueueItem(path=intro_path, item_type="intro", song_id=song_id)

    add_to_queue(controller.queue, song)
    # place intro before the song
    insert_next(controller.queue, intro)
