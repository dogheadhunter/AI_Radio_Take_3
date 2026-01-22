from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional
from .cache import ServiceCache, cache_get, cache_set


@dataclass
class WeatherData:
    temperature: Optional[float]
    conditions: Optional[str]


class WeatherService:
    """Fetches and caches weather data. An API client callable may be injected for testing."""

    def __init__(self, api_client: Optional[Callable[[], WeatherData]] = None, cache_minutes: int = 10):
        self._api_client = api_client or self._default_api_client
        self._cache = ServiceCache(default_ttl_seconds=cache_minutes * 60)

    def _default_api_client(self) -> WeatherData:
        # Fallback fake data when no API client is provided.
        return WeatherData(temperature=65, conditions="clear skies")

    def _fetch_and_cache(self) -> WeatherData:
        data = self._api_client()
        cache_set(self._cache, "current", data)
        return data

    def get_current_weather(self) -> WeatherData:
        cached = cache_get(self._cache, "current")
        if cached is not None:
            return cached
        return self._fetch_and_cache()


def get_current_weather(service: WeatherService) -> WeatherData:
    return service.get_current_weather()


def is_weather_time(service: WeatherService, when: datetime) -> bool:
    # Announce at 6:00, 12:00, and 17:00
    return when.minute == 0 and when.hour in (6, 12, 17)


def format_weather_for_dj(weather: WeatherData) -> str:
    temp_text = f"{int(weather.temperature)}°" if weather.temperature is not None else "a few degrees"
    cond_text = weather.conditions or "some conditions"
    # Produce a colorful, period-style sentence
    return f"Coming up: a {cond_text} day with temperatures around {temp_text}. Stay tuned for more." 
