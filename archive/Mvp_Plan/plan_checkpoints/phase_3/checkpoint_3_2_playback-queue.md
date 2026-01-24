# Checkpoint 3.2: Playback Queue

#### Checkpoint 3.2: Playback Queue
**Manage a queue of audio files to play.**

**Tasks:**
1. Create `src/ai_radio/playback/queue.py`
2. Queue multiple files
3. Auto-advance to next file
4. Support insert (for intros before songs)

**Tests First:**
```python
# tests/playback/test_queue.py
"""Tests for playback queue."""
import pytest
from pathlib import Path
from src.ai_radio. playback.queue import (
    PlaybackQueue,
    add_to_queue,
    insert_next,
    get_next,
    peek_next,
    clear_queue,
    get_queue_length,
    QueueItem,
)


class TestQueueOperations:
    """Test queue management."""
    
    def test_add_increases_length(self):
        """Adding to queue must increase length."""
        queue = PlaybackQueue()
        assert get_queue_length(queue) == 0
        add_to_queue(queue, QueueItem(Path("song. mp3"), "song"))
        assert get_queue_length(queue) == 1
    
    def test_get_next_returns_and_removes(self):
        """get_next must return item and remove from queue."""
        queue = PlaybackQueue()
        item = QueueItem(Path("song.mp3"), "song")
        add_to_queue(queue, item)
        
        returned = get_next(queue)
        assert returned == item
        assert get_queue_length(queue) == 0
    
    def test_peek_does_not_remove(self):
        """peek_next must not remove from queue."""
        queue = PlaybackQueue()
        item = QueueItem(Path("song.mp3"), "song")
        add_to_queue(queue, item)
        
        peek_next(queue)
        assert get_queue_length(queue) == 1
    
    def test_insert_next_goes_to_front(self):
        """insert_next must place item at front of queue."""
        queue = PlaybackQueue()
        add_to_queue(queue, QueueItem(Path("song1.mp3"), "song"))
        add_to_queue(queue, QueueItem(Path("song2.mp3"), "song"))
        
        intro = QueueItem(Path("intro.wav"), "intro")
        insert_next(queue, intro)
        
        next_item = get_next(queue)
        assert next_item == intro
    
    def test_fifo_order(self):
        """Queue must be first-in-first-out."""
        queue = PlaybackQueue()
        items = [QueueItem(Path(f"song{i}.mp3"), "song") for i in range(3)]
        for item in items: 
            add_to_queue(queue, item)
        
        for expected in items:
            actual = get_next(queue)
            assert actual == expected
    
    def test_clear_empties_queue(self):
        """clear_queue must empty the queue."""
        queue = PlaybackQueue()
        for i in range(5):
            add_to_queue(queue, QueueItem(Path(f"song{i}.mp3"), "song"))
        
        clear_queue(queue)
        assert get_queue_length(queue) == 0


class TestQueueWithIntros:
    """Test queue behavior with song intros."""
    
    def test_intro_plays_before_song(self):
        """When song is queued, intro should be insertable before it."""
        queue = PlaybackQueue()
        
        song = QueueItem(Path("song.mp3"), "song", song_id="song_1")
        intro = QueueItem(Path("intro.wav"), "intro", song_id="song_1")
        
        add_to_queue(queue, song)
        insert_next(queue, intro)
        
        first = get_next(queue)
        second = get_next(queue)
        
        assert first. item_type == "intro"
        assert second.item_type == "song"
```

**Success Criteria:**
- [x] All queue tests pass
- [x] FIFO ordering works correctly
- [x] insert_next places items at front
- [x] Queue can be cleared

**Progress:**
- Implemented `PlaybackQueue` with FIFO semantics and helper functions (`add_to_queue`, `insert_next`, `get_next`, `peek_next`, `clear_queue`, `get_queue_length`).
- Added unit tests in `tests/playback/test_queue.py` and verified they pass locally.
**Git Commit:** `feat(playback): add playback queue`
