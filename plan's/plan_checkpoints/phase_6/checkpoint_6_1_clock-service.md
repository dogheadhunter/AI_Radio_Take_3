# Checkpoint 6.1: Clock Service

#### Checkpoint 6.1: Clock Service
**Time tracking and announcement scheduling.**

**Tasks:**
1. Create `src/ai_radio/services/clock. py`
2. Track current time
3. Determine when to announce time
4. Get appropriate time announcement

**Tests First:**
```python
# tests/services/test_clock. py
"""Tests for clock service."""
import pytest
from datetime import datetime, timedelta
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
        assert is_announcement_time(clock, on_hour)
    
    def test_announces_on_half_hour(self):
        """Must announce on the half hour."""
        clock = ClockService()
        half_hour = datetime(2026, 1, 22, 14, 30, 0)
        assert is_announcement_time(clock, half_hour)
    
    def test_no_announce_at_quarter(self):
        """Must not announce at quarter hour."""
        clock = ClockService()
        quarter = datetime(2026, 1, 22, 14, 15, 0)
        assert not is_announcement_time(clock, quarter)
    
    def test_next_announcement_from_10_past(self):
        """Next announcement from : 10 should be : 30."""
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
        assert next_time. minute == 0


class TestTimeFormatting:
    """Test DJ-style time formatting."""
    
    def test_format_includes_hour(self):
        """Formatted time must include hour."""
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 30))
        assert "2" in formatted or "two" in formatted. lower() or "14" in formatted
    
    def test_format_on_hour_says_oclock(self):
        """On-the-hour times should say 'o'clock' or similar."""
        formatted = format_time_for_dj(datetime(2026, 1, 22, 14, 0))
        assert "o'clock" in formatted.lower() or "00" in formatted
```

**Success Criteria:**
- [ ] All clock tests pass
- [ ] Announcement times detected correctly
- [ ] Time formatting is natural

**Git Commit:** `feat(services): add clock service`
