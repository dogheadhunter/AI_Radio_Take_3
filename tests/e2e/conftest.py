"""Pytest fixtures for Playwright E2E tests of the Review GUI.

This module provides fixtures for running end-to-end tests with Playwright.
"""
import pytest
import time
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page


# Streamlit configuration
STREAMLIT_URL = "http://localhost:8501"
STREAMLIT_PORT = 8501
STREAMLIT_STARTUP_TIMEOUT = 15  # seconds


@pytest.fixture(scope="session")
def browser():
    """Launch browser for the entire test session.
    
    Uses Chromium in headless mode by default.
    Can be overridden with --headed flag.
    
    Yields:
        Browser: Playwright browser instance
    """
    with sync_playwright() as p:
        # Launch browser (headless by default)
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser):
    """Create a new page for each test.
    
    Navigates to the Streamlit app and waits for it to be ready.
    
    Args:
        browser: Browser fixture from session
        
    Yields:
        Page: Playwright page instance at Streamlit URL
    """
    page = browser.new_page()
    page.goto(STREAMLIT_URL)
    
    # Wait for Streamlit to be fully loaded
    # Streamlit uses a specific class when ready
    page.wait_for_load_state("networkidle")
    
    # Wait for main heading to ensure app is rendered
    try:
        page.wait_for_selector("h1", timeout=10000)
    except Exception:
        # If heading doesn't appear, at least wait for basic load
        time.sleep(2)
    
    yield page
    page.close()


@pytest.fixture
def mobile_page(browser: Browser):
    """Create a mobile viewport page for each test.
    
    Uses iPhone X dimensions (375x812) for mobile testing.
    
    Args:
        browser: Browser fixture from session
        
    Yields:
        Page: Playwright page instance with mobile viewport
    """
    # iPhone X viewport
    page = browser.new_page(viewport={"width": 375, "height": 812})
    page.goto(STREAMLIT_URL)
    
    # Wait for Streamlit to be fully loaded
    page.wait_for_load_state("networkidle")
    
    # Wait for main heading
    try:
        page.wait_for_selector("h1", timeout=10000)
    except Exception:
        time.sleep(2)
    
    yield page
    page.close()


@pytest.fixture(scope="session")
def streamlit_server():
    """Start Streamlit server for the entire test session.
    
    This fixture starts the Review GUI before tests run and stops it after.
    Only use this if Streamlit is not already running.
    
    Yields:
        subprocess.Popen: The Streamlit server process
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent
    gui_script = project_root / "review_gui.py"
    
    if not gui_script.exists():
        pytest.skip(f"Review GUI not found at {gui_script}")
    
    # Start Streamlit server
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(gui_script),
            f"--server.port={STREAMLIT_PORT}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(project_root),
    )
    
    # Wait for server to be ready
    print(f"Starting Streamlit server on port {STREAMLIT_PORT}...")
    time.sleep(STREAMLIT_STARTUP_TIMEOUT)
    
    # Verify server started
    if process.poll() is not None:
        # Process exited, something went wrong
        stdout, stderr = process.communicate()
        pytest.fail(
            f"Streamlit failed to start:\nSTDOUT:\n{stdout.decode()}\nSTDERR:\n{stderr.decode()}"
        )
    
    print(f"Streamlit server started successfully at {STREAMLIT_URL}")
    
    yield process
    
    # Cleanup - terminate Streamlit server
    print("Stopping Streamlit server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    print("Streamlit server stopped")
