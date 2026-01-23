"""Tests for clock service."""
import pytest
from datetime import datetime
from src.ai_radio.services.clock import (
    ClockService,
    is_announcement_time,
    get_next_announcement_time,
    format_time_for_dj,
)


class TestAnnouncementTiming:
    """Test time announcement scheduling."""

    def test_announces_on_hour(self):
        """Must announce on the hour."""
        clock = ClockService()
        on_hour = datetime(2026, 1, 22, 14, 0, 0)
        assert is_announcement_time(clock, on_hour, window_seconds=2)

    def test_announces_on_half_hour(self):
        """Must announce on the half hour."""
        clock = ClockService()
        half_hour = datetime(2026, 1, 22, 14, 30, 0)
        assert is_announcement_time(clock, half_hour, window_seconds=2)

    def test_announces_within_window(self):
        """Should trigger if second within 0-2 window."""
        clock = ClockService()
        t = datetime(2026, 1, 22, 14, 30, 1)
        assert is_announcement_time(clock, t, window_seconds=2)

    def test_no_announce_at_quarter(self):
        """Must not announce at quarter hour even within window."""
        clock = ClockService()
        quarter = datetime(2026, 1, 22, 14, 15, 1)
        assert not is_announcement_time(clock, quarter, window_seconds=2)

    def test_next_announcement_from_10_past(self):
        """Next announcement from :10 should be :30."""
        clock = ClockService()
        ten_past = datetime(2026, 1, 22, 14, 10, 0)
        next_time = get_next_announcement_time(clock, ten_past)
        assert next_time.minute == 30

    def test_next_announcement_from_40_past(self):
        """Next announcement from :40 should be next hour."""
        clock = ClockService()
        forty_past = datetime(2026, 1, 22, 14, 40, 0)
        next_time = get_next_announcement_time(clock, forty_past)
        assert next_time.hour == 15
        assert next_time.minute == 0


class TestTimeFormatting:
    """Test DJ-style time formatting."""

    def test_numeric_with_ampm(self):
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 30), include_ampm=True, style="numeric")
        assert "2:30" in formatted
        assert "PM" in formatted

    def test_numeric_without_ampm(self):
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 30), include_ampm=False, style="numeric")
        assert "2:30" in formatted
        assert "PM" not in formatted and "AM" not in formatted

    def test_written_style(self):
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 30), include_ampm=True, style="written")
        assert "two" in formatted.lower() or "two thirty" in formatted.lower()
        assert any(x in formatted.lower() for x in ("afternoon", "in the afternoon", "in the evening"))

    def test_casual_style_half_past(self):
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 30), style="casual")
        assert "half past" in formatted.lower()

    def test_oclock_formatting(self):
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 0), style="numeric")
        assert "o'clock" in formatted.lower() or "o'clock" in formatted.lower()

    def test_timezone_support(self):
        # Ensure ClockService returns tz-aware datetime
        from src.ai_radio.services.clock import ClockService
        clock = ClockService(timezone=None)
        now = clock.now()
        assert now.tzinfo is not None

    def test_specific_timezone(self):
        from src.ai_radio.services.clock import ClockService
        clock = ClockService(timezone="UTC")
        now = clock.now()
        assert now.tzname() == "UTC"
