"""
Validated generation pipeline with multi-stage validation.

This is the main entry point for generating validated scripts.

Pipeline stages:
1. Generate script using fluffy model (with lyrics context for thematic bridging)
2. Rule-based validation (encoding, punctuation, structure)
3. LLM character validation (voice, naturalness)
4. Regenerate if validation fails (max retries)
"""
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.validators.rule_based import validate_script, RuleValidationResult
from src.ai_radio.generation.validators.character import validate_character, CharacterValidationResult

logger = logging.getLogger(__name__)

# Default max retries for regeneration
MAX_RETRIES = 3


@dataclass
class ValidatedScript:
    """A script that has passed all validation stages."""
    script_id: str
    text: str
    dj: str
    content_type: str
    artist: Optional[str] = None
    title: Optional[str] = None
    lyrics_context: Optional[str] = None
    
    # Validation metadata
    attempts: int = 1
    rule_validation: Optional[RuleValidationResult] = None
    character_validation: Optional[CharacterValidationResult] = None


@dataclass
class GenerationResult:
    """Result of validated generation attempt."""
    success: bool
    script: Optional[ValidatedScript] = None
    errors: List[str] = field(default_factory=list)
    attempts: int = 0


def load_lyrics(title: str, artist: str, lyrics_dir: Path = Path("music_with_lyrics")) -> Optional[str]:
    """
    Load song lyrics for thematic bridging.
    
    Tries multiple filename patterns to find the lyrics file.
    Returns first few lines for context (not full lyrics).
    """
    if not lyrics_dir.exists():
        return None
    
    # Try different filename patterns
    patterns = [
        f"{title} by {artist}.txt",
        f"{title}.txt",
        f"{artist} - {title}.txt",
    ]
    
    for pattern in patterns:
        lyric_path = lyrics_dir / pattern
        if lyric_path.exists():
            try:
                content = lyric_path.read_text(encoding='utf-8')
                # Return first 500 chars as context (not full lyrics)
                lines = content.strip().split('\n')[:10]  # First 10 lines
                return '\n'.join(lines)
            except Exception as e:
                logger.warning(f"Failed to read lyrics from {lyric_path}: {e}")
    
    return None


def sanitize_text(text: str) -> str:
    """
    Clean up generated text before validation.
    
    This handles encoding issues and basic cleanup,
    but does NOT try to fix grammar (that's what regeneration is for).
    """
    import re
    
    # Fix common encoding issues (double-encoded UTF-8)
    # These patterns appear when UTF-8 is interpreted as Windows-1252
    replacements = [
        ('â€¦', '...'),   # Ellipsis
        ('â€™', "'"),     # Right single quote
        ('â€˜', "'"),     # Left single quote
        ('â€œ', '"'),     # Left double quote
        ('â€', '"'),      # Right double quote (partial)
        ('â€"', '-'),     # Em-dash
        ('â€"', '-'),     # En-dash
        ('Ã©', 'e'),      # Accented e
        ('Ã¨', 'e'),      # Another accent
        ('Ã ', 'a'),      # Accented a
        # Also handle the raw multi-byte sequences
        ('\u00e2\u20ac\u00a6', '...'),  # Ellipsis as UTF-8 misread
        ('\u00e2\u20ac\u2122', "'"),    # Apostrophe
        ('\u00e2\u20ac\u0153', '"'),    # Open quote
        ('\u00e2\u20ac', '"'),          # Close quote partial
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    
    # Also catch any remaining â followed by special chars (likely encoding issue)
    text = re.sub(r'â[€™˜œ""\u20ac\u2122\u0153]+', '...', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Normalize ellipsis
    text = text.replace('...', '…')
    text = re.sub(r'…+', '…', text)  # Multiple ellipsis to one
    
    # Fix double periods
    text = re.sub(r'\.{2,}', '.', text)
    
    # Fix period after ellipsis
    text = text.replace('….', '…')
    text = text.replace('…!', '!')
    text = text.replace('…?', '?')
    
    return text


class ValidatedGenerationPipeline:
    """
    Pipeline for generating scripts with built-in validation.
    
    Uses multi-stage validation:
    1. Generate with fluffy model
    2. Rule-based validation
    3. LLM character validation
    4. Regenerate if fails (max retries)
    """
    
    def __init__(
        self,
        output_dir: Path = Path("data/generated"),
        prompt_version: str = "v2",
        max_retries: int = MAX_RETRIES,
        lyrics_dir: Path = Path("music_with_lyrics"),
    ):
        self.output_dir = output_dir
        self.prompt_version = prompt_version
        self.max_retries = max_retries
        self.lyrics_dir = lyrics_dir
        
        # Use existing pipeline for generation
        self.generation_pipeline = GenerationPipeline(
            output_dir=output_dir,
            prompt_version=prompt_version,
        )
    
    def generate_song_intro(
        self,
        song_id: str,
        artist: str,
        title: str,
        dj: str,
    ) -> GenerationResult:
        """
        Generate a validated song introduction.
        
        Args:
            song_id: Unique identifier for the song
            artist: Artist name
            title: Song title
            dj: DJ name ("julie" or "mr_new_vegas")
        
        Returns:
            GenerationResult with success status and validated script
        """
        errors = []
        attempts = 0
        
        # Load lyrics for thematic bridging
        lyrics_context = load_lyrics(title, artist, self.lyrics_dir)
        
        for attempt in range(self.max_retries):
            attempts += 1
            logger.info(f"Generation attempt {attempts}/{self.max_retries} for {song_id}_{dj}")
            
            # Stage 1: Generate
            try:
                result = self.generation_pipeline.generate_song_intro(
                    song_id=song_id,
                    artist=artist,
                    title=title,
                    dj=dj,
                    text_only=True,
                    lyrics_context=lyrics_context,  # Pass lyrics for thematic bridging
                )
                
                if not result.success or not result.text:
                    errors.append(f"Attempt {attempts}: Generation failed")
                    continue
                
                raw_text = result.text
            except Exception as e:
                errors.append(f"Attempt {attempts}: Generation error - {e}")
                continue
            
            # Sanitize before validation
            text = sanitize_text(raw_text)
            
            # Stage 2: Rule-based validation
            rule_result = validate_script(
                text=text,
                content_type="song_intro",
                artist=artist,
                title=title,
            )
            
            if not rule_result.passed:
                errors.append(f"Attempt {attempts}: Rule validation failed - {rule_result.errors}")
                logger.debug(f"Rule validation errors: {rule_result.errors}")
                continue  # Regenerate
            
            # Stage 3: LLM character validation
            char_result = validate_character(
                client=None,  # Use default client
                text=text,
                dj=dj,
                content_type="song_intro",
            )
            
            if not char_result.passed:
                errors.append(f"Attempt {attempts}: Character validation failed - {char_result.issues}")
                logger.debug(f"Character validation issues: {char_result.issues}")
                continue  # Regenerate
            
            # All validations passed!
            validated_script = ValidatedScript(
                script_id=f"{song_id}_{dj}",
                text=text,
                dj=dj,
                content_type="song_intro",
                artist=artist,
                title=title,
                lyrics_context=lyrics_context,
                attempts=attempts,
                rule_validation=rule_result,
                character_validation=char_result,
            )
            
            return GenerationResult(
                success=True,
                script=validated_script,
                attempts=attempts,
            )
        
        # All retries exhausted
        return GenerationResult(
            success=False,
            errors=errors,
            attempts=attempts,
        )
    
    def generate_batch(
        self,
        songs: List[Dict[str, Any]],
        djs: List[str],
    ) -> List[GenerationResult]:
        """
        Generate validated scripts for a batch of songs.
        
        Args:
            songs: List of song dicts with id, artist, title
            djs: List of DJ names to generate for each song
        
        Returns:
            List of GenerationResult for each song/dj combination
        """
        results = []
        
        for song in songs:
            for dj in djs:
                result = self.generate_song_intro(
                    song_id=song['id'],
                    artist=song['artist'],
                    title=song['title'],
                    dj=dj,
                )
                results.append(result)
                
                if result.success:
                    logger.info(f"✓ {song['id']}_{dj} passed after {result.attempts} attempt(s)")
                else:
                    logger.warning(f"✗ {song['id']}_{dj} failed after {result.attempts} attempts")
        
        return results
