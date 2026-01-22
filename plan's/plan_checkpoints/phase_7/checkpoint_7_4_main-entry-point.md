# Checkpoint 7.4: Main Entry Point

#### Checkpoint 7.4: Main Entry Point
**Create the main script to run the station.**

**Tasks:**
1. Create `src/ai_radio/main.py`
2. Parse command-line arguments
3. Initialize and run station
4. Handle graceful shutdown

**File:  `src/ai_radio/main.py`**
```python
"""
AI Radio Station - Main Entry Point

Usage:
    python -m ai_radio
    python -m ai_radio --config custom_config.py
    python -m ai_radio --dry-run

Options:
    --dry-run       Show configuration and exit
    --no-weather    Disable weather announcements
    --no-shows      Disable radio shows
    --debug         Enable debug logging
"""
import sys
import signal
import argparse
from pathlib import Path

from src.ai_radio.station.controller import StationController, start_station, stop_station
from src.ai_radio.station.display import StationDisplay
from src.ai_radio. station.commands import CommandHandler
from src.ai_radio.utils.logging import setup_logging
from src.ai_radio.config import CATALOG_FILE


def parse_args():
    """Parse command line arguments."""
    parser = argparse. ArgumentParser(
        description="AI Radio Station - Your personal Golden Age radio experience"
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show configuration and exit')
    parser.add_argument('--no-weather', action='store_true',
                        help='Disable weather announcements')
    parser.add_argument('--no-shows', action='store_true',
                        help='Disable radio shows')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    logger = setup_logging("main")
    
    # Dry run - just show config
    if args. dry_run: 
        print("AI Radio Station - Configuration")
        print("=" * 50)
        print(f"Catalog: {CATALOG_FILE}")
        print(f"Catalog exists: {CATALOG_FILE.exists()}")
        if CATALOG_FILE. exists():
            from src.ai_radio.library.catalog import load_catalog
            catalog = load_catalog(CATALOG_FILE)
            print(f"Songs in catalog: {len(catalog)}")
        print(f"Weather enabled: {not args. no_weather}")
        print(f"Shows enabled: {not args.no_shows}")
        return 0
    
    # Check prerequisites
    if not CATALOG_FILE.exists():
        print(f"Error:  Catalog not found at {CATALOG_FILE}")
        print("Run 'python scripts/scan_library.py <music_path>' first.")
        return 1
    
    # Initialize station
    logger.info("Starting AI Radio Station...")
    
    controller = StationController(
        config_overrides={
            'weather_enabled': not args. no_weather,
            'shows_enabled': not args.no_shows,
        }
    )
    display = StationDisplay()
    commands = CommandHandler(controller)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        stop_station(controller)
        sys.exit(0)
    
    signal. signal(signal. SIGINT, signal_handler)
    
    # Start everything
    try: 
        start_station(controller)
        commands.start()
        
        logger.info("Station is now playing!")
        
        # Main loop
        while controller.is_running:
            status = controller.get_status()
            display.update(status)
            
            # Small sleep to prevent CPU spinning
            import time
            time.sleep(0.1)
    
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1
    
    finally:
        commands.stop()
        stop_station(controller)
        logger.info("Station stopped")
    
    return 0


if __name__ == "__main__": 
    sys.exit(main())
```

**Tests for Main:**
```python
# tests/station/test_main. py
"""Tests for main entry point."""
import pytest
from unittest.mock import Mock, patch
from src.ai_radio.main import parse_args, main


class TestParseArgs:
    """Test argument parsing."""
    
    def test_dry_run_flag(self):
        """--dry-run flag must be parsed."""
        with patch('sys.argv', ['main', '--dry-run']):
            args = parse_args()
            assert args.dry_run is True
    
    def test_no_weather_flag(self):
        """--no-weather flag must be parsed."""
        with patch('sys.argv', ['main', '--no-weather']):
            args = parse_args()
            assert args.no_weather is True
    
    def test_defaults(self):
        """Default values must be correct."""
        with patch('sys.argv', ['main']):
            args = parse_args()
            assert args.dry_run is False
            assert args.no_weather is False
            assert args.no_shows is False


class TestMain: 
    """Test main function."""
    
    def test_dry_run_exits_zero(self, mock_catalog_exists):
        """Dry run must exit with code 0."""
        with patch('sys.argv', ['main', '--dry-run']):
            result = main()
            assert result == 0
    
    def test_missing_catalog_exits_one(self, mock_catalog_missing):
        """Missing catalog must exit with code 1."""
        with patch('sys. argv', ['main']):
            result = main()
            assert result == 1
```

**Success Criteria:**
- [ ] All main tests pass
- [ ] `--dry-run` shows configuration
- [ ] Station starts with valid configuration
- [ ] Ctrl+C stops station gracefully
- [ ] Exit codes are correct

**Git Commit:** `feat(station): add main entry point`
