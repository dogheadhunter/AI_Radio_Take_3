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


def stage_generate(pipeline: GenerationPipeline, songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint, test_mode: bool = False, overwrite: bool = False) -> int:
    """Stage 1: Generate text scripts for all songs.
    
    Args:
        pipeline: GenerationPipeline instance
        songs: List of song dictionaries
        djs: List of DJ names
        checkpoint: PipelineCheckpoint for state tracking
        test_mode: If True, use mock generation
        overwrite: If True, regenerate even if files exist
    """
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
                if script_path.exists() and not overwrite:
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
                if outro_path.exists() and not overwrite:
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
        from src.ai_radio.services.weather import WeatherService
        
        logger.info(f"\nGenerating weather announcements for {len(WEATHER_TIMES)} slots...")
        logger.info("Fetching real weather data from Open-Meteo API...")
        
        # Initialize weather service to fetch real weather
        weather_service = WeatherService()
        
        for dj in djs:
            logger.info(f"\nGenerating weather announcements for {dj.upper()}...")
            
            for i, hour in enumerate(WEATHER_TIMES, 1):
                script_path = get_weather_script_path(hour, dj)
                if script_path.exists():
                    logger.debug(f"  [{i}/{len(WEATHER_TIMES)}] Skipping {hour:02d}:00 (already exists)")
                    total_scripts += 1
                else:
                    try:
                        # Fetch weather forecast for the announcement hour and look-ahead
                        current_weather = weather_service.get_forecast_for_hour(hour)
                        
                        # Build comprehensive weather summary with look-ahead forecast
                        # 6 AM: morning weather + preview of day ahead (check 12 PM and 5 PM)
                        # 12 PM: afternoon weather + evening preview (check 5 PM and next morning)
                        # 5 PM: evening weather + night forecast + tomorrow preview (check next 6 AM)
                        
                        if current_weather and current_weather.temperature is not None:
                            temp = int(round(current_weather.temperature))
                            conditions = current_weather.conditions or "clear skies"
                            
                            # Build look-ahead summary based on time
                            if hour == 6:
                                # Morning: preview the day ahead
                                midday = weather_service.get_forecast_for_hour(12)
                                evening = weather_service.get_forecast_for_hour(17)
                                midday_temp = int(round(midday.temperature)) if midday and midday.temperature else temp
                                evening_cond = evening.conditions if evening and evening.conditions else conditions
                                weather_summary = (
                                    f"Good morning! Currently {conditions} with {temp} degrees. "
                                    f"Expect highs around {midday_temp} this afternoon, "
                                    f"with {evening_cond} later this evening."
                                )
                            elif hour == 12:
                                # Afternoon: current + evening preview
                                evening = weather_service.get_forecast_for_hour(17)
                                evening_temp = int(round(evening.temperature)) if evening and evening.temperature else temp
                                evening_cond = evening.conditions if evening and evening.conditions else conditions
                                weather_summary = (
                                    f"Good afternoon! {conditions.capitalize()} right now at {temp} degrees. "
                                    f"This evening expect {evening_cond} with temperatures dropping to around {evening_temp}."
                                )
                            elif hour == 17:
                                # Evening: current + tonight + tomorrow preview
                                tomorrow_morning = weather_service.get_forecast_for_hour(6)  # Next day's 6 AM
                                tomorrow_temp = int(round(tomorrow_morning.temperature)) if tomorrow_morning and tomorrow_morning.temperature else temp
                                tomorrow_cond = tomorrow_morning.conditions if tomorrow_morning and tomorrow_morning.conditions else conditions
                                weather_summary = (
                                    f"Good evening! {conditions.capitalize()} at {temp} degrees. "
                                    f"Clear skies expected tonight. "
                                    f"Tomorrow morning looking at {tomorrow_cond} with temperatures around {tomorrow_temp}."
                                )
                            else:
                                # Fallback for any other hour
                                weather_summary = f"{conditions.capitalize()}, temperature around {temp} degrees"
                                
                            logger.debug(f"  Weather for {hour:02d}:00 - {temp}°F, {conditions}")
                        else:
                            # Fallback if API fails
                            weather_summary = "Clear skies, pleasant temperature expected throughout the day"
                            logger.warning(f"  Using fallback weather data for {hour:02d}:00")
                        
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
