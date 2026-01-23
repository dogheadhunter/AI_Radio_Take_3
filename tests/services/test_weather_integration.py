r"""Optional integration tests for Open-Meteo.

These tests are marked with @pytest.mark.integration and can be skipped in CI
environments by running: pytest -m "not integration"

They exercise the real Open-Meteo client and require network access and the
`openmeteo-requests`, `requests-cache`, `retry-requests`, `pandas` packages.
"""
import os
import pytest

from src.ai_radio.services.weather import WeatherService


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
