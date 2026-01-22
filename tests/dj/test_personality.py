import pytest
from src.ai_radio.dj.personality import (
    DJPersonality,
    load_personality,
    get_random_catchphrase,
    get_random_starter_phrase,
    DJ,
)


class TestLoadPersonality:
    def test_load_returns_personality(self, julie_character_card):
        personality = load_personality(julie_character_card)
        assert isinstance(personality, DJPersonality)

    def test_personality_has_name(self, julie_character_card):
        personality = load_personality(julie_character_card)
        assert personality.name is not None
        assert "Julie" in personality.name

    def test_personality_has_tone(self, julie_character_card):
        personality = load_personality(julie_character_card)
        assert personality.tone is not None

    def test_personality_has_catchphrases(self, julie_character_card):
        personality = load_personality(julie_character_card)
        assert len(personality.catchphrases) > 0


class TestDJTraits:
    def test_julie_has_filler_words(self):
        personality = load_personality(DJ.JULIE)
        assert "um" in personality.speech_patterns.filler_words or \
               "like" in personality.speech_patterns.filler_words

    def test_mr_vegas_has_no_filler_words(self):
        personality = load_personality(DJ.MR_NEW_VEGAS)
        assert len(personality.speech_patterns.filler_words) == 0

    def test_random_catchphrase_from_list(self):
        personality = load_personality(DJ.JULIE)
        catchphrase = get_random_catchphrase(personality)
        assert catchphrase in personality.catchphrases
