"""
Terminal display for station status.
"""
import os
import sys
from datetime import timedelta
from typing import Optional
from src.ai_radio.station.controller import StationStatus, StationState


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def format_uptime(seconds: float) -> str:
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
        f"║  Songs Played: {status.songs_played: <41} ║",
        f"║  Errors: {status.errors_count:<47} ║",
        "╠══════════════════════════════════════════════════════════╣",
        "║  Commands:  [Q]uit  [P]ause  [S]kip  [B]anish             ║",
        "╚══════════════════════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


def format_now_playing(artist: str, title: str) -> str:
    return f"{artist} - {title}"


def format_next_up(song_display: Optional[str]) -> str:
    if song_display is None:
        return "Queuing next song..."
    return song_display


class StationDisplay:
    def __init__(self):
        self.last_status: StationStatus | None = None

    def update(self, status: StationStatus) -> None:
        if self._status_changed(status):
            clear_screen()
            print(format_status(status))
            self.last_status = status

    def _status_changed(self, new_status: StationStatus) -> bool:
        if self.last_status is None:
            return True

        return (
            self.last_status.current_song != new_status.current_song or
            self.last_status.current_dj != new_status.current_dj or
            self.last_status.state != new_status.state or
            self.last_status.next_up != new_status.next_up
        )
