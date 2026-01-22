"""Tests for show player."""
import pytest
from unittest.mock import Mock
from src.ai_radio.shows.show_player import (
    ShowPlayer,
    play_show_block,
    ShowBlockResult,
)


class TestShowBlock:
    """Test show block playback."""

    def test_plays_intro_before_show(self, mock_playback, show_with_intro):
        """DJ intro must play before show."""
        player = ShowPlayer(playback=mock_playback)

        played_items = []
        mock_playback.on_item_started = lambda item: played_items.append(item.item_type)

        play_show_block(player, show_with_intro)

        assert played_items[0] == "show_intro"
        assert played_items[1] == "show"

    def test_plays_outro_after_show(self, mock_playback, show_with_intro):
        """DJ commentary must play after show."""
        player = ShowPlayer(playback=mock_playback)

        played_items = []
        mock_playback.on_item_started = lambda item:  played_items.append(item.item_type)

        play_show_block(player, show_with_intro)

        assert played_items[-1] == "show_outro"

    def test_returns_result_with_duration(self, mock_playback, show_with_intro):
        """Must return result with total duration."""
        player = ShowPlayer(playback=mock_playback)
        result = play_show_block(player, show_with_intro)

        assert isinstance(result, ShowBlockResult)
        assert result.duration_seconds > 0

    def test_resumes_music_after_show(self, show_with_intro):
        """Playback should resume music after the show block finishes."""
        resumed = {"called": False}

        class MockPlayback:
            def __init__(self):
                self.on_item_started = None

            def resume_music(self):
                resumed["called"] = True

        player = ShowPlayer(playback=MockPlayback())
        play_show_block(player, show_with_intro)

        assert resumed["called"] is True
