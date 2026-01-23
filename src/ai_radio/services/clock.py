from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

FormatStyle = Literal["numeric", "written", "casual"]


class ClockService:
    """Simple clock service with timezone support. Allows injection of current time for testing."""

    def __init__(self, timezone: Optional[str] = None):
        self.timezone = self._get_timezone(timezone)

    def _get_timezone(self, tz_name: Optional[str]) -> Optional[ZoneInfo]:
        if tz_name is None:
            return None
        try:
            return ZoneInfo(tz_name)
        except Exception as e:
            logger.warning(f"Invalid timezone {tz_name}, using system timezone: {e}")
            return None

    def now(self) -> datetime:
        """Return timezone-aware current time (system timezone if none configured)."""
        if self.timezone is None:
            return datetime.now().astimezone()
        return datetime.now(self.timezone)

    def get_timezone_name(self) -> str:
        current = self.now()
        return current.tzname() or "UTC"


def is_announcement_time(clock: ClockService, when: datetime, window_seconds: int = 2) -> bool:
    """Returns True for on-the-hour or half-hour announcements within tolerance window.

    Args:
        clock: ClockService instance (for logging/timezone context)
        when: datetime to check
        window_seconds: tolerance window in seconds (0-N)
    """
    is_valid_minute = when.minute in (0, 30)
    is_valid_second = when.second <= window_seconds

    if is_valid_minute and is_valid_second:
        logger.debug(f"Announcement time detected: {when}")
        return True
    return False


def get_next_announcement_time(clock: ClockService, when: datetime) -> datetime:
    """Return the next announcement datetime (next :00 or :30)."""
    if when.minute < 30:
        return when.replace(minute=30, second=0, microsecond=0)
    # >=30 -> next hour
    next_hour = (when + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return next_hour


def format_time_for_dj(
    when: datetime,
    include_ampm: bool = True,
    style: FormatStyle = "numeric",
) -> str:
    """Return DJ-friendly formatting for a time.

    Args:
        when: Time to format
        include_ampm: Include AM/PM suffix
        style: Format style ("numeric", "written", "casual")

    Returns:
        Formatted time string
    """
    hour_12 = when.hour if when.hour <= 12 else when.hour - 12
    if hour_12 == 0:
        hour_12 = 12

    ampm = "AM" if when.hour < 12 else "PM"

    numbers = {
        1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
        7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"
    }

    if style == "numeric":
        if when.minute == 0:
            base = f"{hour_12} o'clock"
        else:
            base = f"{hour_12}:{when.minute:02d}"
        return f"{base} {ampm}" if include_ampm else base

    elif style == "written":
        hour_word = numbers.get(hour_12, str(hour_12))
        if when.minute == 0:
            base = f"{hour_word} o'clock"
        elif when.minute == 30:
            base = f"{hour_word} thirty"
        else:
            base = f"{hour_word} {when.minute:02d}"

        if include_ampm:
            period = "in the morning" if when.hour < 12 else "in the afternoon" if when.hour < 18 else "in the evening"
            return f"{base} {period}"
        return base

    elif style == "casual":
        hour_word = numbers.get(hour_12, str(hour_12))
        if when.minute == 0:
            return f"{hour_word} o'clock"
        elif when.minute == 30:
            return f"half past {hour_word}"
        else:
            return f"{hour_12}:{when.minute:02d}"

    return f"{hour_12}:{when.minute:02d}"


def get_current_timezone(clock: ClockService) -> str:
    """Get current timezone name for display."""
    return clock.get_timezone_name()