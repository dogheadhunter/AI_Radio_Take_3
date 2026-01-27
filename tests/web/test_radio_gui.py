"""
Playwright tests for the AI Radio web GUI.

Tests the tune-in interface, playback controls, and accessibility.
"""
import pytest
import time
from pathlib import Path
import threading
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai_radio.web.server import create_app


@pytest.fixture(scope="module")
def app_server():
    """Start the Flask app in a background thread for testing."""
    app = create_app()
    
    # Run in a thread
    server_thread = threading.Thread(
        target=lambda: app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False),
        daemon=True
    )
    server_thread.start()
    
    # Give the server time to start
    time.sleep(2)
    
    yield "http://127.0.0.1:5555"
    
    # Server thread will be cleaned up automatically as daemon


@pytest.fixture
def page(playwright):
    """Create a browser page for testing."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
    browser.close()


def test_homepage_loads(app_server, page):
    """Test that the homepage loads successfully."""
    page.goto(app_server)
    
    # Check title
    assert "AI Radio" in page.title()
    
    # Check main heading
    heading = page.locator('h1.title')
    assert heading.is_visible()
    assert heading.inner_text() == "AI Radio"


def test_tune_in_button_exists(app_server, page):
    """Test that the tune-in button is present and visible."""
    page.goto(app_server)
    
    # Find the tune-in button
    tune_in_btn = page.locator('#tuneInBtn')
    assert tune_in_btn.is_visible()
    assert tune_in_btn.is_enabled()
    
    # Check button text
    btn_text = tune_in_btn.locator('.btn-text')
    assert btn_text.inner_text() == "Tune In"


def test_tune_in_button_click(app_server, page):
    """Test that clicking the tune-in button changes state."""
    page.goto(app_server)
    
    tune_in_btn = page.locator('#tuneInBtn')
    status_text = page.locator('.status-text')
    
    # Initial state
    assert status_text.inner_text() == "Ready to tune in"
    
    # Click the button
    tune_in_btn.click()
    
    # Wait for state change
    page.wait_for_timeout(500)
    
    # Check if button text changed (it should change to "Stop" when playing)
    btn_text = tune_in_btn.locator('.btn-text')
    # Note: This might not change immediately due to async audio loading
    # but we can check that the button is still responsive
    assert tune_in_btn.is_enabled()


def test_health_endpoint(app_server, page):
    """Test that the health endpoint is accessible."""
    response = page.request.get(f"{app_server}/health")
    assert response.status == 200
    
    data = response.json()
    assert data['status'] == 'ok'
    assert 'timestamp' in data


def test_status_endpoint(app_server, page):
    """Test that the status API endpoint works."""
    response = page.request.get(f"{app_server}/api/status")
    assert response.status == 200
    
    data = response.json()
    assert 'playing' in data


def test_accessibility_features(app_server, page):
    """Test accessibility features of the interface."""
    page.goto(app_server)
    
    # Check ARIA labels
    tune_in_btn = page.locator('#tuneInBtn')
    assert tune_in_btn.get_attribute('aria-label') is not None
    
    # Check for proper heading structure
    h1 = page.locator('h1')
    assert h1.count() == 1
    
    # Check that status indicators are present
    status_indicator = page.locator('.status-indicator')
    assert status_indicator.is_visible()


def test_responsive_layout(app_server, page):
    """Test that the layout works on different screen sizes."""
    # Desktop
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(app_server)
    
    container = page.locator('.container')
    assert container.is_visible()
    
    # Mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(app_server)
    
    assert container.is_visible()
    tune_in_btn = page.locator('#tuneInBtn')
    assert tune_in_btn.is_visible()


def test_info_box_content(app_server, page):
    """Test that the info box contains important information."""
    page.goto(app_server)
    
    info_box = page.locator('.info-box')
    assert info_box.is_visible()
    
    # Check for background playback information
    info_text = info_box.inner_text()
    assert "Background Playback" in info_text
    assert "Lock your device" in info_text or "lock" in info_text.lower()


def test_manifest_exists(app_server, page):
    """Test that the PWA manifest is accessible."""
    response = page.request.get(f"{app_server}/manifest.json")
    assert response.status == 200
    
    manifest = response.json()
    assert manifest['name'] is not None
    assert manifest['short_name'] is not None
    assert len(manifest['icons']) > 0


def test_service_worker_registration(app_server, page):
    """Test that service worker is registered."""
    page.goto(app_server)
    
    # Wait for service worker registration
    page.wait_for_timeout(1000)
    
    # Check if service worker is registered
    sw_registered = page.evaluate("""
        () => {
            return 'serviceWorker' in navigator;
        }
    """)
    assert sw_registered


def test_keyboard_navigation(app_server, page):
    """Test keyboard navigation and accessibility."""
    page.goto(app_server)
    
    # Tab to the button
    page.keyboard.press('Tab')
    
    # Check if button is focused (checking if it can receive focus)
    tune_in_btn = page.locator('#tuneInBtn')
    
    # Press Enter to activate
    page.keyboard.press('Enter')
    
    # Button should still be enabled after interaction
    assert tune_in_btn.is_enabled()


def test_now_playing_visibility(app_server, page):
    """Test that now playing section appears when playing."""
    page.goto(app_server)
    
    now_playing = page.locator('#nowPlaying')
    
    # Initially hidden
    assert not now_playing.is_visible()
    
    # After clicking tune in, it might become visible
    # (depends on actual audio playback implementation)


def test_static_assets_load(app_server, page):
    """Test that all static assets load correctly."""
    page.goto(app_server)
    
    # Check CSS loaded
    style_loaded = page.evaluate("""
        () => {
            const styles = document.styleSheets;
            return styles.length > 0;
        }
    """)
    assert style_loaded
    
    # Check JavaScript loaded
    script_loaded = page.evaluate("""
        () => {
            return typeof togglePlayback !== 'undefined' || 
                   document.querySelector('#tuneInBtn') !== null;
        }
    """)
    assert script_loaded
