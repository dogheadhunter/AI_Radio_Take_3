"""Test weather audio generation."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai_radio.generation.tts_client import TTSClient, generate_audio
from src.ai_radio.config import VOICE_REFERENCES_DIR

# Read the weather text
text_file = Path("data/generated/weather/mr_new_vegas/06-00/mr_new_vegas_0.txt")
text = text_file.read_text(encoding='utf-8')

print(f"Text length: {len(text)} chars")
print(f"Text preview: {text[:100]}...")
print()

# Test TTS
output_path = Path("test_weather_output.wav")
dj_folder = "Mister_New_Vegas"
voice_ref = VOICE_REFERENCES_DIR / dj_folder / "mr_new_vegas.wav"

print(f"Voice reference: {voice_ref}")
print(f"Voice ref exists: {voice_ref.exists()}")
print()

tts = TTSClient()

try:
    print("Generating audio...")
    print(f"TTS URL: {tts.base_url}")
    generate_audio(tts, text=text, output_path=output_path, voice_reference=voice_ref if voice_ref.exists() else None)
    
    if output_path.exists():
        size = output_path.stat().st_size
        print(f"✓ Audio generated: {output_path} ({size} bytes)")
        if size < 1000:
            print("  ⚠ WARNING: File is very small, likely silent fallback")
    else:
        print("✗ Audio file not created")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
