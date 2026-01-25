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
    from src.ai_radio.generation.voice_samples import format_voice_samples
    
    time_part = "the current time"
    time_context = ""
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
        
        # Add time-of-day context so LLM understands the actual period
        if 0 <= hour < 5:
            time_context = " It's the middle of the night/very early morning."
        elif 5 <= hour < 9:
            time_context = " It's early morning."
        elif 9 <= hour < 12:
            time_context = " It's mid-morning."
        elif 12 <= hour < 14:
            time_context = " It's around noon/early afternoon."
        elif 14 <= hour < 17:
            time_context = " It's afternoon."
        elif 17 <= hour < 21:
            time_context = " It's evening."
        else:
            time_context = " It's late night."

    # Get voice samples for the DJ
    dj_name = dj.value if dj else "DJ"
    voice_samples = format_voice_samples(dj_name) if dj else ""
    
    return f"""You are {dj_name}, a radio DJ. Announce that it is now {time_part}.{time_context}

HOW YOU SOUND (study these examples):
{voice_samples}

Write a brief time announcement (1-2 sentences). Sound like the examples above - casual, natural, in character.
Do not mention years or dates. Do not use words like 'wasteland', 'radiation', or 'vault'."""



def build_weather_prompt(dj: DJ, weather_summary: str, hour: int = None) -> str:
    """Build a weather announcement prompt using a short weather summary.
    
    Args:
        dj: DJ personality
        weather_summary: Current or forecast weather summary
        hour: Hour of day (0-23) when this will be broadcast, for context
    """
    from src.ai_radio.generation.voice_samples import format_voice_samples
    
    dj_name = dj.value if dj else "DJ"
    voice_samples = format_voice_samples(dj_name)
    
    # Add context based on time of day
    time_context = ""
    if hour is not None:
        if hour == 6:
            time_context = " You're announcing the morning weather to listeners just waking up."
        elif hour == 12:
            time_context = " It's midday - mention what to expect for the afternoon."
        elif hour == 17:
            time_context = " It's evening - mention conditions for tonight."
    
    return f"""You are {dj_name}, a radio DJ announcing the weather.

HOW YOU SOUND (study these examples):
{voice_samples}

Weather: {weather_summary}{time_context}

Write a brief weather announcement (2-3 sentences). Sound like the examples above - casual, natural, in character.
IMPORTANT: Do NOT use words like: radiation, fallout, mutation, wasteland, vault, nuclear. Just describe normal weather like a 1950s DJ would."""


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
