# Checkpoint 4.1: DJ Personality Model

#### Checkpoint 4.1: DJ Personality Model
**Define DJ personalities as data structures.**

**Tasks:**
1. Create `src/ai_radio/dj/personality.py`
2. Load personality from JSON character cards
3. Provide personality traits for prompt generation

**Tests First:**
```python
# tests/dj/test_personality.py
"""Tests for DJ personality."""
import pytest
from pathlib import Path
from src.ai_radio.dj. personality import (
    DJPersonality,
    load_personality,
    get_random_catchphrase,
    get_random_starter_phrase,
    DJ,
)


class TestLoadPersonality:
    """Test personality loading."""
    
    def test_load_returns_personality(self, julie_character_card):
        """Must return DJPersonality object."""
        personality = load_personality(julie_character_card)
        assert isinstance(personality, DJPersonality)
    
    def test_personality_has_name(self, julie_character_card):
        """Personality must have a name."""
        personality = load_personality(julie_character_card)
        assert personality.name is not None
        assert "Julie" in personality.name
    
    def test_personality_has_tone(self, julie_character_card):
        """Personality must have a tone description."""
        personality = load_personality(julie_character_card)
        assert personality. tone is not None
    
    def test_personality_has_catchphrases(self, julie_character_card):
        """Personality must have catchphrases."""
        personality = load_personality(julie_character_card)
        assert len(personality.catchphrases) > 0


class TestDJTraits:
    """Test DJ-specific traits."""
    
    def test_julie_has_filler_words(self):
        """Julie must have filler words defined."""
        personality = load_personality(DJ. JULIE)
        assert "um" in personality.speech_patterns. filler_words or \
               "like" in personality.speech_patterns.filler_words
    
    def test_mr_vegas_has_no_filler_words(self):
        """Mr. New Vegas must have no filler words."""
        personality = load_personality(DJ.MR_NEW_VEGAS)
        assert len(personality.speech_patterns.filler_words) == 0
    
    def test_random_catchphrase_from_list(self):
        """Random catchphrase must be from defined list."""
        personality = load_personality(DJ.JULIE)
        catchphrase = get_random_catchphrase(personality)
        assert catchphrase in personality.catchphrases
```

**Success Criteria:**
- [ ] All personality tests pass
- [ ] Can load Julie and Mr. New Vegas personalities
- [ ] Personality traits match character cards

**Git Commit:** `feat(dj): add personality model`
