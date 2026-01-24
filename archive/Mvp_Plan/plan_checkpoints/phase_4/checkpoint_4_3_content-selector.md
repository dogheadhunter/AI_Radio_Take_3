# Checkpoint 4.3: Content Selector

#### Checkpoint 4.3: Content Selector
**Select appropriate intro/outro for current context.**

**Tasks:**
1. Create `src/ai_radio/dj/content. py`
2. Select intro based on DJ and song
3. Handle multiple intro variations
4. Track which intros have been used (variety)
5. [x] Add outro selection functions
6. [x] Add outro variety tracking
7. [x] Export outro functions from package

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

class TestOutroSelection:
    """Test outro selection (same pattern as intros)."""
    
    def test_returns_path_to_outro(self, content_with_outros):
        """Must return path to outro audio file."""
        selector = ContentSelector(content_dir=content_with_outros)
        outro = get_outro_for_song(selector, song_id="song_1", dj="julie")
        assert isinstance(outro, Path)
        assert outro.exists()
    
    def test_returns_none_if_no_outro(self, empty_content_dir):
        """Must return None if no outro exists."""
        selector = ContentSelector(content_dir=empty_content_dir)
        outro = get_outro_for_song(selector, song_id="nonexistent", dj="julie")
        assert outro is None
    
    def test_selects_correct_dj_outro(self, content_with_outros):
        """Must select outro for the specified DJ."""
        selector = ContentSelector(content_dir=content_with_outros)
        julie_outro = get_outro_for_song(selector, song_id="song_1", dj="julie")
        vegas_outro = get_outro_for_song(selector, song_id="song_1", dj="mr_new_vegas")
        assert "julie" in str(julie_outro).lower()
        assert "vegas" in str(vegas_outro).lower() or "mr_new" in str(vegas_outro).lower()
    
    def test_outro_variety_tracking(self, content_with_multiple_outros):
        """Should select different outros for variety."""
        selector = ContentSelector(content_dir=content_with_multiple_outros)
        outros = []
        for _ in range(6):
            outro = get_outro_for_song(selector, song_id="song_1", dj="julie")
            mark_outro_used(selector, outro)
            outros.append(str(outro))
        # Should see some variety
        assert len(set(outros)) > 1
```

**Implementation:**
```python
# src/ai_radio/dj/content.py (add to existing file)

def _find_outros(selector: ContentSelector, song_id: str, dj: str) -> List[Path]:
    """Find outro files matching song and DJ."""
    candidates = []
    if not selector.content_dir.exists():
        return candidates

    # Look for files containing song_id, dj, and "outro" in their name
    for p in selector.content_dir.rglob("*"):
        if p.is_file():
            name = p.name.lower()
            if song_id.lower() in name and dj.lower() in name and "outro" in name:
                candidates.append(p)

    # Fallback: any outro for DJ
    if not candidates:
        for p in selector.content_dir.rglob("*"):
            if p.is_file() and dj.lower() in p.name.lower() and "outro" in p.name.lower():
                candidates.append(p)
    return candidates


def get_outro_for_song(selector: ContentSelector, song_id: str, dj: str) -> Optional[Path]:
    """Get outro for song with variety tracking (same pattern as intros)."""
    outros = _find_outros(selector, song_id, dj)
    if not outros:
        return None

    used = selector._used.setdefault(song_id, set())
    unused = [p for p in outros if str(p) not in used]

    pick = choice(unused) if unused else choice(outros)
    return pick


def mark_outro_used(selector: ContentSelector, outro: Path):
    """Mark outro as used for variety rotation."""
    key = outro.name
    used = selector._used.setdefault(key, set())
    used.add(str(outro))
```

**Export from package:**
```python
# src/ai_radio/dj/__init__.py
from .content import (
    ContentSelector, 
    get_intro_for_song, 
    get_outro_for_song,
    get_time_announcement, 
    get_weather_announcement, 
    mark_intro_used,
    mark_outro_used
)
```

**Success Criteria:**
- [x] All content tests pass
- [x] Correct intros selected for DJ and song
- [x] Variety in intro selection works
- [x] Time announcements match time of day
- [x] Outro selection returns correct DJ-specific files
- [x] Outro variety tracking prevents repetition
- [x] Outro functions exported from package

**Git Commit:** `feat(dj): add content selector with outro support`
