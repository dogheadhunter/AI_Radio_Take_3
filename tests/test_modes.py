"""Configuration for test modes - mock vs integration."""
import os
from typing import Literal

TestMode = Literal["mock", "integration"]


def get_test_mode() -> TestMode:
    """Get current test mode from environment.
    
    Set TEST_MODE=integration to run real integration tests.
    Defaults to 'mock' for fast testing.
    """
    mode = os.getenv("TEST_MODE", "mock").lower()
    if mode not in ("mock", "integration"):
        raise ValueError(f"Invalid TEST_MODE: {mode}. Use 'mock' or 'integration'")
    return mode  # type: ignore


def is_mock_mode() -> bool:
    """Check if we're in mock mode (fast tests)."""
    return get_test_mode() == "mock"


def is_integration_mode() -> bool:
    """Check if we're in integration mode (real services)."""
    return get_test_mode() == "integration"
