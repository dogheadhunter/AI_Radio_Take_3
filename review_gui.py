"""
Streamlit-based review GUI for AI Radio generated scripts and audio.

Allows manual review, approval/rejection, version comparison,
and regeneration queueing of generated content.

IMPORTANT: This GUI uses the API layer exclusively for all operations.
No direct LLM/TTS calls - all generation goes through src/ai_radio/api/
to ensure proper lyrics context, validation, and audit loop.
"""
import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import base64
import re
import sys
import time
import logging

# Configure logging for generation tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import GUI utilities and backend (API-powered)
from src.ai_radio.gui import (
    render_diff,
    render_inline_diff,
    VersionManager,
    VersionType,
    inject_mobile_styles,
    render_status_badge,
)
from src.ai_radio.gui import backend as gui_backend

# Constants
DATA_DIR = Path("data")
GENERATED_DIR = DATA_DIR / "generated"
AUDIT_DIR = DATA_DIR / "audit"
REGEN_QUEUE_FILE = DATA_DIR / "regeneration_queue.json"
CATALOG_FILE = DATA_DIR / "catalog.json"
LYRICS_DIR = Path("music_with_lyrics")

# Content types and their folder structure
CONTENT_TYPES = ["intros", "outros", "time", "weather"]
DJS = ["julie", "mr_new_vegas"]

# Failure reason categories by content type
SCRIPT_ISSUES = {
    "intros": [
        "Character voice mismatch",
        "Wrong era references",
        "Forbidden elements (swearing, modern references)",
        "Unnatural flow",
        "Wrong length",
        "Doesn't incorporate lyrics",
        "Factually incorrect"
    ],
    "outros": [
        "Character voice mismatch",
        "Wrong era references",
        "Forbidden elements (swearing, modern references)",
        "Unnatural flow",
        "Wrong length",
        "Doesn't incorporate lyrics",
        "Factually incorrect"
    ],
    "time": [
        "Character voice mismatch",
        "Unnatural flow",
        "Wrong length",
        "Incorrect time"
    ],
    "weather": [
        "Character voice mismatch",
        "Doesn't incorporate weather data",
        "Unnatural flow",
        "Wrong length",
        "Factually incorrect"
    ]
}

AUDIO_ISSUES = [
    "Garbled/distorted audio",
    "Wrong voice",
    "Mispronunciation",
    "Pacing issues",
    "Volume issues",
    "Audio artifacts",
    "Unnatural intonation"
]


@dataclass
class ReviewItem:
    """Represents a script/audio pair for review."""
    content_type: str
    dj: str
    item_id: str
    folder_path: Path
    script_versions: List[Path]
    audio_versions: List[Path]  # Legacy: single audio per version
    audio_30sec: Dict[int, Path] = None  # version -> 30sec audio path
    audio_full: Dict[int, Path] = None   # version -> full audio path
    latest_version: int = 0
    audit_status: Optional[str] = None
    review_status: Optional[str] = None
    
    def __post_init__(self):
        if self.audio_30sec is None:
            self.audio_30sec = {}
        if self.audio_full is None:
            self.audio_full = {}
    
    def get_script_path(self, version: int = None) -> Optional[Path]:
        """Get script path for a specific version (or latest)."""
        if version is None:
            version = self.latest_version
        if version < len(self.script_versions):
            return self.script_versions[version]
        return None
    
    def get_audio_path(self, version: int = None, ref_type: str = None) -> Optional[Path]:
        """Get audio path for a specific version and reference type.
        
        Args:
            version: Script version number (default: latest)
            ref_type: '30sec', 'full', or None (tries full first, then 30sec, then legacy)
        """
        if version is None:
            version = self.latest_version
        
        # If specific type requested
        if ref_type == '30sec' and version in self.audio_30sec:
            return self.audio_30sec[version]
        if ref_type == 'full' and version in self.audio_full:
            return self.audio_full[version]
        
        # Auto-detect: try full, then 30sec, then legacy
        if version in self.audio_full:
            return self.audio_full[version]
        if version in self.audio_30sec:
            return self.audio_30sec[version]
        if version < len(self.audio_versions):
            return self.audio_versions[version]
        return None
    
    def has_dual_audio(self, version: int = None) -> bool:
        """Check if both 30sec and full audio exist for this version."""
        if version is None:
            version = self.latest_version
        return version in self.audio_30sec and version in self.audio_full




def load_review_status(folder_path: Path) -> Dict[str, Any]:
    """Load review status from review_status.json in folder."""
    status_file = folder_path / "review_status.json"
    if status_file.exists():
        try:
            return json.loads(status_file.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {
        "status": "pending",
        "reviewed_at": None,
        "reviewer_notes": "",
        "script_issues": [],
        "audio_issues": []
    }


def save_review_status(folder_path: Path, status: Dict[str, Any]):
    """Save review status to review_status.json in folder."""
    status_file = folder_path / "review_status.json"
    status_file.write_text(json.dumps(status, indent=2), encoding='utf-8')


def get_audit_status(content_type: str, dj: str, item_id: str) -> Optional[str]:
    """Check audit status by looking in audit directory."""
    # Normalize item_id for audit file naming
    safe_id = item_id.replace("/", "_").replace("\\", "_")
    
    for status in ["passed", "failed"]:
        audit_file = AUDIT_DIR / dj / status / f"{safe_id}_{content_type.rstrip('s')}_audit.json"
        if audit_file.exists():
            return status
    return None


def _scan_item_folder(item_folder: Path, dj: str, content_type: str) -> Optional[dict]:
    """Scan a single item folder and return its content info.
    
    Returns dict with script_versions, audio_versions, audio_30sec, audio_full, latest_version
    or None if folder has no content.
    """
    # Find all versions of scripts and audio
    # Note: outros use different naming convention (_outro instead of _0)
    if content_type == "outros":
        # For outros: julie_outro.txt, julie_outro_1.txt, etc.
        script_versions = sorted(item_folder.glob(f"{dj}_outro*.txt"))
        audio_versions = sorted(item_folder.glob(f"{dj}_outro*.wav"))
    else:
        # For other types: julie_0.txt, julie_1.txt, etc.
        script_versions = sorted(item_folder.glob(f"{dj}_*.txt"))
        audio_versions = sorted(item_folder.glob(f"{dj}_*.wav"))
    
    if not script_versions and not audio_versions:
        return None
    
    # Determine latest version number and categorize audio by ref type
    latest_version = 0
    audio_30sec = {}  # version -> path
    audio_full = {}   # version -> path
    
    for path in script_versions:
        try:
            stem_parts = path.stem.split('_')
            if content_type == "outros":
                if len(stem_parts) > 2:
                    version = int(stem_parts[-1])
                    latest_version = max(latest_version, version)
            else:
                version = int(stem_parts[-1])
                latest_version = max(latest_version, version)
        except (ValueError, IndexError):
            pass
    
    for path in audio_versions:
        try:
            stem_parts = path.stem.split('_')
            # Check for new naming: dj_version_reftype.wav (e.g., mr_new_vegas_0_30sec.wav)
            if stem_parts[-1] == '30sec':
                # mr_new_vegas_0_30sec -> version is stem_parts[-2]
                version = int(stem_parts[-2])
                audio_30sec[version] = path
                latest_version = max(latest_version, version)
            elif stem_parts[-1] == 'full':
                # mr_new_vegas_0_full -> version is stem_parts[-2]
                version = int(stem_parts[-2])
                audio_full[version] = path
                latest_version = max(latest_version, version)
            else:
                # Legacy naming: dj_version.wav (e.g., mr_new_vegas_0.wav)
                if content_type == "outros":
                    if len(stem_parts) > 2:
                        version = int(stem_parts[-1])
                        latest_version = max(latest_version, version)
                else:
                    version = int(stem_parts[-1])
                    latest_version = max(latest_version, version)
                    # Store legacy audio in audio_full for backwards compatibility
                    if version not in audio_full:
                        audio_full[version] = path
        except (ValueError, IndexError):
            pass
    
    return {
        'script_versions': script_versions,
        'audio_versions': audio_versions,
        'audio_30sec': audio_30sec,
        'audio_full': audio_full,
        'latest_version': latest_version,
    }


def scan_generated_content() -> List[ReviewItem]:
    """Scan data/generated directory for all content.
    
    Merges content from both legacy doubled paths (intros/intros/dj) 
    and new single paths (intros/dj) to handle transition period.
    """
    items = []
    
    if not GENERATED_DIR.exists():
        return items
    
    for content_type in CONTENT_TYPES:
        content_dir = GENERATED_DIR / content_type
        if not content_dir.exists():
            continue
        
        for dj in DJS:
            # Check both path structures and merge content
            legacy_dj_dir = content_dir / content_type / dj  # doubled: intros/intros/dj
            new_dj_dir = content_dir / dj                     # single: intros/dj
            
            # Collect all item folders from both paths
            item_folders_by_id = {}  # item_id -> (folder_path, prefer_new)
            
            # First add legacy path items
            if legacy_dj_dir.exists():
                for item_folder in legacy_dj_dir.iterdir():
                    if item_folder.is_dir():
                        item_folders_by_id[item_folder.name] = (item_folder, False)
            
            # Then add/override with new path items (new path takes priority)
            if new_dj_dir.exists():
                for item_folder in new_dj_dir.iterdir():
                    if item_folder.is_dir():
                        item_id = item_folder.name
                        if item_id in item_folders_by_id:
                            # Both exist - we need to merge content from both
                            legacy_folder = item_folders_by_id[item_id][0]
                            item_folders_by_id[item_id] = ((legacy_folder, item_folder), True)
                        else:
                            item_folders_by_id[item_id] = (item_folder, False)
            
            # Process each item
            for item_id, (folder_info, is_merged) in item_folders_by_id.items():
                if is_merged:
                    # Merge content from both folders
                    legacy_folder, new_folder = folder_info
                    legacy_content = _scan_item_folder(legacy_folder, dj, content_type)
                    new_content = _scan_item_folder(new_folder, dj, content_type)
                    
                    if not legacy_content and not new_content:
                        continue
                    
                    # Prefer new folder as primary, merge versions
                    primary_folder = new_folder
                    
                    # Combine all versions from both folders
                    all_scripts = []
                    all_audio = []
                    merged_30sec = {}
                    merged_full = {}
                    max_version = 0
                    
                    if legacy_content:
                        all_scripts.extend(legacy_content['script_versions'])
                        all_audio.extend(legacy_content['audio_versions'])
                        merged_30sec.update(legacy_content['audio_30sec'])
                        merged_full.update(legacy_content['audio_full'])
                        max_version = max(max_version, legacy_content['latest_version'])
                    
                    if new_content:
                        all_scripts.extend(new_content['script_versions'])
                        all_audio.extend(new_content['audio_versions'])
                        merged_30sec.update(new_content['audio_30sec'])
                        merged_full.update(new_content['audio_full'])
                        max_version = max(max_version, new_content['latest_version'])
                    
                    # Remove duplicates and sort
                    script_versions = sorted(set(all_scripts), key=lambda p: p.name)
                    audio_versions = sorted(set(all_audio), key=lambda p: p.name)
                    
                else:
                    # Single folder
                    item_folder = folder_info
                    content = _scan_item_folder(item_folder, dj, content_type)
                    if not content:
                        continue
                    
                    primary_folder = item_folder
                    script_versions = content['script_versions']
                    audio_versions = content['audio_versions']
                    merged_30sec = content['audio_30sec']
                    merged_full = content['audio_full']
                    max_version = content['latest_version']
                
                # Get audit and review status
                audit_status = get_audit_status(content_type, dj, item_id)
                review_status_data = load_review_status(primary_folder)
                review_status = review_status_data.get("status", "pending")
                
                items.append(ReviewItem(
                    content_type=content_type,
                    dj=dj,
                    item_id=item_id,
                    folder_path=primary_folder,
                    script_versions=script_versions,
                    audio_versions=audio_versions,
                    latest_version=max_version,
                    audit_status=audit_status,
                    review_status=review_status,
                    audio_30sec=merged_30sec,
                    audio_full=merged_full
                ))
    
    return items


def filter_items(items: List[ReviewItem]) -> List[ReviewItem]:
    """Apply filters to item list."""
    filtered = items
    
    # Content type filter
    if st.session_state.filter_content_type != "All":
        filtered = [i for i in filtered if i.content_type == st.session_state.filter_content_type]
    
    # DJ filter
    if st.session_state.filter_dj != "All":
        filtered = [i for i in filtered if i.dj == st.session_state.filter_dj]
    
    # Audit status filter
    if st.session_state.filter_audit_status != "All":
        filtered = [i for i in filtered if i.audit_status == st.session_state.filter_audit_status.lower()]
    
    # Review status filter
    if st.session_state.filter_review_status != "All":
        filtered = [i for i in filtered if i.review_status == st.session_state.filter_review_status.lower()]
    
    # Search query - normalize underscores to spaces for better matching
    if st.session_state.search_query:
        query = st.session_state.search_query.lower().replace('_', ' ')
        filtered = [i for i in filtered if query in i.item_id.lower().replace('_', ' ')]
    
    return filtered


def add_to_regen_queue(item: ReviewItem, regenerate_type: str, feedback: str):
    """Add an item to the regeneration queue."""
    queue = []
    if REGEN_QUEUE_FILE.exists():
        try:
            queue = json.loads(REGEN_QUEUE_FILE.read_text(encoding='utf-8'))
        except Exception:
            queue = []
    
    queue_item = {
        "content_type": item.content_type,
        "dj": item.dj,
        "item_id": item.item_id,
        "folder_path": str(item.folder_path),
        "regenerate_type": regenerate_type,
        "feedback": feedback,
        "added_at": datetime.now().isoformat()
    }
    
    queue.append(queue_item)
    REGEN_QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding='utf-8')


def get_regen_queue_count() -> int:
    """Get number of items in regeneration queue."""
    if not REGEN_QUEUE_FILE.exists():
        return 0
    try:
        queue = json.loads(REGEN_QUEUE_FILE.read_text(encoding='utf-8'))
        return len(queue)
    except Exception:
        return 0


def clear_regen_queue():
    """Clear the regeneration queue."""
    if REGEN_QUEUE_FILE.exists():
        REGEN_QUEUE_FILE.write_text("[]", encoding='utf-8')


def load_catalog() -> List[Dict]:
    """Load the song catalog from catalog.json."""
    if not CATALOG_FILE.exists():
        return []
    try:
        data = json.loads(CATALOG_FILE.read_text(encoding='utf-8'))
        return data.get("songs", [])
    except Exception as e:
        logger.error(f"Failed to load catalog: {e}")
        return []


def get_song_generation_status(artist: str, title: str, dj: str) -> Dict[str, bool]:
    """Check what has been generated for a song (intro/outro script and audio)."""
    # Normalize names for folder lookup - must match pipeline's _make_song_folder()
    # Pipeline uses: c if c.isalnum() or c in (' ', '-', '_') else '_'
    safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist)
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
    safe_artist = safe_artist.strip().replace(' ', '_')
    safe_title = safe_title.strip().replace(' ', '_')
    folder_name = f"{safe_artist}-{safe_title}"
    
    status = {
        "intro_script": False,
        "intro_audio": False,
        "outro_script": False,
        "outro_audio": False,
    }
    
    # Check intros - both legacy doubled path and new single path
    intro_paths = [
        GENERATED_DIR / "intros" / "intros" / dj / folder_name,  # Legacy doubled path
        GENERATED_DIR / "intros" / dj / folder_name,              # New single path
    ]
    for intro_path in intro_paths:
        if intro_path.exists():
            scripts = list(intro_path.glob(f"{dj}*.txt"))
            audios = list(intro_path.glob(f"{dj}*.wav")) + list(intro_path.glob(f"*_30sec.wav")) + list(intro_path.glob(f"*_full.wav"))
            if scripts:
                status["intro_script"] = True
            if audios:
                status["intro_audio"] = True
    
    # Check outros - both legacy doubled path and new single path
    outro_paths = [
        GENERATED_DIR / "outros" / "outros" / dj / folder_name,  # Legacy doubled path
        GENERATED_DIR / "outros" / dj / folder_name,              # New single path
    ]
    for outro_path in outro_paths:
        if outro_path.exists():
            scripts = list(outro_path.glob(f"{dj}*.txt"))
            audios = list(outro_path.glob(f"{dj}*.wav")) + list(outro_path.glob(f"*_30sec.wav")) + list(outro_path.glob(f"*_full.wav"))
            if scripts:
                status["outro_script"] = True
            if audios:
                status["outro_audio"] = True
    
    return status


def add_catalog_item_to_queue(artist: str, title: str, dj: str, content_type: str, regen_type: str):
    """Add a catalog song to the regeneration queue for generation."""
    # Normalize names for folder path - must match pipeline's _make_song_folder()
    safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist)
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
    safe_artist = safe_artist.strip().replace(' ', '_')
    safe_title = safe_title.strip().replace(' ', '_')
    folder_name = f"{safe_artist}-{safe_title}"
    
    # Use single path structure (correct): intros/dj/folder
    folder_path = GENERATED_DIR / content_type / dj / folder_name
    
    queue = []
    if REGEN_QUEUE_FILE.exists():
        try:
            queue = json.loads(REGEN_QUEUE_FILE.read_text(encoding='utf-8'))
        except Exception:
            queue = []
    
    # Check if already in queue
    for item in queue:
        if (item.get("item_id") == folder_name and 
            item.get("dj") == dj and 
            item.get("content_type") == content_type):
            return False  # Already queued
    
    queue_item = {
        "content_type": content_type,
        "dj": dj,
        "item_id": folder_name,
        "folder_path": str(folder_path),
        "regenerate_type": regen_type,
        "feedback": "",
        "added_at": datetime.now().isoformat(),
        "source": "catalog"
    }
    
    queue.append(queue_item)
    REGEN_QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    logger.info(f"Added to queue: {artist} - {title} ({content_type}/{dj}/{regen_type})")
    return True


def process_regeneration_queue(progress_callback=None, status_callback=None):
    """
    Process items in the regeneration queue with progress tracking.
    
    IMPORTANT: Uses the API layer for all generation to ensure proper
    lyrics context, validation, and audit loop.
    
    Args:
        progress_callback: Function to call with progress (0.0 to 1.0)
        status_callback: Function to call with status messages
        
    Returns:
        Dict with results: {"success_count": int, "failed_count": int, "errors": List[str]}
    """
    if not REGEN_QUEUE_FILE.exists():
        return {"success_count": 0, "failed_count": 0, "errors": []}
    
    try:
        queue = json.loads(REGEN_QUEUE_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        return {"success_count": 0, "failed_count": 0, "errors": [f"Failed to read queue: {str(e)}"]}
    
    if not queue:
        return {"success_count": 0, "failed_count": 0, "errors": []}
    
    results = {
        "success_count": 0,
        "failed_count": 0,
        "errors": []
    }
    
    total_items = len(queue)
    
    for idx, queue_item in enumerate(queue):
        item_progress = idx / total_items
        if progress_callback:
            progress_callback(item_progress)
        
        item_id = queue_item.get("item_id", "Unknown")
        regen_type = queue_item.get("regenerate_type", "both")
        
        if status_callback:
            status_callback(f"Processing {idx + 1}/{total_items}: {item_id} ({regen_type})")
        
        try:
            # Extract information from queue item
            content_type = queue_item["content_type"]
            dj_name = queue_item["dj"]
            feedback = queue_item.get("feedback", "")
            
            logger.info(f"📋 Processing queue item via API: {item_id} ({content_type}/{dj_name}/{regen_type})")
            
            # Use the GUI backend to regenerate through the API layer
            success, error_msg = gui_backend.regenerate_content(
                content_type_str=content_type,
                dj_str=dj_name,
                item_id=item_id,
                regen_type=regen_type,
                feedback=feedback,
            )
            
            if success:
                results["success_count"] += 1
                logger.info(f"✅ Successfully regenerated via API: {item_id}")
            else:
                results["failed_count"] += 1
                results["errors"].append(f"{item_id}: {error_msg or 'Generation failed'}")
                logger.error(f"❌ Failed to regenerate: {item_id}: {error_msg}")
                
        except Exception as e:
            results["failed_count"] += 1
            error_msg = f"{item_id}: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(f"❌ Exception during regeneration: {error_msg}")
            if status_callback:
                status_callback(f"ERROR: {error_msg}")
    
    # Final progress
    if progress_callback:
        progress_callback(1.0)
    
    if status_callback:
        status_callback(f"Complete! {results['success_count']} succeeded, {results['failed_count']} failed")
    
    # Clear queue after processing
    clear_regen_queue()
    
    return results


def _get_next_version_for_regen(folder_path: Path, dj: str, content_type: str) -> int:
    """Get next version number for regeneration."""
    if content_type == "outros":
        existing_files = list(folder_path.glob(f"{dj}_outro*.txt")) + list(folder_path.glob(f"{dj}_outro*.wav"))
    else:
        existing_files = list(folder_path.glob(f"{dj}_*.txt")) + list(folder_path.glob(f"{dj}_*.wav"))
    
    if not existing_files:
        return 0
    
    # Extract version numbers
    versions = []
    for f in existing_files:
        if content_type == "outros":
            if f.stem == f"{dj}_outro":
                versions.append(0)
            else:
                match = re.search(r'_outro_(\d+)', f.stem)
                if match:
                    versions.append(int(match.group(1)))
        else:
            match = re.search(rf'{dj}_(\d+)', f.stem)
            if match:
                versions.append(int(match.group(1)))
    
    return max(versions) + 1 if versions else 0


def _parse_song_info(item_id: str) -> tuple:
    """Parse artist and song from item_id like 'Artist-Song'."""
    parts = item_id.split('-', 1)
    if len(parts) == 2:
        return parts[0].strip().replace('_', ' '), parts[1].strip().replace('_', ' ')
    return None, None


def _parse_time_info(item_id: str) -> tuple:
    """Parse hour and minute from item_id like '12-00'."""
    parts = item_id.split('-')
    if len(parts) >= 2:
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return None, None


def _generate_intro(pipeline, dj, artist: str, title: str, regen_type: str, feedback: str, lyrics_context: str = None) -> tuple:
    """Generate intro with specified parameters. Returns (success, error_message).
    
    If lyrics_context is provided, it will be passed to the pipeline for thematic bridging.
    Supports both GenerationPipeline (basic) and ValidatedGenerationPipeline (with validation).
    """
    from src.ai_radio.generation.validated_pipeline import ValidatedGenerationPipeline
    
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        # Create a song_id from artist-title
        song_id = f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}"
        # Convert DJ enum to string if needed
        dj_str = dj.value if hasattr(dj, 'value') else str(dj)
        logger.info(f"🎙️ Generating intro: {artist} - {title} (DJ: {dj_str}, type: {regen_type})")
        
        # Check if using ValidatedGenerationPipeline (different API)
        if isinstance(pipeline, ValidatedGenerationPipeline):
            # ValidatedGenerationPipeline only does script generation with validation
            # It has its own lyrics loading and validation stages
            logger.info(f"🔍 Using ValidatedGenerationPipeline with rule + LLM validation")
            result = pipeline.generate_song_intro(
                song_id=song_id,
                artist=artist,
                title=title,
                dj=dj_str,
            )
            if result.success:
                logger.info(f"✅ Intro generated and validated: {artist} - {title} (attempts: {result.attempts})")
                return True, None
            else:
                # ValidatedGenerationPipeline returns errors as a list
                error_msg = "; ".join(result.errors) if result.errors else "Validation failed"
                logger.error(f"❌ Intro validation failed: {artist} - {title}: {error_msg}")
                return False, error_msg
        else:
            # Basic GenerationPipeline
            # Load lyrics if not provided and not audio-only
            if lyrics_context is None and not audio_only:
                lyrics_file = find_lyrics_file(f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}")
                if lyrics_file:
                    lyrics_context = load_lyrics(lyrics_file)
                    logger.info(f"📜 Loaded lyrics for thematic bridging: {lyrics_file.name}")
            
            result = pipeline.generate_song_intro(
                song_id=song_id,
                artist=artist,
                title=title,
                dj=dj_str,
                text_only=text_only,
                audio_only=audio_only,
                lyrics_context=lyrics_context,
                audit_feedback=feedback if feedback else None
            )
            if result.success:
                logger.info(f"✅ Intro generated successfully: {artist} - {title}")
                return True, None
            else:
                logger.error(f"❌ Intro generation failed: {artist} - {title}: {result.error}")
                return False, result.error
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Intro generation failed: {artist} - {title}: {error_msg}")
        return False, error_msg


def _generate_outro(pipeline, dj, artist: str, title: str, regen_type: str, feedback: str, lyrics_context: str = None) -> tuple:
    """Generate outro with specified parameters. Returns (success, error_message).
    
    If lyrics_context is provided, it will be passed to the pipeline for thematic bridging.
    Supports both GenerationPipeline (basic) and ValidatedGenerationPipeline (with validation).
    """
    from src.ai_radio.generation.validated_pipeline import ValidatedGenerationPipeline
    
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        # Create a song_id from artist-title
        song_id = f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}"
        # Convert DJ enum to string if needed
        dj_str = dj.value if hasattr(dj, 'value') else str(dj)
        logger.info(f"🎙️ Generating outro: {artist} - {title} (DJ: {dj_str}, type: {regen_type})")
        
        # Check if using ValidatedGenerationPipeline (different API)
        if isinstance(pipeline, ValidatedGenerationPipeline):
            # ValidatedGenerationPipeline only does script generation with validation
            logger.info(f"🔍 Using ValidatedGenerationPipeline with rule + LLM validation")
            result = pipeline.generate_song_outro(
                song_id=song_id,
                artist=artist,
                title=title,
                dj=dj_str,
            )
            if result.success:
                logger.info(f"✅ Outro generated and validated: {artist} - {title} (attempts: {result.attempts})")
                return True, None
            else:
                # ValidatedGenerationPipeline returns errors as a list
                error_msg = "; ".join(result.errors) if result.errors else "Validation failed"
                logger.error(f"❌ Outro validation failed: {artist} - {title}: {error_msg}")
                return False, error_msg
        else:
            # Basic GenerationPipeline
            # Load lyrics if not provided and not audio-only
            if lyrics_context is None and not audio_only:
                lyrics_file = find_lyrics_file(f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}")
                if lyrics_file:
                    lyrics_context = load_lyrics(lyrics_file)
                    logger.info(f"📜 Loaded lyrics for thematic bridging: {lyrics_file.name}")
            
            result = pipeline.generate_song_outro(
                song_id=song_id,
                artist=artist,
                title=title,
                dj=dj_str,
                text_only=text_only,
                audio_only=audio_only,
                lyrics_context=lyrics_context,
                audit_feedback=feedback if feedback else None
            )
            if result.success:
                logger.info(f"✅ Outro generated successfully: {artist} - {title}")
                return True, None
            else:
                logger.error(f"❌ Outro generation failed: {artist} - {title}: {result.error}")
                return False, result.error
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Outro generation failed: {artist} - {title}: {error_msg}")
        return False, error_msg


def _generate_time(pipeline, dj, hour: int, minute: int, regen_type: str, feedback: str) -> tuple:
    """Generate time announcement with specified parameters. Returns (success, error_message)."""
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        logger.info(f"🕐 Generating time: {hour}:{minute:02d} (DJ: {dj}, type: {regen_type})")
        pipeline.generate_time_announcement(
            hour=hour,
            minute=minute,
            dj=dj,
            prompt_version="v2",
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=feedback if feedback else None
        )
        logger.info(f"✅ Time generated successfully: {hour}:{minute:02d}")
        return True, None
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Time generation failed: {hour}:{minute:02d}: {error_msg}")
        return False, error_msg


def _generate_weather(pipeline, dj, hour: int, minute: int, regen_type: str, feedback: str) -> tuple:
    """Generate weather announcement with specified parameters. Returns (success, error_message)."""
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        logger.info(f"🌤️ Generating weather: {hour}:{minute:02d} (DJ: {dj}, type: {regen_type})")
        pipeline.generate_weather_announcement(
            hour=hour,
            minute=minute,
            dj=dj,
            prompt_version="v2",
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=feedback if feedback else None
        )
        logger.info(f"✅ Weather generated successfully: {hour}:{minute:02d}")
        return True, None
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Weather generation failed: {hour}:{minute:02d}: {error_msg}")
        return False, error_msg


def export_reviews_to_csv(items: List[ReviewItem]) -> pd.DataFrame:
    """Export review data to CSV format."""
    rows = []
    for item in items:
        review_status = load_review_status(item.folder_path)
        rows.append({
            "content_type": item.content_type,
            "dj": item.dj,
            "item_id": item.item_id,
            "latest_version": item.latest_version,
            "audit_status": item.audit_status or "unknown",
            "review_status": review_status.get("status", "pending"),
            "reviewed_at": review_status.get("reviewed_at", ""),
            "script_issues": ", ".join(review_status.get("script_issues", [])),
            "audio_issues": ", ".join(review_status.get("audio_issues", [])),
            "reviewer_notes": review_status.get("reviewer_notes", "")
        })
    return pd.DataFrame(rows)


def render_audio_player(audio_path: Path, key_suffix: str = ""):
    """Render HTML5 audio player for a wav file with mobile-friendly styling."""
    if audio_path and audio_path.exists():
        audio_bytes = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        # Mobile-optimized audio player - no background wrapper to respect theme
        audio_html = f"""
        <audio controls style="width: 100%; min-height: 54px; border-radius: 12px; margin: 8px 0;">
            <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.warning("🔇 Audio file not found")


def render_review_item(item: ReviewItem, index: int):
    """Render a single review item with mobile-first design."""
    review_status = load_review_status(item.folder_path)
    
    # Use Streamlit container instead of custom div for theme compatibility
    with st.container():
        st.markdown("---")
        
        # === MOBILE-FRIENDLY HEADER ===
        # Title and status on first row
        if item.content_type in ["intros", "outros"]:
            title, artist = format_song_title(item.item_id)
            st.markdown(f"### 🎵 {title}")
            st.caption(f"by {artist}" if artist else "")
        else:
            st.markdown(f"### {item.item_id.replace('_', ' ')}")
    
    # Status badges - compact inline display
    status_html = f"""
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
        <span class="status-pill status-{review_status['status']}">{review_status['status'].upper()}</span>
        <span class="status-pill" style="background: rgba(128,128,128,0.15); color: inherit;">
            {item.content_type} • {item.dj.replace('_', ' ').title()}
        </span>
    """
    if item.audit_status:
        status_html += f'<span class="status-pill status-{item.audit_status}">Audit: {item.audit_status}</span>'
    status_html += "</div>"
    st.markdown(status_html, unsafe_allow_html=True)
    
    # Check if manually rewritten
    is_rewritten = review_status.get("manually_rewritten", False)
    if is_rewritten:
        edit_count = review_status.get("edit_count", 1)
        st.info(f"✏️ Manually edited" + (f" ({edit_count}x)" if edit_count > 1 else "") + " - Review still required")
    
    # === AUDIO FIRST (Most important for review) ===
    st.markdown("#### 🔊 Audio Preview")
    
    # Version navigation with < > buttons
    if item.latest_version > 0:
        # Initialize version in session state if needed
        version_key = f"version_{item.dj}_{item.item_id}_{index}"
        if version_key not in st.session_state:
            st.session_state[version_key] = item.latest_version
        
        version = st.session_state[version_key]
        
        # Navigation row: < version N of M >
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("◀️", key=f"prev_ver_{index}", disabled=(version == 0), use_container_width=True):
                st.session_state[version_key] = version - 1
                st.rerun()
        with nav_col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; background: rgba(128,128,128,0.1); border-radius: 8px;">
                <strong>Version {version + 1}</strong> of {item.latest_version + 1}
            </div>
            """, unsafe_allow_html=True)
        with nav_col3:
            if st.button("▶️", key=f"next_ver_{index}", disabled=(version >= item.latest_version), use_container_width=True):
                st.session_state[version_key] = version + 1
                st.rerun()
    else:
        version = 0  # Only one version exists, no navigation needed
    
    # Check for dual audio
    if item.has_dual_audio(version):
        audio_tab1, audio_tab2 = st.tabs(["📻 30sec", "📻 Full"])
        with audio_tab1:
            render_audio_player(item.get_audio_path(version, ref_type='30sec'), f"30sec_{index}")
        with audio_tab2:
            render_audio_player(item.get_audio_path(version, ref_type='full'), f"full_{index}")
    else:
        audio_path = item.get_audio_path(version)
        render_audio_player(audio_path, f"main_{index}")
    
    # === SCRIPT SECTION (Collapsible for mobile) ===
    with st.expander("📝 Script", expanded=True):
        script_path = item.get_script_path(version)
        current_script = ""
        
        if script_path and script_path.exists():
            if f"{item.dj}_" in script_path.name or f"{item.dj}_outro" in script_path.name:
                current_script = script_path.read_text(encoding='utf-8')
            else:
                st.error(f"⚠️ Script file mismatch!")
                current_script = f"ERROR: File mismatch"
        
        if current_script:
            # Track original value for auto-save detection
            script_key = f"script_{item.dj}_{item.item_id}_{version}_{index}"
            
            edited_script = st.text_area(
                "Edit script",
                value=current_script,
                height=200,
                key=script_key,
                label_visibility="collapsed",
                help="Edits are auto-saved when you click outside this box"
            )
            
            # Auto-save: Check if value changed from what's on disk
            if edited_script != current_script:
                # Auto-save the changes immediately
                if save_manual_script(item, edited_script, version):
                    st.toast("✅ Auto-saved!", icon="💾")
                    st.rerun()
        else:
            st.warning("No script file found")
    
    # === ORIGINAL SCRIPT COMPARISON (Collapsible - like lyrics) ===
    with st.expander("🔄 Compare with Original/Previous Versions", expanded=False):
        # Get backup file (original before any edits)
        # The backup is stored as script_name.txt.original (not .original replacing .txt)
        script_path = item.get_script_path(version)
        has_original_backup = False
        original_script = ""
        
        if script_path and script_path.exists():
            # Try both naming conventions for backup
            backup_path = Path(str(script_path) + '.original')  # e.g., julie_0.txt.original
            if not backup_path.exists():
                backup_path = script_path.with_suffix('.original')  # e.g., julie_0.original
            
            if backup_path.exists():
                has_original_backup = True
                original_script = backup_path.read_text(encoding='utf-8')
        
        if has_original_backup:
            st.markdown("**📄 Original (before any manual edits):**")
            st.text_area(
                "Original script",
                value=original_script,
                height=150,
                disabled=True,
                key=f"orig_{index}_{version}",
                label_visibility="collapsed"
            )
            
            # Show edit stats
            edit_count = review_status.get("edit_count", 0)
            if edit_count > 0:
                first_edit = review_status.get("original_backup_at", "")
                last_edit = review_status.get("rewritten_at", "")
                st.caption(f"📝 Edited {edit_count} time(s)")
                if first_edit:
                    st.caption(f"First edit: {first_edit[:19]}")
                if last_edit and last_edit != first_edit:
                    st.caption(f"Last edit: {last_edit[:19]}")
        elif is_rewritten:
            # Edited but no backup exists (legacy edits before backup feature)
            st.warning("⚠️ This script was edited before the backup feature was added. Original content is not available.")
            st.caption("Future edits will create a backup of the current version.")
        
        st.markdown("---")
        
        # Version comparison with selector - now with color-coded diff
        st.markdown("**📚 Compare with other versions (color-coded diff):**")
        
        # Build list of available versions to compare
        available_versions = []
        for v in range(item.latest_version + 1):
            v_path = item.get_script_path(v)
            if v_path and v_path.exists():
                label = f"Version {v}"
                if v == version:
                    label += " (current)"
                if v == item.latest_version:
                    label += " (latest)"
                available_versions.append((v, label))
        
        if len(available_versions) > 1:
            # Filter out current version for comparison
            compare_options = [(v, label) for v, label in available_versions if v != version]
            
            if compare_options:
                compare_version = st.selectbox(
                    "Select version to compare:",
                    options=[v for v, _ in compare_options],
                    format_func=lambda x: next(label for v, label in compare_options if v == x),
                    key=f"compare_select_{index}"
                )
                
                compare_path = item.get_script_path(compare_version)
                if compare_path and compare_path.exists():
                    compare_script = compare_path.read_text(encoding='utf-8')
                    
                    # Show diff rendering toggle
                    diff_mode = st.radio(
                        "View mode:",
                        ["Side-by-side text", "Color diff (inline)", "Color diff (table)"],
                        horizontal=True,
                        key=f"diff_mode_{index}",
                        label_visibility="collapsed"
                    )
                    
                    if diff_mode == "Side-by-side text":
                        # Original plain text comparison
                        col_old, col_new = st.columns(2)
                        with col_old:
                            st.caption(f"Version {compare_version}")
                            st.text_area(
                                f"Version {compare_version}",
                                value=compare_script,
                                height=150,
                                disabled=True,
                                key=f"compare_{index}_{compare_version}",
                                label_visibility="collapsed"
                            )
                        with col_new:
                            st.caption(f"Version {version} (current)")
                            st.text_area(
                                f"Version {version}",
                                value=current_script,
                                height=150,
                                disabled=True,
                                key=f"current_{index}_{version}_cmp",
                                label_visibility="collapsed"
                            )
                    elif diff_mode == "Color diff (inline)":
                        # Use inline diff rendering (mobile-friendly)
                        diff_html = render_inline_diff(compare_script, current_script)
                        st.markdown(diff_html, unsafe_allow_html=True)
                    else:
                        # Use table diff rendering
                        diff_html = render_diff(compare_script, current_script)
                        st.markdown(f'<div style="overflow-x: auto; font-size: 0.85rem;">{diff_html}</div>', unsafe_allow_html=True)
        else:
            st.caption("No other versions available for comparison")
    
    # === REFERENCE MATERIALS (Collapsed by default on mobile) ===
    if item.content_type in ["intros", "outros"]:
        with st.expander("📜 Song Lyrics", expanded=False):
            lyrics_file = find_lyrics_file(item.item_id)
            if lyrics_file:
                lyrics = load_lyrics(lyrics_file)
                st.text_area("Lyrics", value=lyrics, height=150, disabled=True, 
                           key=f"lyrics_{index}_{version}", label_visibility="collapsed")
            else:
                st.info("No lyrics file found")
    
    # === QUICK ACTIONS (Prominent for mobile) ===
    st.markdown("#### ⚡ Quick Actions")
    
    # Regeneration buttons in a responsive grid
    regen_cols = st.columns(3)
    with regen_cols[0]:
        if st.button("📝 Regen Script", key=f"regen_s_{index}", use_container_width=True):
            add_to_regen_queue(item, "script", "Quick regen from review")
            st.toast("Added to queue!", icon="✅")
            st.rerun()
    with regen_cols[1]:
        if st.button("🔊 Regen Audio", key=f"regen_a_{index}", use_container_width=True):
            add_to_regen_queue(item, "audio", "Quick regen from review")
            st.toast("Added to queue!", icon="✅")
            st.rerun()
    with regen_cols[2]:
        if st.button("🔄 Regen Both", key=f"regen_b_{index}", use_container_width=True):
            add_to_regen_queue(item, "both", "Quick regen from review")
            st.toast("Added to queue!", icon="✅")
            st.rerun()
    
    # === REGENERATE AUDIO FROM CURRENT SCRIPT (for manual edits) ===
    # Check if script was manually edited
    if review_status.get("manually_rewritten", False):
        st.markdown("---")
        st.markdown("**🔊 Regenerate Audio from Edited Script**")
        st.caption("Generate new audio using the current (edited) script text, without validation.")
        
        if st.button(
            "🎤 Generate Audio from Current Script",
            key=f"audio_from_edit_{index}",
            use_container_width=True,
            type="primary"
        ):
            # Add to queue with audio-only regeneration
            add_to_regen_queue(item, "audio", "Audio from manual edit - no script validation")
            st.toast("Added to queue! Audio will be generated from current script.", icon="🎤")
            st.rerun()
    
    # === REVIEW DECISION (Most important - always visible) ===
    st.markdown("---")
    st.markdown("#### 📋 Review Decision")
    
    # Issue selection - using tabs for mobile-friendly organization
    issue_tab1, issue_tab2 = st.tabs(["Script Issues", "Audio Issues"])
    
    with issue_tab1:
        script_issue_options = SCRIPT_ISSUES.get(item.content_type, [])
        selected_script_issues = st.multiselect(
            "Select script issues",
            script_issue_options,
            default=review_status.get("script_issues", []),
            key=f"script_issues_{index}",
            label_visibility="collapsed"
        )
    
    with issue_tab2:
        selected_audio_issues = st.multiselect(
            "Select audio issues",
            AUDIO_ISSUES,
            default=review_status.get("audio_issues", []),
            key=f"audio_issues_{index}",
            label_visibility="collapsed"
        )
    
    # Notes field
    reviewer_notes = st.text_area(
        "Notes (optional)",
        value=review_status.get("reviewer_notes", ""),
        key=f"notes_{index}",
        height=60,
        placeholder="Add any notes here..."
    )
    
    # === APPROVE/REJECT BUTTONS (Large, prominent, mobile-friendly) ===
    st.markdown("---")
    approve_col, reject_col = st.columns(2)
    
    with approve_col:
        if st.button("✅ APPROVE", key=f"approve_{index}", use_container_width=True, type="primary"):
            new_status = {
                "status": "approved",
                "reviewed_at": datetime.now().isoformat(),
                "reviewer_notes": reviewer_notes,
                "script_issues": selected_script_issues,
                "audio_issues": selected_audio_issues
            }
            # Preserve manual rewrite info
            if is_rewritten:
                new_status["manually_rewritten"] = True
                new_status["rewritten_version"] = review_status.get("rewritten_version")
                new_status["edit_count"] = review_status.get("edit_count", 1)
            save_review_status(item.folder_path, new_status)
            st.success("✅ Approved!")
            st.rerun()
    
    with reject_col:
        if st.button("❌ REJECT", key=f"reject_{index}", use_container_width=True):
            new_status = {
                "status": "rejected",
                "reviewed_at": datetime.now().isoformat(),
                "reviewer_notes": reviewer_notes,
                "script_issues": selected_script_issues,
                "audio_issues": selected_audio_issues
            }
            if is_rewritten:
                new_status["manually_rewritten"] = True
                new_status["rewritten_version"] = review_status.get("rewritten_version")
                new_status["edit_count"] = review_status.get("edit_count", 1)
            save_review_status(item.folder_path, new_status)
            st.error("❌ Rejected")
            st.rerun()


def find_lyrics_file(song_id: str) -> Optional[Path]:
    """Find lyrics file for a given song ID."""
    if not LYRICS_DIR.exists():
        return None
    
    # Parse song_id format: "Artist-Title" or "Artist_Name-Song_Title"
    # Lyrics files format: "Title by Artist.txt"
    parts = song_id.split('-', 1)
    if len(parts) < 2:
        return None
    
    # Folder naming: single underscore = space, double underscore = quote
    # But apostrophes in lyrics files (like I'm) become underscore in folder (I_m)
    # So we need smart matching
    
    def folder_to_display(text: str) -> str:
        """Convert folder name to display format."""
        # Double underscore = quote character
        text = text.replace('__', '"')
        # Single underscore = space (but also catches apostrophe cases)
        text = text.replace('_', ' ')
        return text
    
    def normalize_for_matching(text: str) -> str:
        """Normalize text for fuzzy matching."""
        # Remove all quotes and apostrophes
        text = text.replace('"', '').replace('"', '').replace('"', '')
        text = text.replace("'", '').replace("'", '').replace("'", '')
        # Remove other special chars except spaces
        text = re.sub(r'[^a-z0-9\s]', '', text.lower())
        # Remove all spaces for matching (handles "I m" vs "Im" issue)
        text = text.replace(' ', '')
        return text
    
    artist_part = folder_to_display(parts[0])
    title_part = folder_to_display(parts[1])
    
    # Try exact match first
    expected_filename = f"{title_part} by {artist_part}.txt"
    lyrics_path = LYRICS_DIR / expected_filename
    if lyrics_path.exists():
        return lyrics_path
    
    # Try normalized matching (removes all spaces, quotes, apostrophes)
    expected_normalized = normalize_for_matching(f"{title_part} by {artist_part}")
    for lyrics_file in LYRICS_DIR.glob("*.txt"):
        if normalize_for_matching(lyrics_file.stem) == expected_normalized:
            return lyrics_file
    
    return None


def format_song_title(item_id: str) -> tuple[str, str]:
    """Convert folder name format to readable song title and artist.
    
    Args:
        item_id: Folder name like "Artist__Nickname__Name-Song_Title"
    
    Returns:
        Tuple of (title, artist) for display
    """
    # Split on first dash to get artist and title
    parts = item_id.split('-', 1)
    if len(parts) < 2:
        # Not a song, return as-is with underscores replaced
        return (item_id.replace('_', ' '), "")
    
    def folder_to_display(text: str) -> str:
        """Convert folder name to display format.
        
        Folder naming convention:
        - Triple underscore (___) = ampersand for "Artist & Artist"
        - Name__Nickname__Surname = quoted nickname like Arthur "Big Boy" Crudup
        - Double underscore (__) between phrases = space separator
        - _m, _s, _t, _ll, _re, _ve, _d = apostrophe contractions
        - Other single underscores = space
        """
        # Triple underscore = ampersand (for "Artist & Artist")
        text = text.replace('___', ' & ')
        
        # Detect nickname pattern: Name__Nickname__Surname
        # E.g., Arthur__Big_Boy__Crudup -> Arthur "Big Boy" Crudup
        text = re.sub(r'([A-Z][a-z]+)__([A-Z][a-z]+(?:_[A-Z][a-z]+)?)__([A-Z][a-z]+)', 
                      lambda m: m.group(1) + ' "' + m.group(2).replace('_', ' ') + '" ' + m.group(3), 
                      text)
        
        # Handle common apostrophe patterns: _m -> 'm, _s -> 's, _t -> 't, etc.
        text = re.sub(r"_([mstMST])(?=_|$)", r"'\1", text)
        text = re.sub(r"_(ll|re|ve|d)(?=_|$)", r"'\1", text)
        
        # Double underscore that remains = just a space (phrase separator)
        text = text.replace('__', ' ')
        
        # Remaining single underscores are spaces
        text = text.replace('_', ' ')
        
        # Clean up any double spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    artist_part = folder_to_display(parts[0])
    title_part = folder_to_display(parts[1])
    
    # Return as tuple (title, artist)
    return (title_part, artist_part)


def get_available_songs() -> List[Dict[str, str]]:
    """Get list of available songs from lyrics directory."""
    songs = []
    if not LYRICS_DIR.exists():
        return songs
    
    for lyrics_file in LYRICS_DIR.glob("*.txt"):
        # Parse filename: "Title by Artist.txt"
        filename = lyrics_file.stem
        match = re.match(r"(.+?)\s+by\s+(.+)", filename)
        if match:
            title, artist = match.groups()
            # Create ID matching generated content naming
            song_id = f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}"
            songs.append({
                "id": song_id,
                "title": title,
                "artist": artist,
                "lyrics_file": lyrics_file
            })
    
    return sorted(songs, key=lambda x: f"{x['artist']} - {x['title']}")


def load_lyrics(lyrics_file: Path) -> str:
    """Load lyrics from file."""
    try:
        return lyrics_file.read_text(encoding='utf-8')
    except Exception as e:
        return f"Error loading lyrics: {e}"


def get_song_content(song_id: str) -> Dict[str, List[ReviewItem]]:
    """Get all intros and outros for a specific song."""
    content = {"intros": [], "outros": []}
    
    for content_type in ["intros", "outros"]:
        for dj in DJS:
            # Check both legacy doubled path and new single path
            possible_folders = [
                GENERATED_DIR / content_type / content_type / dj / song_id,  # Legacy doubled path
                GENERATED_DIR / content_type / dj / song_id,                  # New single path
            ]
            
            for folder in possible_folders:
                if not folder.exists():
                    continue
                    
                # Scan for versions
                script_versions = []
                audio_versions = []
                audio_30sec = {}
                audio_full = {}
                
                if content_type == "outros":
                    # Outros use different naming: dj_outro.txt, dj_outro_1.txt, etc.
                    base_script = folder / f"{dj}_outro.txt"
                    base_audio = folder / f"{dj}_outro.wav"
                    base_audio_full = folder / f"{dj}_outro_full.wav"
                    base_audio_30sec = folder / f"{dj}_outro_30sec.wav"
                    if base_script.exists():
                        script_versions.append(base_script)
                    if base_audio.exists():
                        audio_versions.append(base_audio)
                    if base_audio_full.exists():
                        audio_full[0] = base_audio_full
                    if base_audio_30sec.exists():
                        audio_30sec[0] = base_audio_30sec
                    
                    # Check for numbered versions
                    for i in range(1, 100):
                        script = folder / f"{dj}_outro_{i}.txt"
                        audio = folder / f"{dj}_outro_{i}.wav"
                        audio_f = folder / f"{dj}_outro_{i}_full.wav"
                        audio_30 = folder / f"{dj}_outro_{i}_30sec.wav"
                        if script.exists():
                            script_versions.append(script)
                        if audio.exists():
                            audio_versions.append(audio)
                        if audio_f.exists():
                            audio_full[i] = audio_f
                        if audio_30.exists():
                            audio_30sec[i] = audio_30
                        if not script.exists() and not audio.exists() and not audio_f.exists() and not audio_30.exists():
                            break
                else:
                    # Standard naming: dj_0.txt, dj_1.txt, dj_0_full.wav, dj_0_30sec.wav, etc.
                    for i in range(100):
                        script = folder / f"{dj}_{i}.txt"
                        audio = folder / f"{dj}_{i}.wav"
                        audio_f = folder / f"{dj}_{i}_full.wav"
                        audio_30 = folder / f"{dj}_{i}_30sec.wav"
                        if script.exists():
                            script_versions.append(script)
                        if audio.exists():
                            audio_versions.append(audio)
                            # Store legacy audio in audio_full for backwards compatibility
                            if i not in audio_full:
                                audio_full[i] = audio
                        if audio_f.exists():
                            audio_full[i] = audio_f
                        if audio_30.exists():
                            audio_30sec[i] = audio_30
                        if not script.exists() and not audio.exists() and not audio_f.exists() and not audio_30.exists():
                            break
                
                if script_versions or audio_versions or audio_full or audio_30sec:
                    latest = max(
                        len(script_versions) - 1 if script_versions else 0,
                        len(audio_versions) - 1 if audio_versions else 0,
                        max(audio_full.keys()) if audio_full else 0,
                        max(audio_30sec.keys()) if audio_30sec else 0
                    )
                    review_status_data = load_review_status(folder)
                    audit_status = get_audit_status(content_type, dj, song_id)
                    
                    item = ReviewItem(
                        content_type=content_type,
                        dj=dj,
                        item_id=song_id,
                        folder_path=folder,
                        script_versions=script_versions,
                        audio_versions=audio_versions,
                        latest_version=latest,
                        audit_status=audit_status,
                        review_status=review_status_data.get("status", "pending"),
                        audio_30sec=audio_30sec,
                        audio_full=audio_full
                    )
                    content[content_type].append(item)
                    break  # Found content in this path, don't check the other
    
    return content


def save_manual_script(item: ReviewItem, new_script: str, version: int) -> bool:
    """Save manually edited script as a NEW version (preserves history).
    
    According to issue requirements: manual edits should create NEW versions,
    never overwrite existing versions. This preserves full version history.
    
    Args:
        item: ReviewItem being edited
        new_script: The new script text
        version: The version being edited (used for reference, not modified)
        
    Returns:
        True if save succeeded
    """
    try:
        # Use the version manager to create a new version
        success, version_info = gui_backend.save_manual_edit(
            folder_path=item.folder_path,
            dj_str=item.dj,
            content_type=item.content_type,
            new_script=new_script,
            notes=f"Manual edit from Review GUI (based on v{version})",
        )
        
        if not success:
            st.error("Failed to create new version")
            return False
        
        # Update review status
        review_status = load_review_status(item.folder_path)
        
        # Mark as manually rewritten
        review_status["manually_rewritten"] = True
        review_status["rewritten_version"] = version_info.version if version_info else version + 1
        review_status["rewritten_at"] = datetime.now().isoformat()
        
        # Track edit count
        edit_count = review_status.get("edit_count", 0) + 1
        review_status["edit_count"] = edit_count
        
        # IMPORTANT: Reset status to pending - manual edits require re-review
        review_status["status"] = "pending"
        
        save_review_status(item.folder_path, review_status)
        
        logger.info(f"Created new version {version_info.version if version_info else 'unknown'} for {item.item_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving script: {e}")
        st.error(f"Error saving script: {e}")
        return False


def render_song_editor_page():
    """Render the song-specific editor page."""
    st.title("Song Editor")
    st.markdown("View and edit all content for a specific song")
    
    # Get available songs
    songs = get_available_songs()
    
    if not songs:
        st.warning("No songs found in music_with_lyrics directory")
        return
    
    # Song selector
    song_options = [f"{s['artist']} - {s['title']}" for s in songs]
    
    # Initialize song selection in session state
    if 'selected_song_idx' not in st.session_state:
        st.session_state.selected_song_idx = 0
    
    selected_idx = st.selectbox(
        "Select Song",
        range(len(song_options)),
        format_func=lambda x: song_options[x],
        index=st.session_state.selected_song_idx,
        key="song_selector"
    )
    st.session_state.selected_song_idx = selected_idx
    
    selected_song = songs[selected_idx]
    
    # Display song info
    st.subheader(f"{selected_song['title']}")
    st.markdown(f"**Artist:** {selected_song['artist']}")
    st.markdown(f"**Song ID:** `{selected_song['id']}`")
    
    # Load and display lyrics
    with st.expander("Song Lyrics", expanded=False):
        lyrics = load_lyrics(selected_song['lyrics_file'])
        st.text_area(
            "Lyrics",
            value=lyrics,
            height=300,
            disabled=True,
            key=f"lyrics_{selected_song['id']}"
        )
    
    st.markdown("---")
    
    # Get all content for this song
    song_content = get_song_content(selected_song['id'])
    
    # Display intros
    st.header("Intros")
    if song_content['intros']:
        for item in song_content['intros']:
            render_song_content_editor(item, selected_song, "intro")
    else:
        st.info("No intros generated for this song yet")
    
    st.markdown("---")
    
    # Display outros
    st.header("Outros")
    if song_content['outros']:
        for item in song_content['outros']:
            render_song_content_editor(item, selected_song, "outro")
    else:
        st.info("No outros generated for this song yet")


def render_song_content_editor(item: ReviewItem, song_info: Dict, content_label: str):
    """Render an editable content item in the song editor - mobile optimized."""
    with st.container():
        # Compact header for mobile
        st.markdown(f"### 🎙️ {item.dj.replace('_', ' ').title()} - {content_label.title()}")
        
        # Status badges inline
        status_html = '<div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">'
        if item.audit_status:
            status_html += f'<span class="status-pill status-{item.audit_status}">{item.audit_status}</span>'
        status_html += f'<span class="status-pill status-{item.review_status}">{item.review_status}</span>'
        status_html += '</div>'
        st.markdown(status_html, unsafe_allow_html=True)
        
        # Check if manually rewritten
        review_status = load_review_status(item.folder_path)
        is_rewritten = review_status.get("manually_rewritten", False)
        
        if is_rewritten:
            st.success(f"✏️ Manually edited (v{review_status.get('rewritten_version', '?')})")
        
        # Version selector
        version_options = list(range(len(item.script_versions)))
        if version_options:
            selected_version = st.selectbox(
                "Version",
                version_options,
                index=min(item.latest_version, len(version_options) - 1),
                key=f"ver_{item.dj}_{item.content_type}_{item.item_id}"
            )
        else:
            st.warning("No versions available")
            return
        
        # Get script content
        script_path = item.get_script_path(selected_version)
        current_script = None
        if script_path and script_path.exists():
            current_script = script_path.read_text(encoding='utf-8')
        
        # === AUDIO FIRST (most important) ===
        st.markdown("#### 🔊 Audio")
        if item.has_dual_audio(selected_version):
            audio_tab1, audio_tab2 = st.tabs(["30sec", "Full"])
            with audio_tab1:
                audio_30sec_path = item.get_audio_path(selected_version, ref_type='30sec')
                if audio_30sec_path and audio_30sec_path.exists():
                    st.audio(audio_30sec_path.read_bytes(), format="audio/wav")
            with audio_tab2:
                audio_full_path = item.get_audio_path(selected_version, ref_type='full')
                if audio_full_path and audio_full_path.exists():
                    st.audio(audio_full_path.read_bytes(), format="audio/wav")
        else:
            audio_path = item.get_audio_path(selected_version)
            if audio_path and audio_path.exists():
                st.audio(audio_path.read_bytes(), format="audio/wav")
            else:
                st.info("No audio file")
        
        # === SCRIPT EDITOR ===
        st.markdown("#### ✏️ Edit Script")
        if current_script is not None:
            edited_script = st.text_area(
                "Script",
                value=current_script,
                height=250,
                key=f"edit_{item.dj}_{item.content_type}_{selected_version}",
                label_visibility="collapsed"
            )
            
            # Action buttons
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if edited_script != current_script:
                    if st.button("💾 Save", key=f"save_{item.dj}_{item.content_type}_{selected_version}", 
                               use_container_width=True, type="primary"):
                        if save_manual_script(item, edited_script, selected_version):
                            st.success("✅ Saved!")
                            st.rerun()
                else:
                    st.caption("No changes")
            
            with action_col2:
                if st.button("🔊 Regen Audio", key=f"regen_{item.dj}_{item.content_type}_{selected_version}",
                           use_container_width=True):
                    add_to_regen_queue(item, "audio", "Regen from song editor")
                    st.toast("Added to queue!", icon="✅")
        else:
            st.warning(f"Script not found: {script_path}")
        
        # Reference materials (collapsed)
        with st.expander("📜 Reference", expanded=False):
            st.markdown("**Song Lyrics:**")
            lyrics = load_lyrics(song_info['lyrics_file'])
            st.text_area("Lyrics", value=lyrics, height=120, disabled=True,
                       key=f"lyr_{item.dj}_{item.content_type}_{selected_version}",
                       label_visibility="collapsed")
        
        st.markdown("---")


def init_session_state():
    """Initialize session state variables."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'items_per_page' not in st.session_state:
        st.session_state.items_per_page = 10
    if 'filter_content_type' not in st.session_state:
        st.session_state.filter_content_type = "All"
    if 'filter_dj' not in st.session_state:
        st.session_state.filter_dj = "All"
    if 'filter_audit_status' not in st.session_state:
        st.session_state.filter_audit_status = "All"
    if 'filter_review_status' not in st.session_state:
        st.session_state.filter_review_status = "All"
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    # Queue processing results (persisted across reruns)
    if 'queue_results' not in st.session_state:
        st.session_state.queue_results = None
    # Active tab
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Review"
    # Catalog filters
    if 'catalog_search' not in st.session_state:
        st.session_state.catalog_search = ""
    if 'catalog_dj' not in st.session_state:
        st.session_state.catalog_dj = "julie"


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Radio Review GUI",
        page_icon=":radio:",
        layout="wide",
        initial_sidebar_state="collapsed"  # Start collapsed on mobile
    )
    
    # Add comprehensive mobile-optimized CSS
    st.markdown("""
    <style>
    /* ========================================
       MOBILE-FIRST DESIGN SYSTEM
       Theme-aware (works in light AND dark mode)
       ======================================== */
    
    /* CSS Variables for consistent theming */
    :root {
        --touch-target-min: 48px;
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --border-radius: 12px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.15);
        --color-approve: #22c55e;
        --color-reject: #ef4444;
        --color-pending: #f59e0b;
        --color-primary: #3b82f6;
    }
    
    /* ========================================
       BASE MOBILE STYLES (applied first)
       ======================================== */
    
    /* Increase base font size for readability */
    .stApp {
        font-size: 16px;
    }
    
    /* Universal touch-friendly button styling */
    .stButton > button {
        min-height: var(--touch-target-min);
        padding: var(--spacing-md);
        font-size: 1rem;
        font-weight: 600;
        border-radius: var(--border-radius);
        margin: var(--spacing-xs) 0;
        box-shadow: var(--shadow-sm);
        transition: transform 0.1s, box-shadow 0.2s;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Text areas - larger and more readable */
    .stTextArea > div > div > textarea {
        font-size: 1rem;
        line-height: 1.6;
        padding: var(--spacing-md);
        border-radius: var(--border-radius);
        min-height: 150px;
    }
    
    /* Select boxes - larger touch targets */
    .stSelectbox > div > div {
        min-height: var(--touch-target-min);
    }
    
    .stSelectbox [data-baseweb="select"] {
        min-height: var(--touch-target-min);
    }
    
    /* Multiselect - easier to tap */
    .stMultiSelect [data-baseweb="tag"] {
        min-height: 36px;
        font-size: 0.9rem;
    }
    
    /* Audio player - full width and prominent */
    audio {
        width: 100%;
        min-height: 54px;
        border-radius: var(--border-radius);
    }
    
    /* Expander headers - larger touch target */
    .streamlit-expanderHeader {
        min-height: var(--touch-target-min);
        font-size: 1rem;
        font-weight: 600;
        padding: var(--spacing-md) !important;
    }
    
    /* ========================================
       MOBILE LAYOUT (< 768px)
       ======================================== */
    @media (max-width: 768px) {
        /* Hide sidebar toggle hint on mobile */
        [data-testid="collapsedControl"] {
            position: fixed;
            top: 0.5rem;
            left: 0.5rem;
            z-index: 1000;
        }
        
        /* Stack columns vertically */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* Reduce main padding */
        .main .block-container {
            padding: var(--spacing-sm) var(--spacing-md) 100px var(--spacing-md);
            max-width: 100%;
        }
        
        /* Larger buttons for touch */
        .stButton > button {
            min-height: 56px;
            font-size: 1.1rem;
            width: 100%;
        }
        
        /* Larger text areas on mobile */
        .stTextArea > div > div > textarea {
            font-size: 1.1rem;
            min-height: 200px;
        }
        
        /* Hide non-essential elements */
        .desktop-only {
            display: none !important;
        }
        
        /* Full-width metrics */
        [data-testid="metric-container"] {
            padding: var(--spacing-sm);
        }
        
        /* Audio player more prominent */
        audio {
            min-height: 60px;
            margin: var(--spacing-md) 0;
        }
        
        /* Compact header */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2, .stSubheader {
            font-size: 1.25rem !important;
        }
    }
    
    /* ========================================
       STATUS PILLS (theme-aware)
       ======================================== */
    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        gap: 4px;
    }
    
    .status-approved { background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
    .status-rejected { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .status-pending { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .status-passed { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
    .status-failed { background: rgba(236, 72, 153, 0.2); color: #ec4899; border: 1px solid #ec4899; }
    
    /* ========================================
       UTILITY CLASSES (theme-aware)
       ======================================== */
    .unsaved-warning {
        background: rgba(245, 158, 11, 0.15);
        border-left: 4px solid var(--color-pending);
        padding: var(--spacing-md);
        border-radius: var(--border-radius);
        margin: var(--spacing-md) 0;
        color: inherit;
    }
    
    .success-saved {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid var(--color-approve);
        padding: var(--spacing-md);
        border-radius: var(--border-radius);
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .keyboard-hint {
        font-size: 0.8rem;
        color: #6b7280;
        font-style: italic;
        padding: var(--spacing-xs);
    }
    
    /* Hide keyboard hint on mobile */
    @media (max-width: 768px) {
        .keyboard-hint {
            display: none;
        }
    }
    
    /* Swipe hint for mobile */
    .swipe-hint {
        display: none;
        text-align: center;
        color: #9ca3af;
        font-size: 0.9rem;
        padding: var(--spacing-sm);
    }
    
    @media (max-width: 768px) {
        .swipe-hint {
            display: block;
        }
    }
    
    /* ========================================
       TABLET STYLES (768px - 1024px)
       ======================================== */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding: var(--spacing-md);
        }
    }
    
    /* ========================================
       DESKTOP STYLES (> 1024px)
       ======================================== */
    @media (min-width: 1025px) {
        .mobile-only {
            display: none !important;
        }
        
        /* Sidebar visible by default */
        [data-testid="stSidebar"] {
            min-width: 280px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Main page header - compact for mobile
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
        <span style="font-size: 2rem;">📻</span>
        <div>
            <h1 style="margin: 0; font-size: 1.5rem;">AI Radio Review</h1>
            <p style="margin: 0; color: #6b7280; font-size: 0.9rem;" class="desktop-only">
                Manual review and approval system
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mobile-only quick stats bar
    st.markdown('<p class="swipe-hint">👆 Tap items to review • Swipe to scroll</p>', unsafe_allow_html=True)
    
    # Sidebar (filters for Review List mode)
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        
        # Content type filter - using radio for mobile-friendliness
        content_type_options = ["All"] + CONTENT_TYPES
        content_type_index = content_type_options.index(st.session_state.filter_content_type) if st.session_state.filter_content_type in content_type_options else 0
        st.session_state.filter_content_type = st.selectbox(
            "📂 Content Type",
            content_type_options,
            index=content_type_index
        )
        
        # DJ filter
        dj_options = ["All"] + DJS
        dj_index = dj_options.index(st.session_state.filter_dj) if st.session_state.filter_dj in dj_options else 0
        st.session_state.filter_dj = st.selectbox(
            "🎙️ DJ",
            dj_options,
            index=dj_index
        )
        
        # Status filters in columns
        col_audit, col_review = st.columns(2)
        with col_audit:
            st.session_state.filter_audit_status = st.selectbox(
                "🔍 Audit",
                ["All", "Passed", "Failed"],
                index=["All", "Passed", "Failed"].index(st.session_state.filter_audit_status) if st.session_state.filter_audit_status in ["All", "Passed", "Failed"] else 0
            )
        with col_review:
            st.session_state.filter_review_status = st.selectbox(
                "📋 Review",
                ["All", "Pending", "Approved", "Rejected"],
                index=["All", "Pending", "Approved", "Rejected"].index(st.session_state.filter_review_status) if st.session_state.filter_review_status in ["All", "Pending", "Approved", "Rejected"] else 0
            )
        
        # Search
        st.session_state.search_query = st.text_input(
            "🔎 Search",
            value=st.session_state.search_query,
            placeholder="Search by song/item..."
        )
        
        # Items per page - smaller options for mobile
        st.session_state.items_per_page = st.select_slider(
            "Items per page",
            options=[1, 3, 5, 10, 20],
            value=st.session_state.items_per_page if st.session_state.items_per_page in [1, 3, 5, 10, 20] else 5
        )
        
        st.markdown("---")
        
        # Queue status - prominent
        queue_count = get_regen_queue_count()
        if queue_count > 0:
            st.markdown(f"### 🔄 Queue: {queue_count} items")
            if st.button("▶️ Process Queue", use_container_width=True, type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(progress):
                    progress_bar.progress(progress)
                
                def update_status(status):
                    status_text.text(status)
                
                update_status("Starting...")
                results = process_regeneration_queue(
                    progress_callback=update_progress,
                    status_callback=update_status
                )
                
                # Store results in session state for persistent display
                st.session_state.queue_results = results
                st.rerun()
            
            if st.button("🗑️ Clear Queue", use_container_width=True):
                clear_regen_queue()
                st.session_state.queue_results = None
                st.rerun()
        else:
            st.caption("Queue empty")
        
        # Show persistent queue results if any
        if st.session_state.queue_results:
            results = st.session_state.queue_results
            if results["success_count"] > 0:
                st.success(f"✅ {results['success_count']} generated!")
            if results["failed_count"] > 0:
                st.error(f"❌ {results['failed_count']} failed")
                with st.expander("View errors"):
                    for err in results.get("errors", []):
                        st.text(err)
            if st.button("Clear results", use_container_width=True):
                st.session_state.queue_results = None
                st.rerun()
        
        # Refresh button
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Tab-based navigation
    tab_review, tab_catalog = st.tabs(["📋 Review", "🎵 Catalog"])
    
    with tab_review:
        render_review_tab()
    
    with tab_catalog:
        render_catalog_tab()


def render_review_tab():
    """Render the review tab content."""
    # Main content area
    all_items = scan_generated_content()
    filtered_items = filter_items(all_items)
    
    # Compact statistics bar
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("Total", len(all_items))
    with stat_cols[1]:
        st.metric("Filtered", len(filtered_items))
    with stat_cols[2]:
        approved_count = sum(1 for i in filtered_items if load_review_status(i.folder_path)["status"] == "approved")
        st.metric("✅", approved_count)
    with stat_cols[3]:
        rejected_count = sum(1 for i in filtered_items if load_review_status(i.folder_path)["status"] == "rejected")
        st.metric("❌", rejected_count)
    
    # Progress bar showing review completion
    if len(filtered_items) > 0:
        reviewed_count = approved_count + rejected_count
        progress = reviewed_count / len(filtered_items)
        st.progress(progress, text=f"Reviewed: {reviewed_count}/{len(filtered_items)} ({progress:.0%})")
    
    # Export button (collapsed on mobile)
    with st.expander("📥 Export", expanded=False):
        if len(filtered_items) > 0:
            csv_df = export_reviews_to_csv(filtered_items)
            csv_data = csv_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"review_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # MOBILE-FRIENDLY PAGINATION - Prominent at top
    total_pages = max(1, (len(filtered_items) + st.session_state.items_per_page - 1) // st.session_state.items_per_page)
    
    # Ensure current page is valid
    if st.session_state.current_page >= total_pages:
        st.session_state.current_page = total_pages - 1
    if st.session_state.current_page < 0:
        st.session_state.current_page = 0
    
    # Top pagination bar - mobile optimized
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        if st.button("⬅️ Prev", disabled=(st.session_state.current_page == 0), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    
    with nav_col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 8px; background: rgba(128,128,128,0.1); border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);">
            <strong>{st.session_state.current_page + 1}</strong> / {total_pages}
        </div>
        """, unsafe_allow_html=True)
    
    with nav_col3:
        if st.button("Next ➡️", disabled=(st.session_state.current_page >= total_pages - 1), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()
    
    # Page jump (collapsed on mobile)
    with st.expander("Jump to page", expanded=False):
        jump_page = st.number_input(
            "Go to page",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.current_page + 1,
            step=1,
            label_visibility="collapsed"
        )
        if st.button("Go", use_container_width=True):
            st.session_state.current_page = jump_page - 1
            st.rerun()
    
    st.markdown("---")
    
    # Display items for current page
    start_idx = st.session_state.current_page * st.session_state.items_per_page
    end_idx = min(start_idx + st.session_state.items_per_page, len(filtered_items))
    page_items = filtered_items[start_idx:end_idx]
    
    if not page_items:
        st.info("📭 No items found. Try adjusting your filters.")
    else:
        for idx, item in enumerate(page_items):
            render_review_item(item, start_idx + idx)
    
    # BOTTOM PAGINATION (duplicate for mobile convenience)
    if len(filtered_items) > 0:
        st.markdown("---")
        bottom_col1, bottom_col2, bottom_col3 = st.columns([1, 2, 1])
        
        with bottom_col1:
            if st.button("⬅️ Prev", key="prev_bottom", disabled=(st.session_state.current_page == 0), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        
        with bottom_col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; background: rgba(128,128,128,0.1); border-radius: 8px; border: 1px solid rgba(128,128,128,0.2);">
                <strong>{st.session_state.current_page + 1}</strong> / {total_pages}
            </div>
            """, unsafe_allow_html=True)
        
        with bottom_col3:
            if st.button("Next ➡️", key="next_bottom", disabled=(st.session_state.current_page >= total_pages - 1), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
        
        # Add extra padding at bottom for mobile
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)


def render_catalog_tab():
    """Render the catalog browser tab for generating new content."""
    st.markdown("### 🎵 Song Catalog")
    st.caption("Browse songs and generate intros/outros")
    
    # Filters
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input(
            "🔎 Search songs",
            value=st.session_state.catalog_search,
            placeholder="Search by artist or title...",
            key="catalog_search_input"
        )
        st.session_state.catalog_search = search
    
    with col2:
        dj = st.selectbox(
            "🎙️ DJ",
            ["julie", "mr_new_vegas"],
            index=0 if st.session_state.catalog_dj == "julie" else 1,
            key="catalog_dj_select"
        )
        st.session_state.catalog_dj = dj
    
    # Load catalog
    catalog = load_catalog()
    
    if not catalog:
        st.warning("No catalog found. Check data/catalog.json")
        return
    
    # Filter by search
    if search:
        search_lower = search.lower()
        catalog = [
            s for s in catalog 
            if search_lower in s.get("artist", "").lower() 
            or search_lower in s.get("title", "").lower()
        ]
    
    st.caption(f"Showing {len(catalog)} songs")
    
    # Display songs in a paginated list
    songs_per_page = 10
    total_pages = max(1, (len(catalog) + songs_per_page - 1) // songs_per_page)
    
    if 'catalog_page' not in st.session_state:
        st.session_state.catalog_page = 0
    
    # Pagination controls
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️", key="cat_prev", disabled=(st.session_state.catalog_page == 0)):
            st.session_state.catalog_page -= 1
            st.rerun()
    with nav_col2:
        st.markdown(f"<div style='text-align:center;'><strong>{st.session_state.catalog_page + 1}</strong> / {total_pages}</div>", unsafe_allow_html=True)
    with nav_col3:
        if st.button("➡️", key="cat_next", disabled=(st.session_state.catalog_page >= total_pages - 1)):
            st.session_state.catalog_page += 1
            st.rerun()
    
    # Get current page of songs
    start_idx = st.session_state.catalog_page * songs_per_page
    end_idx = start_idx + songs_per_page
    page_songs = catalog[start_idx:end_idx]
    
    # Display each song
    for song in page_songs:
        artist = song.get("artist", "Unknown")
        title = song.get("title", "Unknown")
        
        # Get generation status
        status = get_song_generation_status(artist, title, dj)
        
        # Status indicators
        intro_status = ""
        if status["intro_script"] and status["intro_audio"]:
            intro_status = "✅"
        elif status["intro_script"]:
            intro_status = "📝"
        elif status["intro_audio"]:
            intro_status = "🔊"
        else:
            intro_status = "❌"
        
        outro_status = ""
        if status["outro_script"] and status["outro_audio"]:
            outro_status = "✅"
        elif status["outro_script"]:
            outro_status = "📝"
        elif status["outro_audio"]:
            outro_status = "🔊"
        else:
            outro_status = "❌"
        
        with st.expander(f"**{title}** — {artist}  [{intro_status} Intro | {outro_status} Outro]"):
            # Two-column layout: lyrics on left, info/actions on right
            col_lyrics, col_actions = st.columns([1, 1])
            
            with col_lyrics:
                st.markdown("**📜 Lyrics:**")
                # Find and display lyrics
                lyrics_file = find_lyrics_file(f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}")
                if lyrics_file:
                    lyrics = load_lyrics(lyrics_file)
                    # Show preview (first 300 chars) with option to expand
                    if len(lyrics) > 300:
                        st.text_area(
                            "Lyrics preview",
                            value=lyrics[:300] + "...",
                            height=120,
                            disabled=True,
                            key=f"lyrics_preview_{song['id']}",
                            label_visibility="collapsed"
                        )
                        with st.expander("📖 Full Lyrics"):
                            st.text_area(
                                "Full lyrics",
                                value=lyrics,
                                height=200,
                                disabled=True,
                                key=f"lyrics_full_{song['id']}",
                                label_visibility="collapsed"
                            )
                    else:
                        st.text_area(
                            "Lyrics",
                            value=lyrics,
                            height=120,
                            disabled=True,
                            key=f"lyrics_{song['id']}",
                            label_visibility="collapsed"
                        )
                else:
                    st.info("No lyrics file found")
            
            with col_actions:
                st.caption(f"Intro: Script {'✅' if status['intro_script'] else '❌'} | Audio {'✅' if status['intro_audio'] else '❌'}")
                st.caption(f"Outro: Script {'✅' if status['outro_script'] else '❌'} | Audio {'✅' if status['outro_audio'] else '❌'}")
                
                # Generation buttons
                st.markdown("**Generate:**")
                
                content_type = st.selectbox(
                    "Content",
                    ["intros", "outros"],
                    key=f"ct_{song['id']}",
                    label_visibility="collapsed"
                )
                regen_type = st.selectbox(
                    "Generate",
                    ["both", "script", "audio"],
                    key=f"rt_{song['id']}",
                    label_visibility="collapsed"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("➕ Queue", key=f"add_{song['id']}", use_container_width=True):
                        if add_catalog_item_to_queue(artist, title, dj, content_type, regen_type):
                            st.success(f"Added!")
                            st.rerun()
                        else:
                            st.warning("Already in queue")
                
                with col_btn2:
                    if st.button("⚡ Now", key=f"gen_{song['id']}", type="primary", use_container_width=True):
                        with st.spinner(f"Generating..."):
                            try:
                                item_id = f"{artist.replace(' ', '_')}-{title.replace(' ', '_')}"
                                
                                success, error = gui_backend.regenerate_content(
                                    content_type_str=content_type,
                                    dj_str=dj,
                                    item_id=item_id,
                                    regen_type=regen_type,
                                    feedback="",
                                )
                                
                                if success:
                                    st.success(f"✅ Generated!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {error}")
                            except Exception as e:
                                st.error(f"❌ {str(e)}")
                
                # Jump to Review button (if content exists)
                if status["intro_script"] or status["outro_script"]:
                    if st.button("📋 Go to Review", key=f"review_{song['id']}", use_container_width=True):
                        # Set search filter to find this song
                        st.session_state.search_query = title
                        st.session_state.filter_content_type = "All"
                        st.rerun()
    
    # Legend
    st.markdown("---")
    st.caption("**Legend:** ✅ Complete | 📝 Script only | 🔊 Audio only | ❌ Not generated")


if __name__ == "__main__":
    main()
