"""Generation API for triggering content creation.

This module provides functions to trigger generation of scripts
and audio files programmatically without CLI dependencies.
"""
import logging
from pathlib import Path
from typing import Optional, List

from src.ai_radio.config import GENERATED_DIR, DATA_DIR
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.core.paths import (
    get_script_path,
    get_audio_path,
    get_time_script_path,
    get_time_audio_path,
    get_weather_script_path,
    get_weather_audio_path,
)
from src.ai_radio.core.sanitizer import (
    sanitize_script,
    truncate_after_song_intro,
    validate_time_announcement,
    validate_weather_announcement,
)
from src.ai_radio.api.schemas import (
    ContentType,
    DJ,
    GenerationResult,
    SongInfo,
)

logger = logging.getLogger(__name__)


class GenerationAPI:
    """API for triggering content generation.
    
    Provides methods to generate scripts and audio files for
    song intros, outros, time announcements, and weather reports.
    
    Example:
        api = GenerationAPI()
        result = api.generate_intro(
            song=SongInfo(id="1", artist="Johnny Cash", title="Ring of Fire"),
            dj=DJ.JULIE
        )
        if result.success:
            print(f"Generated script: {result.script_path}")
    """
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        test_mode: bool = False,
        pipeline: Optional[GenerationPipeline] = None,
    ):
        """Initialize the Generation API.
        
        Args:
            output_dir: Override for output directory (default: config.GENERATED_DIR)
            test_mode: If True, use mock generation (no LLM calls)
            pipeline: Pre-configured GenerationPipeline (optional)
        """
        self.output_dir = output_dir or GENERATED_DIR
        self.test_mode = test_mode
        self._pipeline = pipeline
    
    @property
    def pipeline(self) -> GenerationPipeline:
        """Get or create the generation pipeline."""
        if self._pipeline is None:
            lyrics_dir = Path("music_with_lyrics")
            self._pipeline = GenerationPipeline(
                output_dir=self.output_dir,
                prompt_version='v2',
                lyrics_dir=lyrics_dir if lyrics_dir.exists() else None,
            )
        return self._pipeline
    
    def generate_intro(
        self,
        song: SongInfo,
        dj: DJ,
        text_only: bool = True,
        overwrite: bool = False,
        lyrics_context: Optional[str] = None,
        audit_feedback: Optional[str] = None,
    ) -> GenerationResult:
        """Generate a song intro script.
        
        Args:
            song: Song information
            dj: DJ personality to use
            text_only: If True, generate only text (no audio)
            overwrite: If True, regenerate even if script exists
            lyrics_context: Optional lyrics to include in prompt
            audit_feedback: Optional feedback from previous audit
            
        Returns:
            GenerationResult with success status and paths
        """
        script_path = get_script_path(song.to_dict(), dj.value, content_type='intros')
        
        # Check if already exists
        if script_path.exists() and not overwrite:
            return GenerationResult(
                success=True,
                content_type=ContentType.INTRO,
                dj=dj,
                text=script_path.read_text(encoding='utf-8'),
                script_path=script_path,
                song=song,
            )
        
        try:
            result = self.pipeline.generate_song_intro(
                song_id=str(song.id),
                artist=song.artist,
                title=song.title,
                dj=dj.value,
                text_only=text_only,
                lyrics_context=lyrics_context,
                audit_feedback=audit_feedback,
            )
            
            if result.success and result.text:
                # Sanitize and truncate
                sanitized = sanitize_script(result.text)
                truncated = truncate_after_song_intro(sanitized, song.artist, song.title)
                
                if truncated:
                    script_path.parent.mkdir(parents=True, exist_ok=True)
                    script_path.write_text(truncated, encoding='utf-8')
                    
                    return GenerationResult(
                        success=True,
                        content_type=ContentType.INTRO,
                        dj=dj,
                        text=truncated,
                        script_path=script_path,
                        audio_path=get_audio_path(song.to_dict(), dj.value, content_type='intros') if not text_only else None,
                        song=song,
                    )
                else:
                    return GenerationResult(
                        success=False,
                        content_type=ContentType.INTRO,
                        dj=dj,
                        error="Script validation failed after sanitization",
                        song=song,
                    )
            else:
                return GenerationResult(
                    success=False,
                    content_type=ContentType.INTRO,
                    dj=dj,
                    error=f"Generation failed: {getattr(result, 'error', 'unknown')}",
                    song=song,
                )
                
        except Exception as e:
            logger.error(f"Error generating intro for {song.title}: {e}")
            return GenerationResult(
                success=False,
                content_type=ContentType.INTRO,
                dj=dj,
                error=str(e),
                song=song,
            )
    
    def generate_outro(
        self,
        song: SongInfo,
        dj: DJ,
        text_only: bool = True,
        overwrite: bool = False,
        lyrics_context: Optional[str] = None,
        audit_feedback: Optional[str] = None,
    ) -> GenerationResult:
        """Generate a song outro script.
        
        Args:
            song: Song information
            dj: DJ personality to use
            text_only: If True, generate only text (no audio)
            overwrite: If True, regenerate even if script exists
            lyrics_context: Optional lyrics to include in prompt
            audit_feedback: Optional feedback from previous audit
            
        Returns:
            GenerationResult with success status and paths
        """
        script_path = get_script_path(song.to_dict(), dj.value, content_type='outros')
        
        # Check if already exists
        if script_path.exists() and not overwrite:
            return GenerationResult(
                success=True,
                content_type=ContentType.OUTRO,
                dj=dj,
                text=script_path.read_text(encoding='utf-8'),
                script_path=script_path,
                song=song,
            )
        
        try:
            result = self.pipeline.generate_song_outro(
                song_id=str(song.id),
                artist=song.artist,
                title=song.title,
                dj=dj.value,
                text_only=text_only,
                lyrics_context=lyrics_context,
                audit_feedback=audit_feedback,
            )
            
            if result.success and result.text:
                sanitized = sanitize_script(result.text)
                
                if sanitized:
                    script_path.parent.mkdir(parents=True, exist_ok=True)
                    script_path.write_text(sanitized, encoding='utf-8')
                    
                    return GenerationResult(
                        success=True,
                        content_type=ContentType.OUTRO,
                        dj=dj,
                        text=sanitized,
                        script_path=script_path,
                        song=song,
                    )
                else:
                    return GenerationResult(
                        success=False,
                        content_type=ContentType.OUTRO,
                        dj=dj,
                        error="Script validation failed after sanitization",
                        song=song,
                    )
            else:
                return GenerationResult(
                    success=False,
                    content_type=ContentType.OUTRO,
                    dj=dj,
                    error=f"Generation failed: {getattr(result, 'error', 'unknown')}",
                    song=song,
                )
                
        except Exception as e:
            logger.error(f"Error generating outro for {song.title}: {e}")
            return GenerationResult(
                success=False,
                content_type=ContentType.OUTRO,
                dj=dj,
                error=str(e),
                song=song,
            )
    
    def generate_time_announcement(
        self,
        hour: int,
        minute: int,
        dj: DJ,
        text_only: bool = True,
        overwrite: bool = False,
    ) -> GenerationResult:
        """Generate a time announcement script.
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0 or 30 typically)
            dj: DJ personality to use
            text_only: If True, generate only text (no audio)
            overwrite: If True, regenerate even if script exists
            
        Returns:
            GenerationResult with success status and paths
        """
        script_path = get_time_script_path(hour, minute, dj.value)
        
        if script_path.exists() and not overwrite:
            return GenerationResult(
                success=True,
                content_type=ContentType.TIME,
                dj=dj,
                text=script_path.read_text(encoding='utf-8'),
                script_path=script_path,
                hour=hour,
                minute=minute,
            )
        
        try:
            result = self.pipeline.generate_time_announcement(
                hour=hour,
                minute=minute,
                dj=dj.value,
                text_only=text_only,
            )
            
            if result.success and result.text:
                sanitized = sanitize_script(result.text, content_type="time")
                passed, reason = validate_time_announcement(sanitized)
                
                if passed:
                    script_path.parent.mkdir(parents=True, exist_ok=True)
                    script_path.write_text(sanitized, encoding='utf-8')
                    
                    return GenerationResult(
                        success=True,
                        content_type=ContentType.TIME,
                        dj=dj,
                        text=sanitized,
                        script_path=script_path,
                        hour=hour,
                        minute=minute,
                    )
                else:
                    return GenerationResult(
                        success=False,
                        content_type=ContentType.TIME,
                        dj=dj,
                        error=f"Validation failed: {reason}",
                        hour=hour,
                        minute=minute,
                    )
            else:
                return GenerationResult(
                    success=False,
                    content_type=ContentType.TIME,
                    dj=dj,
                    error=f"Generation failed: {getattr(result, 'error', 'unknown')}",
                    hour=hour,
                    minute=minute,
                )
                
        except Exception as e:
            logger.error(f"Error generating time announcement for {hour:02d}:{minute:02d}: {e}")
            return GenerationResult(
                success=False,
                content_type=ContentType.TIME,
                dj=dj,
                error=str(e),
                hour=hour,
                minute=minute,
            )
    
    def generate_weather_announcement(
        self,
        hour: int,
        dj: DJ,
        weather_summary: str,
        text_only: bool = True,
        overwrite: bool = False,
    ) -> GenerationResult:
        """Generate a weather announcement script.
        
        Args:
            hour: Hour for the announcement (typically 6, 12, or 17)
            dj: DJ personality to use
            weather_summary: Text summary of current weather
            text_only: If True, generate only text (no audio)
            overwrite: If True, regenerate even if script exists
            
        Returns:
            GenerationResult with success status and paths
        """
        script_path = get_weather_script_path(hour, dj.value)
        
        if script_path.exists() and not overwrite:
            return GenerationResult(
                success=True,
                content_type=ContentType.WEATHER,
                dj=dj,
                text=script_path.read_text(encoding='utf-8'),
                script_path=script_path,
                hour=hour,
            )
        
        try:
            result = self.pipeline.generate_weather_announcement(
                hour=hour,
                minute=0,
                weather_data={'summary': weather_summary},
                dj=dj.value,
                text_only=text_only,
            )
            
            if result.success and result.text:
                sanitized = sanitize_script(result.text, content_type="weather")
                passed, reason = validate_weather_announcement(sanitized)
                
                if passed:
                    script_path.parent.mkdir(parents=True, exist_ok=True)
                    script_path.write_text(sanitized, encoding='utf-8')
                    
                    return GenerationResult(
                        success=True,
                        content_type=ContentType.WEATHER,
                        dj=dj,
                        text=sanitized,
                        script_path=script_path,
                        hour=hour,
                    )
                else:
                    return GenerationResult(
                        success=False,
                        content_type=ContentType.WEATHER,
                        dj=dj,
                        error=f"Validation failed: {reason}",
                        hour=hour,
                    )
            else:
                return GenerationResult(
                    success=False,
                    content_type=ContentType.WEATHER,
                    dj=dj,
                    error=f"Generation failed: {getattr(result, 'error', 'unknown')}",
                    hour=hour,
                )
                
        except Exception as e:
            logger.error(f"Error generating weather announcement for {hour:02d}:00: {e}")
            return GenerationResult(
                success=False,
                content_type=ContentType.WEATHER,
                dj=dj,
                error=str(e),
                hour=hour,
            )
    
    def generate_batch(
        self,
        songs: List[SongInfo],
        djs: List[DJ],
        content_types: List[ContentType],
        text_only: bool = True,
        skip_existing: bool = True,
    ) -> List[GenerationResult]:
        """Generate content for multiple songs/DJs.
        
        Args:
            songs: List of songs to process
            djs: List of DJs to generate for
            content_types: Types of content to generate
            text_only: If True, generate only text (no audio)
            skip_existing: If True, skip items that already exist
            
        Returns:
            List of GenerationResult for each item
        """
        results = []
        
        for dj in djs:
            for song in songs:
                for ct in content_types:
                    if ct == ContentType.INTRO:
                        result = self.generate_intro(
                            song=song,
                            dj=dj,
                            text_only=text_only,
                            overwrite=not skip_existing,
                        )
                        results.append(result)
                    elif ct == ContentType.OUTRO:
                        result = self.generate_outro(
                            song=song,
                            dj=dj,
                            text_only=text_only,
                            overwrite=not skip_existing,
                        )
                        results.append(result)
        
        return results
