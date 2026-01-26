"""E2E test marker registration.

All tests in this package are automatically marked as @pytest.mark.e2e.
"""

def pytest_collection_modifyitems(items):
    """Auto-mark all tests in this package as e2e."""
    import pytest
    for item in items:
        if 'e2e' in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

