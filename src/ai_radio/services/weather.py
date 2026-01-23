from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
import logging
from .cache import ServiceCache, cache_get, cache_set, is_cache_valid
from src.ai_radio.config import (
    WEATHER_LATITUDE,
    WEATHER_LONGITUDE,
    WEATHER_TIMEZONE,
    WEATHER_CACHE_MINUTES,
    WEATHER_UNITS,
)

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    temperature: Optional[float]
    conditions: Optional[str]
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    description: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    forecast_hour: Optional[int] = None  # The hour this weather is for (0-23)
    is_forecast: bool = False  # True if this is a future forecast, False if current



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
        # Map our config units to Open-Meteo parameter
        temperature_unit = "fahrenheit" if WEATHER_UNITS == "imperial" else "celsius"

        params = {
            "latitude": float(self._lat),
            "longitude": float(self._lon),
            "hourly": "temperature_2m,weathercode,relativehumidity_2m,windspeed_10m",
            "timezone": self._tz,
            "temperature_unit": temperature_unit,
        }

        from src.ai_radio.config import WEATHER_API_TIMEOUT
        try:
            responses = client.weather_api(url, params=params, timeout=WEATHER_API_TIMEOUT)
        except Exception as e:
            logger.error(f"Open-Meteo API request failed: {e}")
            # Propagate so _fetch_and_cache can handle fallback
            raise

        if not responses:
            return WeatherData(temperature=None, conditions=None, raw=None)

        response = responses[0]

        # Extract hourly variables
        hourly = response.Hourly()
        # Temperature as numpy array
        try:
            temp_vals = hourly.Variables(0).ValuesAsNumpy()
            weathercode_vals = None
            humidity_vals = None
            wind_vals = None

            # Optional variables may be present at expected indices
            try:
                weathercode_vals = hourly.Variables(1).ValuesAsNumpy()
            except Exception:
                weathercode_vals = None
            try:
                humidity_vals = hourly.Variables(2).ValuesAsNumpy()
            except Exception:
                humidity_vals = None
            try:
                wind_vals = hourly.Variables(3).ValuesAsNumpy()
            except Exception:
                wind_vals = None

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

        # Try to get weathercode, humidity, and wind values
        try:
            weathercode = int(weathercode_vals[idx]) if weathercode_vals is not None and idx != -1 else None
        except Exception:
            weathercode = None
        try:
            humidity = int(humidity_vals[idx]) if humidity_vals is not None and idx != -1 else None
        except Exception:
            humidity = None
        try:
            wind_speed = float(wind_vals[idx]) if wind_vals is not None and idx != -1 else None
        except Exception:
            wind_speed = None

        conditions = weathercode_map.get(weathercode, f'code {weathercode}') if weathercode is not None else None
        description = conditions

        return WeatherData(
            temperature=temp,
            conditions=conditions,
            humidity=humidity,
            wind_speed=wind_speed,
            description=description,
            raw={'params': params},
            forecast_hour=None,
            is_forecast=False,
        )
    
    def get_forecast_for_hour(self, target_hour: int) -> WeatherData:
        """Get weather forecast for a specific hour today (0-23).
        
        This is useful for generating announcements at midnight that will be played later in the day.
        For example, at midnight, you can generate a 6 AM announcement with the forecast for 6 AM.
        
        Args:
            target_hour: Hour of the day (0-23) to get forecast for
            
        Returns:
            WeatherData for that specific hour with is_forecast=True
        """
        try:
            import openmeteo_requests
            import requests_cache
            from retry_requests import retry
            import pandas as pd
        except Exception:
            return WeatherData(temperature=65, conditions="clear skies", raw=None, forecast_hour=target_hour, is_forecast=True)
        
        # Setup cached session and retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        client = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        temperature_unit = "fahrenheit" if WEATHER_UNITS == "imperial" else "celsius"
        params = {
            "latitude": float(self._lat),
            "longitude": float(self._lon),
            "hourly": "temperature_2m,weathercode,relativehumidity_2m,windspeed_10m",
            "timezone": self._tz,
            "temperature_unit": temperature_unit,
        }

        try:
            responses = client.weather_api(url, params=params)
        except Exception as e:
            logger.error(f"Open-Meteo API request failed: {e}")
            raise

        if not responses:
            return WeatherData(temperature=None, conditions=None, raw=None, forecast_hour=target_hour, is_forecast=True)

        response = responses[0]
        hourly = response.Hourly()
        
        try:
            temp_vals = hourly.Variables(0).ValuesAsNumpy()
            weathercode_vals = None
            humidity_vals = None
            wind_vals = None
            try:
                weathercode_vals = hourly.Variables(1).ValuesAsNumpy()
            except Exception:
                weathercode_vals = None
            try:
                humidity_vals = hourly.Variables(2).ValuesAsNumpy()
            except Exception:
                humidity_vals = None
            try:
                wind_vals = hourly.Variables(3).ValuesAsNumpy()
            except Exception:
                wind_vals = None

            time_start = hourly.Time()
            time_end = hourly.TimeEnd()
            interval = hourly.Interval()
        except Exception:
            return WeatherData(temperature=None, conditions=None, raw=None, forecast_hour=target_hour, is_forecast=True)

        # Build pandas index
        times = pd.date_range(
            start=pd.to_datetime(time_start + response.UtcOffsetSeconds(), unit='s', utc=True),
            end=pd.to_datetime(time_end + response.UtcOffsetSeconds(), unit='s', utc=True),
            freq=pd.Timedelta(seconds=interval),
            inclusive='left',
        )
        
        # Find the entry that matches target_hour (today)
        from zoneinfo import ZoneInfo
        tz_info = ZoneInfo(self._tz)
        now_local = datetime.now(tz_info)
        target_time = now_local.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        
        # Convert to pandas timestamp for indexing
        target_ts = pd.Timestamp(target_time)
        
        # Find closest time index
        df = pd.DataFrame({
            'temperature_2m': temp_vals,
            'weathercode': weathercode_vals if weathercode_vals is not None else [None]*len(temp_vals),
            'relativehumidity_2m': humidity_vals if humidity_vals is not None else [None]*len(temp_vals),
            'windspeed_10m': wind_vals if wind_vals is not None else [None]*len(temp_vals),
        }, index=times)
        
        idx = df.index.get_indexer([target_ts], method='nearest')[0]
        if idx == -1 or idx >= len(df):
            return WeatherData(temperature=None, conditions=None, raw=None, forecast_hour=target_hour, is_forecast=True)
        
        temp = float(df.iloc[idx]['temperature_2m'])
        weathercode = int(df.iloc[idx]['weathercode']) if df.iloc[idx]['weathercode'] is not None else None
        humidity = int(df.iloc[idx]['relativehumidity_2m']) if df.iloc[idx]['relativehumidity_2m'] is not None else None
        wind_speed = float(df.iloc[idx]['windspeed_10m']) if df.iloc[idx]['windspeed_10m'] is not None else None
        
        # Map weathercode to text
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
        conditions = weathercode_map.get(weathercode, f'code {weathercode}') if weathercode is not None else None
        
        return WeatherData(temperature=temp, conditions=conditions, humidity=humidity, wind_speed=wind_speed, raw={'params': params}, forecast_hour=target_hour, is_forecast=True)

    def _fetch_and_cache(self) -> WeatherData:
        try:
            data = self._api_client()
            cache_set(self._cache, "current", data)
            return data
        except Exception as e:
            logger.error(f"Weather API fetch failed: {e}")
            # Try to return expired cache even if expired
            cached = cache_get(self._cache, "current", ignore_expiry=True)
            if cached is not None:
                logger.warning("Using expired weather cache due to API failure")
                return cached
            # Fallback to fake data
            logger.warning("Using fallback weather data due to API failure")
            return WeatherData(temperature=65, conditions="clear skies", raw=None)

    def get_current_weather(self) -> WeatherData:
        # Try to peek at cached value without deleting expired entries so we can
        # reuse expired cache if an API fetch fails.
        cached = cache_get(self._cache, "current", ignore_expiry=True)
        if cached is not None and is_cache_valid(self._cache, "current"):
            return cached
        return self._fetch_and_cache()


def get_current_weather(service: WeatherService) -> WeatherData:
    return service.get_current_weather()


def is_weather_time(service: WeatherService, when: datetime) -> bool:
    # Announce at minutes==0 and hours in configured list
    from src.ai_radio.config import WEATHER_TIMES
    return when.minute == 0 and when.hour in tuple(WEATHER_TIMES)


def format_weather_for_dj(weather: WeatherData, units: str = "imperial") -> str:
    # Temperature text with full unit name for better TTS clarity
    if weather.temperature is not None:
        temp_val = int(round(weather.temperature))
        if units == "metric":
            temp_text = f"{temp_val} degrees Celsius"
        else:
            temp_text = f"{temp_val} degrees Fahrenheit"
    else:
        temp_text = "a few degrees"

    cond_text = weather.conditions or "some conditions"

    extras = []
    if weather.humidity is not None:
        extras.append(f"humidity around {int(round(weather.humidity))} percent")
    if weather.wind_speed is not None:
        # Open‑Meteo returns wind speed in m/s. Convert to user-facing units and round sensibly
        wind = weather.wind_speed
        if units == "metric":
            wind_val = round(wind, 1)
            if float(wind_val).is_integer():
                wind_int = int(wind_val)
                unit_text = "meter per second" if wind_int == 1 else "meters per second"
                wind_text = f"winds of {wind_int} {unit_text}"
            else:
                wind_text = f"winds of {wind_val:.1f} meters per second"
        else:
            # Convert m/s to mph (1 m/s = 2.2369362920544 mph)
            wind_mph = wind * 2.2369362920544
            wind_val = round(wind_mph, 1)
            if float(wind_val).is_integer():
                wind_int = int(wind_val)
                unit_text = "mile per hour" if wind_int == 1 else "miles per hour"
                wind_text = f"winds of {wind_int} {unit_text}"
            else:
                wind_text = f"winds of {wind_val:.1f} miles per hour"
        extras.append(wind_text)

    extra_text = f" with {' and '.join(extras)}" if extras else ""

    # Construct period-style announcement, avoiding symbols that TTS might mispronounce
    return f"Coming up: a {cond_text} day with temperatures around {temp_text}{extra_text}. Stay tuned for more." 
