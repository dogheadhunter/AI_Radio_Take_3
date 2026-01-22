# Checkpoint 4.2: DJ Scheduler

#### Checkpoint 4.2: DJ Scheduler
**Switch DJs based on time of day.**

**Tasks:**
1. Create `src/ai_radio/dj/scheduler. py`
2. Determine current DJ based on time
3. Handle DJ transitions
4. Emit events for DJ changes

**Tests First:**
```python
# tests/dj/test_scheduler. py
"""Tests for DJ scheduler."""
import pytest
from datetime import datetime, time
from src.ai_radio. dj.scheduler import (
    DJScheduler,
    get_current_dj,
    get_next_transition,
    is_transition_time,
    DJ,
)


class TestGetCurrentDJ: 
    """Test current DJ determination."""
    
    def test_julie_in_morning(self):
        """Julie must be active at 8 AM."""
        scheduler = DJScheduler()
        morning = datetime(2026, 1, 22, 8, 0)
        assert get_current_dj(scheduler, morning) == DJ.JULIE
    
    def test_julie_in_afternoon(self):
        """Julie must be active at 2 PM."""
        scheduler = DJScheduler()
        afternoon = datetime(2026, 1, 22, 14, 0)
        assert get_current_dj(scheduler, afternoon) == DJ.JULIE
    
    def test_mr_vegas_in_evening(self):
        """Mr. New Vegas must be active at 8 PM."""
        scheduler = DJScheduler()
        evening = datetime(2026, 1, 22, 20, 0)
        assert get_current_dj(scheduler, evening) == DJ.MR_NEW_VEGAS
    
    def test_mr_vegas_at_midnight(self):
        """Mr. New Vegas must be active at midnight."""
        scheduler = DJScheduler()
        midnight = datetime(2026, 1, 22, 0, 0)
        assert get_current_dj(scheduler, midnight) == DJ.MR_NEW_VEGAS
    
    def test_mr_vegas_at_5am(self):
        """Mr. New Vegas must be active at 5 AM."""
        scheduler = DJScheduler()
        early = datetime(2026, 1, 22, 5, 0)
        assert get_current_dj(scheduler, early) == DJ.MR_NEW_VEGAS
    
    def test_julie_at_6am(self):
        """Julie must take over at 6 AM."""
        scheduler = DJScheduler()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert get_current_dj(scheduler, six_am) == DJ.JULIE


class TestTransitions:
    """Test DJ transition detection."""
    
    def test_transition_at_7pm(self):
        """7 PM must be a transition time."""
        scheduler = DJScheduler()
        seven_pm = datetime(2026, 1, 22, 19, 0)
        assert is_transition_time(scheduler, seven_pm)
    
    def test_transition_at_6am(self):
        """6 AM must be a transition time."""
        scheduler = DJScheduler()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert is_transition_time(scheduler, six_am)
    
    def test_not_transition_at_noon(self):
        """Noon must not be a transition time."""
        scheduler = DJScheduler()
        noon = datetime(2026, 1, 22, 12, 0)
        assert not is_transition_time(scheduler, noon)
    
    def test_get_next_transition_from_morning(self):
        """Next transition from morning must be 7 PM."""
        scheduler = DJScheduler()
        morning = datetime(2026, 1, 22, 10, 0)
        next_trans = get_next_transition(scheduler, morning)
        assert next_trans. hour == 19
```

**Success Criteria:**
- [ ] All scheduler tests pass
- [ ] Correct DJ returned for all times
- [ ] Transition times detected correctly

**Git Commit:** `feat(dj): add DJ scheduler`
