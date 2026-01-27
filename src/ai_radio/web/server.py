"""
Flask server for AI Radio web streaming interface.

Provides a simple web UI with a tune-in button for 24/7 radio playback.
"""
from flask import Flask, Response, send_from_directory, jsonify
from pathlib import Path
import threading
import time
import io
from typing import Generator

from src.ai_radio.station.controller import StationController
from src.ai_radio.utils.logging import setup_logging

logger = setup_logging("radio_server")

# Global controller instance
_controller = None
_controller_lock = threading.Lock()


def get_controller() -> StationController:
    """Get or create the station controller singleton."""
    global _controller
    with _controller_lock:
        if _controller is None:
            _controller = StationController()
        return _controller


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder=str(Path(__file__).parent / 'static'),
                static_url_path='')
    
    @app.route('/')
    def index():
        """Serve the main tune-in page."""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'ok',
            'service': 'AI Radio',
            'timestamp': time.time()
        })
    
    @app.route('/stream')
    def stream():
        """
        Stream audio endpoint.
        
        Note: This is a placeholder for the streaming endpoint.
        In a production system, this would:
        1. Connect to the station controller's audio output
        2. Stream audio chunks in real-time
        3. Handle reconnections and buffering
        
        For MVP, we'll use a simple approach that signals the controller
        to start playing and provides a continuous audio stream.
        """
        def generate() -> Generator[bytes, None, None]:
            """Generate audio stream chunks."""
            # For MVP, we'll provide a simple response
            # In production, this would stream actual audio data
            controller = get_controller()
            
            # This is a placeholder - real implementation would:
            # - Start the station controller if not running
            # - Capture audio output
            # - Stream it in chunks
            
            # For now, send a simple message
            yield b"AI Radio stream - implementation pending"
        
        return Response(generate(), mimetype='audio/mpeg')
    
    @app.route('/api/status')
    def status():
        """Get current playback status."""
        try:
            controller = get_controller()
            return jsonify({
                'playing': True,  # Placeholder
                'current_track': 'AI Radio - 24/7 Golden Age Hits'
            })
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask server."""
    logger.info(f"Starting AI Radio web server on {host}:{port}")
    app = create_app()
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    # Only enable debug mode if explicitly requested via CLI
    # Direct execution is for testing only - use scripts/run_radio_server.py
    import sys
    debug = '--debug' in sys.argv
    run_server(debug=debug)
