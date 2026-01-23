# Checkpoint 6.1a: Enhanced Clock Service

#### Checkpoint 6.1a: Enhanced Clock Service
**Add timezone awareness, AM/PM formatting, and improved scheduling to the clock service.**

## Overview
The current `ClockService` uses `datetime.now()` and formats times without AM/PM. This enhancement adds timezone support, improved formatting options, relaxed scheduling windows, and integrates formatted time into generation prompts.

## Tasks

### Task 1: Add Timezone Awareness to ClockService
- [ ] Add timezone configuration to `config.py` (default to system timezone)
- [ ] Update `ClockService.now()` to return timezone-aware datetime
- [ ] Add `get_current_timezone()` helper function
- [ ] Support both system timezone and configured timezone
- [ ] Add tests for timezone handling

### Task 2: Enhance Time Formatting
- [ ] Add `include_ampm` parameter to `format_time_for_dj()`
- [ ] Add `format_style` parameter ("numeric", "written", "casual")
- [ ] Support multiple format styles (e.g., "2:30 PM", "half past two", "two thirty in the afternoon")
- [ ] Add tests for all format variations

### Task 3: Relax Scheduling Window
- [ ] Update `is_announcement_time()` to accept seconds 0-2 (not just 0)
- [ ] Add configuration for scheduling window tolerance
- [ ] Add logging when announcement time is detected
- [ ] Add tests for window tolerance

### Task 4: Update Time Announcement Prompts
- [ ] Modify `build_time_announcement_prompt()` to accept hour and minute parameters
- [ ] Include formatted time string in prompt so LLM says correct time
- [ ] Add variation to prevent repetitive announcements
- [ ] Add tests for prompt generation

### Task 5: Integration Testing
- [ ] Test timezone conversions with mock times
- [ ] Test announcement scheduling with various time windows
- [ ] Test full flow: ClockService → format → prompt → generation
- [ ] Verify AM/PM is spoken correctly in generated audio

## Implementation Details

**File: `src/ai_radio/config.py`**

Add timezone configuration:

```python
# Time and timezone settings
TIME_ANNOUNCE_INTERVAL_MINUTES = 30
TIMEZONE = None  # None = system timezone, or "America/New_York", "UTC", etc.
ANNOUNCEMENT_WINDOW_SECONDS = 2  # Allow 0-2 seconds for scheduling tolerance
```

**File: `src/ai_radio/services/clock.py`**

Enhanced clock service:

```python
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
        """Initialize clock service.
        
        Args:
            timezone: Optional timezone string (e.g., "America/New_York"). 
                     None uses system timezone.
        """
        self.timezone = self._get_timezone(timezone)

    def _get_timezone(self, tz_name: Optional[str]) -> Optional[ZoneInfo]:
        """Get ZoneInfo object from timezone name."""
        if tz_name is None:
            return None  # Use system timezone
        try:
            return ZoneInfo(tz_name)
        except Exception as e:
            logger.warning(f"Invalid timezone {tz_name}, using system timezone: {e}")
            return None

    def now(self) -> datetime:
        """Get current time in configured timezone."""
        if self.timezone is None:
            return datetime.now().astimezone()  # System timezone
        return datetime.now(self.timezone)

    def get_timezone_name(self) -> str:
        """Get current timezone name for display."""
        current = self.now()
        return current.tzname() or "UTC"


def is_announcement_time(clock: ClockService, when: datetime, window_seconds: int = 2) -> bool:
    """Returns True for on-the-hour or half-hour announcements.
    
    Args:
        clock: ClockService instance
        when: Time to check
        window_seconds: Tolerance window (0-N seconds)
        
    Returns:
        True if within announcement window
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
    style: FormatStyle = "numeric"
) -> str:
    """Return DJ-friendly formatting for a time.

    Args:
        when: Time to format
        include_ampm: Include AM/PM suffix
        style: Format style ("numeric", "written", "casual")

    Returns:
        Formatted time string
    
    Examples:
        numeric: "2:30 PM" or "2 o'clock PM"
        written: "two thirty in the afternoon" or "two o'clock in the afternoon"
        casual: "half past two" or "two o'clock"
    """
    hour_12 = when.hour if when.hour <= 12 else when.hour - 12
    if hour_12 == 0:
        hour_12 = 12

    # Determine AM/PM
    ampm = "AM" if when.hour < 12 else "PM"
    
    # Written number mapping
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
    """Get current timezone name."""
    return clock.get_timezone_name()
```

**File: `src/ai_radio/generation/prompts.py`**

Update time announcement prompt:

```python
def build_time_announcement_prompt(hour: int, minute: int, dj: str) -> str:
    """Build prompt for time announcement.
    
    Args:
        hour: Hour in 24-hour format (0-23)
        minute: Minute (0, 30)
        dj: DJ personality name
        
    Returns:
        Prompt string for LLM
    """
    from datetime import datetime
    from ai_radio.services.clock import format_time_for_dj
    
    # Create datetime for formatting
    now = datetime.now().replace(hour=hour, minute=minute, second=0)
    
    # Format in different styles based on DJ
    if dj == "julie":
        formatted_time = format_time_for_dj(now, include_ampm=True, style="casual")
        personality = "friendly and warm"
    elif dj == "mr_new_vegas":
        formatted_time = format_time_for_dj(now, include_ampm=True, style="written")
        personality = "smooth and romantic"
    else:
        formatted_time = format_time_for_dj(now, include_ampm=True, style="numeric")
        personality = "professional"
    
    prompt = (
        f"You are a {personality} radio DJ. "
        f"Announce that it is now {formatted_time}. "
        "Keep it brief (1-2 sentences), natural, and engaging. "
        "Do not repeat the exact same phrasing every time."
    )
    return prompt
```

## Success Criteria

### Functionality
- [ ] ClockService returns timezone-aware datetime objects
- [ ] Configured timezone is respected (test with different timezones)
- [ ] System timezone is used when no timezone configured
- [ ] `format_time_for_dj()` produces all format styles correctly
- [ ] AM/PM is included when requested
- [ ] Scheduling window accepts seconds 0-2 (configurable)

### Quality
- [ ] Timezone conversions are accurate
- [ ] Format styles sound natural for each DJ personality
- [ ] Time announcement prompts include correct formatted time
- [ ] Generated announcements say the correct time with AM/PM
- [ ] No timezone-related bugs (edge cases like DST transitions)

### Testing
- [ ] Unit tests for all timezone scenarios
- [ ] Unit tests for all format styles and variations
- [ ] Unit tests for scheduling window tolerance
- [ ] Integration test: full flow from ClockService to generated audio
- [ ] Test with mocked times to verify correctness

## Validation Commands

```bash
# Run unit tests
.venv/Scripts/pytest tests/test_services_clock.py -v
.venv/Scripts/pytest tests/test_generation_prompts.py::test_time_announcement_prompt -v

# Test timezone handling
python -c "
from src.ai_radio.services.clock import ClockService, format_time_for_dj
from datetime import datetime

# Test system timezone
clock = ClockService()
print(f'System timezone: {clock.get_timezone_name()}')
print(f'Current time: {clock.now()}')

# Test specific timezone
clock_ny = ClockService(timezone='America/New_York')
print(f'NY time: {clock_ny.now()}')

# Test formatting
now = datetime.now()
print(f'Numeric: {format_time_for_dj(now, style=\"numeric\")}')
print(f'Written: {format_time_for_dj(now, style=\"written\")}')
print(f'Casual: {format_time_for_dj(now, style=\"casual\")}')
"

# Test announcement window
python -c "
from src.ai_radio.services.clock import ClockService, is_announcement_time
from datetime import datetime

clock = ClockService()

# Should be True (second 0)
time1 = datetime(2026, 1, 22, 14, 30, 0)
print(f'{time1}: {is_announcement_time(clock, time1)}')

# Should be True (second 1, within window)
time2 = datetime(2026, 1, 22, 14, 30, 1)
print(f'{time2}: {is_announcement_time(clock, time2)}')

# Should be False (second 5, outside window)
time3 = datetime(2026, 1, 22, 14, 30, 5)
print(f'{time3}: {is_announcement_time(clock, time3)}')
"

# Test time announcement prompt
python -c "
from src.ai_radio.generation.prompts import build_time_announcement_prompt

prompt = build_time_announcement_prompt(14, 30, 'julie')
print(f'Julie prompt: {prompt}')

prompt = build_time_announcement_prompt(14, 30, 'mr_new_vegas')
print(f'Mr. New Vegas prompt: {prompt}')
"
```

## Anti-Regression Tests

```python
# tests/test_services_clock.py

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from ai_radio.services.clock import (
    ClockService, 
    is_announcement_time, 
    format_time_for_dj,
    get_current_timezone
)


class TestTimezoneSupport:
    """Test timezone awareness."""
    
    def test_system_timezone_when_none(self):
        """Should use system timezone when none specified."""
        clock = ClockService()
        now = clock.now()
        assert now.tzinfo is not None
    
    def test_specific_timezone(self):
        """Should use specified timezone."""
        clock = ClockService(timezone="America/New_York")
        now = clock.now()
        assert "America/New_York" in str(now.tzinfo) or now.tzname() in ("EST", "EDT")
    
    def test_invalid_timezone_fallback(self):
        """Should fallback to system timezone on invalid timezone."""
        clock = ClockService(timezone="Invalid/Timezone")
        now = clock.now()
        assert now.tzinfo is not None
    
    def test_get_timezone_name(self):
        """Should return timezone name."""
        clock = ClockService(timezone="UTC")
        tz_name = clock.get_timezone_name()
        assert tz_name == "UTC"


class TestEnhancedFormatting:
    """Test enhanced time formatting."""
    
    def test_numeric_with_ampm(self):
        """Numeric style should include AM/PM when requested."""
        time = datetime(2026, 1, 22, 14, 30)
        formatted = format_time_for_dj(time, include_ampm=True, style="numeric")
        assert "2:30" in formatted
        assert "PM" in formatted
    
    def test_numeric_without_ampm(self):
        """Numeric style should exclude AM/PM when not requested."""
        time = datetime(2026, 1, 22, 14, 30)
        formatted = format_time_for_dj(time, include_ampm=False, style="numeric")
        assert "2:30" in formatted
        assert "PM" not in formatted and "AM" not in formatted
    
    def test_written_style(self):
        """Written style should spell out time."""
        time = datetime(2026, 1, 22, 14, 30)
        formatted = format_time_for_dj(time, include_ampm=True, style="written")
        assert "two" in formatted.lower()
        assert "thirty" in formatted.lower() or "30" in formatted
        assert "afternoon" in formatted.lower()
    
    def test_casual_style_half_past(self):
        """Casual style should say 'half past' for 30 minutes."""
        time = datetime(2026, 1, 22, 14, 30)
        formatted = format_time_for_dj(time, style="casual")
        assert "half past" in formatted.lower()
    
    def test_oclock_formatting(self):
        """On-the-hour should say 'o'clock'."""
        time = datetime(2026, 1, 22, 14, 0)
        formatted = format_time_for_dj(time, style="numeric")
        assert "o'clock" in formatted.lower()


class TestSchedulingWindow:
    """Test relaxed scheduling window."""
    
    def test_exact_second_zero(self):
        """Should trigger on exact second 0."""
        clock = ClockService()
        time = datetime(2026, 1, 22, 14, 30, 0)
        assert is_announcement_time(clock, time, window_seconds=2)
    
    def test_within_window(self):
        """Should trigger within window."""
        clock = ClockService()
        time = datetime(2026, 1, 22, 14, 30, 1)
        assert is_announcement_time(clock, time, window_seconds=2)
    
    def test_outside_window(self):
        """Should not trigger outside window."""
        clock = ClockService()
        time = datetime(2026, 1, 22, 14, 30, 5)
        assert not is_announcement_time(clock, time, window_seconds=2)
    
    def test_wrong_minute(self):
        """Should not trigger on wrong minute even with window."""
        clock = ClockService()
        time = datetime(2026, 1, 22, 14, 15, 0)
        assert not is_announcement_time(clock, time, window_seconds=2)


# tests/test_generation_prompts.py

def test_time_announcement_prompt_includes_time():
    """Time announcement prompt should include formatted time."""
    from ai_radio.generation.prompts import build_time_announcement_prompt
    
    prompt = build_time_announcement_prompt(14, 30, "julie")
    
    # Should include time reference
    assert "2:30" in prompt or "half past" in prompt.lower() or "two thirty" in prompt.lower()

def test_time_announcement_prompt_varies_by_dj():
    """Prompts should vary by DJ personality."""
    from ai_radio.generation.prompts import build_time_announcement_prompt
    
    julie_prompt = build_time_announcement_prompt(14, 30, "julie")
    vegas_prompt = build_time_announcement_prompt(14, 30, "mr_new_vegas")
    
    # Should have different formatting or personality
    assert julie_prompt != vegas_prompt
```

## Git Commit

```bash
git add src/ai_radio/config.py
git add src/ai_radio/services/clock.py
git add src/ai_radio/generation/prompts.py
git add tests/test_services_clock.py
git add tests/test_generation_prompts.py
git commit -m "feat(clock): enhance clock service with timezone and formatting

- Add timezone awareness with configurable timezone support
- Enhance format_time_for_dj() with multiple styles (numeric, written, casual)
- Add AM/PM formatting option
- Relax scheduling window to 0-2 seconds (configurable)
- Update build_time_announcement_prompt() to include formatted time
- Add comprehensive tests for all enhancements
- Support system timezone fallback
"
```

## Dependencies
- **Requires**: Checkpoint 6.1 (Clock Service) - Basic implementation must exist
- **Requires**: Python 3.9+ for `zoneinfo` module
- **Enhances**: Checkpoint 2.6 (Batch Time Announcements) - Prompts will include accurate time

## Notes
- Python's `zoneinfo` requires Python 3.9+. For Python 3.8, use `backports.zoneinfo` package.
- Timezone configuration is optional; system timezone is used by default.
- Scheduling window helps prevent missed announcements due to timing precision issues.
- Format styles allow personality-based time announcements (Julie casual, Mr. New Vegas formal).
- DST transitions are handled automatically by zoneinfo.
- Consider adding NTP sync documentation for production deployments requiring high accuracy.
