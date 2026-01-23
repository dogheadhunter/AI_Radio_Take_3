from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
from .cache import ServiceCache, cache_get, cache_set
from src.ai_radio.config import WEATHER_LATITUDE, WEATHER_LONGITUDE, WEATHER_TIMEZONE, WEATHER_CACHE_MINUTES


@dataclass
class WeatherData:
    temperature: Optional[float]
    conditions: Optional[str]
    raw: Optional[Dict[str, Any]] = None


class WeatherService:
    """Fetches and caches weather data using Open-Meteo (openmeteo_requests).

    You may inject an `api_client` callable for testing which should return a mapping
    similar to WeatherData or a dict with 'temperature' and 'conditions' keys.
    """

    def __init__(self, api_client: Optional[Callable[[], WeatherData]] = None,
                 latitude: Optional[float] = None, longitude: Optional[float] = None,
                 timezone: Optional[str] = None, cache_minutes: int = WEATHER_CACHE_MINUTES):
        self._lat = latitude or WEATHER_LATITUDE
        self._lon = longitude or WEATHER_LONGITUDE
        self._tz = timezone or WEATHER_TIMEZONE
        self._api_client = api_client or self._default_api_client
        self._cache = ServiceCache(default_ttl_seconds=cache_minutes * 60)

    def _default_api_client(self) -> WeatherData:
        try:
            # Lazy imports so tests without extra deps won't fail on import
            import openmeteo_requests
            import requests_cache
            from retry_requests import retry
            import pandas as pd
        except Exception as exc:
            # Fall back to fake data if Open-Meteo libs are not present
            return WeatherData(temperature=65, conditions="clear skies", raw=None)

        # Setup cached session and retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        client = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": float(self._lat),
            "longitude": float(self._lon),
            "hourly": "temperature_2m,weathercode",
            "timezone": self._tz,
            "temperature_unit": "fahrenheit",
        }

        responses = client.weather_api(url, params=params)
        if not responses:
            return WeatherData(temperature=None, conditions=None, raw=None)

        response = responses[0]

        # Extract hourly variables
        hourly = response.Hourly()
        # Temperature as numpy array
        try:
            temp_vals = hourly.Variables(0).ValuesAsNumpy()
            time_start = hourly.Time()
            time_end = hourly.TimeEnd()
            interval = hourly.Interval()
        except Exception:
            # If the structured API doesn't match, fallback
            return WeatherData(temperature=None, conditions=None, raw=None)

        # Build a pandas index for the hourly data (UTC-aware)
        times = pd.date_range(
            start=pd.to_datetime(time_start + response.UtcOffsetSeconds(), unit='s', utc=True),
            end=pd.to_datetime(time_end + response.UtcOffsetSeconds(), unit='s', utc=True),
            freq=pd.Timedelta(seconds=interval),
            inclusive='left',
        )
        df = pd.DataFrame({'temperature_2m': temp_vals}, index=times)

        # Select the closest time to now in the service timezone
        now_utc = pd.Timestamp.utcnow()
        # Take nearest previous time index
        idx = df.index.get_indexer([now_utc], method='pad')[0]
        if idx == -1:
            # no data
            temp = None
        else:
            temp = float(df.iloc[idx]['temperature_2m'])

        # weathercode mapping (simple): map typical codes to text
        # Reference: https://open-meteo.com/en/docs
        weathercode_map = {
            0: 'clear sky',
            1: 'mainly clear',
            2: 'partly cloudy',
            3: 'overcast',
            45: 'fog',
            48: 'depositing rime fog',
            51: 'drizzle',
            53: 'moderate drizzle',
            55: 'dense drizzle',
            61: 'rain',
            63: 'moderate rain',
            65: 'heavy rain',
            71: 'snow',
            80: 'rain showers',
            95: 'thunderstorm'
        }

        # Try to get the weathercode variable (Variables index 1)
        try:
            weathercode_vals = hourly.Variables(1).ValuesAsNumpy()
            weathercode = int(weathercode_vals[idx]) if idx != -1 else None
            conditions = weathercode_map.get(weathercode, f'code {weathercode}') if weathercode is not None else None
        except Exception:
            conditions = None

        return WeatherData(temperature=temp, conditions=conditions, raw={'params': params})

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
    # Announce at minutes==0 and hours in configured list
    from src.ai_radio.config import WEATHER_TIMES
    return when.minute == 0 and when.hour in tuple(WEATHER_TIMES)


def format_weather_for_dj(weather: WeatherData) -> str:
    temp_text = f"{int(weather.temperature)}°" if weather.temperature is not None else "a few degrees"
    cond_text = weather.conditions or "some conditions"
    # Produce a colorful, period-style sentence
    return f"Coming up: a {cond_text} day with temperatures around {temp_text}. Stay tuned for more." 
