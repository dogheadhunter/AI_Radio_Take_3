"""
AI Radio Station - Main entry point
"""
import sys
import signal
import argparse
import time

from src.ai_radio.station.controller import StationController, start_station, stop_station
from src.ai_radio.station.display import StationDisplay
from src.ai_radio.station.commands import CommandHandler
from src.ai_radio.utils.logging import setup_logging
from src.ai_radio.config import CATALOG_FILE


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Radio Station - Your personal Golden Age radio experience"
    )
    parser.add_argument('--dry-run', action='store_true', help='Show configuration and exit')
    parser.add_argument('--no-weather', action='store_true', help='Disable weather announcements')
    parser.add_argument('--no-shows', action='store_true', help='Disable radio shows')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    return parser.parse_args()


def main():
    args = parse_args()
    logger = setup_logging("main")

    if args.dry_run:
        print("AI Radio Station - Configuration")
        print("=" * 50)
        print(f"Catalog: {CATALOG_FILE}")
        print(f"Catalog exists: {CATALOG_FILE.exists()}")
        if CATALOG_FILE.exists():
            from src.ai_radio.library.catalog import load_catalog
            catalog = load_catalog(CATALOG_FILE)
            print(f"Songs in catalog: {len(catalog)}")
        print(f"Weather enabled: {not args.no_weather}")
        print(f"Shows enabled: {not args.no_shows}")
        return 0

    if not CATALOG_FILE.exists():
        print(f"Error:  Catalog not found at {CATALOG_FILE}")
        print("Run 'python scripts/scan_library.py <music_path>' first.")
        return 1

    logger.info("Starting AI Radio Station...")

    controller = StationController(
        config_overrides={
            'weather_enabled': not args.no_weather,
            'shows_enabled': not args.no_shows,
        }
    )
    display = StationDisplay()
    commands = CommandHandler(controller)

    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        stop_station(controller)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        start_station(controller)
        commands.start()
        logger.info("Station is now playing!")

        while controller.is_running:
            status = controller.get_status()
            display.update(status)
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
