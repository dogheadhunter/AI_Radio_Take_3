"""Integration test for real audio playback using pygame.

This test is marked integration and will be skipped if pygame is not installed in
the test environment.
"""
import time
import wave
import struct
from unittest.mock import Mock

import pytest

from src.ai_radio.playback.player import PygameAudioPlayer


@pytest.mark.integration
def test_pygame_can_play_wav(tmp_path):
    pytest.importorskip("pygame")

    # Create a short 220Hz tone WAV file
    sample_rate = 44100
    duration = 0.2
    freq = 220.0
    n_samples = int(sample_rate * duration)

    wav_path = tmp_path / "tone.wav"
    with wave.open(str(wav_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            value = int(32767.0 * 0.1 * __import__("math").sin(2.0 * __import__("math").pi * freq * t))
            wf.writeframes(struct.pack("h", value))

    player = PygameAudioPlayer()
    if not player._pygame_available:
        pytest.skip("pygame was not initialized; skipping real playback test")

    callback = Mock()
    player.play(wav_path, on_complete=callback)

    # Wait a short time to ensure playback started
    time.sleep(0.05)
    assert player.is_playing() or player.state == player.state.PLAYING

    # Wait for completion (with timeout)
    timeout = 5.0
    start = time.time()
    while time.time() - start < timeout and callback.call_count == 0:
        time.sleep(0.05)

    assert callback.call_count == 1
    assert player.state == player.state.COMPLETED
