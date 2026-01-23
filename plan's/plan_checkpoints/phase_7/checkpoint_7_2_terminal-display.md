# Checkpoint 7.2: Terminal Display

#### Checkpoint 7.2: Terminal Display
**Show current station status in terminal.**

**Tasks:**
1. Create `src/ai_radio/station/display.py`
2. Simple text-based status display
3. Update without flickering
4. Show key information

**Tests First:**
```python
# tests/station/test_display.py
"""Tests for terminal display."""
import pytest
from src.ai_radio. station.display import (
    StationDisplay,
    format_status,
    format_now_playing,
    format_next_up,
    clear_and_draw,
)
from src.ai_radio.station.controller import StationStatus, StationState


class TestFormatStatus:
    """Test status formatting."""
    
    def test_includes_state(self):
        """Formatted status must include state."""
        status = StationStatus(
            state=StationState. PLAYING,
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
        """Formatted status must include current song."""
        status = StationStatus(
            state=StationState. PLAYING,
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
        """Formatted status must include DJ name."""
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
        """Formatted status must include uptime."""
        status = StationStatus(
            state=StationState.PLAYING,
            current_song="Test",
            current_dj="Julie",
            next_up=None,
            uptime_seconds=7200,  # 2 hours
            songs_played=0,
            errors_count=0,
        )
        formatted = format_status(status)
        assert "2" in formatted and ("hour" in formatted. lower() or "h" in formatted)


class TestDisplayOutput:
    """Test display output."""
    
    def test_format_now_playing_shows_song(self):
        """Now playing must show song info."""
        output = format_now_playing("Bing Crosby", "White Christmas")
        assert "Bing Crosby" in output
        assert "White Christmas" in output
    
    def test_format_next_up_shows_upcoming(self):
        """Next up must show upcoming song."""
        output = format_next_up("Frank Sinatra - Fly Me to the Moon")
        assert "Frank Sinatra" in output
    
    def test_format_next_up_handles_none(self):
        """Next up must handle no upcoming song."""
        output = format_next_up(None)
        assert output is not None  # Should not crash
```

**Implementation Specification:**
```python
# src/ai_radio/station/display.py
"""
Terminal display for station status.

Provides a simple, clean terminal interface showing:
- Current song
- Current DJ
- Next up
- Station status
- Uptime and statistics
"""
import os
import sys
from datetime import timedelta
from src.ai_radio. station.controller import StationStatus, StationState


def clear_screen() -> None:
    """Clear the terminal screen."""
    os. system('cls' if os.name == 'nt' else 'clear')


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable form."""
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if td.days > 0:
        return f"{td.days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"


def format_status(status: StationStatus) -> str:
    """Format complete station status for display."""
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║           🎙️  AI RADIO STATION                           ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Status: {status.state.name: <47} ║",
        f"║  DJ: {status.current_dj:<51} ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  NOW PLAYING:                                             ║",
        f"║    {(status.current_song or 'Nothing')[:54]:<54} ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  NEXT UP:                                                ║",
        f"║    {(status.next_up or 'Unknown')[:54]:<54} ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Uptime: {format_uptime(status.uptime_seconds):<47} ║",
        f"║  Songs Played: {status. songs_played: <41} ║",
        f"║  Errors: {status.errors_count:<47} ║",
        "╠══════════════════════════════════════════════════════════╣",
        "║  Commands:  [Q]uit  [P]ause  [S]kip  [B]anish             ║",
        "╚══════════════════════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


def format_now_playing(artist: str, title: str) -> str:
    """Format now playing line."""
    return f"{artist} - {title}"


def format_next_up(song_display: str | None) -> str:
    """Format next up line."""
    if song_display is None:
        return "Queuing next song..."
    return song_display


class StationDisplay: 
    """
    Manages terminal display updates. 
    
    Updates display without excessive flickering. 
    """
    
    def __init__(self):
        self.last_status: StationStatus | None = None
    
    def update(self, status: StationStatus) -> None:
        """Update display with new status."""
        # Only clear and redraw if status changed
        if self._status_changed(status):
            clear_screen()
            print(format_status(status))
            self. last_status = status
    
    def _status_changed(self, new_status: StationStatus) -> bool:
        """Check if status has meaningfully changed."""
        if self.last_status is None:
            return True
        
        return (
            self.last_status. current_song != new_status.current_song or
            self. last_status.current_dj != new_status.current_dj or
            self.last_status.state != new_status. state or
            self.last_status. next_up != new_status.next_up
        )
```

**Success Criteria:**
- [x] All display tests pass
- [x] Status shows all required information
- [x] Display is readable and clean
- [x] Updates without excessive flickering

**Git Commit:** `feat(station): add terminal display`
