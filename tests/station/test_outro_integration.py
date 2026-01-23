from pathlib import Path
from datetime import datetime
import pytest

from src.ai_radio.station.controller import StationController
from src.ai_radio.playback.queue import QueueItem, peek_next, get_next
from src.ai_radio.dj.scheduler import DJScheduler
from src.ai_radio.services.clock import ClockService


@pytest.fixture
def controller_with_content(tmp_path: Path):
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    # create an outro file for julie/song_test
    p = content_dir / "julie_song_test_outro.mp3"
    p.write_text("outro")

    controller = StationController()
    controller.content_selector = controller.content_selector.__class__(content_dir=content_dir)
    # Ensure clock returns a Julie time by default
    controller.clock_service = ClockService()
    return controller


@pytest.fixture
def controller_with_empty_content(tmp_path: Path):
    content_dir = tmp_path / "empty"
    content_dir.mkdir()

    controller = StationController()
    controller.content_selector = controller.content_selector.__class__(content_dir=content_dir)
    return controller


@pytest.fixture
def controller_with_multiple_outros(tmp_path: Path):
    content_dir = tmp_path / "multiple"
    content_dir.mkdir()
    for i in range(3):
        (content_dir / f"julie_song_test_outro_{i}.mp3").write_text("x")

    controller = StationController()
    controller.content_selector = controller.content_selector.__class__(content_dir=content_dir)
    return controller


class TestOutroIntegration:
    def test_queues_outro_after_song_finishes(self, controller_with_content):
        controller = controller_with_content

        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="song_test")
        controller._handle_item_finished(song)

        next_item = peek_next(controller.playback_queue)
        assert next_item is not None
        assert next_item.item_type == "outro"
        assert next_item.song_id == "song_test"

    def test_outro_uses_current_dj(self, controller_with_content):
        controller = controller_with_content
        # set clock to a time that maps to Julie
        controller.clock_service = ClockService()
        controller.clock_service.now = lambda: datetime(2026, 1, 22, 10, 0)

        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="song_test")
        controller._handle_item_finished(song)

        next_item = peek_next(controller.playback_queue)
        assert next_item is not None
        assert "julie" in str(next_item.path).lower()

    def test_no_outro_when_none_available(self, controller_with_empty_content):
        controller = controller_with_empty_content
        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="unknown_song")

        # Should not raise
        controller._handle_item_finished(song)

        next_item = peek_next(controller.playback_queue)
        assert next_item is None

    def test_skips_outro_during_show(self, controller_with_content):
        controller = controller_with_content
        # Mark a show currently playing
        controller.current_item = QueueItem(path=Path("show.mp3"), item_type="show")

        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="song_test")
        controller._handle_item_finished(song)

        next_item = peek_next(controller.playback_queue)
        assert next_item is None or next_item.item_type != "outro"

    def test_outro_variety_tracking(self, controller_with_multiple_outros):
        controller = controller_with_multiple_outros

        outro_paths = []
        for _ in range(5):
            song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="song_test")
            controller._handle_item_finished(song)

            next_item = peek_next(controller.playback_queue)
            if next_item and next_item.item_type == "outro":
                outro_paths.append(str(next_item.path))
                # consume the outro so next iteration can pick another
                get_next(controller.playback_queue)

        assert len(set(outro_paths)) > 1

    def test_outro_count_increments(self, controller_with_content):
        controller = controller_with_content
        initial_count = controller.get_status().outros_played

        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="song_test")
        controller._handle_item_finished(song)

        new_count = controller.get_status().outros_played
        assert new_count == initial_count + 1
