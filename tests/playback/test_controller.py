"""Tests for playback controller."""
from pathlib import Path

import pytest

from src.ai_radio.playback.controller import (
    PlaybackController,
    start_playback,
    pause_playback,
    resume_playback,
    skip_current,
    add_song_with_intro,
)
from src.ai_radio.playback.queue import QueueItem


class TestPlaybackController:
    def test_start_begins_playing(self, mock_queue_with_items):
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        assert controller.is_playing

    def test_auto_advances_to_next(self, mock_queue_with_items):
        controller = PlaybackController(queue=mock_queue_with_items)

        items_played = []
        controller.on_item_started = lambda item: items_played.append(item)

        start_playback(controller)

        # Simulate first item completing
        controller.player._simulate_complete()

        # After completing first, controller should auto-play next -> length 2 started
        assert len(items_played) == 2

    def test_skip_advances_to_next(self, mock_queue_with_items):
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)

        first_item = controller.current_item
        skip_current(controller)

        assert controller.current_item != first_item

    def test_pause_stops_without_advancing(self, mock_queue_with_items):
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)

        current = controller.current_item
        pause_playback(controller)

        assert not controller.is_playing
        assert controller.current_item == current

    def test_resume_continues_current(self, mock_queue_with_items):
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        pause_playback(controller)
        resume_playback(controller)

        assert controller.is_playing


class TestSongWithIntro:
    def test_adds_intro_then_song(self, tmp_path):
        controller = PlaybackController()

        add_song_with_intro(
            controller,
            song_path=tmp_path / "song.mp3",
            intro_path=tmp_path / "intro.wav",
            song_id="song_1",
        )

        # Should have 2 items in queue
        assert controller.queue_length == 2

    def test_intro_plays_first(self, mock_player, tmp_path):
        controller = PlaybackController()

        played = []
        controller.on_item_started = lambda item: played.append(item.item_type)

        add_song_with_intro(
            controller,
            song_path=tmp_path / "song.mp3",
            intro_path=tmp_path / "intro.wav",
            song_id="song_1",
        )

        # Create the actual files so playback won't raise
        (tmp_path / "song.mp3").write_bytes(b"\x00")
        (tmp_path / "intro.wav").write_bytes(b"\x00")

        start_playback(controller)
        # Finish intro
        controller.player._simulate_complete()

        assert played == ["intro", "song"]
