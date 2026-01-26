"""Path utilities for AI Radio generation pipeline.

This module provides centralized path construction for scripts, audio files,
and audit results across different content types (intros, outros, time, weather).
"""
from pathlib import Path
from typing import Dict
from src.ai_radio.config import GENERATED_DIR, DATA_DIR


def _sanitize_filename_part(text: str) -> str:
    """Sanitize a string for use in filenames."""
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in text)
    return safe.strip().replace(' ', '_')


# ============================================================================
# Song-based paths (intros/outros)
# ============================================================================

def get_script_path(song: Dict, dj: str, content_type: str = "intros") -> Path:
    """Get the path to a script file for given content type ('intros' or 'outros')."""
    safe_artist = _sanitize_filename_part(song['artist'])
    safe_title = _sanitize_filename_part(song['title'])
    folder_name = f"{safe_artist}-{safe_title}"
    
    if content_type == 'outros':
        return GENERATED_DIR / "outros" / dj / folder_name / f"{dj}_outro.txt"
    # default: intros
    return GENERATED_DIR / "intros" / dj / folder_name / f"{dj}_0.txt"


def get_audio_path(song: Dict, dj: str, content_type: str = "intros") -> Path:
    """Get the path to an audio file for given content type ('intros' or 'outros')."""
    safe_artist = _sanitize_filename_part(song['artist'])
    safe_title = _sanitize_filename_part(song['title'])
    folder_name = f"{safe_artist}-{safe_title}"
    
    if content_type == 'outros':
        return GENERATED_DIR / "outros" / dj / folder_name / f"{dj}_outro.wav"
    # default: intros
    return GENERATED_DIR / "intros" / dj / folder_name / f"{dj}_0.wav"


def get_audit_path(song: Dict, dj: str, passed: bool, content_type: str = 'song_intro') -> Path:
    """Get the path to an audit result file for a given content type (e.g., 'song_intro', 'song_outro')."""
    safe_artist = _sanitize_filename_part(song['artist'])
    safe_title = _sanitize_filename_part(song['title'])
    folder_name = f"{safe_artist}-{safe_title}"
    status_folder = "passed" if passed else "failed"
    # Include content type in audit filename to avoid collisions (intro vs outro)
    return DATA_DIR / "audit" / dj / status_folder / f"{folder_name}_{content_type}_audit.json"


# ============================================================================
# Time announcement paths
# ============================================================================

def get_time_script_path(hour: int, minute: int, dj: str) -> Path:
    """Get the path to a time announcement script."""
    time_id = f"{hour:02d}-{minute:02d}"
    return GENERATED_DIR / "time" / dj / time_id / f"{dj}_0.txt"


def get_time_audio_path(hour: int, minute: int, dj: str) -> Path:
    """Get the path to a time announcement audio file."""
    time_id = f"{hour:02d}-{minute:02d}"
    return GENERATED_DIR / "time" / dj / time_id / f"{dj}_0.wav"


def get_time_audit_path(hour: int, minute: int, dj: str, passed: bool) -> Path:
    """Get the path to a time announcement audit result file."""
    time_id = f"{hour:02d}-{minute:02d}"
    status_folder = "passed" if passed else "failed"
    return DATA_DIR / "audit" / dj / status_folder / f"{time_id}_time_announcement_audit.json"


# ============================================================================
# Weather announcement paths
# ============================================================================

def get_weather_script_path(hour: int, dj: str) -> Path:
    """Get the path to a weather announcement script."""
    time_id = f"{hour:02d}-00"
    return GENERATED_DIR / "weather" / dj / time_id / f"{dj}_0.txt"


def get_weather_audio_path(hour: int, dj: str) -> Path:
    """Get the path to a weather announcement audio file."""
    time_id = f"{hour:02d}-00"
    return GENERATED_DIR / "weather" / dj / time_id / f"{dj}_0.wav"


def get_weather_audit_path(hour: int, dj: str, passed: bool) -> Path:
    """Get the path to a weather announcement audit result file."""
    time_id = f"{hour:02d}-00"
    status_folder = "passed" if passed else "failed"
    return DATA_DIR / "audit" / dj / status_folder / f"{time_id}_weather_announcement_audit.json"
