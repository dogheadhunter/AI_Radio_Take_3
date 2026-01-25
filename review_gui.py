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

# Constants
DATA_DIR = Path("data")
GENERATED_DIR = DATA_DIR / "generated"
AUDIT_DIR = DATA_DIR / "audit"
REGEN_QUEUE_FILE = DATA_DIR / "regeneration_queue.json"

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


def init_session_state():
    """Initialize Streamlit session state."""
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
                color = "🟢" if item.audit_status == "passed" else "🔴"
                st.caption(f"Audit: {color}")
            
            review_color = {"pending": "⚪", "approved": "🟢", "rejected": "🔴"}.get(review_status["status"], "⚪")
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
            with st.expander("📊 Compare Versions"):
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
        with st.expander("✏️ Review Decision", expanded=(review_status["status"] == "pending")):
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
                if st.button("✅ Approve", key=f"approve_{index}", use_container_width=True):
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
                if st.button("❌ Reject", key=f"reject_{index}", use_container_width=True):
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
                if st.button("🔄 Regen Script", key=f"regen_script_{index}", use_container_width=True):
                    feedback = f"Script issues: {', '.join(selected_script_issues)}. {reviewer_notes}"
                    add_to_regen_queue(item, "script", feedback)
                    st.info("Added to regeneration queue")
            
            with col4:
                if st.button("🔊 Regen Audio", key=f"regen_audio_{index}", use_container_width=True):
                    feedback = f"Audio issues: {', '.join(selected_audio_issues)}. {reviewer_notes}"
                    add_to_regen_queue(item, "audio", feedback)
                    st.info("Added to regeneration queue")
            
            with col5:
                if st.button("🔄🔊 Regen Both", key=f"regen_both_{index}", use_container_width=True):
                    feedback = f"Script issues: {', '.join(selected_script_issues)}. Audio issues: {', '.join(selected_audio_issues)}. {reviewer_notes}"
                    add_to_regen_queue(item, "both", feedback)
                    st.info("Added to regeneration queue")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Radio Review GUI",
        page_icon="🎙️",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("🎙️ AI Radio Review GUI")
    st.markdown("Manual review and approval system for generated scripts and audio")
    
    # Sidebar
    with st.sidebar:
        st.header("Filters")
        
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
        st.header("Actions")
        
        # Refresh button
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        # Regeneration queue status
        queue_count = get_regen_queue_count()
        st.metric("Regen Queue", queue_count)
        
        if queue_count > 0:
            if st.button("🗑️ Clear Queue", use_container_width=True):
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
            label="📥 Export Reviews to CSV",
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
