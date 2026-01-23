import pytest
from unittest.mock import Mock
from src.ai_radio.station.commands import (
    CommandHandler,
    Command,
    parse_key,
    execute_command,
)


class TestParseKey:
    def test_q_is_quit(self):
        assert parse_key('q') == Command.QUIT
        assert parse_key('Q') == Command.QUIT

    def test_p_is_pause(self):
        assert parse_key('p') == Command.PAUSE
        assert parse_key('P') == Command.PAUSE

    def test_s_is_skip(self):
        assert parse_key('s') == Command.SKIP
        assert parse_key('S') == Command.SKIP

    def test_b_is_banish(self):
        assert parse_key('b') == Command.BANISH
        assert parse_key('B') == Command.BANISH

    def test_f_is_flag(self):
        assert parse_key('f') == Command.FLAG
        assert parse_key('F') == Command.FLAG

    def test_unknown_key_is_none(self):
        assert parse_key('x') is None
        assert parse_key('1') is None


class MockController:
    def __init__(self):
        self.stop = Mock()
        self.pause = Mock()
        self.resume = Mock()
        self.skip = Mock()
        self.banish_song = Mock()
        self.flag_intro = Mock()
        self.promote_song = Mock()
        self.is_playing = True
        self.current_song_id = None
        self.current_song_display = ""
        self.current_intro_path = None


@pytest.fixture
def mock_controller():
    return MockController()


class TestExecuteCommand:
    def test_quit_stops_station(self, mock_controller):
        execute_command(Command.QUIT, mock_controller)
        mock_controller.stop.assert_called_once()

    def test_pause_pauses_playback(self, mock_controller):
        mock_controller.is_playing = True
        execute_command(Command.PAUSE, mock_controller)
        mock_controller.pause.assert_called_once()

    def test_pause_resumes_if_not_playing(self, mock_controller):
        mock_controller.is_playing = False
        execute_command(Command.PAUSE, mock_controller)
        mock_controller.resume.assert_called_once()

    def test_skip_advances_song(self, mock_controller):
        execute_command(Command.SKIP, mock_controller)
        mock_controller.skip.assert_called_once()

    def test_banish_banishes_current_song(self, mock_controller):
        mock_controller.current_song_id = "song_123"
        mock_controller.current_song_display = "Artist - Song"
        execute_command(Command.BANISH, mock_controller)
        mock_controller.banish_song.assert_called_once_with("song_123")
        mock_controller.skip.assert_called()

    def test_flag_flags_current_intro(self, mock_controller):
        mock_controller.current_intro_path = "/path/to/intro.wav"
        execute_command(Command.FLAG, mock_controller)
        mock_controller.flag_intro.assert_called_once()
