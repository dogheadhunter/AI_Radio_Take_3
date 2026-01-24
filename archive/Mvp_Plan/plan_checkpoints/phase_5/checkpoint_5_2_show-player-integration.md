# Checkpoint 5.2: Show Player Integration

#### Checkpoint 5.2: Show Player Integration
**Integrate shows with DJ and playback.**

**Tasks:**
1. Create `src/ai_radio/shows/show_player.py`
2. Generate DJ intro for shows (if not pre-generated)
3. Play intro → show → DJ commentary
4. Return to music after show

**Tests First:**
```python
# tests/shows/test_show_player.py
"""Tests for show player."""
import pytest
from unittest.mock import Mock
from src.ai_radio. shows.show_player import (
    ShowPlayer,
    play_show_block,
    ShowBlockResult,
)


class TestShowBlock:
    """Test show block playback."""
    
    def test_plays_intro_before_show(self, mock_playback, show_with_intro):
        """DJ intro must play before show."""
        player = ShowPlayer(playback=mock_playback)
        
        played_items = []
        mock_playback.on_item_started = lambda item: played_items.append(item.item_type)
        
        play_show_block(player, show_with_intro)
        
        assert played_items[0] == "show_intro"
        assert played_items[1] == "show"
    
    def test_plays_outro_after_show(self, mock_playback, show_with_intro):
        """DJ commentary must play after show."""
        player = ShowPlayer(playback=mock_playback)
        
        played_items = []
        mock_playback.on_item_started = lambda item:  played_items.append(item.item_type)
        
        play_show_block(player, show_with_intro)
        
        assert played_items[-1] == "show_outro"
    
    def test_returns_result_with_duration(self, mock_playback, show_with_intro):
        """Must return result with total duration."""
        player = ShowPlayer(playback=mock_playback)
        result = play_show_block(player, show_with_intro)
        
        assert isinstance(result, ShowBlockResult)
        assert result.duration_seconds > 0
```

**Success Criteria:**
- [x] All show player tests pass
- [x] Shows play with DJ intro and outro
- [x] Control returns to music after show

**Git Commit:** `feat(shows): add show player integration`
