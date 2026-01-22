"""Convert MP3 voice references to WAV format for TTS."""
from pathlib import Path
from pydub import AudioSegment

def convert_voice_references():
    voices_dir = Path("assets/voice_references")
    
    # Convert Julie.mp3 to julie.wav
    if (voices_dir / "Julie.mp3").exists():
        print("Converting Julie.mp3 to julie.wav...")
        audio = AudioSegment.from_mp3(voices_dir / "Julie.mp3")
        audio = audio.set_channels(1)  # mono
        audio = audio.set_frame_rate(22050)  # 22.05 kHz
        audio.export(voices_dir / "julie.wav", format="wav")
        print("✓ julie.wav created")
    
    # Convert Mister_New_Vegas.mp3 to mr_new_vegas.wav
    if (voices_dir / "Mister_New_Vegas.mp3").exists():
        print("Converting Mister_New_Vegas.mp3 to mr_new_vegas.wav...")
        audio = AudioSegment.from_mp3(voices_dir / "Mister_New_Vegas.mp3")
        audio = audio.set_channels(1)  # mono
        audio = audio.set_frame_rate(22050)  # 22.05 kHz
        audio.export(voices_dir / "mr_new_vegas.wav", format="wav")
        print("✓ mr_new_vegas.wav created")
    
    print("\nVoice references ready for TTS!")

if __name__ == '__main__':
    convert_voice_references()
