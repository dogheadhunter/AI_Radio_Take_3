"""Stage 1: Generate text scripts for all songs.

This module contains the generation stage of the pipeline, responsible for
creating text scripts for song intros, outros, time announcements, and
weather announcements.
"""
import logging
from pathlib import Path
from typing import List, Dict

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.config import GENERATED_DIR, DATA_DIR
from src.ai_radio.core.paths import (
    get_script_path,
    get_time_script_path,
    get_weather_script_path
)
from src.ai_radio.core.sanitizer import (
    sanitize_script,
    truncate_after_song_intro,
    validate_time_announcement,
    validate_weather_announcement
)
from src.ai_radio.core.checkpoint import PipelineCheckpoint

logger = logging.getLogger(__name__)


def stage_generate(pipeline: GenerationPipeline, songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint, test_mode: bool = False) -> int:
    """Stage 1: Generate text scripts for all songs."""
    logger.info("=" * 60)
    logger.info("STAGE 1: GENERATE SCRIPTS")
    logger.info("=" * 60)
    
    if checkpoint.is_stage_completed("generate"):
        logger.info("Stage 1 already completed, skipping...")
        return checkpoint.state["stages"]["generate"]["scripts_generated"]
    
    checkpoint.mark_stage_started("generate")
    
    total_scripts = 0
    content_types = checkpoint.state.get("config", {}).get("content_types", [])

    for dj in djs:
        logger.info(f"\nGenerating scripts for {dj.upper()}...")
        
        for i, song in enumerate(songs, 1):
            # Intros
            if "intros" in content_types:
                script_path = get_script_path(song, dj, content_type='intros')
                if script_path.exists():
                    logger.debug(f"  [{i}/{len(songs)}] Skipping intro {song['title']} (already exists)")
                    total_scripts += 1
                else:
                    try:
                        result = pipeline.generate_song_intro(
                            song_id=str(song['id']),
                            artist=song['artist'],
                            title=song['title'],
                            dj=dj,
                            text_only=True
                        )
                        
                        if result.success and result.text:
                            # Sanitize and truncate
                            sanitized = sanitize_script(result.text)
                            truncated = truncate_after_song_intro(sanitized, song['artist'], song['title'])
                            
                            if truncated:
                                # Save the script
                                script_path.parent.mkdir(parents=True, exist_ok=True)
                                script_path.write_text(truncated, encoding='utf-8')
                                total_scripts += 1
                                logger.info(f"  [{i}/{len(songs)}] ✓ intro {song['title']}")
                            else:
                                logger.warning(f"  [{i}/{len(songs)}] ✗ intro {song['title']} (validation failed)")
                        else:
                            logger.warning(f"  [{i}/{len(songs)}] ✗ intro {song['title']} (generation failed)")
                    except Exception as e:
                        logger.error(f"  [{i}/{len(songs)}] ✗ intro {song['title']} - Error: {e}")
            
            # Outros
            if "outros" in content_types:
                outro_path = get_script_path(song, dj, content_type='outros')
                if outro_path.exists():
                    logger.debug(f"  [{i}/{len(songs)}] Skipping outro {song['title']} (already exists)")
                    total_scripts += 1
                else:
                    try:
                        result = pipeline.generate_song_outro(
                            song_id=str(song['id']),
                            artist=song['artist'],
                            title=song['title'],
                            dj=dj,
                            text_only=True
                        )
                        
                        if result.success and result.text:
                            sanitized = sanitize_script(result.text)
                            # Outros are typically short; save as-is after sanitization
                            if sanitized:
                                outro_path.parent.mkdir(parents=True, exist_ok=True)
                                outro_path.write_text(sanitized, encoding='utf-8')
                                total_scripts += 1
                                logger.info(f"  [{i}/{len(songs)}] ✓ outro {song['title']}")
                            else:
                                logger.warning(f"  [{i}/{len(songs)}] ✗ outro {song['title']} (validation failed)")
                        else:
                            logger.warning(f"  [{i}/{len(songs)}] ✗ outro {song['title']} (generation failed)")
                    except Exception as e:
                        logger.error(f"  [{i}/{len(songs)}] ✗ outro {song['title']} - Error: {e}")
    
    # Time announcements (if requested)
    if "time" in content_types:
        # Get time slots from checkpoint config
        time_slots = checkpoint.state.get("config", {}).get("time_slots", [])
        logger.info(f"\nGenerating time announcements for {len(time_slots)} slots...")
        
        for dj in djs:
            logger.info(f"\nGenerating time announcements for {dj.upper()}...")
            
            for i, (hour, minute) in enumerate(time_slots, 1):
                script_path = get_time_script_path(hour, minute, dj)
                if script_path.exists():
                    logger.debug(f"  [{i}/{len(time_slots)}] Skipping {hour:02d}:{minute:02d} (already exists)")
                    total_scripts += 1
                else:
                    try:
                        result = pipeline.generate_time_announcement(
                            hour=hour,
                            minute=minute,
                            dj=dj,
                            text_only=True
                        )
                        
                        if result.success and result.text:
                            # Sanitize the script (time-specific)
                            sanitized = sanitize_script(result.text, content_type="time")
                            
                            # Use dedicated time validation function
                            passed, reason = validate_time_announcement(sanitized)
                            
                            if passed:
                                script_path.parent.mkdir(parents=True, exist_ok=True)
                                script_path.write_text(sanitized, encoding='utf-8')
                                total_scripts += 1
                                logger.info(f"  [{i}/{len(time_slots)}] ✓ time {hour:02d}:{minute:02d}")
                            else:
                                logger.warning(f"  [{i}/{len(time_slots)}] ✗ time {hour:02d}:{minute:02d} ({reason})")
                        else:
                            logger.warning(f"  [{i}/{len(time_slots)}] ✗ time {hour:02d}:{minute:02d} (generation failed)")
                    except Exception as e:
                        logger.error(f"  [{i}/{len(time_slots)}] ✗ time {hour:02d}:{minute:02d} - Error: {e}")
    
    # Weather announcements (if requested)
    if "weather" in content_types:
        from src.ai_radio.config import WEATHER_TIMES
        
        # Hardcoded test weather data - keep it subtle and timeless
        SAMPLE_WEATHER = [
            "Clear skies, temperature around 75 degrees, perfect evening",
            "Partly cloudy with a chance of afternoon showers",
            "Dust storm moving in from the west, expect reduced visibility",
        ]
        
        logger.info(f"\nGenerating weather announcements for {len(WEATHER_TIMES)} slots...")
        
        for dj in djs:
            logger.info(f"\nGenerating weather announcements for {dj.upper()}...")
            
            for i, hour in enumerate(WEATHER_TIMES, 1):
                script_path = get_weather_script_path(hour, dj)
                if script_path.exists():
                    logger.debug(f"  [{i}/{len(WEATHER_TIMES)}] Skipping {hour:02d}:00 (already exists)")
                    total_scripts += 1
                else:
                    # Use hardcoded weather data cycling through the samples
                    weather_summary = SAMPLE_WEATHER[i % len(SAMPLE_WEATHER)]
                    
                    try:
                        result = pipeline.generate_weather_announcement(
                            hour=hour,
                            minute=0,  # Weather announcements are on the hour
                            weather_data={'summary': weather_summary},
                            dj=dj,
                            text_only=True
                        )
                        
                        if result.success and result.text:
                            # Sanitize the script (weather-specific)
                            sanitized = sanitize_script(result.text, content_type="weather")
                            
                            # Use dedicated weather validation function
                            passed, reason = validate_weather_announcement(sanitized)
                            
                            if passed:
                                script_path.parent.mkdir(parents=True, exist_ok=True)
                                script_path.write_text(sanitized, encoding='utf-8')
                                total_scripts += 1
                                logger.info(f"  [{i}/{len(WEATHER_TIMES)}] ✓ weather {hour:02d}:00")
                            else:
                                logger.warning(f"  [{i}/{len(WEATHER_TIMES)}] ✗ weather {hour:02d}:00 ({reason})")
                        else:
                            logger.warning(f"  [{i}/{len(WEATHER_TIMES)}] ✗ weather {hour:02d}:00 (generation failed)")
                    except Exception as e:
                        logger.error(f"  [{i}/{len(WEATHER_TIMES)}] ✗ weather {hour:02d}:00 - Error: {e}")
    
    checkpoint.mark_stage_completed("generate", scripts_generated=total_scripts)
    logger.info(f"\n✓ Stage 1 complete: {total_scripts} scripts generated")
    return total_scripts
