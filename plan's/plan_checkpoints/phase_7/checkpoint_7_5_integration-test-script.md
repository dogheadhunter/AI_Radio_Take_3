# Checkpoint 7.5: Integration Test Script

#### Checkpoint 7.5: Integration Test Script
**Create a comprehensive integration test.**

**Tasks:**
1. Create `tests/integration/test_full_station.py`
2. Test complete startup → play → shutdown cycle
3. Test all subsystems working together

**File: `tests/integration/test_full_station.py`**
```python
"""
Full station integration tests. 

These tests verify the complete system works together.
They may take longer to run and require actual audio files. 

Run with:  pytest tests/integration/ -v -m integration
"""
import pytest
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


@pytest.mark.integration
class TestFullStationCycle:
    """Test complete station operation."""
    
    def test_startup_plays_first_song(self, configured_station):
        """Station must start playing within 5 seconds."""
        controller = configured_station
        
        controller.start()
        
        # Wait for first song
        timeout = 5
        start = time.time()
        while time.time() - start < timeout:
            if controller.current_song is not None:
                break
            time. sleep(0.1)
        
        assert controller.current_song is not None
        controller.stop()
    
    def test_auto_advances_to_next_song(self, configured_station, short_audio_files):
        """Station must auto-advance when song ends."""
        controller = configured_station
        
        # Use very short audio for test
        controller.start()
        
        first_song = None
        timeout = 10
        start = time.time()
        
        while time.time() - start < timeout:
            if controller.current_song is not None:
                if first_song is None:
                    first_song = controller. current_song
                elif controller.current_song != first_song: 
                    # Advanced to second song
                    break
            time.sleep(0.1)
        
        assert controller.current_song != first_song
        controller.stop()
    
    def test_dj_is_correct_for_time(self, configured_station):
        """DJ must match the current time of day."""
        controller = configured_station
        
        with patch_current_time(datetime(2026, 1, 22, 10, 0)):
            controller.start()
            assert controller.current_dj. name. lower() == "julie"
            controller. stop()
        
        with patch_current_time(datetime(2026, 1, 22, 22, 0)):
            controller.start()
            assert "vegas" in controller.current_dj.name.lower()
            controller.stop()
    
    def test_graceful_shutdown(self, configured_station):
        """Station must shut down gracefully."""
        controller = configured_station
        controller.start()
        
        # Let it run briefly
        time.sleep(1)
        
        # Should not raise
        controller.stop()
        
        assert controller.is_stopped
    
    def test_logs_all_songs_played(self, configured_station, caplog):
        """Station must log all songs played."""
        controller = configured_station
        controller.start()
        
        # Let it play a couple songs
        time. sleep(5)
        controller.stop()
        
        # Check logs contain song information
        assert any("Playing" in record.message for record in caplog.records)


@pytest.mark.integration
class TestErrorRecovery:
    """Test station error recovery."""
    
    def test_recovers_from_missing_song(self, configured_station, catalog_with_missing_file):
        """Station must skip missing songs and continue."""
        controller = configured_station
        controller.start()
        
        # Should not crash
        time.sleep(3)
        
        assert controller.is_playing
        controller.stop()
    
    def test_logs_errors(self, configured_station, catalog_with_missing_file, caplog):
        """Station must log errors."""
        controller = configured_station
        controller.start()
        time.sleep(3)
        controller. stop()
        
        # Should have logged the error
        assert any("error" in record.message. lower() for record in caplog.records)
```

**Success Criteria:**
- [ ] Integration tests pass
- [ ] Station completes full cycle
- [ ] Error recovery works
- [ ] Logging captures everything

**Git Commit:** `test(integration): add full station integration tests`
