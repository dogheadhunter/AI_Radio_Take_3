from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Optional
import threading
import time

from src.ai_radio.utils.errors import AudioFileError


class PlayerState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()
    COMPLETED = auto()


@dataclass
class AudioPlayer:
    """A minimal, test-friendly audio player abstraction.

    This implementation intentionally keeps logic simple so it can be unit
    tested without an actual audio backend. Real playback backends (pygame,
    vlc) can be integrated behind the same interface later.
    """

    state: PlayerState = PlayerState.STOPPED
    current_path: Optional[Path] = None
    _on_complete: Optional[Callable[[], None]] = None
    _position_seconds: float = 0.0

    def play(self, path: Path, on_complete: Optional[Callable[[], None]] = None):
        if not path.exists():
            raise AudioFileError(f"Audio file not found: {path}")
        self.current_path = path
        self._on_complete = on_complete
        self.state = PlayerState.PLAYING
        self._position_seconds = 0.0

    def stop(self):
        self.state = PlayerState.STOPPED
        self._on_complete = None

    def _simulate_complete(self):
        """Test helper to simulate that playback finished."""
        self.state = PlayerState.COMPLETED
        if self._on_complete:
            # call callback and clear it to mimic one-shot behavior
            cb = self._on_complete
            self._on_complete = None
            cb()

    def is_playing(self) -> bool:
        return self.state == PlayerState.PLAYING

    def get_position(self) -> float:
        return self._position_seconds


# Real pygame-backed player
class PygameAudioPlayer(AudioPlayer):
    """A real audio player implementation using pygame.mixer.

    This class initializes the pygame mixer on first use and plays audio in a
    background thread so tests can wait for completion.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = threading.Event()
        self._pygame_available = False
        try:
            import pygame  # type: ignore
            pygame.mixer.init()
            self._pygame = pygame
            self._pygame_available = True
        except Exception:
            # Will remain unavailable; callers can detect this and skip real playback
            self._pygame_available = False

    def play(self, path: Path, on_complete: Optional[Callable[[], None]] = None):
        if not path.exists():
            raise AudioFileError(f"Audio file not found: {path}")
        if not self._pygame_available:
            raise AudioFileError("pygame is not available for real playback")

        self.current_path = path
        self._on_complete = on_complete
        self.state = PlayerState.PLAYING

        # Use music playback to handle common formats
        try:
            self._pygame.mixer.music.load(str(path))
            self._pygame.mixer.music.play()
        except Exception as exc:
            self.state = PlayerState.STOPPED
            raise AudioFileError(f"Playback error: {exc}") from exc

        # Start monitor thread
        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
        self._monitor_thread.start()

    def _monitor_playback(self):
        # Poll until playback ends
        while not self._stop_monitor.is_set():
            try:
                busy = self._pygame.mixer.music.get_busy()
            except Exception:
                busy = False
            if not busy:
                # playback finished
                self.state = PlayerState.COMPLETED
                if self._on_complete:
                    cb = self._on_complete
                    self._on_complete = None
                    cb()
                return
            time.sleep(0.05)

    def stop(self):
        if self._pygame_available:
            try:
                self._pygame.mixer.music.stop()
            except Exception:
                pass
        self._stop_monitor.set()
        self.state = PlayerState.STOPPED
        self._on_complete = None

    def is_playing(self) -> bool:
        if not self._pygame_available:
            return False
        try:
            return bool(self._pygame.mixer.music.get_busy())
        except Exception:
            return False

    def get_position(self) -> float:
        if not self._pygame_available:
            return super().get_position()
        try:
            ms = self._pygame.mixer.music.get_pos()
            return ms / 1000.0
        except Exception:
            return super().get_position()


# Factory

def create_audio_player(use_pygame: bool = False) -> AudioPlayer:
    if use_pygame:
        p = PygameAudioPlayer()
        if not p._pygame_available:
            raise RuntimeError("pygame is not available")
        return p
    return AudioPlayer()


# Convenience functions matching the planned API

def play_file(player: AudioPlayer, path: Path, on_complete: Optional[Callable[[], None]] = None):
    player.play(path, on_complete=on_complete)


def stop_playback(player: AudioPlayer):
    player.stop()


def is_playing(player: AudioPlayer) -> bool:
    return player.is_playing()


def get_current_position(player: AudioPlayer) -> float:
    return player.get_position()
