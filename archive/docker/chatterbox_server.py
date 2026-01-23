"""
Flask server wrapper for Chatterbox TTS that provides a /synthesize endpoint.
Compatible with AI_Radio TTSClient interface.

Local-only server - uses chatterbox-src in the repository.
"""
from flask import Flask, request, jsonify, send_file
import tempfile
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global model instance
model = None

def get_chatterbox_path():
    """Get the Chatterbox source path from the repository."""
    # Primary: chatterbox/src in the repo root
    repo_path = Path(__file__).parent.parent / "chatterbox" / "src"
    if repo_path.exists():
        return str(repo_path)
    
    # Fallback: environment variable
    env_path = os.environ.get("CHATTERBOX_SRC")
    if env_path and os.path.exists(env_path):
        return env_path
    
    raise RuntimeError(
        f"Chatterbox source not found. Expected at: {repo_path}\n"
        "Install with: .venv\\Scripts\\pip install -e ./chatterbox"
    )

def load_chatterbox():
    """Load Chatterbox model on startup"""
    global model
    
    # Add chatterbox to path
    chatterbox_path = get_chatterbox_path()
    if chatterbox_path not in sys.path:
        sys.path.insert(0, chatterbox_path)
        logger.info(f"Added Chatterbox path: {chatterbox_path}")
    
    try:
        import torch
        import torchaudio as ta
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Chatterbox-Turbo on {device}...")
        
        if device == "cuda":
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        
        model = ChatterboxTurboTTS.from_pretrained(device=device)
        logger.info("Chatterbox model loaded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to load Chatterbox: {e}")
        logger.warning("Server will return errors on /synthesize requests")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None
    })

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """
    Synthesize speech from text using Chatterbox.
    
    Expected JSON body:
    {
        "text": "Text to synthesize",
        "voice_reference": "/path/to/reference.wav"  # optional
    }
    
    Returns: WAV audio file
    """
    if model is None:
        return jsonify({'error': 'Chatterbox model not loaded'}), 500
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text in request'}), 400
        
        text = data['text']
        voice_reference = data.get('voice_reference')
        
        logger.info(f"Synthesizing: {text[:50]}...")
        logger.info(f"Voice reference: {voice_reference}")
        
        # Generate audio
        import torchaudio as ta
        if voice_reference and os.path.exists(voice_reference):
            wav = model.generate(text, audio_prompt_path=voice_reference)
        else:
            # Use default voice if no reference provided
            logger.warning("No valid voice reference provided, using default voice")
            wav = model.generate(text)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            ta.save(tmp_path, wav, model.sr)
        
        # Send file and clean up
        response = send_file(tmp_path, mimetype='audio/wav', as_attachment=True, download_name='output.wav')
        
        # Schedule cleanup after response
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.error(f"Failed to clean up temp file: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/speech', methods=['POST'])
def speech():
    """
    Docker-compatible /speech endpoint.
    
    Expected JSON body (Docker Chatterbox format):
    {
        "text": "Text to synthesize",
        "audio_prompt": "base64-encoded audio file",  # optional
        "exaggeration": 0.5,
        "cfg": 0.5,
        "temperature": 0.8
    }
    
    Returns: WAV audio bytes
    """
    if model is None:
        return jsonify({'error': 'Chatterbox model not loaded'}), 500
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text in request'}), 400
        
        text = data['text']
        audio_prompt_b64 = data.get('audio_prompt')
        
        logger.info(f"Synthesizing: {text[:50]}...")
        
        # Generate audio
        import torchaudio as ta
        import tempfile
        import base64
        
        if audio_prompt_b64:
            # Decode base64 audio prompt and save to temp file
            audio_bytes = base64.b64decode(audio_prompt_b64)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                tmp_audio.write(audio_bytes)
                audio_prompt_path = tmp_audio.name
            
            logger.info(f"Using voice reference from base64 audio_prompt")
            wav = model.generate(text, audio_prompt_path=audio_prompt_path)
            
            # Cleanup temp audio file
            try:
                os.unlink(audio_prompt_path)
            except Exception:
                pass
        else:
            logger.warning("No audio_prompt provided, using default voice")
            wav = model.generate(text)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            ta.save(tmp_path, wav, model.sr)
        
        # Read file and send as bytes
        with open(tmp_path, 'rb') as f:
            audio_data = f.read()
        
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Failed to clean up temp file: {e}")
        
        # Return raw audio bytes (like Docker Chatterbox)
        from flask import Response
        return Response(audio_data, mimetype='audio/wav')
        
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Chatterbox TTS Server...")
    
    # Load model on startup
    load_chatterbox()
    
    # Start Flask server
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
