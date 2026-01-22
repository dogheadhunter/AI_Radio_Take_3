"""Tests for audio player."""
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.ai_radio.playback.player import AudioPlayer, play_file, stop_playback, is_playing, get_current_position, PlayerState
from src.ai_radio.playback.player import AudioPlayer
from src.ai_radio.utils.errors import AudioFileError


class TestAudioPlayer:
    def test_play_changes_state_to_playing(self, sample_audio):
        player = AudioPlayer()
        play_file(player, sample_audio)
        assert player.state == PlayerState.PLAYING

    def test_stop_changes_state_to_stopped(self, sample_audio):
        player = AudioPlayer()
        play_file(player, sample_audio)
        stop_playback(player)
        assert player.state == PlayerState.STOPPED

    def test_is_playing_returns_correct_state(self, sample_audio):
        player = AudioPlayer()
        assert not is_playing(player)
        play_file(player, sample_audio)
        assert is_playing(player)

    def test_raises_for_nonexistent_file(self):
        player = AudioPlayer()
        with pytest.raises(AudioFileError):
            play_file(player, Path("/nonexistent/file.mp3"))

    def test_calls_completion_callback(self, sample_audio):
        player = AudioPlayer()
        callback = Mock()
        play_file(player, sample_audio, on_complete=callback)

        # Simulate playback completion
        player._simulate_complete()

        callback.assert_called_once()


class TestPlayerIntegration:
    """Integration tests with real audio.

    Run with: pytest -m integration
    """

    @pytest.mark.integration
    def test_plays_real_audio(self, sample_audio):
        player = AudioPlayer()
        play_file(player, sample_audio)

        # Wait a moment
        import time

        time.sleep(0.01)

        assert is_playing(player) or player.state == PlayerState.COMPLETED
        stop_playback(player)
