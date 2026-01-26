"""Backend service layer for Review GUI.

This module provides all data operations for the Review GUI using
the API layer exclusively. No direct pipeline or LLM calls.

The GUI should ONLY use functions from this module for:
- Loading content and catalog
- Triggering regeneration
- Managing review status and versions

This ensures the GUI always goes through the proper pipeline with
lyrics, validation, and audit loop.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from src.ai_radio.api import ContentAPI, GenerationAPI, ReviewAPI, AuditAPI
from src.ai_radio.api.schemas import (
    ContentItem,
    ContentType,
    DJ,
    GenerationResult,
    ReviewItem,
    ReviewStatus,
    SongInfo,
    AuditResult,
)
from src.ai_radio.gui.version import (
    VersionManager,
    VersionInfo,
    VersionType,
    VersionMetadata,
)
from src.ai_radio.config import DATA_DIR, GENERATED_DIR, CATALOG_FILE

logger = logging.getLogger(__name__)

# Module-level API instances (lazy initialization)
_content_api: Optional[ContentAPI] = None
_generation_api: Optional[GenerationAPI] = None
_review_api: Optional[ReviewAPI] = None
_audit_api: Optional[AuditAPI] = None


def _get_content_api() -> ContentAPI:
    """Get or create ContentAPI instance."""
    global _content_api
    if _content_api is None:
        _content_api = ContentAPI()
    return _content_api


def _get_generation_api(test_mode: bool = False):
    """Get or create AuditedGenerationAPI instance."""
    from src.ai_radio.api.audited import AuditedGenerationAPI
    global _generation_api
    if _generation_api is None:
        _generation_api = AuditedGenerationAPI(test_mode=test_mode)
    return _generation_api


def _get_review_api(test_mode: bool = False) -> ReviewAPI:
    """Get or create ReviewAPI instance."""
    global _review_api
    if _review_api is None:
        _review_api = ReviewAPI(test_mode=test_mode)
    return _review_api


def _get_audit_api(test_mode: bool = False) -> AuditAPI:
    """Get or create AuditAPI instance."""
    global _audit_api
    if _audit_api is None:
        _audit_api = AuditAPI(test_mode=test_mode)
    return _audit_api


# Content type mapping
CONTENT_TYPE_MAP = {
    "intros": ContentType.INTRO,
    "outros": ContentType.OUTRO,
    "time": ContentType.TIME,
    "weather": ContentType.WEATHER,
}

DJ_MAP = {
    "julie": DJ.JULIE,
    "mr_new_vegas": DJ.MR_NEW_VEGAS,
}

# Cached catalog lookup for better performance
_catalog_lookup_cache: Optional[Dict[str, SongInfo]] = None


def _get_catalog_lookup() -> Dict[str, SongInfo]:
    """Get or create a lookup dictionary for fast song access.
    
    Returns:
        Dict mapping lowercase "artist|title" to SongInfo
    """
    global _catalog_lookup_cache
    if _catalog_lookup_cache is None:
        catalog = load_catalog()
        _catalog_lookup_cache = {
            f"{s.artist.lower()}|{s.title.lower()}": s
            for s in catalog
        }
    return _catalog_lookup_cache


def _find_song_in_catalog(artist: str, title: str) -> Optional[SongInfo]:
    """Find a song in the catalog by artist and title.
    
    Uses cached lookup for O(1) access instead of O(n) iteration.
    
    Args:
        artist: Artist name (case-insensitive)
        title: Song title (case-insensitive)
        
    Returns:
        SongInfo if found, None otherwise
    """
    lookup = _get_catalog_lookup()
    key = f"{artist.lower()}|{title.lower()}"
    return lookup.get(key)


def load_catalog() -> List[SongInfo]:
    """Load the song catalog using ContentAPI.
    
    Returns:
        List of SongInfo objects
    """
    api = _get_content_api()
    return api.load_catalog()


def get_song_generation_status(song: SongInfo, dj_str: str) -> Dict[str, bool]:
    """Check generation status for a song.
    
    Args:
        song: SongInfo object
        dj_str: DJ name string (julie, mr_new_vegas)
        
    Returns:
        Dict with intro_script, intro_audio, outro_script, outro_audio booleans
    """
    api = _get_content_api()
    dj = DJ_MAP.get(dj_str, DJ.JULIE)
    
    status = {
        "intro_script": False,
        "intro_audio": False,
        "outro_script": False,
        "outro_audio": False,
    }
    
    # Check intro
    intro = api.get_script(ContentType.INTRO, dj, song=song)
    if intro:
        status["intro_script"] = intro.has_script
        status["intro_audio"] = intro.has_audio
    
    # Check outro
    outro = api.get_script(ContentType.OUTRO, dj, song=song)
    if outro:
        status["outro_script"] = outro.has_script
        status["outro_audio"] = outro.has_audio
    
    return status


def regenerate_content(
    content_type_str: str,
    dj_str: str,
    item_id: str,
    regen_type: str,
    feedback: str = "",
) -> Tuple[bool, Optional[str]]:
    """Regenerate content through the API layer.
    
    This is the ONLY way the GUI should trigger generation.
    Goes through the full pipeline with lyrics, validation, and audit.
    
    Args:
        content_type_str: Content type (intros, outros, time, weather)
        dj_str: DJ name (julie, mr_new_vegas)
        item_id: Item identifier (artist-song or HH-MM)
        regen_type: What to regenerate (script, audio, both)
        feedback: Optional feedback for regeneration
        
    Returns:
        Tuple of (success, error_message)
    """
    api = _get_generation_api()
    content_type = CONTENT_TYPE_MAP.get(content_type_str)
    dj = DJ_MAP.get(dj_str, DJ.JULIE)
    
    if content_type is None:
        return False, f"Unknown content type: {content_type_str}"
    
    try:
        if content_type == ContentType.INTRO:
            return _regenerate_song_intro(api, dj, item_id, regen_type, feedback)
        elif content_type == ContentType.OUTRO:
            return _regenerate_song_outro(api, dj, item_id, regen_type, feedback)
        elif content_type == ContentType.TIME:
            return _regenerate_time(api, dj, item_id, regen_type)
        elif content_type == ContentType.WEATHER:
            return _regenerate_weather(api, dj, item_id)
        else:
            return False, f"Unsupported content type: {content_type}"
    except Exception as e:
        logger.error(f"Regeneration failed: {e}")
        return False, str(e)


def _parse_song_from_item_id(item_id: str) -> Tuple[str, str]:
    """Parse artist and title from item_id like 'Artist_Name-Song_Title'.
    
    Returns:
        Tuple of (artist, title) with underscores replaced by spaces
    """
    parts = item_id.split("-", 1)
    if len(parts) == 2:
        artist = parts[0].replace("_", " ").strip()
        title = parts[1].replace("_", " ").strip()
        return artist, title
    return item_id.replace("_", " "), ""


def _parse_time_from_item_id(item_id: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse hour and minute from item_id like '12-00'.
    
    Returns:
        Tuple of (hour, minute) or (None, None) if invalid
    """
    parts = item_id.split("-")
    if len(parts) >= 2:
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return None, None


def _regenerate_song_intro(
    api,  # Now AuditedGenerationAPI
    dj: DJ,
    item_id: str,
    regen_type: str,
    feedback: str,
) -> Tuple[bool, Optional[str]]:
    """Regenerate a song intro through the audited API."""
    artist, title = _parse_song_from_item_id(item_id)
    if not title:
        return False, f"Could not parse artist/title from: {item_id}"
    
    # Find song in catalog using optimized lookup
    song = _find_song_in_catalog(artist, title)
    
    if song is None:
        # Create a new SongInfo if not in catalog
        song = SongInfo(id=item_id, artist=artist, title=title)
    
    # Route to appropriate generation method
    logger.info(f"Regenerating intro via audited API: {artist} - {title} (DJ: {dj.value}, type: {regen_type})")
    
    if regen_type == "audio":
        # Audio-only: Skip stages, just generate audio
        result = api.generate_intro(
            song=song,
            dj=dj,
            text_only=False,
            overwrite=True,
        )
    else:
        # Script or both: Use audited pipeline
        text_only = regen_type == "script"
        result = api.generate_intro_with_audit(
            song=song,
            dj=dj,
            max_retries=5,
            text_only=text_only,
            user_feedback=feedback if feedback else None,
        )
    
    if result.success:
        audit_info = ""
        if result.audit_passed is not None:
            audit_info = f" (audit: {'✅ passed' if result.audit_passed else '❌ failed'}, score: {result.audit_score})"
        logger.info(f"✅ Intro regenerated via API: {artist} - {title}{audit_info}")
        return True, None
    else:
        logger.error(f"❌ Intro regeneration failed: {result.error}")
        return False, result.error


def _regenerate_song_outro(
    api,  # Now AuditedGenerationAPI
    dj: DJ,
    item_id: str,
    regen_type: str,
    feedback: str,
) -> Tuple[bool, Optional[str]]:
    """Regenerate a song outro through the audited API."""
    artist, title = _parse_song_from_item_id(item_id)
    if not title:
        return False, f"Could not parse artist/title from: {item_id}"
    
    # Find song in catalog using optimized lookup
    song = _find_song_in_catalog(artist, title)
    
    if song is None:
        song = SongInfo(id=item_id, artist=artist, title=title)
    
    logger.info(f"Regenerating outro via audited API: {artist} - {title} (DJ: {dj.value}, type: {regen_type})")
    
    if regen_type == "audio":
        # Audio-only: Skip stages
        result = api.generate_outro(
            song=song,
            dj=dj,
            text_only=False,
            overwrite=True,
        )
    else:
        # Script or both: Use audited pipeline (once we implement generate_outro_with_audit)
        # For now, fall back to non-audited
        text_only = regen_type == "script"
        result = api.generate_outro(
            song=song,
            dj=dj,
            text_only=text_only,
            overwrite=True,
            audit_feedback=feedback if feedback else None,
        )
    
    if result.success:
        logger.info(f"✅ Outro regenerated via API: {artist} - {title}")
        return True, None
    else:
        logger.error(f"❌ Outro regeneration failed: {result.error}")
        return False, result.error


def _regenerate_time(
    api: GenerationAPI,
    dj: DJ,
    item_id: str,
    regen_type: str,
) -> Tuple[bool, Optional[str]]:
    """Regenerate a time announcement through the API."""
    hour, minute = _parse_time_from_item_id(item_id)
    if hour is None:
        return False, f"Could not parse time from: {item_id}"
    
    text_only = regen_type == "script"
    
    logger.info(f"Regenerating time via API: {hour:02d}:{minute:02d} (DJ: {dj.value})")
    
    result = api.generate_time_announcement(
        hour=hour,
        minute=minute,
        dj=dj,
        text_only=text_only,
        overwrite=True,
    )
    
    if result.success:
        return True, None
    else:
        return False, result.error


def _regenerate_weather(
    api: GenerationAPI,
    dj: DJ,
    item_id: str,
) -> Tuple[bool, Optional[str]]:
    """Regenerate a weather announcement through the API."""
    hour, _ = _parse_time_from_item_id(item_id)
    if hour is None:
        return False, f"Could not parse weather hour from: {item_id}"
    
    logger.info(f"Regenerating weather via API: {hour:02d}:00 (DJ: {dj.value})")
    
    # For now, use a placeholder weather summary
    # In a real implementation, this would fetch from weather API
    result = api.generate_weather_announcement(
        hour=hour,
        dj=dj,
        weather_summary="Current conditions",
        text_only=True,
        overwrite=True,
    )
    
    if result.success:
        return True, None
    else:
        return False, result.error


def save_manual_edit(
    folder_path: Path,
    dj_str: str,
    content_type: str,
    new_script: str,
    notes: str = "",
) -> Tuple[bool, Optional[VersionInfo]]:
    """Save a manual script edit as a new version.
    
    Creates a new version file and updates the version metadata.
    Does NOT regenerate audio - use regenerate_audio_for_version for that.
    
    Args:
        folder_path: Path to the content folder
        dj_str: DJ name
        content_type: Content type string
        new_script: New script text
        notes: Optional notes about the edit
        
    Returns:
        Tuple of (success, VersionInfo or None)
    """
    try:
        manager = VersionManager(folder_path, dj_str, content_type)
        version_info = manager.create_version(
            script_text=new_script,
            version_type=VersionType.MANUAL_EDIT,
            notes=notes or "Manual edit from Review GUI",
        )
        logger.info(f"Created new version {version_info.version} at {folder_path}")
        return True, version_info
    except Exception as e:
        logger.error(f"Failed to save manual edit: {e}")
        return False, None


def get_version_metadata(
    folder_path: Path,
    dj_str: str,
    content_type: str,
) -> VersionMetadata:
    """Get version metadata for a content item.
    
    Args:
        folder_path: Path to content folder
        dj_str: DJ name
        content_type: Content type
        
    Returns:
        VersionMetadata with all versions
    """
    manager = VersionManager(folder_path, dj_str, content_type)
    return manager.load_metadata()


def get_script_text(folder_path: Path, dj_str: str, content_type: str, version: int) -> Optional[str]:
    """Get script text for a specific version.
    
    Args:
        folder_path: Path to content folder
        dj_str: DJ name
        content_type: Content type
        version: Version number
        
    Returns:
        Script text or None if not found
    """
    manager = VersionManager(folder_path, dj_str, content_type)
    script_path = manager.get_script_path(version)
    
    if script_path.exists():
        return script_path.read_text(encoding='utf-8')
    return None


def approve_content(item: ReviewItem, notes: str = "") -> bool:
    """Approve a content item through the API.
    
    Args:
        item: ReviewItem to approve
        notes: Reviewer notes
        
    Returns:
        True if successful
    """
    try:
        api = _get_review_api()
        api.approve(item, notes=notes)
        return True
    except Exception as e:
        logger.error(f"Failed to approve: {e}")
        return False


def reject_content(item: ReviewItem, reason: str, queue_regen: bool = False) -> bool:
    """Reject a content item through the API.
    
    Args:
        item: ReviewItem to reject
        reason: Rejection reason
        queue_regen: Whether to queue for regeneration
        
    Returns:
        True if successful
    """
    try:
        api = _get_review_api()
        api.reject(item, reason=reason, queue_regen=queue_regen)
        return True
    except Exception as e:
        logger.error(f"Failed to reject: {e}")
        return False


def get_review_stats(dj_str: Optional[str] = None) -> Dict:
    """Get review statistics.
    
    Args:
        dj_str: Optional DJ filter
        
    Returns:
        Dictionary with review stats
    """
    api = _get_review_api()
    dj = DJ_MAP.get(dj_str) if dj_str else None
    return api.get_review_stats(dj=dj)


def list_content(
    dj_str: Optional[str] = None,
    content_type_str: Optional[str] = None,
    include_text: bool = False,
) -> List[ContentItem]:
    """List generated content through the API.
    
    Args:
        dj_str: Optional DJ filter
        content_type_str: Optional content type filter
        include_text: Whether to include script text
        
    Returns:
        List of ContentItem objects
    """
    api = _get_content_api()
    dj = DJ_MAP.get(dj_str) if dj_str else None
    content_type = CONTENT_TYPE_MAP.get(content_type_str) if content_type_str else None
    
    return api.list_scripts(dj=dj, content_type=content_type, include_text=include_text)


def get_audit_status(content_type_str: str, dj_str: str, item_id: str) -> Optional[str]:
    """Get audit status for a content item.
    
    Args:
        content_type_str: Content type
        dj_str: DJ name
        item_id: Item identifier
        
    Returns:
        'passed', 'failed', or None
    """
    # For now, check file-based audit status
    # This could be moved to AuditAPI
    from src.ai_radio.config import DATA_DIR
    
    audit_dir = DATA_DIR / "audit"
    safe_id = item_id.replace("/", "_").replace("\\", "_")
    
    # Normalize content type for audit file naming
    content_suffix = content_type_str.rstrip("s")  # intros -> intro
    
    for status in ["passed", "failed"]:
        audit_file = audit_dir / dj_str / status / f"{safe_id}_{content_suffix}_audit.json"
        if audit_file.exists():
            return status
    
    return None
