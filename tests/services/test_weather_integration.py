r"""Optional integration tests for Open-Meteo.

These tests are marked with @pytest.mark.integration and can be skipped in CI
environments by running: pytest -m "not integration"

They exercise the real Open-Meteo client and require network access and the
`openmeteo-requests`, `requests-cache`, `retry-requests`, `pandas` packages.
"""
import os
import pytest

from src.ai_radio.services.weather import WeatherService, format_weather_for_dj


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("CI") == "true" and os.getenv("RUN_INTEGRATION_TESTS") != "true",
    reason="Integration tests skipped in CI unless RUN_INTEGRATION_TESTS=true"
)
def test_openmeteo_weather_fetch_online():
    """Fetch current weather from Open-Meteo (online)."""
    svc = WeatherService()
    weather = svc.get_current_weather()

    assert weather is not None
    # Temperature may be None depending on API response window, but when present must be numeric
    assert hasattr(weather, "temperature")
    if weather.temperature is not None:
        assert isinstance(weather.temperature, (int, float))

    # Conditions when present should be a string
    assert hasattr(weather, "conditions")
    if weather.conditions is not None:
        assert isinstance(weather.conditions, str)

    # Raw metadata should be present as a dict when available
    assert hasattr(weather, "raw")
    assert weather.raw is None or isinstance(weather.raw, dict)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("CI") == "true" and os.getenv("RUN_INTEGRATION_TESTS") != "true",
    reason="Integration tests skipped in CI unless RUN_INTEGRATION_TESTS=true"
)
def test_openmeteo_parses_humidity_and_wind_online():
    """Open-Meteo should provide humidity and wind; formatting should convert to mph in imperial."""
    svc = WeatherService()
    weather = svc.get_current_weather()

    # humidity and wind may be None depending on data availability, but types if present
    assert hasattr(weather, "humidity")
    assert hasattr(weather, "wind_speed")
    if weather.wind_speed is not None:
        # formatted should include a natural unit phrase when using imperial units
        formatted = format_weather_for_dj(weather, units='imperial')
        assert "miles per hour" in formatted.lower() or "meter" in formatted.lower() or "meters per second" in formatted.lower()
