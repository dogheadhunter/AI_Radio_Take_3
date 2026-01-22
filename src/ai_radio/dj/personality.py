from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import random
from typing import List, Optional


@dataclass
class SpeechPatterns:
    filler_words: List[str]


@dataclass
class DJPersonality:
    name: str
    tone: Optional[str]
    catchphrases: List[str]
    speech_patterns: SpeechPatterns


class DJ(Enum):
    JULIE = "julie"
    MR_NEW_VEGAS = "mr_new_vegas"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_personality(source) -> DJPersonality:
    """Load a DJ personality from a path or a DJ enum."""
    if isinstance(source, DJ):
        path = Path(__file__).parent / "character_cards" / f"{source.value}.json"
    else:
        path = Path(source)

    data = _load_json(path)

    speech = data.get("speech_patterns", {})
    speech_patterns = SpeechPatterns(filler_words=speech.get("filler_words", []))

    return DJPersonality(
        name=data.get("name", ""),
        tone=data.get("tone"),
        catchphrases=data.get("catchphrases", []),
        speech_patterns=speech_patterns,
    )


def get_random_catchphrase(personality: DJPersonality) -> Optional[str]:
    if not personality or not personality.catchphrases:
        return None
    return random.choice(personality.catchphrases)


def get_random_starter_phrase(personality: DJPersonality) -> Optional[str]:
    # Starter phrases may be represented as a subset of catchphrases; fall back to catchphrases
    return get_random_catchphrase(personality)
