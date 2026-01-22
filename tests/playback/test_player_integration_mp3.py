"""Integration test: create MP3 via pydub and play with pygame."""
import time

import pytest

pytestmark = pytest.mark.integration


def test_pygame_can_play_mp3(tmp_path):
    pytest.importorskip("pygame")
    # pydub and ffmpeg must be present to export mp3
    pydub = pytest.importorskip("pydub")

    # Create short tone WAV using pydub and export to mp3
    from pydub import AudioSegment
    from pydub.generators import Sine

    tone = Sine(220).to_audio_segment(duration=200)
    wav_path = tmp_path / "tone.wav"
    mp3_path = tmp_path / "tone.mp3"
    tone.export(wav_path, format="wav")
    # Export to mp3 using ffmpeg
    tone.export(mp3_path, format="mp3")

    # Now attempt to play using PygameAudioPlayer
    from src.ai_radio.playback.player import PygameAudioPlayer
    player = PygameAudioPlayer()
    if not player._pygame_available:
        pytest.skip("pygame not initialized; skipping")

    callback_called = False

    def cb():
        nonlocal callback_called
        callback_called = True

    player.play(mp3_path, on_complete=cb)

    # Wait for playback to start
    time.sleep(0.05)
    assert player.is_playing() or player.state == player.state.PLAYING

    # Wait for completion
    timeout = 5.0
    import time as _time
    start = _time.time()
    while _time.time() - start < timeout and not callback_called:
        _time.sleep(0.05)

    assert callback_called
    assert player.state == player.state.COMPLETED
