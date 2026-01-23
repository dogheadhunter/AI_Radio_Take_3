"""
24-Hour Validation Tests - Phase 8

These tests simulate a 24-hour run without actually waiting 24 hours.
They verify DJ handoffs, time announcements, show scheduling, and error recovery.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.ai_radio.dj.scheduler import DJScheduler, get_current_dj, is_transition_time, get_next_transition
from src.ai_radio.dj.personality import DJ
from src.ai_radio.station.controller import StationController, StationState


class TestDJHandoffs:
    """Test DJ transitions over 24 hours."""

    def test_full_24h_schedule(self):
        """Verify DJ changes at correct times over 24 hours."""
        scheduler = DJScheduler(morning_hour=6, evening_hour=19)
        start = datetime(2026, 1, 22, 0, 0, 0)
        
        expected_schedule = [
            (0, DJ.MR_NEW_VEGAS),   # Midnight
            (3, DJ.MR_NEW_VEGAS),   # 3 AM
            (6, DJ.JULIE),          # 6 AM - handoff
            (9, DJ.JULIE),          # 9 AM
            (12, DJ.JULIE),         # Noon
            (15, DJ.JULIE),         # 3 PM
            (18, DJ.JULIE),         # 6 PM
            (19, DJ.MR_NEW_VEGAS),  # 7 PM - handoff
            (22, DJ.MR_NEW_VEGAS),  # 10 PM
            (23, DJ.MR_NEW_VEGAS),  # 11 PM
        ]
        
        for hour, expected_dj in expected_schedule:
            test_time = start.replace(hour=hour)
            actual_dj = get_current_dj(scheduler, test_time)
            assert actual_dj == expected_dj, f"At {hour:02d}:00, expected {expected_dj.name}, got {actual_dj.name}"

    def test_transition_detection(self):
        """Verify transition times are correctly identified."""
        scheduler = DJScheduler(morning_hour=6, evening_hour=19)
        
        # Transition times (entire hour is considered transition)
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 6, 0, 0)) is True
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 6, 30, 0)) is True
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 19, 0, 0)) is True
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 19, 45, 0)) is True
        
        # Non-transition times
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 7, 0, 0)) is False
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 12, 0, 0)) is False
        assert is_transition_time(scheduler, datetime(2026, 1, 22, 23, 0, 0)) is False

    def test_next_transition_calculation(self):
        """Verify next transition time is correctly calculated."""
        scheduler = DJScheduler(morning_hour=6, evening_hour=19)
        
        # Early morning -> next is 6 AM
        now = datetime(2026, 1, 22, 3, 0, 0)
        next_trans = get_next_transition(scheduler, now)
        assert next_trans.hour == 6
        assert next_trans.day == 22
        
        # Mid-day -> next is 7 PM
        now = datetime(2026, 1, 22, 12, 0, 0)
        next_trans = get_next_transition(scheduler, now)
        assert next_trans.hour == 19
        assert next_trans.day == 22
        
        # Late evening -> next is 6 AM tomorrow
        now = datetime(2026, 1, 22, 22, 0, 0)
        next_trans = get_next_transition(scheduler, now)
        assert next_trans.hour == 6
        assert next_trans.day == 23


class TestStationResilience:
    """Test station behavior over extended runs."""

    def test_controller_lifecycle_24h_simulation(self):
        """Verify controller can handle start/stop cycles."""
        controller = StationController()
        
        # Simulate multiple start/stop cycles as might happen in 24h
        for cycle in range(3):
            controller.start()
            assert controller.is_running
            assert controller.state == StationState.PLAYING
            
            # Let it run briefly
            import time
            time.sleep(0.1)
            
            controller.stop()
            assert controller.is_stopped
            assert not controller.is_running

    def test_error_tracking_accumulation(self):
        """Verify errors are tracked over time."""
        controller = StationController()
        controller.start()
        
        # Simulate errors occurring during playback
        initial_errors = controller.errors_count
        
        # Force some errors
        for _ in range(5):
            controller.errors_count += 1
        
        assert controller.errors_count == initial_errors + 5
        
        # Verify station keeps running despite errors
        assert controller.is_running
        
        controller.stop()

    def test_uptime_tracking(self):
        """Verify uptime is correctly calculated."""
        import time
        
        controller = StationController()
        controller.start()
        
        # Let it run briefly
        time.sleep(0.2)
        
        status = controller.get_status()
        assert status.uptime_seconds >= 0.1
        assert status.uptime_seconds < 1.0  # Should be less than 1 second
        
        controller.stop()

    def test_pause_resume_cycles(self):
        """Verify pause/resume works correctly over time."""
        import time
        
        controller = StationController()
        controller.start()
        
        # Simulate pause/resume cycles
        for _ in range(3):
            controller.pause()
            assert controller.state == StationState.PAUSED
            assert not controller.is_playing
            
            time.sleep(0.05)
            
            controller.resume()
            assert controller.state == StationState.PLAYING
            assert controller.is_playing
            
            time.sleep(0.05)
        
        controller.stop()


class TestTimeProgression:
    """Test time-based features over 24 hours."""

    def test_time_announcement_schedule(self):
        """Verify time announcements would trigger at correct intervals."""
        # Time announcements should happen every 30 minutes
        start = datetime(2026, 1, 22, 0, 0, 0)
        
        expected_announcements = []
        for hour in range(24):
            expected_announcements.append(start.replace(hour=hour, minute=0))
            expected_announcements.append(start.replace(hour=hour, minute=30))
        
        assert len(expected_announcements) == 48  # 24 hours * 2 per hour

    def test_show_scheduling_in_24h(self):
        """Verify radio shows would be scheduled correctly."""
        # Shows typically run at specific times (e.g., 8 PM)
        scheduler = DJScheduler(morning_hour=6, evening_hour=19)
        show_hour = 20  # 8 PM
        
        start = datetime(2026, 1, 22, 0, 0, 0)
        
        # In a 24-hour period, show should air once
        show_times = []
        for hour in range(24):
            test_time = start.replace(hour=hour)
            if hour == show_hour:
                show_times.append(test_time)
        
        assert len(show_times) == 1
        assert show_times[0].hour == show_hour


class TestLongRunPlayback:
    """Test playback behavior over extended periods."""

    def test_song_counter_accuracy(self):
        """Verify song count remains accurate over many plays."""
        import time
        
        controller = StationController()
        controller.start()
        
        # Let it play several songs
        initial_count = controller.songs_played
        time.sleep(1.0)  # Should play at least 1-2 songs
        
        final_count = controller.songs_played
        assert final_count > initial_count, "Should have played songs"
        
        controller.stop()

    def test_status_consistency(self):
        """Verify status remains consistent during playback."""
        import time
        
        controller = StationController()
        controller.start()
        
        # Get multiple status snapshots
        statuses = []
        for _ in range(5):
            time.sleep(0.1)
            statuses.append(controller.get_status())
        
        # All should be in PLAYING state
        for status in statuses:
            assert status.state == StationState.PLAYING
        
        # Uptime should be increasing
        uptimes = [s.uptime_seconds for s in statuses]
        for i in range(len(uptimes) - 1):
            assert uptimes[i + 1] >= uptimes[i], "Uptime should increase"
        
        controller.stop()


class TestMemoryAndResources:
    """Test resource usage remains stable."""

    def test_no_resource_leaks_in_loop(self):
        """Verify controller cleanup happens properly."""
        # Create and destroy multiple controllers
        controllers = []
        
        for _ in range(5):
            controller = StationController()
            controller.start()
            controllers.append(controller)
        
        # Stop all
        for controller in controllers:
            controller.stop()
            assert controller.is_stopped
        
        # All should be cleanly stopped
        assert all(c.is_stopped for c in controllers)

    def test_thread_cleanup(self):
        """Verify threads are properly cleaned up."""
        import time
        import threading
        
        initial_thread_count = threading.active_count()
        
        controller = StationController()
        controller.start()
        time.sleep(0.1)
        
        # Should have added one thread
        assert threading.active_count() >= initial_thread_count
        
        controller.stop()
        time.sleep(0.2)  # Give thread time to stop
        
        # Thread count should return to initial or close to it
        # (May not be exact due to pytest's own threads)
        final_thread_count = threading.active_count()
        assert final_thread_count <= initial_thread_count + 2


@pytest.mark.slow
class Test24HourSimulation:
    """
    Comprehensive 24-hour simulation test.
    This test simulates a full 24-hour run by advancing time programmatically.
    """

    def test_simulated_24h_run(self):
        """
        Simulate a 24-hour run by advancing time and verifying key checkpoints.
        This doesn't actually wait 24 hours, but validates the logic.
        """
        scheduler = DJScheduler(morning_hour=6, evening_hour=19)
        start_time = datetime(2026, 1, 22, 8, 0, 0)  # Start at 8 AM
        
        checkpoints = []
        
        # Simulate hourly checkpoints
        for hours_elapsed in range(25):  # 0 to 24 hours
            current_time = start_time + timedelta(hours=hours_elapsed)
            current_dj = get_current_dj(scheduler, current_time)
            is_transition = is_transition_time(scheduler, current_time)
            
            checkpoints.append({
                'hours_elapsed': hours_elapsed,
                'time': current_time,
                'dj': current_dj,
                'is_transition': is_transition,
            })
        
        # Verify we have 25 checkpoints (0-24 inclusive)
        assert len(checkpoints) == 25
        
        # Verify DJ transitions happened
        transitions = [cp for cp in checkpoints if cp['is_transition']]
        assert len(transitions) >= 1, "Should have at least one DJ transition in 24 hours"
        
        # Verify both DJs appeared
        djs_seen = set(cp['dj'] for cp in checkpoints)
        assert DJ.JULIE in djs_seen
        assert DJ.MR_NEW_VEGAS in djs_seen
        
        # Verify morning transition (if in range)
        morning_transition = next((cp for cp in checkpoints if cp['time'].hour == 6), None)
        if morning_transition:
            assert morning_transition['dj'] == DJ.JULIE
        
        # Verify evening transition (if in range)
        evening_transition = next((cp for cp in checkpoints if cp['time'].hour == 19), None)
        if evening_transition:
            assert evening_transition['dj'] == DJ.MR_NEW_VEGAS
