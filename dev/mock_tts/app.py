from flask import Flask, request, send_file, jsonify
import io
import wave

app = Flask(__name__)

@app.route('/synthesize', methods=['POST', 'HEAD'])
def synthesize():
    # HEAD should return 200 to signal endpoint available
    if request.method == 'HEAD':
        return ('', 200)

    data = request.get_json() or {}
    text = data.get('text', 'Hello from mock TTS')

    # Create a tiny WAV in memory (mono, 16-bit, 22050Hz)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        # Generate a short silent audio of 0.1s
        frames = b"\x00\x00" * 2205
        wf.writeframes(frames)

    buffer.seek(0)
    return send_file(buffer, mimetype='audio/wav', as_attachment=False, download_name='mock.wav')

@app.route('/', methods=['GET'])
def index():
    return jsonify({"service": "mock-tts", "status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
