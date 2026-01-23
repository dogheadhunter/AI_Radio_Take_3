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
        from datetime import datetime
        from src.ai_radio.services.clock import format_time_for_dj

        dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        if dj == DJ.JULIE:
            formatted = format_time_for_dj(dt, include_ampm=True, style="casual")
        elif dj == DJ.MR_NEW_VEGAS:
            formatted = format_time_for_dj(dt, include_ampm=True, style="written")
        else:
            formatted = format_time_for_dj(dt, include_ampm=True, style="numeric")
        time_part = formatted

    dj_part = f" for {dj.value}" if dj else ""
    return (
        f"You are a radio DJ. Announce that it is now {time_part}. "
        "Keep it brief (1-2 sentences), natural, and engaging. "
        "Do not repeat the exact same phrasing every time." "")



def build_weather_prompt(dj: DJ, weather_summary: str, hour: int = None) -> str:
    """Build a weather announcement prompt using a short weather summary.
    
    Args:
        dj: DJ personality
        weather_summary: Current or forecast weather summary
        hour: Hour of day (0-23) when this will be broadcast, for context
    """
    if dj == DJ.JULIE:
        traits = "friendly, warm, and conversational"
    else:
        traits = "suave, smooth, and theatrical like a classic Vegas lounge DJ"
    
    # Add context based on time of day
    time_context = ""
    if hour is not None:
        if hour == 6:
            time_context = " You're announcing the morning weather to listeners just waking up. Mention what to expect for the day ahead."
        elif hour == 12:
            time_context = " It's midday. Mention the current conditions and what to expect for the afternoon and evening."
        elif hour == 17:
            time_context = " It's evening time. Mention current conditions and what to expect tonight and tomorrow morning."
    
    return f"""You are a radio DJ announcing the weather to your listeners.
Your style is {traits}.{time_context}
Weather: {weather_summary}

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
