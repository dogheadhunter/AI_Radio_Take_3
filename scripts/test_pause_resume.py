"""Manual test that verifies pause and resume behavior for the PlaybackController.

Usage:
  python scripts/test_pause_resume.py

This script will:
- Create a short intro and song
- Start playback
- Pause while the intro is playing
- Resume playback and verify final completion

Outputs event trace to stdout for human verification.
"""
import time
import wave
import math
import struct
import tempfile
from pathlib import Path
import sys

# Ensure package imports work when run from repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai_radio.playback.player import PygameAudioPlayer
from src.ai_radio.playback.controller import PlaybackController, add_song_with_intro, start_playback, pause_playback, resume_playback


def _make_tone(path: Path, freq=440.0, duration_ms=1000, sample_rate=44100, volume=0.1):
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            value = int(32767.0 * volume * math.sin(2.0 * math.pi * freq * t))
            wf.writeframes(struct.pack("h", value))


def main():
    tmp = Path(tempfile.mkdtemp(prefix="ai_radio_pause_resume_"))
    intro = tmp / "intro.wav"
    song = tmp / "song.wav"

    print("Creating test files in:", tmp)
    _make_tone(intro, freq=880.0, duration_ms=800)
    _make_tone(song, freq=440.0, duration_ms=1600)

    player = PygameAudioPlayer()
    if not player._pygame_available:
        print("pygame not initialized; cannot run test")
        return

    controller = PlaybackController(player=player)

    controller.on_item_started = lambda item: print(f"STARTED -> {item.item_type}: {item.path.name}")
    controller.on_item_finished = lambda item: print(f"FINISHED -> {item.item_type}: {item.path.name}")

    add_song_with_intro(controller, song_path=song, intro_path=intro, song_id="test_1")

    print("Starting playback...")
    start_playback(controller)

    # Wait for intro to start
    time.sleep(0.05)

    # Pause playback while intro is running
    print("Pausing playback for 1s...")
    pause_playback(controller)
    print("Controller is_playing:", controller.is_playing, "current_item:", controller.current_item)

    time.sleep(1.0)

    print("Resuming playback...")
    resume_playback(controller)

    # Wait for completion
    while controller.is_playing or controller.queue_length > 0:
        time.sleep(0.05)

    print("Test complete. Final state:", controller.is_playing, controller.current_item)


if __name__ == "__main__":
    main()
