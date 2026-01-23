import pytest
from src.ai_radio.station.display import (
    StationDisplay,
    format_status,
    format_now_playing,
    format_next_up,
)
from src.ai_radio.station.controller import StationStatus, StationState


class TestFormatStatus:
    def test_includes_state(self):
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Test Song",
            current_dj="Julie",
            next_up="Next Song",
            uptime_seconds=3600,
            songs_played=10,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "PLAYING" in formatted or "Playing" in formatted

    def test_includes_current_song(self):
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Bing Crosby - White Christmas",
            current_dj="Julie",
            next_up=None,
            uptime_seconds=0,
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "Bing Crosby" in formatted
        assert "White Christmas" in formatted

    def test_includes_dj_name(self):
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Test",
            current_dj="Mr. New Vegas",
            next_up=None,
            uptime_seconds=0,
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "Mr. New Vegas" in formatted or "Vegas" in formatted

    def test_includes_uptime(self):
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Test",
            current_dj="Julie",
            next_up=None,
            uptime_seconds=7200,
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "2" in formatted and ("hour" in formatted.lower() or "h" in formatted)


class TestDisplayOutput:
    def test_format_now_playing_shows_song(self):
        output = format_now_playing("Bing Crosby", "White Christmas")
        assert "Bing Crosby" in output
        assert "White Christmas" in output

    def test_format_next_up_shows_upcoming(self):
        output = format_next_up("Frank Sinatra - Fly Me to the Moon")
        assert "Frank Sinatra" in output

    def test_format_next_up_handles_none(self):
        output = format_next_up(None)
        assert output is not None


def test_display_update_changes():
    display = StationDisplay()
    status1 = StationStatus(
        state=StationState.PLAYING,
        current_song="Song A",
        current_dj="Julie",
        next_up=None,
        uptime_seconds=0,
        songs_played=0,
        errors_count=0,
    )
    status2 = StationStatus(
        state=StationState.PLAYING,
        current_song="Song B",
        current_dj="Julie",
        next_up=None,
        uptime_seconds=0,
        songs_played=1,
        errors_count=0,
    )

    display.update(status1)
    assert display.last_status is not None
    display.update(status2)
    assert display.last_status.current_song == "Song B"
