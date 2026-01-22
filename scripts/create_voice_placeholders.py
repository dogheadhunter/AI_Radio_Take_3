"""Generate placeholder voice reference files for Julie and Mr. New Vegas.

These are minimal WAV files to bootstrap the system. Replace with actual voice samples
for production use.
"""
import wave
from pathlib import Path

def create_placeholder_voice(output_path: Path, duration_seconds: float = 3.0):
    """Create a silent WAV file as a placeholder."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with wave.open(str(output_path), 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(22050)  # 22.05 kHz
        
        # Generate silent frames
        num_frames = int(22050 * duration_seconds)
        silent_frames = b'\x00\x00' * num_frames
        wf.writeframes(silent_frames)
    
    print(f"Created placeholder: {output_path}")

if __name__ == '__main__':
    PROJECT_ROOT = Path(__file__).parent.parent
    voices_dir = PROJECT_ROOT / 'assets' / 'voice_references'
    
    create_placeholder_voice(voices_dir / 'julie.wav')
    create_placeholder_voice(voices_dir / 'mr_new_vegas.wav')
    
    print("\nPlaceholder voice files created!")
    print("Replace these with actual voice samples for better TTS quality.")
