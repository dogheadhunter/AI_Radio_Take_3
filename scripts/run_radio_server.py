#!/usr/bin/env python3
"""
Launch the AI Radio web server for 24/7 streaming.

Usage:
    python scripts/run_radio_server.py [--host HOST] [--port PORT] [--debug]

Example:
    python scripts/run_radio_server.py --port 8080
    python scripts/run_radio_server.py --host 0.0.0.0 --port 5000 --debug
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_radio.web.server import run_server
from src.ai_radio.utils.logging import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Radio Web Server - Stream 24/7 radio with a simple tune-in interface"
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with auto-reload'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    logger = setup_logging("run_radio_server")
    
    print("=" * 60)
    print("AI RADIO - WEB STREAMING SERVER")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print(f"\nOpen your browser to: http://localhost:{args.port}")
    print("=" * 60)
    print()
    
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\nServer stopped.")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
