"""Prompt templates for DJ personalities."""
from enum import Enum
from typing import Optional


class DJ(Enum):
    JULIE = "julie"
    MR_NEW_VEGAS = "mr_new_vegas"


def build_song_intro_prompt(dj: DJ, artist: str, title: str, year: Optional[int] = None) -> str:
    traits = ""
    if dj == DJ.JULIE:
        # Julie is friendly and earnest
        traits = "A friendly, earnest DJ who uses warm, conversational language and mild filler words."
    else:
        # Mr. New Vegas is suave and romantic
        traits = "A suave, romantic DJ with a smooth, theatrical tone."

    year_part = f" ({year})" if year else ""

    prompt = (
        f"You are a radio DJ. {traits} "
        f"Introduce the next song: '{title}' by {artist}{year_part}. "
        "Keep it short, evocative, and appropriate for a daytime audience."
    )
    return prompt


def build_time_announcement_prompt(hour: int = None, minute: int = None, dj: DJ = None) -> str:
    """Build a time announcement prompt. If hour/minute are omitted, produces a generic prompt.

    Examples:
        build_time_announcement_prompt(14, 30, DJ.JULIE)
        build_time_announcement_prompt(dj=DJ.MR_NEW_VEGAS)
    """
    time_part = "the current time"
    if hour is not None and minute is not None:
        # Format time in 12-hour notation with AM/PM
        suffix = "AM"
        h = hour
        if hour == 0:
            h = 12
            suffix = "AM"
        elif 1 <= hour < 12:
            suffix = "AM"
        elif hour == 12:
            suffix = "PM"
        else:
            h = hour - 12
            suffix = "PM"
        time_part = f"{h}:{minute:02d} {suffix}"

    dj_part = f" for {dj.value}" if dj else ""
    return f"Announce {time_part} in a way that matches the DJ personality{dj_part}."


def build_weather_prompt(dj: DJ, weather_summary: str) -> str:
    """Build a weather announcement prompt using a short weather summary."""
    if dj == DJ.JULIE:
        traits = "friendly, warm, and conversational"
    else:
        traits = "suave, smooth, and theatrical like a classic Vegas lounge DJ"
    
    return f"""You are a radio DJ announcing the current weather to your listeners.
Your style is {traits}.
Current weather: {weather_summary}

Write a brief, natural weather announcement (2-3 sentences) that sounds like you're speaking directly to your radio audience. Stay in character and make it engaging."""


def build_song_outro_prompt(dj: DJ, artist: str, title: str, next_song: str = None) -> str:
    """Build a short outro prompt for a song.

    The prompt asks the LLM to produce a brief closing line that could tease the next song
    or provide a short comment on the artist/song.
    """
    traits = ""
    if dj == DJ.JULIE:
        traits = "A friendly, earnest DJ who leaves listeners with a warm, conversational closing line."
    else:
        traits = "A suave, romantic DJ who gives a smooth, theatrical closing line."

    next_part = f" Also, tease the next song: {next_song}." if next_song else ""

    prompt = (
        f"You are a radio DJ. {traits} "
        f"Close out the song '{title}' by {artist}.{next_part} Keep it short (one sentence)."
    )
    return prompt
