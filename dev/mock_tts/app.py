from flask import Flask, request, send_file, jsonify
import io
import wave
import struct
import math

app = Flask(__name__)

def generate_simple_speech(text, sample_rate=22050):
    """
    Generate simple beep-tone audio based on text length.
    Creates a sequence of tones that vary based on characters.
    
    Args:
        text: Text to "synthesize"
        sample_rate: Audio sample rate (default 22050 Hz)
    
    Returns:
        bytes: WAV audio data
    """
    # Duration: roughly 0.08 seconds per character (simulating speech)
    duration = max(1.0, len(text) * 0.08)  # minimum 1 second
    num_samples = int(sample_rate * duration)
    
    # Generate audio samples with varying tones based on text
    samples = []
    for i in range(num_samples):
        # Base frequency: vary based on character position in text
        char_index = int((i / num_samples) * len(text))
        char_value = ord(text[char_index]) if char_index < len(text) else 65
        
        # Map character to frequency (200-800 Hz range for speech-like tones)
        frequency = 200 + (char_value % 600)
        
        # Generate sine wave
        t = i / sample_rate
        amplitude = 0.3  # Keep volume moderate
        sample_value = amplitude * math.sin(2 * math.pi * frequency * t)
        
        # Add slight envelope (fade in/out)
        envelope = 1.0
        fade_duration = 0.1  # 100ms fade
        fade_samples = int(sample_rate * fade_duration)
        if i < fade_samples:
            envelope = i / fade_samples
        elif i > num_samples - fade_samples:
            envelope = (num_samples - i) / fade_samples
        
        sample_value *= envelope
        
        # Convert to 16-bit PCM
        sample_int = int(sample_value * 32767)
        samples.append(struct.pack('<h', sample_int))
    
    return b''.join(samples)

@app.route('/synthesize', methods=['POST', 'HEAD'])
def synthesize():
    # HEAD should return 200 to signal endpoint available
    if request.method == 'HEAD':
        return ('', 200)

    data = request.get_json() or {}
    text = data.get('text', 'Hello from mock TTS')

    # Create WAV with simple tone-based audio
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        # Generate tone-based audio based on text
        frames = generate_simple_speech(text)
        wf.writeframes(frames)

    buffer.seek(0)
    return send_file(buffer, mimetype='audio/wav', as_attachment=False, download_name='mock.wav')

@app.route('/', methods=['GET'])
def index():
    return jsonify({"service": "mock-tts-improved", "status": "ok"})

if __name__ == '__main__':
    print("Starting Improved Mock TTS server on port 3000...")
    print("This server generates simple tone-based audio for testing.")
    app.run(host='0.0.0.0', port=3000)
