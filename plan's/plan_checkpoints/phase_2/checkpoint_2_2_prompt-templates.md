# Checkpoint 2.2: Prompt Templates

#### Checkpoint 2.2:  Prompt Templates
**Create prompt templates for DJ personalities.**

**Tasks:**
1. Create `src/ai_radio/generation/prompts.py`
2. Define templates for Julie and Mr. New Vegas
3. Templates for intros, outros, time, weather

**Tests First:**
```python
# tests/generation/test_prompts.py
"""Tests for prompt templates."""
import pytest
from src.ai_radio.generation. prompts import (
    build_song_intro_prompt,
    build_time_announcement_prompt,
    build_weather_prompt,
    DJ,
)


class TestSongIntroPrompt:
    """Test song intro prompt generation."""
    
    def test_includes_song_title(self):
        """Prompt must include the song title."""
        prompt = build_song_intro_prompt(
            dj=DJ. JULIE,
            artist="Bing Crosby",
            title="White Christmas",
            year=1942,
        )
        assert "White Christmas" in prompt
    
    def test_includes_artist(self):
        """Prompt must include the artist name."""
        prompt = build_song_intro_prompt(
            dj=DJ. JULIE,
            artist="Bing Crosby",
            title="White Christmas",
            year=1942,
        )
        assert "Bing Crosby" in prompt
    
    def test_julie_prompt_has_julie_traits(self):
        """Julie prompt must include her personality traits."""
        prompt = build_song_intro_prompt(
            dj=DJ.JULIE,
            artist="Test",
            title="Test",
        )
        # Should mention filler words, friendly tone, etc.
        assert "friend" in prompt. lower() or "earnest" in prompt.lower()
    
    def test_mr_vegas_prompt_has_his_traits(self):
        """Mr.  New Vegas prompt must include his personality traits."""
        prompt = build_song_intro_prompt(
            dj=DJ.MR_NEW_VEGAS,
            artist="Test",
            title="Test",
        )
        # Should mention suave, romantic, etc.
        assert "suave" in prompt.lower() or "romantic" in prompt.lower()
    
    def test_different_djs_produce_different_prompts(self):
        """Julie and Mr. New Vegas prompts must be different."""
        julie_prompt = build_song_intro_prompt(DJ.JULIE, "Test", "Test")
        vegas_prompt = build_song_intro_prompt(DJ.MR_NEW_VEGAS, "Test", "Test")
        assert julie_prompt != vegas_prompt
```

**Success Criteria:**
- [ ] All prompt tests pass
- [ ] Prompts capture DJ personality from character cards
- [ ] Prompts are complete and self-contained

**Git Commit:** `feat(generation): add prompt templates`
