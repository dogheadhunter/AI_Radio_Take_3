"""
Integration-style tests for full station cycle (short, safe versions).
Marked as integration but small enough to run in CI.
"""
import pytest
import time
from datetime import datetime
from unittest.mock import patch

from src.ai_radio.station.controller import StationController


@pytest.mark.integration
class TestFullStationCycle:
    def test_startup_plays_first_song(self):
        controller = StationController()
        controller.start()

        timeout = 5
        start = time.time()
        while time.time() - start < timeout:
            if controller.current_song is not None:
                break
            time.sleep(0.1)

        assert controller.current_song is not None
        controller.stop()

    def test_auto_advances_to_next_song(self):
        controller = StationController()
        controller.start()

        first_song = None
        timeout = 10
        start = time.time()

        while time.time() - start < timeout:
            if controller.current_song is not None:
                if first_song is None:
                    first_song = controller.current_song
                elif controller.current_song != first_song:
                    break
            time.sleep(0.1)

        assert controller.current_song != first_song
        controller.stop()

    def test_graceful_shutdown(self):
        controller = StationController()
        controller.start()
        time.sleep(1)
        controller.stop()
        assert controller.is_stopped


@pytest.mark.integration
class TestErrorRecovery:
    def test_logs_errors(self, caplog):
        controller = StationController()
        # Force an error by replacing _play_next
        def bad_play():
            raise RuntimeError("boom")
        controller._play_next = bad_play

        controller.start()
        time.sleep(0.2)
        controller.stop()

        assert any("error" in record.message.lower() or "exception" in record.levelname.lower() for record in caplog.records)
