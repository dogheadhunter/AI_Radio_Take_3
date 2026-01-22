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


def build_time_announcement_prompt(dj: DJ) -> str:
    return f"Announce the current time in a way that matches the DJ personality: {dj.value}."


def build_weather_prompt(dj: DJ, weather_summary: str) -> str:
    return f"Announce the weather ({weather_summary}) in the style of {dj.value}."
