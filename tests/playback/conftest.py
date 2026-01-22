import pytest
from pathlib import Path

from src.ai_radio.playback.player import AudioPlayer
from src.ai_radio.playback.queue import PlaybackQueue, QueueItem, add_to_queue


@pytest.fixture
def sample_audio(tmp_path):
    p = tmp_path / "sample.wav"
    p.write_bytes(b"RIFF\x00\x00\x00\x00WAVE")
    return p


@pytest.fixture
def mock_queue_with_items(tmp_path):
    queue = PlaybackQueue()
    # create dummy files
    song1 = tmp_path / "song1.mp3"
    song2 = tmp_path / "song2.mp3"
    song1.write_bytes(b"\x00")
    song2.write_bytes(b"\x00")

    add_to_queue(queue, QueueItem(path=song1, item_type="song", song_id="s1"))
    add_to_queue(queue, QueueItem(path=song2, item_type="song", song_id="s2"))
    return queue


@pytest.fixture
def mock_player():
    return AudioPlayer()
