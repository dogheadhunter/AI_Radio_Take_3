from dataclasses import dataclass
from datetime import datetime, timedelta


class ClockService:
    """Simple clock service. Allows injection of current time for testing."""

    def now(self) -> datetime:
        return datetime.now()


def is_announcement_time(clock: ClockService, when: datetime) -> bool:
    """Returns True for on-the-hour or half-hour announcements."""
    return when.minute in (0, 30) and when.second == 0


def get_next_announcement_time(clock: ClockService, when: datetime) -> datetime:
    """Return the next announcement datetime (next :00 or :30)."""
    if when.minute < 30:
        return when.replace(minute=30, second=0, microsecond=0)
    # >=30 -> next hour
    next_hour = (when + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return next_hour


def format_time_for_dj(when: datetime) -> str:
    """Return DJ-friendly formatting for a time.

    Examples: "2:30" or "2 o'clock" for on-the-hour.
    """
    hour_12 = when.hour if when.hour <= 12 else when.hour - 12
    if hour_12 == 0:
        hour_12 = 12

    if when.minute == 0:
        return f"{hour_12} o'clock"
    return f"{hour_12}:{when.minute:02d}"
