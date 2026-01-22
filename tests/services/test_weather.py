"""Tests for weather service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from src.ai_radio.services.weather import (
    WeatherService,
    get_current_weather,
    is_weather_time,
    format_weather_for_dj,
    WeatherData,
)


class TestWeatherFetch:
    """Test weather data fetching."""

    def test_returns_weather_data(self, mock_weather_api):
        """Must return WeatherData object."""
        service = WeatherService(api_client=mock_weather_api)
        weather = get_current_weather(service)
        assert isinstance(weather, WeatherData)

    def test_weather_has_temperature(self, mock_weather_api):
        """Weather must include temperature."""
        service = WeatherService(api_client=mock_weather_api)
        weather = get_current_weather(service)
        assert weather.temperature is not None

    def test_weather_has_conditions(self, mock_weather_api):
        """Weather must include conditions description."""
        service = WeatherService(api_client=mock_weather_api)
        weather = get_current_weather(service)
        assert weather.conditions is not None

    def test_caches_results(self, mock_weather_api):
        """Must cache results to avoid API spam."""
        service = WeatherService(api_client=mock_weather_api)

        get_current_weather(service)
        get_current_weather(service)

        # API should only be called once
        assert mock_weather_api.call_count == 1

    def test_cache_expires(self, mock_weather_api):
        """Cache must expire after timeout."""
        service = WeatherService(api_client=mock_weather_api, cache_minutes=1)

        get_current_weather(service)

        # Simulate time passing
        service._cache._entries["current"].created = datetime.now() - timedelta(minutes=2)

        get_current_weather(service)

        # API should be called twice
        assert mock_weather_api.call_count == 2


class TestWeatherTiming:
    """Test weather announcement timing."""

    def test_weather_at_6am(self):
        """Must announce weather at 6 AM."""
        service = WeatherService()
        six_am = datetime(2026, 1, 22, 6, 0)
        assert is_weather_time(service, six_am)

    def test_weather_at_noon(self):
        """Must announce weather at 12 PM."""
        service = WeatherService()
        noon = datetime(2026, 1, 22, 12, 0)
        assert is_weather_time(service, noon)

    def test_weather_at_5pm(self):
        """Must announce weather at 5 PM."""
        service = WeatherService()
        five_pm = datetime(2026, 1, 22, 17, 0)
        assert is_weather_time(service, five_pm)

    def test_no_weather_at_3pm(self):
        """Must not announce weather at 3 PM."""
        service = WeatherService()
        three_pm = datetime(2026, 1, 22, 15, 0)
        assert not is_weather_time(service, three_pm)


class TestWeatherFormatting:
    """Test period-style weather formatting."""

    def test_format_includes_temperature(self):
        """Formatted weather must include temperature."""
        weather = WeatherData(temperature=45, conditions="cloudy")
        formatted = format_weather_for_dj(weather)
        assert "45" in formatted

    def test_format_is_period_style(self):
        """Format should be period-flavored, not clinical."""
        weather = WeatherData(temperature=25, conditions="snow")
        formatted = format_weather_for_dj(weather)
        # Should use colorful language, not just "25 degrees snow"
        assert len(formatted) > 20  # More than minimal
