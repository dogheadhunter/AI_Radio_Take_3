import pytest
from unittest.mock import Mock
from src.ai_radio.services.weather import WeatherData


@pytest.fixture
def mock_weather_api():
    """Provides a mock API callable for the WeatherService and tracks calls."""
    mock = Mock()
    # Return a WeatherData instance so the service gets the expected type
    mock.return_value = WeatherData(temperature=45, conditions="cloudy")
    return mock
