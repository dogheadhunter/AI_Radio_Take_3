from datetime import datetime, timedelta
from typing import Optional
from .personality import DJ


class DJScheduler:
    def __init__(self, morning_hour: int = 6, evening_hour: int = 19):
        self.morning_hour = morning_hour
        self.evening_hour = evening_hour


def get_current_dj(scheduler: DJScheduler, when: Optional[datetime] = None) -> DJ:
    if when is None:
        when = datetime.now()

    hour = when.hour
    # Julie: 06:00 <= hour < 19:00
    if scheduler.morning_hour <= hour < scheduler.evening_hour:
        return DJ.JULIE
    # Mr. New Vegas: 19:00 <= hour < 24 or 0 <= hour < 6
    return DJ.MR_NEW_VEGAS


def is_transition_time(scheduler: DJScheduler, when: Optional[datetime] = None) -> bool:
    if when is None:
        from datetime import datetime
        when = datetime.now()
    return when.hour in (scheduler.morning_hour, scheduler.evening_hour)


def get_next_transition(scheduler: DJScheduler, now: Optional[datetime] = None) -> datetime:
    if now is None:
        now = datetime.now()

    today_morning = now.replace(hour=scheduler.morning_hour, minute=0, second=0, microsecond=0)
    today_evening = now.replace(hour=scheduler.evening_hour, minute=0, second=0, microsecond=0)

    candidates = []
    for dt in (today_morning, today_evening):
        if dt > now:
            candidates.append(dt)
    if candidates:
        return min(candidates)

    # Otherwise return the next day's morning
    return today_morning + timedelta(days=1)
