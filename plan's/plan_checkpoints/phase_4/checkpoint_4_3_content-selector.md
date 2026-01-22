# Checkpoint 4.3: Content Selector

#### Checkpoint 4.3: Content Selector
**Select appropriate intro/outro for current context.**

**Tasks:**
1. Create `src/ai_radio/dj/content. py`
2. Select intro based on DJ and song
3. Handle multiple intro variations
4. Track which intros have been used (variety)

**Tests First:**
```python
# tests/dj/test_content. py
"""Tests for DJ content selection."""
import pytest
from pathlib import Path
from src.ai_radio. dj.content import (
    ContentSelector,
    get_intro_for_song,
    get_time_announcement,
    get_weather_announcement,
    mark_intro_used,
)


class TestIntroSelection:
    """Test intro selection."""
    
    def test_returns_path_to_audio(self, content_with_intros):
        """Must return path to intro audio file."""
        selector = ContentSelector(content_dir=content_with_intros)
        intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
        assert isinstance(intro, Path)
        assert intro.exists()
    
    def test_returns_none_if_no_intro(self, empty_content_dir):
        """Must return None if no intro exists."""
        selector = ContentSelector(content_dir=empty_content_dir)
        intro = get_intro_for_song(selector, song_id="nonexistent", dj="julie")
        assert intro is None
    
    def test_selects_different_intro_each_time(self, content_with_multiple_intros):
        """Should select different intros for variety."""
        selector = ContentSelector(content_dir=content_with_multiple_intros)
        
        intros = []
        for _ in range(10):
            intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
            mark_intro_used(selector, intro)
            intros.append(intro)
        
        # Should have used multiple different intros
        unique_intros = set(intros)
        assert len(unique_intros) > 1
    
    def test_selects_correct_dj_intro(self, content_with_both_djs):
        """Must select intro for the specified DJ."""
        selector = ContentSelector(content_dir=content_with_both_djs)
        
        julie_intro = get_intro_for_song(selector, song_id="song_1", dj="julie")
        vegas_intro = get_intro_for_song(selector, song_id="song_1", dj="mr_new_vegas")
        
        assert "julie" in str(julie_intro).lower()
        assert "vegas" in str(vegas_intro).lower() or "mr_new" in str(vegas_intro).lower()


class TestTimeAnnouncements:
    """Test time announcement selection."""
    
    def test_returns_audio_path(self, content_with_time):
        """Must return path to time announcement audio."""
        selector = ContentSelector(content_dir=content_with_time)
        from datetime import datetime
        
        announcement = get_time_announcement(
            selector, 
            dj="julie", 
            time=datetime(2026, 1, 22, 14, 30)
        )
        assert isinstance(announcement, Path)
    
    def test_different_for_different_times(self, content_with_time):
        """Different times should have different announcements."""
        selector = ContentSelector(content_dir=content_with_time)
        from datetime import datetime
        
        two_pm = get_time_announcement(selector, "julie", datetime(2026, 1, 22, 14, 0))
        three_pm = get_time_announcement(selector, "julie", datetime(2026, 1, 22, 15, 0))
        
        assert two_pm != three_pm
```

**Success Criteria:**
- [x] All content tests pass
- [x] Correct intros selected for DJ and song
- [x] Variety in intro selection works
- [x] Time announcements match time of day

**Git Commit:** `feat(dj): add content selector`
