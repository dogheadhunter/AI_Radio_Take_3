"""Manual playback test script for Phase 3 (Audio Playback Engine).

Creates two short tones and their intros, queues them in the PlaybackController,
and plays them using the `PygameAudioPlayer`. This script is intended for
manual verification and demos.

Usage:
    python scripts/test_playback.py

Note: Requires `pygame` to be installed and initialized in the environment.
"""

import time
import wave
import math
import struct
import tempfile
from pathlib import Path

from src.ai_radio.playback.player import PygameAudioPlayer
from src.ai_radio.playback.controller import PlaybackController, add_song_with_intro, start_playback


def _make_tone(path: Path, freq=440.0, duration_ms=500, sample_rate=44100, volume=0.1):
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
    tmp = Path(tempfile.mkdtemp(prefix="ai_radio_playback_"))
    intro1 = tmp / "intro1.wav"
    song1 = tmp / "song1.wav"
    intro2 = tmp / "intro2.wav"
    song2 = tmp / "song2.wav"

    print("Creating test audio files in:", tmp)
    _make_tone(intro1, freq=880.0, duration_ms=300)
    _make_tone(song1, freq=440.0, duration_ms=1200)
    _make_tone(intro2, freq=660.0, duration_ms=300)
    _make_tone(song2, freq=330.0, duration_ms=1200)

    player = PygameAudioPlayer()
    if not player._pygame_available:
        print("pygame not available or failed to initialize. Install pygame and retry.")
        return

    controller = PlaybackController(player=player)

    controller.on_item_started = lambda item: print(f"STARTED -> {item.item_type}: {item.path.name}")
    controller.on_item_finished = lambda item: print(f"FINISHED -> {item.item_type}: {item.path.name}")

    add_song_with_intro(controller, song_path=song1, intro_path=intro1, song_id="song_1")
    add_song_with_intro(controller, song_path=song2, intro_path=intro2, song_id="song_2")

    print("Starting playback...")
    start_playback(controller)

    # Wait until everything finishes
    while controller.is_playing or controller.queue_length > 0:
        time.sleep(0.1)

    print("Playback complete. Test files located at:", tmp)


if __name__ == "__main__":
    main()
