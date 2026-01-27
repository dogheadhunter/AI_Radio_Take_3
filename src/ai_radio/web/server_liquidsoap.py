"""
Flask server for Golden Age Of Radio Broadcast - Liquidsoap proxy.

Proxies the continuous stream from Liquidsoap to browsers.
"""
from flask import Flask, send_from_directory, Response, jsonify
import requests
import os

# Get static folder path
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, 
            static_folder=STATIC_FOLDER,
            static_url_path='')

# Liquidsoap URLs
LIQUIDSOAP_STREAM = "http://localhost:8000/stream"
LIQUIDSOAP_METADATA = "http://localhost:8000/metadata"

@app.route('/')
def index():
    """Serve the main radio UI page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/stream')
def stream():
    """Proxy the continuous Liquidsoap stream with optimized buffering"""
    print("🎵 Client tuning in - proxying from Liquidsoap...")
    try:
        session = requests.Session()
        req = session.get(LIQUIDSOAP_STREAM, stream=True, timeout=10)
        
        return Response(
            req.iter_content(chunk_size=16384),
            content_type='audio/x-wav',
            direct_passthrough=True,
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Accept-Ranges': 'none',
                'X-Content-Type-Options': 'nosniff'
            }
        )
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Liquidsoap on port 8000")
        print("   Make sure Liquidsoap is running!")
        return "Liquidsoap stream unavailable. Is it running?", 503
    except Exception as e:
        print(f"❌ Error proxying stream: {e}")
        return f"Stream error: {e}", 503

@app.route('/api/now-playing')
def now_playing():
    """Fetch current track metadata from Liquidsoap"""
    try:
        resp = requests.get(LIQUIDSOAP_METADATA, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return jsonify({
                'artist': data.get('artist', 'Unknown Artist'),
                'title': data.get('title', 'Unknown Title'),
                'status': 'live'
            })
        else:
            return jsonify({'error': 'Metadata unavailable'}), 503
    except Exception as e:
        print(f"❌ Metadata fetch failed: {e}")
        return jsonify({'error': str(e)}), 503

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Golden Age Radio'})

def run_server(host='0.0.0.0', port=8501):
    """Run the Flask server with optimized settings"""
    print(f"🎵 Golden Age Radio Flask proxy starting on http://{host}:{port}")
    print(f"   Proxying Liquidsoap stream from {LIQUIDSOAP_STREAM}")
    print(f"   Make sure Liquidsoap is running first!")
    
    try:
        from waitress import serve
        print("   Using Waitress WSGI server for better performance")
        serve(app, host=host, port=port, threads=4, channel_timeout=300)
    except ImportError:
        print("   Using Flask dev server (install 'waitress' for better performance)")
        app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()
