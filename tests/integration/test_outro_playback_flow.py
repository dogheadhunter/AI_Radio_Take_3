from pathlib import Path
from datetime import datetime

from src.ai_radio.station.controller import StationController
from src.ai_radio.dj.content import ContentSelector
from src.ai_radio.playback.queue import add_to_queue, QueueItem
from src.ai_radio.playback.controller import start_playback


def test_play_song_outro_next_song(tmp_path: Path):
    # Prepare content dir with outro for song s1 and DJ julie
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    (content_dir / "julie_s1_outro.mp3").write_bytes(b"x")

    # Prepare songs
    song1 = tmp_path / "song1.mp3"
    song2 = tmp_path / "song2.mp3"
    song1.write_bytes(b"x")
    song2.write_bytes(b"x")

    controller = StationController()
    controller.content_selector = ContentSelector(content_dir=content_dir)
    # Force Julie time
    controller.clock_service.now = lambda: datetime(2026, 1, 22, 10, 0)

    # Queue songs
    add_to_queue(controller.playback_queue, QueueItem(path=song1, item_type="song", song_id="s1"))
    add_to_queue(controller.playback_queue, QueueItem(path=song2, item_type="song", song_id="s2"))

    # Capture started items
    started = []
    controller.on_item_started = lambda item: started.append(item.item_type)

    # Start playback
    start_playback(controller.playback_controller)

    # Simulate song1 completing -> should queue outro and start it
    controller.playback_controller.player._simulate_complete()
    # Simulate outro completing -> should start song2
    controller.playback_controller.player._simulate_complete()

    assert started == ["song", "outro", "song"]
