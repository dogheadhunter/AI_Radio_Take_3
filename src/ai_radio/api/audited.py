"""Audited Generation API - uses staged pipeline with audit validation.

This module extends GenerationAPI to use the modular staged pipeline
with automatic audit validation and retry loops, matching the behavior
of scripts/generate_with_audit.py.

The key difference from GenerationAPI:
- Calls stage functions (stage_generate, stage_audit, stage_regenerate, stage_audio)
- Automatically audits generated scripts
- Retries failed scripts up to max_retries times with audit feedback
- Only generates audio for scripts that pass audit
- Auto-loads lyrics context from music_with_lyrics/
"""
import logging
from pathlib import Path
from typing import Optional

from src.ai_radio.api.generation import GenerationAPI
from src.ai_radio.api.schemas import GenerationResult, ContentType, DJ, SongInfo
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.stages import stage_generate, stage_audit, stage_regenerate, stage_audio
from src.ai_radio.core.checkpoint import PipelineCheckpoint

logger = logging.getLogger(__name__)


class AuditedGenerationAPI(GenerationAPI):
    """Generation API with automatic audit validation.
    
    This class wraps the staged pipeline to provide single-item generation
    with audit loops. It's designed for GUI and programmatic use where
    quality validation is required.
    
    Example:
        api = AuditedGenerationAPI()
        result = api.generate_intro_with_audit(
            song=SongInfo(id="1", artist="Artist", title="Song"),
            dj=DJ.JULIE,
            max_retries=5,
            text_only=False  # Generate script + audio if passed
        )
        
        if result.success and result.audit_passed:
            print(f"Generated and validated: {result.script_path}")
        else:
            print(f"Failed audit: {result.audit_score}")
    """
    
    def generate_intro_with_audit(
        self,
        song: SongInfo,
        dj: DJ,
        max_retries: int = 5,
        text_only: bool = True,
        user_feedback: Optional[str] = None,
    ) -> GenerationResult:
        """Generate intro with automatic audit validation loop.
        
        This method replicates the staged pipeline behavior for single items:
        1. stage_generate - Generate script with lyrics context
        2. stage_audit - Audit quality with LLM
        3. stage_regenerate - Retry with feedback if failed (up to max_retries)
        4. stage_audio - Generate audio if passed and not text_only
        
        Args:
            song: Song information (artist, title)
            dj: DJ personality to use
            max_retries: Maximum regeneration attempts (default: 5)
            text_only: If True, skip audio generation
            user_feedback: Optional feedback to include in first generation
            
        Returns:
            GenerationResult with audit_passed and audit_score fields populated
        """
        songs = [song.to_dict()]
        djs = [dj.value]
        
        # Create temporary checkpoint file for single-item operations
        import tempfile
        checkpoint_file = Path(tempfile.mktemp(suffix='.json'))
        checkpoint = PipelineCheckpoint(state_file=checkpoint_file)
        
        try:
            # Stage 1: Generate script
            from datetime import datetime
            start_time = datetime.now()
            logger.info(f"[{start_time.strftime('%H:%M:%S')}] Generating intro: {song.artist} - {song.title} (DJ: {dj.value})")
            stage_generate(
                pipeline=self.pipeline,
                songs=songs,
                djs=djs,
                checkpoint=checkpoint,
                test_mode=self.test_mode,
                overwrite=True,  # Force regeneration
            )
            gen_time = datetime.now()
            logger.info(f"[{gen_time.strftime('%H:%M:%S')}] Generation took {(gen_time - start_time).total_seconds():.1f}s")
            
            # Stage 2: Audit
            audit_start = datetime.now()
            logger.info(f"[{audit_start.strftime('%H:%M:%S')}] Auditing intro: {song.artist} - {song.title}")
            audit_results = stage_audit(
                songs=songs,
                djs=djs,
                checkpoint=checkpoint,
                test_mode=self.test_mode,
            )
            audit_time = datetime.now()
            logger.info(f"[{audit_time.strftime('%H:%M:%S')}] Audit took {(audit_time - audit_start).total_seconds():.1f}s")
            
            # Stage 3: Regenerate if failed
            if audit_results.get('failed', 0) > 0:
                regen_start = datetime.now()
                logger.info(f"[{regen_start.strftime('%H:%M:%S')}] Audit failed, regenerating up to {max_retries} times")
                regenerated = stage_regenerate(
                    pipeline=self.pipeline,
                    songs=songs,
                    djs=djs,
                    max_retries=max_retries,
                    test_mode=self.test_mode,
                )
                regen_time = datetime.now()
                logger.info(f"[{regen_time.strftime('%H:%M:%S')}] Regeneration took {(regen_time - regen_start).total_seconds():.1f}s - {regenerated} scripts")
            
            # Stage 4: Audio generation (only if passed and not text_only)
            if not text_only:
                audio_start = datetime.now()
                logger.info(f"[{audio_start.strftime('%H:%M:%S')}] Generating audio for intro")
                audio_count = stage_audio(
                    songs=songs,
                    djs=djs,
                    checkpoint=checkpoint,
                )
                audio_time = datetime.now()
                logger.info(f"[{audio_time.strftime('%H:%M:%S')}] Audio generation took {(audio_time - audio_start).total_seconds():.1f}s - {audio_count} files")
            
            # Return result with audit info
            total_time = datetime.now()
            logger.info(f"[{total_time.strftime('%H:%M:%S')}] Total pipeline time: {(total_time - start_time).total_seconds():.1f}s")
            return self._build_result_from_stages(song, dj, ContentType.INTRO)
            
        except Exception as e:
            logger.error(f"Error in audited generation: {e}")
            return GenerationResult(
                success=False,
                content_type=ContentType.INTRO,
                dj=dj,
                error=str(e),
                song=song,
            )
    
    def _build_result_from_stages(
        self, 
        song: SongInfo, 
        dj: DJ, 
        content_type: ContentType
    ) -> GenerationResult:
        """Build GenerationResult from files created by stages."""
        from src.ai_radio.core.paths import get_script_path, get_audio_path, get_audit_path
        import json
        
        script_path = get_script_path(
            song.to_dict(), 
            dj.value, 
            content_type='intros' if content_type == ContentType.INTRO else 'outros'
        )
        
        audio_path = get_audio_path(
            song.to_dict(),
            dj.value,
            content_type='intros' if content_type == ContentType.INTRO else 'outros'
        )
        
        # Check audit result
        audit_path_passed = get_audit_path(
            song.to_dict(),
            dj.value,
            passed=True,
            content_type='song_intro' if content_type == ContentType.INTRO else 'song_outro'
        )
        
        audit_path_failed = get_audit_path(
            song.to_dict(),
            dj.value,
            passed=False,
            content_type='song_intro' if content_type == ContentType.INTRO else 'song_outro'
        )
        
        # Determine audit status - prioritize failed if both exist
        audit_passed = None
        audit_score = None
        
        if audit_path_failed.exists():
            audit_passed = False
            with open(audit_path_failed, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)
                audit_score = audit_data.get('score', 0)
        elif audit_path_passed.exists():
            audit_passed = True
            with open(audit_path_passed, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)
                audit_score = audit_data.get('score', 0)
        
        # Read script text
        text = None
        if script_path.exists():
            text = script_path.read_text(encoding='utf-8')
        
        return GenerationResult(
            success=script_path.exists(),
            content_type=content_type,
            dj=dj,
            text=text,
            script_path=script_path if script_path.exists() else None,
            audio_path=audio_path if audio_path.exists() else None,
            audit_passed=audit_passed,
            audit_score=audit_score,
            song=song,
        )
