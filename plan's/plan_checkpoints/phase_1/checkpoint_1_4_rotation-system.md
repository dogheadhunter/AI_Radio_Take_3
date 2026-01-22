# Checkpoint 1.4: Rotation System

#### Checkpoint 1.4: Rotation System
**Core/Discovery/Banished playlist management.**

**Tasks:**
1. Create `src/ai_radio/library/rotation.py`
2. Implement tier assignment logic
3. Implement graduation and banishment
4. Implement song selection with proper ratios

**Tests First:**
```python
# tests/library/test_rotation.py
"""Tests for rotation system."""
import pytest
from src.ai_radio. library.rotation import (
    RotationManager,
    SongTier,
    get_next_song,
    banish_song,
    promote_song,
    record_play,
)


class TestSongTiers:
    """Test tier assignment."""
    
    def test_new_songs_are_discovery(self, rotation_manager):
        """New songs must start in Discovery tier."""
        song = mock_song()
        tier = rotation_manager.get_tier(song. id)
        assert tier == SongTier.DISCOVERY
    
    def test_promoted_songs_are_core(self, rotation_manager):
        """Promoted songs must be in Core tier."""
        song = mock_song()
        promote_song(rotation_manager, song. id)
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier.CORE
    
    def test_banished_songs_are_banished(self, rotation_manager):
        """Banished songs must be in Banished tier."""
        song = mock_song()
        banish_song(rotation_manager, song.id)
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier. BANISHED


class TestAutomaticGraduation:
    """Test automatic promotion after plays."""
    
    def test_graduates_after_threshold(self, rotation_manager):
        """Song must graduate to Core after enough plays."""
        from src.ai_radio.config import DISCOVERY_GRADUATION_PLAYS
        song = mock_song()
        
        for _ in range(DISCOVERY_GRADUATION_PLAYS):
            record_play(rotation_manager, song. id)
        
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier. CORE
    
    def test_does_not_graduate_early(self, rotation_manager):
        """Song must not graduate before threshold."""
        from src.ai_radio.config import DISCOVERY_GRADUATION_PLAYS
        song = mock_song()
        
        for _ in range(DISCOVERY_GRADUATION_PLAYS - 1):
            record_play(rotation_manager, song. id)
        
        tier = rotation_manager.get_tier(song.id)
        assert tier == SongTier. DISCOVERY


class TestSongSelection:
    """Test song selection respects ratios."""
    
    def test_never_selects_banished(self, rotation_manager_with_songs):
        """Banished songs must never be selected."""
        banished_id = "banished_song"
        banish_song(rotation_manager_with_songs, banished_id)
        
        # Select 100 songs, none should be banished
        selected = [get_next_song(rotation_manager_with_songs) for _ in range(100)]
        assert banished_id not in [s.id for s in selected]
    
    def test_respects_core_ratio_approximately(self, rotation_manager_with_mixed_tiers):
        """Core songs should be selected ~70% of the time."""
        from src.ai_radio.config import CORE_PLAYLIST_RATIO
        
        selections = [get_next_song(rotation_manager_with_mixed_tiers) for _ in range(1000)]
        core_count = sum(1 for s in selections if s.tier == SongTier. CORE)
        
        # Allow 10% margin of error
        expected = CORE_PLAYLIST_RATIO * 1000
        assert abs(core_count - expected) < 100
```

**Success Criteria:**
- [ ] All `test_rotation.py` tests pass
- [ ] Banished songs never play
- [ ] Core/Discovery ratio is approximately correct
- [ ] Auto-graduation works after threshold plays

**Validation:**
```bash
# Human runs:
pytest tests/library/test_rotation.py -v
```

**Git Commit:** `feat(library): add rotation system`
