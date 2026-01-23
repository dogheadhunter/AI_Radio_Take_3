# Checkpoint 6.2a: Weather API Integration

#### Checkpoint 6.2a: Weather API Integration
**Replace fake weather data with real API integration (OpenWeatherMap).**

## Overview
The current `WeatherService` returns fake weather data (`temperature=65, conditions="clear skies"`). This enhancement integrates with OpenWeatherMap API (or similar) to fetch real weather data with proper error handling, caching, and configuration.

## Tasks

### Task 1: Add Weather API Configuration
- [ ] Add OpenWeatherMap API key to environment variables
- [ ] Add weather location configuration (city, coordinates)
- [ ] Add API endpoint and timeout configuration
- [ ] Document how to obtain and configure API key
- [ ] Add fallback behavior when API unavailable

### Task 2: Implement OpenWeather API Client
- [ ] Create `weather_api.py` with OpenWeatherMap client
- [ ] Implement `fetch_current_weather()` function
- [ ] Parse API response into `WeatherData` format
- [ ] Add error handling for network failures
- [ ] Add error handling for invalid API keys
- [ ] Add request timeout support

### Task 3: Update WeatherService Integration
- [ ] Replace `_default_api_client()` with real API client
- [ ] Support API client injection for testing
- [ ] Add fallback to fake data when API fails
- [ ] Add logging for API calls and errors
- [ ] Update caching to prevent excessive API calls

### Task 4: Enhanced Weather Data
- [ ] Extend `WeatherData` with additional fields (humidity, wind, description)
- [ ] Update `format_weather_for_dj()` to use richer data
- [ ] Add weather condition mapping (e.g., "partly cloudy" → "scattered clouds")
- [ ] Support Fahrenheit and Celsius (configurable)

### Task 5: Testing and Validation
- [ ] Add mock API client for testing
- [ ] Test with real API (integration test)
- [ ] Test error scenarios (network failure, invalid key, bad response)
- [ ] Test fallback behavior
- [ ] Verify caching reduces API calls

## Implementation Details

**File: `.env.example`**

Add environment variable template:

```bash
# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_LOCATION=New York,US
OPENWEATHER_UNITS=imperial  # imperial (F) or metric (C)
```

**File: `src/ai_radio/config.py`**

Add weather API configuration:

```python
import os

# Weather API settings
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_LOCATION = os.getenv("OPENWEATHER_LOCATION", "Las Vegas,US")
OPENWEATHER_UNITS = os.getenv("OPENWEATHER_UNITS", "imperial")  # imperial or metric
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_API_TIMEOUT = 5  # seconds
WEATHER_CACHE_MINUTES = 30
WEATHER_FALLBACK_ENABLED = True  # Use fake data when API fails
```

**File: `src/ai_radio/services/weather_api.py`**

OpenWeatherMap API client:

```python
"""OpenWeatherMap API client."""
import requests
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Weather data structure."""
    temperature: Optional[float]
    conditions: Optional[str]
    description: Optional[str] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None


class OpenWeatherClient:
    """Client for OpenWeatherMap API."""
    
    def __init__(
        self, 
        api_key: str, 
        location: str, 
        units: str = "imperial",
        api_url: str = "https://api.openweathermap.org/data/2.5/weather",
        timeout: int = 5
    ):
        """Initialize OpenWeather client.
        
        Args:
            api_key: OpenWeatherMap API key
            location: Location string (e.g., "New York,US" or "London,UK")
            units: Units system ("imperial" for F, "metric" for C)
            api_url: API endpoint URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.location = location
        self.units = units
        self.api_url = api_url
        self.timeout = timeout
    
    def fetch_current_weather(self) -> WeatherData:
        """Fetch current weather from OpenWeatherMap API.
        
        Returns:
            WeatherData object with current conditions
            
        Raises:
            requests.RequestException: On network errors
            ValueError: On invalid API response
        """
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not configured")
        
        params = {
            "q": self.location,
            "appid": self.api_key,
            "units": self.units,
        }
        
        logger.debug(f"Fetching weather for {self.location}")
        
        try:
            response = requests.get(
                self.api_url, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_response(data)
            
        except requests.Timeout:
            logger.error(f"Weather API timeout after {self.timeout}s")
            raise
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse weather API response: {e}")
            raise ValueError(f"Invalid API response: {e}")
    
    def _parse_response(self, data: Dict[str, Any]) -> WeatherData:
        """Parse OpenWeatherMap API response.
        
        Args:
            data: JSON response from API
            
        Returns:
            WeatherData object
        """
        try:
            temp = data["main"]["temp"]
            conditions = data["weather"][0]["main"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            
            logger.info(f"Weather fetched: {temp}°, {conditions}")
            
            return WeatherData(
                temperature=temp,
                conditions=conditions,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed,
            )
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected API response structure: {e}")


def create_weather_client(
    api_key: Optional[str] = None,
    location: Optional[str] = None,
    units: Optional[str] = None,
) -> OpenWeatherClient:
    """Create OpenWeatherClient with config defaults.
    
    Args:
        api_key: Optional API key (uses config if not provided)
        location: Optional location (uses config if not provided)
        units: Optional units (uses config if not provided)
        
    Returns:
        Configured OpenWeatherClient
    """
    from ai_radio.config import (
        OPENWEATHER_API_KEY,
        OPENWEATHER_LOCATION,
        OPENWEATHER_UNITS,
        OPENWEATHER_API_URL,
        WEATHER_API_TIMEOUT,
    )
    
    return OpenWeatherClient(
        api_key=api_key or OPENWEATHER_API_KEY,
        location=location or OPENWEATHER_LOCATION,
        units=units or OPENWEATHER_UNITS,
        api_url=OPENWEATHER_API_URL,
        timeout=WEATHER_API_TIMEOUT,
    )
```

**File: `src/ai_radio/services/weather.py`**

Update WeatherService to use real API:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional
import logging
from .cache import ServiceCache, cache_get, cache_set

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Weather data structure."""
    temperature: Optional[float]
    conditions: Optional[str]
    description: Optional[str] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None


class WeatherService:
    """Fetches and caches weather data. An API client callable may be injected for testing."""

    def __init__(
        self, 
        api_client: Optional[Callable[[], WeatherData]] = None, 
        location: Optional[str] = None,
        cache_minutes: int = 30,
        enable_fallback: bool = True
    ):
        """Initialize WeatherService.
        
        Args:
            api_client: Optional API client callable (for testing)
            location: Optional location override
            cache_minutes: Cache duration in minutes
            enable_fallback: Use fake data when API fails
        """
        self._api_client = api_client or self._create_default_client(location)
        self._cache = ServiceCache(default_ttl_seconds=cache_minutes * 60)
        self._enable_fallback = enable_fallback

    def _create_default_client(self, location: Optional[str]) -> Callable[[], WeatherData]:
        """Create default OpenWeather API client."""
        from ai_radio.config import OPENWEATHER_API_KEY
        
        if not OPENWEATHER_API_KEY:
            logger.warning("No OpenWeatherMap API key configured, using fallback data")
            return self._fallback_client
        
        try:
            from ai_radio.services.weather_api import create_weather_client
            client = create_weather_client(location=location)
            return client.fetch_current_weather
        except ImportError as e:
            logger.error(f"Failed to import weather API client: {e}")
            return self._fallback_client

    def _fallback_client(self) -> WeatherData:
        """Fallback fake data when no API client is available."""
        logger.debug("Using fallback weather data")
        return WeatherData(
            temperature=65, 
            conditions="clear skies",
            description="clear sky",
            humidity=50,
            wind_speed=5.0,
        )

    def _fetch_and_cache(self) -> WeatherData:
        """Fetch weather from API and cache result."""
        try:
            data = self._api_client()
            cache_set(self._cache, "current", data)
            return data
        except Exception as e:
            logger.error(f"Weather API fetch failed: {e}")
            
            # Try to return cached data even if expired
            cached = cache_get(self._cache, "current", ignore_expiry=True)
            if cached is not None:
                logger.warning("Using expired weather cache due to API failure")
                return cached
            
            # Fallback to fake data if enabled
            if self._enable_fallback:
                logger.warning("Using fallback weather data due to API failure")
                return self._fallback_client()
            
            raise

    def get_current_weather(self) -> WeatherData:
        """Get current weather (from cache or API).
        
        Returns:
            WeatherData object
        """
        cached = cache_get(self._cache, "current")
        if cached is not None:
            logger.debug("Returning cached weather data")
            return cached
        return self._fetch_and_cache()


def get_current_weather(service: WeatherService) -> WeatherData:
    """Get current weather from service."""
    return service.get_current_weather()


def is_weather_time(service: WeatherService, when: datetime) -> bool:
    """Check if it's time for weather announcement."""
    # Announce at 6:00, 12:00, and 17:00
    return when.minute == 0 and when.hour in (6, 12, 17)


def format_weather_for_dj(weather: WeatherData, units: str = "imperial") -> str:
    """Format weather data for DJ announcement.
    
    Args:
        weather: WeatherData object
        units: Unit system ("imperial" or "metric")
        
    Returns:
        Formatted weather string
    """
    # Temperature
    if weather.temperature is not None:
        temp = int(weather.temperature)
        unit = "degrees" if units == "imperial" else "degrees Celsius"
        temp_text = f"{temp} {unit}"
    else:
        temp_text = "mild temperatures"
    
    # Conditions
    if weather.description:
        cond_text = weather.description
    elif weather.conditions:
        cond_text = weather.conditions.lower()
    else:
        cond_text = "pleasant weather"
    
    # Additional details
    extras = []
    if weather.humidity and weather.humidity > 70:
        extras.append("humid conditions")
    if weather.wind_speed and weather.wind_speed > 15:
        extras.append("breezy")
    
    extra_text = f" with {' and '.join(extras)}" if extras else ""
    
    # Construct period-style announcement
    return f"Looking outside, we've got {cond_text} with {temp_text}{extra_text}. "
```

**File: `src/ai_radio/services/cache.py`**

Add ignore_expiry option:

```python
def cache_get(cache: ServiceCache, key: str, ignore_expiry: bool = False) -> Optional[Any]:
    """Get cached value if not expired.
    
    Args:
        cache: ServiceCache instance
        key: Cache key
        ignore_expiry: Return value even if expired
        
    Returns:
        Cached value or None
    """
    entry = cache._cache.get(key)
    if entry is None:
        return None
    
    if ignore_expiry:
        return entry.value
    
    if entry.is_expired():
        return None
    
    return entry.value
```

## Success Criteria

> Note: This project uses Open‑Meteo (openmeteo_requests) for live weather data rather than OpenWeatherMap. The checklist below is satisfied using Open‑Meteo.

### Functionality
- [x] Open‑Meteo client fetches real weather data
- [x] API key configuration works via environment variable (provider-specific; Open‑Meteo does not require a key)
- [x] Location is configurable (via `WEATHER_LATITUDE`, `WEATHER_LONGITUDE`, `WEATHER_TIMEZONE`)
- [x] Units (F/C) are configurable (`WEATHER_UNITS`)
- [x] Caching prevents excessive API calls (service-level cache + `requests_cache`, default 30 minutes)
- [x] Fallback to fake data when API unavailable (fallback client)
- [x] Expired cache used as fallback during API failures

### Quality
- [x] Error handling for API failures (network, parsing, timeouts)
- [x] Proper logging at various levels (debug, info, warning, error)
- [x] Timeout prevents hanging requests (`WEATHER_API_TIMEOUT` applied to API call)
- [x] API response parsing is robust (safe indexing and fallbacks)
- [x] Weather data includes rich information (temperature, conditions, humidity, wind)

### Testing
- [x] Unit tests with mocked API clients and error scenarios
- [x] Integration test with real API (optional, marked integration)
- [x] Test error scenarios (timeout, generic failures) and fallback behavior
- [x] Test caching behavior (including reuse of expired cache as fallback)


## Validation Commands

```bash
# Set up API key (get free key from openweathermap.org)
echo "OPENWEATHER_API_KEY=your_key_here" >> .env
echo "OPENWEATHER_LOCATION=Las Vegas,US" >> .env

# Test API client directly
python -c "
from src.ai_radio.services.weather_api import create_weather_client

client = create_weather_client()
weather = client.fetch_current_weather()
print(f'Temperature: {weather.temperature}°')
print(f'Conditions: {weather.conditions}')
print(f'Description: {weather.description}')
print(f'Humidity: {weather.humidity}%')
print(f'Wind: {weather.wind_speed} mph')
"

# Test WeatherService with real API
python -c "
from src.ai_radio.services.weather import WeatherService, format_weather_for_dj

service = WeatherService()
weather = service.get_current_weather()
formatted = format_weather_for_dj(weather)
print(formatted)
"

# Test caching (should only make one API call)
python -c "
from src.ai_radio.services.weather import WeatherService

service = WeatherService()
w1 = service.get_current_weather()
w2 = service.get_current_weather()
w3 = service.get_current_weather()
print(f'All requests returned same data: {w1 == w2 == w3}')
"

# Test fallback when API key missing
python -c "
import os
os.environ.pop('OPENWEATHER_API_KEY', None)
from src.ai_radio.services.weather import WeatherService

service = WeatherService()
weather = service.get_current_weather()
print(f'Fallback temp: {weather.temperature}')
"

# Run unit tests
.venv/Scripts/pytest tests/test_weather_api.py -v
.venv/Scripts/pytest tests/test_services_weather.py -v
```

## Anti-Regression Tests

```python
# tests/test_weather_api.py

import pytest
import responses
from ai_radio.services.weather_api import OpenWeatherClient, WeatherData


@pytest.fixture
def mock_api_response():
    """Mock OpenWeatherMap API response."""
    return {
        "main": {
            "temp": 72.5,
            "humidity": 65
        },
        "weather": [{
            "main": "Clouds",
            "description": "scattered clouds"
        }],
        "wind": {
            "speed": 8.5
        }
    }


@responses.activate
def test_fetch_current_weather_success(mock_api_response):
    """Should successfully fetch and parse weather data."""
    responses.add(
        responses.GET,
        "https://api.openweathermap.org/data/2.5/weather",
        json=mock_api_response,
        status=200
    )
    
    client = OpenWeatherClient(
        api_key="test_key",
        location="Test City,US"
    )
    
    weather = client.fetch_current_weather()
    
    assert weather.temperature == 72.5
    assert weather.conditions == "Clouds"
    assert weather.description == "scattered clouds"
    assert weather.humidity == 65
    assert weather.wind_speed == 8.5


@responses.activate
def test_fetch_weather_timeout():
    """Should raise exception on timeout."""
    responses.add(
        responses.GET,
        "https://api.openweathermap.org/data/2.5/weather",
        body=Exception("Timeout")
    )
    
    client = OpenWeatherClient(
        api_key="test_key",
        location="Test City,US",
        timeout=1
    )
    
    with pytest.raises(Exception):
        client.fetch_current_weather()


@responses.activate
def test_fetch_weather_invalid_key():
    """Should handle invalid API key gracefully."""
    responses.add(
        responses.GET,
        "https://api.openweathermap.org/data/2.5/weather",
        json={"cod": 401, "message": "Invalid API key"},
        status=401
    )
    
    client = OpenWeatherClient(
        api_key="invalid_key",
        location="Test City,US"
    )
    
    with pytest.raises(Exception):
        client.fetch_current_weather()


def test_missing_api_key():
    """Should raise error when API key not provided."""
    client = OpenWeatherClient(
        api_key="",
        location="Test City,US"
    )
    
    with pytest.raises(ValueError, match="API key not configured"):
        client.fetch_current_weather()


# tests/test_services_weather.py

def test_weather_service_with_mock_client():
    """WeatherService should work with injected client."""
    from ai_radio.services.weather import WeatherService, WeatherData
    
    mock_weather = WeatherData(
        temperature=75,
        conditions="Sunny",
        description="clear sky"
    )
    
    mock_client = lambda: mock_weather
    service = WeatherService(api_client=mock_client)
    
    weather = service.get_current_weather()
    assert weather.temperature == 75
    assert weather.conditions == "Sunny"


def test_weather_service_caching():
    """WeatherService should cache results."""
    from ai_radio.services.weather import WeatherService, WeatherData
    
    call_count = 0
    
    def counting_client():
        nonlocal call_count
        call_count += 1
        return WeatherData(temperature=70, conditions="Clear")
    
    service = WeatherService(api_client=counting_client)
    
    # Multiple calls should only hit API once
    service.get_current_weather()
    service.get_current_weather()
    service.get_current_weather()
    
    assert call_count == 1


def test_weather_service_fallback_on_error():
    """WeatherService should fallback to fake data on API error."""
    from ai_radio.services.weather import WeatherService
    
    def failing_client():
        raise Exception("API error")
    
    service = WeatherService(
        api_client=failing_client,
        enable_fallback=True
    )
    
    # Should not raise, should return fallback
    weather = service.get_current_weather()
    assert weather.temperature is not None
```

## Git Commit

```bash
git add .env.example
git add src/ai_radio/config.py
git add src/ai_radio/services/weather_api.py
git add src/ai_radio/services/weather.py
git add src/ai_radio/services/cache.py
git add tests/test_weather_api.py
git add tests/test_services_weather.py
git add requirements.txt  # Add requests if not present
git commit -m "feat(weather): integrate OpenWeatherMap API

- Add OpenWeatherClient for fetching real weather data
- Support API key configuration via environment variables
- Add robust error handling and timeout support
- Implement fallback to fake data when API unavailable
- Use expired cache as fallback during API failures
- Extend WeatherData with humidity and wind information
- Enhance format_weather_for_dj() with richer formatting
- Add comprehensive tests for API client and service
"
```

## Dependencies
- **Requires**: Checkpoint 6.2 (Weather Service) - Basic implementation must exist
- **Requires**: `requests` library - Add to requirements.txt
- **Requires**: `responses` library for testing - Add to dev requirements
- **Requires**: OpenWeatherMap API key (free tier available)
- **Enhances**: Checkpoint 2.7 (Batch Weather Announcements) - Will use real data

## Notes
- OpenWeatherMap free tier allows 60 calls/minute, 1,000,000 calls/month.
- Default 30-minute cache prevents excessive API usage (48 calls/day max).
- Fallback behavior ensures station continues running even without API access.
- Consider implementing weather forecast support for future enhancements.
- Alternative APIs: WeatherAPI, Weatherstack, Visual Crossing (if OpenWeather unavailable).
- Units are configurable (imperial=Fahrenheit, metric=Celsius).

## Getting Started

1. Sign up for free OpenWeatherMap API key: https://openweathermap.org/api
2. Add key to `.env` file:
   ```bash
   OPENWEATHER_API_KEY=your_api_key_here
   OPENWEATHER_LOCATION=Your City,US
   ```
3. Install requirements: `pip install requests responses`
4. Run tests: `pytest tests/test_weather_api.py -v`
5. Test live API: See validation commands above
