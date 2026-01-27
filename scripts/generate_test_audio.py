"""Generate test audio samples for time and weather announcements."""
import sys
from pathlib import Path
import random
import logging

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Setup logging to see GPU/CPU messages
logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.ai_radio.generation.tts_client import TTSClient, generate_audio
from src.ai_radio.core.paths import get_time_script_path, get_time_audio_path, get_weather_script_path, get_weather_audio_path
from src.ai_radio.config import VOICE_REFERENCES_DIR

def main():
    print("Generating test audio samples...")
    print("=" * 60)
    
    # Initialize TTS client (this will trigger model loading and GPU detection)
    print("\nInitializing TTS client...")
    tts_client = TTSClient()
    
    # Test samples to generate:
    # - All 3 weather slots for both DJs
    # - 2 random time slots for both DJs
    
    weather_hours = [6, 12, 17]
    time_hours = random.sample(range(24), 2)  # Pick 2 random hours
    
    print(f"\nSelected random time slots: {time_hours[0]}:00, {time_hours[1]}:00")
    print(f"Weather slots: 6:00, 12:00, 17:00")
    
    djs = ['julie', 'mr_new_vegas']
    total = 0
    
    for dj in djs:
        print(f"\n{dj.upper().replace('_', ' ')}")
        print("-" * 40)
        
        # Voice reference
        dj_folder = "Julie" if dj == "julie" else "Mister_New_Vegas"
        voice_ref = VOICE_REFERENCES_DIR / dj_folder / f"{dj}.wav"
        
        if not voice_ref.exists():
            print(f"  WARNING: Voice reference not found: {voice_ref}")
            voice_ref = None
        
        # Generate weather audio
        print("\n  Weather announcements:")
        for hour in weather_hours:
            script_path = get_weather_script_path(hour, dj)
            audio_path = get_weather_audio_path(hour, dj)
            
            if not script_path.exists():
                print(f"    ✗ {hour:02d}:00 - Script not found")
                continue
            
            if audio_path.exists():
                print(f"    ⊙ {hour:02d}:00 - Audio already exists, skipping")
                continue
            
            try:
                script_text = script_path.read_text(encoding='utf-8')
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                generate_audio(tts_client, script_text, audio_path, voice_reference=voice_ref)
                print(f"    ✓ {hour:02d}:00 - Generated")
                total += 1
            except Exception as e:
                print(f"    ✗ {hour:02d}:00 - Error: {e}")
        
        # Generate time audio
        print("\n  Time announcements:")
        for hour in time_hours:
            script_path = get_time_script_path(hour, 0, dj)
            audio_path = get_time_audio_path(hour, 0, dj)
            
            if not script_path.exists():
                print(f"    ✗ {hour:02d}:00 - Script not found")
                continue
            
            if audio_path.exists():
                print(f"    ⊙ {hour:02d}:00 - Audio already exists, skipping")
                continue
            
            try:
                script_text = script_path.read_text(encoding='utf-8')
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                generate_audio(tts_client, script_text, audio_path, voice_reference=voice_ref)
                print(f"    ✓ {hour:02d}:00 - Generated")
                total += 1
            except Exception as e:
                print(f"    ✗ {hour:02d}:00 - Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Complete! Generated {total} audio files")
    print("\nTest samples location:")
    print(f"  Weather: data/generated/weather/{{dj}}/{{hour}}-00/")
    print(f"  Time: data/generated/time/{{dj}}/{{hour}}-00/")

if __name__ == '__main__':
    main()
