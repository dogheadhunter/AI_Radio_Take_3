"""Playback package for AI Radio Station.

Provides a high-level API for audio playback, queue management, and a controller
that ties them together for continuous playback.
"""

from .player import AudioPlayer, PlayerState, play_file, stop_playback, is_playing, get_current_position
from .queue import PlaybackQueue, QueueItem, add_to_queue, insert_next, get_next, peek_next, clear_queue, get_queue_length
from .controller import PlaybackController, start_playback, pause_playback, resume_playback, skip_current, add_song_with_intro

__all__ = [
    "AudioPlayer",
    "PlayerState",
    "play_file",
    "stop_playback",
    "is_playing",
    "get_current_position",
    "PlaybackQueue",
    "QueueItem",
    "add_to_queue",
    "insert_next",
    "get_next",
    "peek_next",
    "clear_queue",
    "get_queue_length",
    "PlaybackController",
    "start_playback",
    "pause_playback",
    "resume_playback",
    "skip_current",
    "add_song_with_intro",
]
