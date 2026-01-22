from datetime import datetime
from src.ai_radio.dj.scheduler import DJScheduler, get_current_dj, get_next_transition, is_transition_time
from src.ai_radio.dj.personality import DJ


class TestGetCurrentDJ:
    def test_julie_in_morning(self):
        scheduler = DJScheduler()
        morning = datetime(2026, 1, 22, 8, 0)
        assert get_current_dj(scheduler, morning) == DJ.JULIE

    def test_julie_in_afternoon(self):
        scheduler = DJScheduler()
        afternoon = datetime(2026, 1, 22, 14, 0)
        assert get_current_dj(scheduler, afternoon) == DJ.JULIE

    def test_mr_vegas_in_evening(self):
        scheduler = DJScheduler()
        evening = datetime(2026, 1, 22, 20, 0)
        assert get_current_dj(scheduler, evening) == DJ.MR_NEW_VEGAS

    def test_mr_vegas_at_midnight(self):
        scheduler = DJScheduler()
        midnight = datetime(2026, 1, 22, 0, 0)
        assert get_current_dj(scheduler, midnight) == DJ.MR_NEW_VEGAS

    def test_mr_vegas_at_5am(self):
        scheduler = DJScheduler()
        early = datetime(2026, 1, 22, 5, 0)
        assert get_current_dj(scheduler, early) == DJ.MR_NEW_VEGAS

    def test_julie_at_6am(self):
        scheduler = DJScheduler()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert get_current_dj(scheduler, six_am) == DJ.JULIE


class TestTransitions:
    def test_transition_at_7pm(self):
        scheduler = DJScheduler()
        seven_pm = datetime(2026, 1, 22, 19, 0)
        assert is_transition_time(scheduler, seven_pm)

    def test_transition_at_6am(self):
        scheduler = DJScheduler()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert is_transition_time(scheduler, six_am)

    def test_not_transition_at_noon(self):
        scheduler = DJScheduler()
        noon = datetime(2026, 1, 22, 12, 0)
        assert not is_transition_time(scheduler, noon)

    def test_get_next_transition_from_morning(self):
        scheduler = DJScheduler()
        morning = datetime(2026, 1, 22, 10, 0)
        next_trans = get_next_transition(scheduler, morning)
        assert next_trans.hour == 19
