"""
Flask server wrapper for Chatterbox TTS that provides a /synthesize endpoint.
Compatible with AI_Radio TTSClient interface.
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
CHATTERBOX_PATH = r"C:\Users\doghe\chatterbox"

def load_chatterbox():
    """Load Chatterbox model on startup"""
    global model
    
    # Add chatterbox to path
    if CHATTERBOX_PATH not in sys.path:
        sys.path.insert(0, CHATTERBOX_PATH)
    
    try:
        import torch
        import torchaudio as ta
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Chatterbox-Turbo on {device}...")
        
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

if __name__ == '__main__':
    logger.info("Starting Chatterbox TTS Server...")
    
    # Load model on startup
    load_chatterbox()
    
    # Start Flask server
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
