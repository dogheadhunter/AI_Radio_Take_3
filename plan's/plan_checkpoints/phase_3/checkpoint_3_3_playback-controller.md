# Checkpoint 3.3: Playback Controller

#### Checkpoint 3.3: Playback Controller
**Combine player and queue for continuous playback.**

**Tasks:**
1. Create `src/ai_radio/playback/controller.py`
2. Automatically advance through queue
3. Emit events for song changes
4. Handle empty queue gracefully

**Tests First:**
```python
# tests/playback/test_controller. py
"""Tests for playback controller."""
import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path
from src. ai_radio.playback.controller import (
    PlaybackController,
    start_playback,
    pause_playback,
    resume_playback,
    skip_current,
    add_song_with_intro,
)


class TestPlaybackController:
    """Test playback controller operations."""
    
    def test_start_begins_playing(self, mock_player, mock_queue_with_items):
        """start_playback must begin playing first item."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        assert controller.is_playing
    
    def test_auto_advances_to_next(self, mock_player, mock_queue_with_items):
        """Must automatically play next item when current finishes."""
        controller = PlaybackController(queue=mock_queue_with_items)
        
        items_played = []
        controller.on_item_started = lambda item: items_played.append(item)
        
        start_playback(controller)
        
        # Simulate first item completing
        controller._on_playback_complete()
        
        assert len(items_played) == 2
    
    def test_skip_advances_to_next(self, mock_player, mock_queue_with_items):
        """skip_current must stop current and play next."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        
        first_item = controller.current_item
        skip_current(controller)
        
        assert controller.current_item != first_item
    
    def test_pause_stops_without_advancing(self, mock_player, mock_queue_with_items):
        """pause_playback must stop but keep current item."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        
        current = controller.current_item
        pause_playback(controller)
        
        assert not controller.is_playing
        assert controller.current_item == current
    
    def test_resume_continues_current(self, mock_player, mock_queue_with_items):
        """resume_playback must continue from pause."""
        controller = PlaybackController(queue=mock_queue_with_items)
        start_playback(controller)
        pause_playback(controller)
        resume_playback(controller)
        
        assert controller.is_playing


class TestSongWithIntro:
    """Test adding songs with their intros."""
    
    def test_adds_intro_then_song(self, mock_player):
        """add_song_with_intro must queue intro before song."""
        controller = PlaybackController()
        
        add_song_with_intro(
            controller,
            song_path=Path("song. mp3"),
            intro_path=Path("intro.wav"),
            song_id="song_1",
        )
        
        # Should have 2 items in queue
        assert controller.queue_length == 2
    
    def test_intro_plays_first(self, mock_player):
        """Intro must play before its song."""
        controller = PlaybackController()
        
        played = []
        controller. on_item_started = lambda item: played.append(item. item_type)
        
        add_song_with_intro(
            controller,
            song_path=Path("song.mp3"),
            intro_path=Path("intro. wav"),
            song_id="song_1",
        )
        
        start_playback(controller)
        controller._on_playback_complete()  # Finish intro
        
        assert played == ["intro", "song"]
```

**Success Criteria:**
- [ ] All controller tests pass
- [ ] Auto-advances through queue
- [ ] Pause/resume works correctly
- [ ] Skip advances to next item
- [ ] Songs play after their intros

**Git Commit:** `feat(playback): add playback controller`
