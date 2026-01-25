"""
Streamlit-based review GUI for AI Radio generated scripts and audio.

Allows manual review, approval/rejection, version comparison,
and regeneration queueing of generated content.
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

# Constants
DATA_DIR = Path("data")
GENERATED_DIR = DATA_DIR / "generated"
AUDIT_DIR = DATA_DIR / "audit"
REGEN_QUEUE_FILE = DATA_DIR / "regeneration_queue.json"
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
    audio_versions: List[Path]
    latest_version: int
    audit_status: Optional[str] = None
    review_status: Optional[str] = None
    
    def get_script_path(self, version: int = None) -> Optional[Path]:
        """Get script path for a specific version (or latest)."""
        if version is None:
            version = self.latest_version
        if version < len(self.script_versions):
            return self.script_versions[version]
        return None
    
    def get_audio_path(self, version: int = None) -> Optional[Path]:
        """Get audio path for a specific version (or latest)."""
        if version is None:
            version = self.latest_version
        if version < len(self.audio_versions):
            return self.audio_versions[version]
        return None




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


def scan_generated_content() -> List[ReviewItem]:
    """Scan data/generated directory for all content."""
    items = []
    
    if not GENERATED_DIR.exists():
        return items
    
    for content_type in CONTENT_TYPES:
        content_dir = GENERATED_DIR / content_type
        if not content_dir.exists():
            continue
        
        for dj in DJS:
            dj_dir = content_dir / dj
            if not dj_dir.exists():
                continue
            
            # Each subdirectory is an item (song folder, time slot, weather condition)
            for item_folder in dj_dir.iterdir():
                if not item_folder.is_dir():
                    continue
                
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
                    continue
                
                # Determine latest version number
                latest_version = 0
                for path in script_versions + audio_versions:
                    try:
                        # Handle both _outro and _N naming
                        stem_parts = path.stem.split('_')
                        if content_type == "outros":
                            # julie_outro or julie_outro_1
                            if len(stem_parts) > 2:
                                version = int(stem_parts[-1])
                                latest_version = max(latest_version, version)
                        else:
                            # julie_0 or julie_1
                            version = int(stem_parts[-1])
                            latest_version = max(latest_version, version)
                    except (ValueError, IndexError):
                        pass
                
                # Get audit and review status
                item_id = item_folder.name
                audit_status = get_audit_status(content_type, dj, item_id)
                review_status_data = load_review_status(item_folder)
                review_status = review_status_data.get("status", "pending")
                
                items.append(ReviewItem(
                    content_type=content_type,
                    dj=dj,
                    item_id=item_id,
                    folder_path=item_folder,
                    script_versions=script_versions,
                    audio_versions=audio_versions,
                    latest_version=latest_version,
                    audit_status=audit_status,
                    review_status=review_status
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
    
    # Search query
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered = [i for i in filtered if query in i.item_id.lower()]
    
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


def process_regeneration_queue(progress_callback=None, status_callback=None):
    """
    Process items in the regeneration queue with progress tracking.
    
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
    
    # Import generation pipeline
    try:
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        from src.ai_radio.generation.pipeline import GenerationPipeline
        from src.ai_radio.generation.prompts import DJ
    except Exception as e:
        return {"success_count": 0, "failed_count": 0, "errors": [f"Failed to import generation pipeline: {str(e)}"]}
    
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
            folder_path = Path(queue_item["folder_path"])
            feedback = queue_item.get("feedback", "")
            
            # Create DJ enum
            dj = DJ.JULIE if dj_name == "julie" else DJ.MR_NEW_VEGAS
            
            # Initialize pipeline
            pipeline = GenerationPipeline()
            
            # Determine version number
            version = _get_next_version_for_regen(folder_path, dj_name, content_type)
            
            # Generate based on type
            success = False
            if content_type == "intros":
                artist, song = _parse_song_info(item_id)
                if artist and song:
                    success = _generate_intro(pipeline, dj, artist, song, regen_type, feedback)
            elif content_type == "outros":
                artist, song = _parse_song_info(item_id)
                if artist and song:
                    success = _generate_outro(pipeline, dj, artist, song, regen_type, feedback)
            elif content_type == "time":
                hour, minute = _parse_time_info(item_id)
                if hour is not None:
                    success = _generate_time(pipeline, dj, hour, minute, regen_type, feedback)
            elif content_type == "weather":
                hour, minute = _parse_time_info(item_id)
                if hour is not None:
                    success = _generate_weather(pipeline, dj, hour, minute, regen_type, feedback)
            
            if success:
                results["success_count"] += 1
            else:
                results["failed_count"] += 1
                results["errors"].append(f"{item_id}: Generation returned False")
                
        except Exception as e:
            results["failed_count"] += 1
            error_msg = f"{item_id}: {str(e)}"
            results["errors"].append(error_msg)
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


def _generate_intro(pipeline, dj, artist: str, song: str, regen_type: str, feedback: str) -> bool:
    """Generate intro with specified parameters."""
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        pipeline.generate_song_intro(
            artist=artist,
            song=song,
            dj=dj,
            prompt_version="v2",
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=feedback if feedback else None
        )
        return True
    except Exception:
        return False


def _generate_outro(pipeline, dj, artist: str, song: str, regen_type: str, feedback: str) -> bool:
    """Generate outro with specified parameters."""
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        pipeline.generate_song_outro(
            artist=artist,
            song=song,
            dj=dj,
            prompt_version="v2",
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=feedback if feedback else None
        )
        return True
    except Exception:
        return False


def _generate_time(pipeline, dj, hour: int, minute: int, regen_type: str, feedback: str) -> bool:
    """Generate time announcement with specified parameters."""
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        pipeline.generate_time_announcement(
            hour=hour,
            minute=minute,
            dj=dj,
            prompt_version="v2",
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=feedback if feedback else None
        )
        return True
    except Exception:
        return False


def _generate_weather(pipeline, dj, hour: int, minute: int, regen_type: str, feedback: str) -> bool:
    """Generate weather announcement with specified parameters."""
    try:
        text_only = regen_type == "script"
        audio_only = regen_type == "audio"
        pipeline.generate_weather_announcement(
            hour=hour,
            minute=minute,
            dj=dj,
            prompt_version="v2",
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=feedback if feedback else None
        )
        return True
    except Exception:
        return False


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


def render_audio_player(audio_path: Path):
    """Render HTML5 audio player for a wav file."""
    if audio_path and audio_path.exists():
        audio_bytes = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio controls style="width: 100%;">
            <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.warning("Audio file not found")


def render_review_item(item: ReviewItem, index: int):
    """Render a single review item with all controls."""
    review_status = load_review_status(item.folder_path)
    
    # Header with metadata
    with st.container():
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.subheader(f"{item.item_id}")
        with col2:
            st.caption(f"**Type:** {item.content_type}")
        with col3:
            st.caption(f"**DJ:** {item.dj}")
        with col4:
            # Status badges
            if item.audit_status:
                color = "[PASS]" if item.audit_status == "passed" else "[FAIL]"
                st.caption(f"Audit: {color}")
            
            review_color = {"pending": "[PEND]", "approved": "[APPR]", "rejected": "[REJ]"}.get(review_status["status"], "[PEND]")
            st.caption(f"Review: {review_color}")
        
        # Version selector
        version = st.selectbox(
            "Version",
            range(item.latest_version + 1),
            index=item.latest_version,
            key=f"version_{index}"
        )
        
        # Display script and audio side by side
        col_script, col_audio = st.columns(2)
        
        with col_script:
            st.markdown("**Script:**")
            script_path = item.get_script_path(version)
            if script_path and script_path.exists():
                script_text = script_path.read_text(encoding='utf-8')
                st.text_area(
                    "Script content",
                    script_text,
                    height=150,
                    key=f"script_{index}_{version}",
                    label_visibility="collapsed"
                )
            else:
                st.warning("No script file found")
        
        with col_audio:
            st.markdown("**Audio:**")
            audio_path = item.get_audio_path(version)
            render_audio_player(audio_path)
        
        # Version comparison (if multiple versions exist)
        if item.latest_version > 0:
            with st.expander("Compare Versions"):
                compare_ver = st.selectbox(
                    "Compare with version",
                    [v for v in range(item.latest_version + 1) if v != version],
                    key=f"compare_{index}"
                )
                
                if compare_ver != version:
                    comp_script_path = item.get_script_path(compare_ver)
                    if comp_script_path and comp_script_path.exists():
                        comp_script = comp_script_path.read_text(encoding='utf-8')
                        st.text_area(
                            f"Version {compare_ver} script",
                            comp_script,
                            height=100,
                            key=f"comp_script_{index}_{compare_ver}"
                        )
        
        # Review decision section
        with st.expander("Review Decision", expanded=(review_status["status"] == "pending")):
            # Script issues
            st.markdown("**Script Issues:**")
            script_issue_options = SCRIPT_ISSUES.get(item.content_type, [])
            selected_script_issues = st.multiselect(
                "Select script issues",
                script_issue_options,
                default=review_status.get("script_issues", []),
                key=f"script_issues_{index}",
                label_visibility="collapsed"
            )
            
            # Audio issues
            st.markdown("**Audio Issues:**")
            selected_audio_issues = st.multiselect(
                "Select audio issues",
                AUDIO_ISSUES,
                default=review_status.get("audio_issues", []),
                key=f"audio_issues_{index}",
                label_visibility="collapsed"
            )
            
            # Notes
            reviewer_notes = st.text_area(
                "Reviewer Notes",
                value=review_status.get("reviewer_notes", ""),
                key=f"notes_{index}",
                height=80
            )
            
            # Action buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("Approve", key=f"approve_{index}", use_container_width=True):
                    new_status = {
                        "status": "approved",
                        "reviewed_at": datetime.now().isoformat(),
                        "reviewer_notes": reviewer_notes,
                        "script_issues": selected_script_issues,
                        "audio_issues": selected_audio_issues
                    }
                    save_review_status(item.folder_path, new_status)
                    st.success("Approved!")
                    st.rerun()
            
            with col2:
                if st.button("Reject", key=f"reject_{index}", use_container_width=True):
                    new_status = {
                        "status": "rejected",
                        "reviewed_at": datetime.now().isoformat(),
                        "reviewer_notes": reviewer_notes,
                        "script_issues": selected_script_issues,
                        "audio_issues": selected_audio_issues
                    }
                    save_review_status(item.folder_path, new_status)
                    st.error("Rejected!")
                    st.rerun()
            
            with col3:
                if st.button("Regen Script", key=f"regen_script_{index}", use_container_width=True):
                    feedback = f"Script issues: {', '.join(selected_script_issues)}. {reviewer_notes}"
                    add_to_regen_queue(item, "script", feedback)
                    st.info("Added to regeneration queue")
            
            with col4:
                if st.button("Regen Audio", key=f"regen_audio_{index}", use_container_width=True):
                    feedback = f"Audio issues: {', '.join(selected_audio_issues)}. {reviewer_notes}"
                    add_to_regen_queue(item, "audio", feedback)
                    st.info("Added to regeneration queue")
            
            with col5:
                if st.button("Regen Both", key=f"regen_both_{index}", use_container_width=True):
                    feedback = f"Script issues: {', '.join(selected_script_issues)}. Audio issues: {', '.join(selected_audio_issues)}. {reviewer_notes}"
                    add_to_regen_queue(item, "both", feedback)
                    st.info("Added to regeneration queue")


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
            folder = GENERATED_DIR / content_type / dj / song_id
            if folder.exists():
                # Scan for versions
                script_versions = []
                audio_versions = []
                
                if content_type == "outros":
                    # Outros use different naming: dj_outro.txt, dj_outro_1.txt, etc.
                    base_script = folder / f"{dj}_outro.txt"
                    base_audio = folder / f"{dj}_outro.wav"
                    if base_script.exists():
                        script_versions.append(base_script)
                    if base_audio.exists():
                        audio_versions.append(base_audio)
                    
                    # Check for numbered versions
                    for i in range(1, 100):
                        script = folder / f"{dj}_outro_{i}.txt"
                        audio = folder / f"{dj}_outro_{i}.wav"
                        if script.exists():
                            script_versions.append(script)
                        if audio.exists():
                            audio_versions.append(audio)
                        if not script.exists() and not audio.exists():
                            break
                else:
                    # Standard naming: dj_0.txt, dj_1.txt, etc.
                    for i in range(100):
                        script = folder / f"{dj}_{i}.txt"
                        audio = folder / f"{dj}_{i}.wav"
                        if script.exists():
                            script_versions.append(script)
                        if audio.exists():
                            audio_versions.append(audio)
                        if not script.exists() and not audio.exists():
                            break
                
                if script_versions or audio_versions:
                    latest = max(len(script_versions), len(audio_versions)) - 1
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
                        review_status=review_status_data.get("status", "pending")
                    )
                    content[content_type].append(item)
    
    return content


def save_manual_script(item: ReviewItem, new_script: str, version: int) -> bool:
    """Save manually edited script and mark it as rewritten."""
    try:
        script_path = item.get_script_path(version)
        if script_path:
            # Save the new script
            script_path.write_text(new_script, encoding='utf-8')
            
            # Mark as manually rewritten in review status
            review_status = load_review_status(item.folder_path)
            review_status["manually_rewritten"] = True
            review_status["rewritten_version"] = version
            review_status["rewritten_at"] = datetime.now().isoformat()
            save_review_status(item.folder_path, review_status)
            
            return True
    except Exception as e:
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
    """Render an editable content item in the song editor."""
    with st.container():
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.subheader(f"{item.dj.replace('_', ' ').title()} - {content_label.title()}")
        with col2:
            # Status indicators
            if item.audit_status:
                status_emoji = "[PASS]" if item.audit_status == "passed" else "[FAIL]"
                st.markdown(f"Audit: {status_emoji}")
        with col3:
            review_emoji = {"approved": "[APPR]", "rejected": "[REJ]", "pending": "[PEND]"}
            st.markdown(f"Review: {review_emoji.get(item.review_status, '[PEND]')}")
        
        # Check if manually rewritten
        review_status = load_review_status(item.folder_path)
        is_rewritten = review_status.get("manually_rewritten", False)
        rewritten_version = review_status.get("rewritten_version", None)
        
        if is_rewritten:
            st.success(f"[MANUAL] Manually rewritten (version {rewritten_version}) - This version will be used for audio generation")
        
        # Version selector
        version_options = list(range(len(item.script_versions)))
        if version_options:
            selected_version = st.selectbox(
                "Version",
                version_options,
                index=min(item.latest_version, len(version_options) - 1),
                key=f"version_{item.dj}_{item.content_type}_{item.item_id}"
            )
        else:
            st.warning("No versions available")
            return
        
        # Get script path and content before rendering columns
        script_path = item.get_script_path(selected_version)
        current_script = None
        if script_path and script_path.exists():
            current_script = script_path.read_text(encoding='utf-8')
        
        # Two column layout: Edit Script | Reference Materials (with audio inline)
        col_edit, col_reference = st.columns([1, 1])
        
        with col_edit:
            st.markdown("**Edit Script:**")
            if current_script is not None:
                # Editable script area
                edited_script = st.text_area(
                    "Your edits",
                    value=current_script,
                    height=400,
                    key=f"script_edit_{item.dj}_{item.content_type}_{selected_version}",
                    help="Edit the script here. Changes will be saved when you click 'Save Changes'"
                )
                
                # Save button
                col_save, col_regen = st.columns(2)
                with col_save:
                    if edited_script != current_script:
                        if st.button(f"Save Changes", key=f"save_{item.dj}_{item.content_type}_{selected_version}"):
                            if save_manual_script(item, edited_script, selected_version):
                                st.success("Script saved and marked as manually rewritten!")
                                st.rerun()
                
                with col_regen:
                    if st.button(f"Regenerate Audio", key=f"regen_audio_{item.dj}_{item.content_type}_{selected_version}"):
                        # Add to regeneration queue for audio only
                        feedback = "Manual script edit - regenerate audio with updated script"
                        add_to_regen_queue(item, "audio", feedback)
                        st.info("Added to regeneration queue")
            else:
                st.warning(f"Script file not found: {script_path}")
        
        with col_reference:
            st.markdown("**Reference Materials:**")
            
            # Show song lyrics
            st.markdown("*Song Lyrics:*")
            lyrics = load_lyrics(song_info['lyrics_file'])
            st.text_area(
                "Lyrics for reference",
                value=lyrics,
                height=150,
                disabled=True,
                key=f"ref_lyrics_{item.dj}_{item.content_type}_{selected_version}",
                label_visibility="collapsed"
            )
            
            # Show original generated script (version 0 if available, otherwise current version)
            st.markdown("*Original Generated Script:*")
            # Always try to show version 0 as the "original" for comparison
            original_script_path = item.get_script_path(0)
            if original_script_path and original_script_path.exists():
                original_script = original_script_path.read_text(encoding='utf-8')
                comparison_label = "Version 0 (original)" if selected_version != 0 else "Current version"
                st.text_area(
                    f"Original script for comparison ({comparison_label})",
                    value=original_script,
                    height=120,
                    disabled=True,
                    key=f"ref_script_{item.dj}_{item.content_type}_{selected_version}",
                    label_visibility="collapsed"
                )
            elif current_script is not None:
                # Fallback to current script if version 0 doesn't exist
                st.text_area(
                    "Original script for comparison",
                    value=current_script,
                    height=120,
                    disabled=True,
                    key=f"ref_script_{item.dj}_{item.content_type}_{selected_version}",
                    label_visibility="collapsed"
                )
            else:
                st.info("No original script available")
            
            # Audio player inline with reference materials
            st.markdown("*Audio Preview:*")
            audio_path = item.get_audio_path(selected_version)
            if audio_path and audio_path.exists():
                try:
                    audio_bytes = audio_path.read_bytes()
                    st.audio(audio_bytes, format="audio/wav")
                except Exception as e:
                    st.error(f"Error loading audio: {e}")
            else:
                st.info("No audio file for this version")
        
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
    if 'page_mode' not in st.session_state:
        st.session_state.page_mode = "Review List"


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Radio Review GUI",
        page_icon=":radio:",
        layout="wide"
    )
    
    init_session_state()
    
    # Page mode selector in sidebar
    with st.sidebar:
        st.session_state.page_mode = st.radio(
            "Page",
            ["Review List", "Song Editor"],
            index=["Review List", "Song Editor"].index(st.session_state.page_mode) if st.session_state.page_mode in ["Review List", "Song Editor"] else 0
        )
        st.markdown("---")
    
    # Route to appropriate page
    if st.session_state.page_mode == "Song Editor":
        render_song_editor_page()
        return
    
    # Original Review List page
    st.title("AI Radio Review GUI")
    st.markdown("Manual review and approval system for generated scripts and audio")
    
    # Sidebar (filters for Review List mode)
    with st.sidebar:
        # Collapsible filters section
        with st.expander("Filters", expanded=True):
            # Content type filter
            st.session_state.filter_content_type = st.selectbox(
                "Content Type",
                ["All"] + CONTENT_TYPES,
                index=["All"] + CONTENT_TYPES.index(st.session_state.filter_content_type) if st.session_state.filter_content_type in CONTENT_TYPES else 0
            )
            
            # DJ filter
            st.session_state.filter_dj = st.selectbox(
                "DJ",
                ["All"] + DJS,
                index=["All"] + DJS.index(st.session_state.filter_dj) if st.session_state.filter_dj in DJS else 0
            )
            
            # Audit status filter
            st.session_state.filter_audit_status = st.selectbox(
                "Audit Status",
                ["All", "Passed", "Failed"],
                index=["All", "Passed", "Failed"].index(st.session_state.filter_audit_status) if st.session_state.filter_audit_status in ["All", "Passed", "Failed"] else 0
            )
            
            # Review status filter
            st.session_state.filter_review_status = st.selectbox(
                "Review Status",
                ["All", "Pending", "Approved", "Rejected"],
                index=["All", "Pending", "Approved", "Rejected"].index(st.session_state.filter_review_status) if st.session_state.filter_review_status in ["All", "Pending", "Approved", "Rejected"] else 0
            )
            
            # Search
            st.session_state.search_query = st.text_input(
                "Search Item ID",
                value=st.session_state.search_query
            )
            
            # Items per page
            st.session_state.items_per_page = st.selectbox(
                "Items per page",
                [5, 10, 20, 50],
                index=[5, 10, 20, 50].index(st.session_state.items_per_page)
            )
        
        st.markdown("---")
        
        # Collapsible actions section
        with st.expander("Actions", expanded=True):
            # Refresh button
            if st.button("Refresh", use_container_width=True):
                st.rerun()
            
            # Regeneration queue status
            queue_count = get_regen_queue_count()
            st.metric("Regen Queue", queue_count)
            
            if queue_count > 0:
                # Process Queue button
                if st.button("Process Queue", use_container_width=True, type="primary"):
                    # Initialize progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def update_progress(progress):
                        progress_bar.progress(progress)
                    
                    def update_status(status):
                        status_text.text(status)
                    
                    # Process the queue
                    update_status("Starting regeneration...")
                    results = process_regeneration_queue(
                        progress_callback=update_progress,
                        status_callback=update_status
                    )
                    
                    # Show results
                    if results["success_count"] > 0:
                        st.success(f"Regenerated {results['success_count']} items successfully!")
                    
                    if results["failed_count"] > 0:
                        st.error(f"Failed to regenerate {results['failed_count']} items")
                        if results["errors"]:
                            with st.expander("View Errors"):
                                for error in results["errors"]:
                                    st.text(error)
                    
                    # Rerun to clear the progress display and update queue count
                    st.rerun()
                
                # Clear Queue button
                if st.button("Clear Queue", use_container_width=True):
                    clear_regen_queue()
                    st.success("Queue cleared!")
                    st.rerun()
    
    # Main content area
    # Scan and filter items
    all_items = scan_generated_content()
    filtered_items = filter_items(all_items)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", len(all_items))
    with col2:
        st.metric("Filtered Items", len(filtered_items))
    with col3:
        approved_count = sum(1 for i in filtered_items if load_review_status(i.folder_path)["status"] == "approved")
        st.metric("Approved", approved_count)
    with col4:
        rejected_count = sum(1 for i in filtered_items if load_review_status(i.folder_path)["status"] == "rejected")
        st.metric("Rejected", rejected_count)
    
    # Export button
    if len(filtered_items) > 0:
        csv_df = export_reviews_to_csv(filtered_items)
        csv_data = csv_df.to_csv(index=False)
        st.download_button(
            label="Export Reviews to CSV",
            data=csv_data,
            file_name=f"review_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Pagination
    total_pages = (len(filtered_items) + st.session_state.items_per_page - 1) // st.session_state.items_per_page
    
    if total_pages > 0:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page = max(0, st.session_state.current_page - 1)
                st.rerun()
        with col2:
            st.markdown(f"<div style='text-align: center;'>Page {st.session_state.current_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("Next ➡️", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page = min(total_pages - 1, st.session_state.current_page + 1)
                st.rerun()
    
    # Display items for current page
    start_idx = st.session_state.current_page * st.session_state.items_per_page
    end_idx = min(start_idx + st.session_state.items_per_page, len(filtered_items))
    page_items = filtered_items[start_idx:end_idx]
    
    if not page_items:
        st.info("No items found matching the current filters.")
    else:
        for idx, item in enumerate(page_items):
            render_review_item(item, start_idx + idx)


if __name__ == "__main__":
    main()
