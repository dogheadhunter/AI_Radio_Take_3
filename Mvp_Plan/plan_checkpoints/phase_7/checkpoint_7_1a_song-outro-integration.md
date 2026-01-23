# Checkpoint 7.1a: Song Outro Playback Integration

#### Checkpoint 7.1a: Integrate Song Outros into Playback Flow
**Wire up on_item_finished hook to automatically play outros after songs.**

## Overview
Extend StationController to automatically queue and play DJ outro commentary after each song finishes. This uses the existing `on_item_finished` event hook from PlaybackController.

## Tasks

### Task 1: Add Outro Integration to StationController
- [ ] Initialize ContentSelector in StationController `__init__`
- [ ] Set up `on_item_finished` callback in playback controller
- [ ] Implement `_handle_song_finished()` method
- [ ] Check if finished item is a song
- [ ] Get outro file for song from ContentSelector
- [ ] Insert outro into queue as next item

### Task 2: Implement Outro Queueing Logic
- [ ] Create `_queue_outro_for_song()` helper method
- [ ] Call `get_outro_for_song(selector, song_id, current_dj)`
- [ ] If outro found, create QueueItem with `item_type="outro"`
- [ ] Use `insert_next()` to place outro at front of queue
- [ ] Mark outro as used for variety tracking
- [ ] Log outro queueing for debugging

### Task 3: Handle Outro Playback Edge Cases
- [ ] Skip outro if none available (graceful fallback)
- [ ] Skip outro during radio shows (shows have their own outro)
- [ ] Skip outro if next item is time/weather announcement
- [ ] Log when outro is skipped and why
- [ ] Ensure outro doesn't interfere with DJ handoff

### Task 4: Add Outro Playback Tests
- [ ] Test outro queued after song finishes
- [ ] Test outro uses correct DJ
- [ ] Test outro not queued when none available
- [ ] Test outro skipped during radio shows
- [ ] Test outro variety tracking works
- [ ] Integration test: play song → outro → next song

### Task 5: Add Playback Event Logging
- [ ] Log `on_item_started` for outros
- [ ] Log `on_item_finished` for outros
- [ ] Include outro path and song_id in logs
- [ ] Add outro count to station stats

## Implementation Details

**File: `src/ai_radio/station/controller.py`**

Add outro integration to station controller:

```python
# In StationController.__init__
from src.ai_radio.dj.content import ContentSelector, get_outro_for_song, mark_outro_used
from src.ai_radio.playback.queue import insert_next, QueueItem

def __init__(self, config_overrides: dict = None):
    # ... existing init code ...
    
    # Content selector for intros/outros
    content_dir = Path("data/generated")
    self.content_selector = ContentSelector(content_dir=content_dir)
    
    # Set up playback event hooks
    self.playback_controller.on_item_started = self._handle_item_started
    self.playback_controller.on_item_finished = self._handle_item_finished
    
    # Stats
    self.outros_played = 0


def _handle_item_finished(self, finished_item: QueueItem):
    """Handle item finishing playback (outro queueing happens here)."""
    self.logger.debug(f"Item finished: {finished_item.item_type} - {finished_item.path.name}")
    
    # If song finished, queue outro
    if finished_item.item_type == "song":
        self._queue_outro_for_song(finished_item)


def _queue_outro_for_song(self, song_item: QueueItem):
    """Queue DJ outro after song finishes."""
    song_id = song_item.song_id
    if not song_id:
        self.logger.warning("Song has no ID, cannot queue outro")
        return
    
    # Skip outro during radio shows (shows have their own outros)
    if self._is_show_playing():
        self.logger.debug(f"Skipping outro during show: {song_id}")
        return
    
    # Skip outro if next item is announcement
    next_item = peek_next(self.playback_queue)
    if next_item and next_item.item_type in ("time", "weather", "dj_handoff"):
        self.logger.debug(f"Skipping outro before {next_item.item_type}: {song_id}")
        return
    
    # Get current DJ
    current_dj = get_current_dj(self.dj_scheduler, self.clock_service.now())
    
    # Get outro from content selector
    outro_path = get_outro_for_song(
        self.content_selector,
        song_id=song_id,
        dj=current_dj.name
    )
    
    if not outro_path:
        self.logger.debug(f"No outro found for {song_id}/{current_dj.name}")
        return
    
    # Queue outro to play next
    outro_item = QueueItem(
        path=outro_path,
        item_type="outro",
        song_id=song_id
    )
    
    insert_next(self.playback_queue, outro_item)
    mark_outro_used(self.content_selector, outro_path)
    
    self.outros_played += 1
    self.logger.info(f"Queued outro: {outro_path.name} for song {song_id}")


def _is_show_playing(self) -> bool:
    """Check if a radio show is currently playing."""
    # Check current item or recent items in queue
    if self.current_item and self.current_item.item_type in ("show", "show_intro", "show_outro"):
        return True
    return False


def get_status(self) -> StationStatus:
    """Get current station status (add outros_played stat)."""
    uptime = 0.0
    if self.start_time:
        uptime = (datetime.now() - self.start_time).total_seconds()
    
    return StationStatus(
        state=self.state,
        current_song=self.current_song,
        current_dj=self.current_dj.name,
        next_up=None,
        uptime_seconds=uptime,
        songs_played=self.songs_played,
        outros_played=self.outros_played,  # NEW
        errors_count=self.errors_count,
    )
```

**File: `src/ai_radio/station/status.py`**

Add outros_played to status:

```python
@dataclass
class StationStatus:
    state: StationState
    current_song: Optional[str]
    current_dj: str
    next_up: Optional[str]
    uptime_seconds: float
    songs_played: int
    outros_played: int  # NEW
    errors_count: int
```

## Success Criteria

### Functionality
- [ ] Outro automatically queued after each song finishes
- [ ] Outro uses current DJ's voice/personality
- [ ] Outro plays before next song (insert_next works)
- [ ] Outro skipped gracefully when none available
- [ ] Outro skipped during radio shows
- [ ] Outro skipped before announcements

### Quality
- [ ] No crashes or errors during outro queueing
- [ ] Outro variety tracking prevents repetition
- [ ] Playback flow feels natural (song → outro → next song)
- [ ] Logging provides clear visibility into outro decisions

### Testing
- [ ] All unit tests pass
- [ ] Integration test: full flow with outro playback
- [ ] Manual test: listen to station and verify outros play
- [ ] Verify outro count increments in station stats

## Validation Commands

```bash
# Run unit tests for outro integration
.venv/Scripts/pytest tests/station/test_controller.py::TestOutroIntegration -v

# Integration test: play station with outros
python scripts/test_station.py --duration 300

# Check outro stats
python -c "
from src.ai_radio.station.controller import StationController
controller = StationController()
controller.start()
import time
time.sleep(60)
status = controller.get_status()
print(f'Songs played: {status.songs_played}')
print(f'Outros played: {status.outros_played}')
controller.stop()
"

# Manual verification: check logs for outro queueing
tail -f logs/station.log | grep -i outro
```

## Anti-Regression Tests

```python
# tests/station/test_controller.py

class TestOutroIntegration:
    """Test song outro playback integration."""
    
    def test_queues_outro_after_song_finishes(self, controller_with_content):
        """Must queue outro when song finishes."""
        controller = controller_with_content
        
        # Create song item
        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="test_song")
        
        # Simulate song finishing
        controller._handle_item_finished(song)
        
        # Check that outro was queued
        next_item = peek_next(controller.playback_queue)
        assert next_item is not None
        assert next_item.item_type == "outro"
        assert next_item.song_id == "test_song"
    
    def test_outro_uses_current_dj(self, controller_with_content):
        """Outro must use current DJ's voice."""
        controller = controller_with_content
        
        # Set current DJ to Julie
        with patch_current_time(datetime(2026, 1, 22, 10, 0)):  # Julie's time
            song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="test_song")
            controller._handle_item_finished(song)
            
            next_item = peek_next(controller.playback_queue)
            assert "julie" in str(next_item.path).lower()
    
    def test_no_outro_when_none_available(self, controller_with_empty_content):
        """Must not crash when no outro exists."""
        controller = controller_with_empty_content
        
        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="unknown_song")
        
        # Should not raise
        controller._handle_item_finished(song)
        
        # Queue should be empty (no outro added)
        next_item = peek_next(controller.playback_queue)
        assert next_item is None
    
    def test_skips_outro_during_show(self, controller_with_content):
        """Must not queue outro during radio shows."""
        controller = controller_with_content
        
        # Set current item to show
        controller.current_item = QueueItem(path=Path("show.mp3"), item_type="show")
        
        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="test_song")
        controller._handle_item_finished(song)
        
        # No outro should be queued
        next_item = peek_next(controller.playback_queue)
        assert next_item is None or next_item.item_type != "outro"
    
    def test_outro_variety_tracking(self, controller_with_multiple_outros):
        """Should rotate through different outros."""
        controller = controller_with_multiple_outros
        
        outro_paths = []
        for _ in range(5):
            song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="test_song")
            controller._handle_item_finished(song)
            
            next_item = peek_next(controller.playback_queue)
            if next_item and next_item.item_type == "outro":
                outro_paths.append(str(next_item.path))
                # Consume the outro
                get_next(controller.playback_queue)
        
        # Should have some variety
        assert len(set(outro_paths)) > 1
    
    def test_outro_count_increments(self, controller_with_content):
        """Outro count should increment in status."""
        controller = controller_with_content
        
        initial_count = controller.get_status().outros_played
        
        song = QueueItem(path=Path("test.mp3"), item_type="song", song_id="test_song")
        controller._handle_item_finished(song)
        
        new_count = controller.get_status().outros_played
        assert new_count == initial_count + 1
```

## Git Commit

```bash
git add src/ai_radio/station/controller.py
git add src/ai_radio/station/status.py
git add tests/station/test_controller.py
git commit -m "feat(station): integrate song outro playback

- Wire on_item_finished hook to queue outros after songs
- Add _queue_outro_for_song() with smart skip logic
- Skip outros during shows and before announcements
- Add outro variety tracking via ContentSelector
- Add outros_played to station status
- Include comprehensive tests for outro integration
"
```

## Dependencies
- **Requires**: Checkpoint 4.3 (Content Selector with outro functions)
- **Requires**: Checkpoint 7.1 (Station Controller base implementation)
- **Enhances**: Checkpoint 2.8 (uses generated outro files)
- **Related**: Phase 3 (Playback Controller with on_item_finished hook)

## Notes
- Outros use `on_item_finished` hook, intros use `on_item_started` hook
- Outros are optional: if none exist, playback continues normally
- Show outros (from show_player.py) are separate from song outros
- Consider adding configuration: `ENABLE_SONG_OUTROS = True/False`
- Future enhancement: support for "cold" outros (no music bed) vs "hot" outros (with music fade)
