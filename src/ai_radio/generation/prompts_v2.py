"""Improved prompt templates for DJ personalities (v2).

These produce a dict with 'system' and 'user' prompts so the LLM client
can use a system + user separation or concatenate them if the LLM
client requires a single string.
"""
from typing import Optional, Dict, List
from src.ai_radio.generation.prompts import DJ


# Few-shot example lines for Julie and Mr. New Vegas (short, representative)
JULIE_EXAMPLES: List[str] = [
    "Hey folks, stick around — this next one might just brighten your afternoon.",
    "Here's a little number that always reminds me of summer drives.",
    "Coming up next, a tune to make your day hum a little sweeter.",
    "Take it in and let the melody do the rest — enjoy.",
    "This is for anyone who loves a good melody and a warm afternoon." 
]

MR_NV_EXAMPLES: List[str] = [
    "Ladies and gentlemen, settle in — this one's a slow dance for the soul.",
    "A little something to set the mood as the lights grow low.",
    "Cue the romance, here's a song that'll sweep you off your feet.",
    "Wrap your ears around this smooth number, if I may be so bold.",
    "For the lovers and the late-night dreamers — this one's for you." 
]

# Forbidden words / phrases pulled from style guides
FORBIDDEN_WORDS = [
    "awesome", "cool", "vibe", "party started", "emoji", "modern slang", "profanity"
]


def _build_system_prompt(dj: DJ, examples: List[str], voice_summary: str) -> str:
    """Constructs the system prompt describing role, constraints, and few-shot examples."""
    examples_block = "\n".join(f"- {e}" for e in examples)
    forbidden_block = ", ".join(FORBIDDEN_WORDS)

    system = (
        "You are a radio DJ persona. Follow this system instruction carefully.\n"
        f"Role: {dj.value}.\n"
        f"Voice: {voice_summary}. Be concise and in-character.\n"
        "Era constraints: Avoid anachronistic modern slang unless explicitly allowed.\n"
        f"Forbidden elements (DO NOT INCLUDE): {forbidden_block}.\n"
        "Few-shot examples (use these as stylistic guides):\n"
        f"{examples_block}\n"
        "When generating, keep output natural, avoid forced catchphrases, and favor short, vivid lines."
    )
    return system


def build_song_intro_prompt_v2(
    dj: DJ,
    artist: str,
    title: str,
    year: Optional[int] = None,
    lyrics_context: Optional[str] = None,
) -> Dict[str, str]:
    """Build improved song intro prompt v2.

    Returns a dict: { 'system': <str>, 'user': <str> }
    """
    if dj == DJ.JULIE:
        examples = JULIE_EXAMPLES
        voice = "Friendly, earnest, warm, conversational; uses mild filler naturally."
    else:
        examples = MR_NV_EXAMPLES
        voice = "Suave, romantic, theatrical; classic mid-century phrasing."

    system = _build_system_prompt(dj, examples, voice)

    year_part = f" ({year})" if year else ""
    lyrics_part = lyrics_context or "No lyrics available"

    user = (
        f"Generate a song intro for the radio:\n"
        f"Artist: {artist}\n"
        f"Title: {title}{year_part}\n"
        f"Lyrics context: {lyrics_part}\n\n"
        "Requirements:\n"
        "- Length: 2-4 sentences.\n"
        "- Must sound natural and conversational (do not force filler words).\n"
        "- Avoid repeating the exact song title verbatim if it sounds clunky.\n"
        "- Output: plain text script (no markdown or annotations)."
    )

    return {"system": system, "user": user}


def build_song_outro_prompt_v2(dj: DJ, artist: str, title: str, next_song: Optional[str] = None) -> Dict[str, str]:
    if dj == DJ.JULIE:
        examples = JULIE_EXAMPLES[:3]
        voice = "Friendly, short, transitional."
    else:
        examples = MR_NV_EXAMPLES[:3]
        voice = "Suave, short, romantic." 

    system = _build_system_prompt(dj, examples, voice)

    next_part = f"Also tease next song: {next_song}." if next_song else ""
    user = (
        f"Write a song outro for '{title}' by {artist}. {next_part}\n"
        "Requirements:\n- Length: 1-2 sentences.\n- Keep it transitional and brief."
    )

    return {"system": system, "user": user}


def build_time_prompt_v2(dj: DJ, hour: Optional[int] = None, minute: Optional[int] = None) -> Dict[str, str]:
    if dj == DJ.JULIE:
        examples = [
            "It's 8:30 in the morning — time to wake those ukulele strings.",
            "Five past the hour, and the city's humming along.",
            "Half past two — keep your feet tapping."
        ]
        voice = "Casual, clear, upbeat."
    else:
        examples = [
            "It's 9:00 — a fine hour for a slow number.",
            "Quarter past eight, the night grows soft and inviting.",
            "Half past, and the lounge lights are low."
        ]
        voice = "Smooth, theatrical, slightly formal."

    system = _build_system_prompt(dj, examples, voice)

    if hour is not None and minute is not None:
        user = f"Announce the time: {hour:02d}:{minute:02d}. Keep it natural and fit the DJ persona. Length: 1 sentence."
    else:
        user = "Announce the current time naturally in one sentence."

    return {"system": system, "user": user}


def build_weather_prompt_v2(dj: DJ, weather_summary: str, hour: Optional[int] = None) -> Dict[str, str]:
    if dj == DJ.JULIE:
        examples = [
            "A sunny morning with a gentle breeze — perfect for a walk.",
            "Clouds rolling in this afternoon but still mild and pleasant.",
            "Expect a chilly evening, so grab a jacket."
        ]
        voice = "Friendly, informative, warm."
    else:
        examples = [
            "Clear skies for the evening — a perfect night to step out.",
            "A brisk afternoon ahead, dress warmly for an elegant stroll.",
            "Late showers expected, but we'll clear out by dawn."
        ]
        voice = "Suave, dramatic, vivid."

    system = _build_system_prompt(dj, examples, voice)

    time_note = f" (for hour {hour:02d})" if hour is not None else ""
    user = (
        f"Weather summary: {weather_summary}{time_note}\n"
        "Write a 2-3 sentence weather announcement that sounds like you're speaking directly to your radio audience."
    )

    return {"system": system, "user": user}
