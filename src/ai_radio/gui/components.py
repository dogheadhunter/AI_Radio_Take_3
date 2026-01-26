"""Reusable Streamlit components for AI Radio Review GUI.

Provides mobile-first UI components with large touch targets,
dark/light mode support, and accessible design.
"""
import base64
from pathlib import Path
from typing import Optional, Callable
import streamlit as st


# Minimum touch target size (48px as per WCAG guidelines)
MIN_TOUCH_TARGET = 48


def render_audio_player(
    audio_path: Path,
    label: str = "Audio",
    key: Optional[str] = None,
) -> bool:
    """Render an audio player for a WAV file.
    
    Args:
        audio_path: Path to the audio file
        label: Label to display above the player
        key: Optional unique key for the component
        
    Returns:
        True if audio was rendered, False if file doesn't exist
    """
    if not audio_path or not audio_path.exists():
        st.caption(f"🔇 {label}: No audio available")
        return False
    
    try:
        audio_bytes = audio_path.read_bytes()
        st.caption(f"🔊 {label}")
        st.audio(audio_bytes, format="audio/wav")
        return True
    except Exception as e:
        st.error(f"Error loading audio: {e}")
        return False


def render_script_editor(
    script_text: str,
    key: str,
    placeholder: str = "Edit script text...",
    height: int = 200,
    on_change: Optional[Callable] = None,
) -> str:
    """Render a mobile-friendly script text editor.
    
    Args:
        script_text: Initial text content
        key: Unique key for the text area
        placeholder: Placeholder text
        height: Height of the text area in pixels
        on_change: Optional callback when text changes
        
    Returns:
        The current text in the editor
    """
    # Add mobile-friendly styling
    st.markdown(f"""
    <style>
    /* Mobile-friendly text area */
    [data-testid="stTextArea"] textarea {{
        font-size: 16px !important;  /* Prevent zoom on iOS */
        min-height: {height}px !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    return st.text_area(
        label="Script Content",
        value=script_text,
        height=height,
        key=key,
        placeholder=placeholder,
        label_visibility="collapsed",
        on_change=on_change,
    )


def render_status_badge(status: str, size: str = "normal") -> str:
    """Render a colored status badge.
    
    Args:
        status: Status string (approved, rejected, pending, passed, failed)
        size: Badge size (small, normal, large)
        
    Returns:
        HTML string for the badge
    """
    status_lower = status.lower() if status else "unknown"
    
    colors = {
        "approved": ("#22c55e", "rgba(34, 197, 94, 0.15)"),  # Green
        "rejected": ("#ef4444", "rgba(239, 68, 68, 0.15)"),  # Red
        "pending": ("#f59e0b", "rgba(245, 158, 11, 0.15)"),  # Orange
        "passed": ("#3b82f6", "rgba(59, 130, 246, 0.15)"),   # Blue
        "failed": ("#ec4899", "rgba(236, 72, 153, 0.15)"),   # Pink
        "regenerating": ("#8b5cf6", "rgba(139, 92, 246, 0.15)"),  # Purple
        "unknown": ("#6b7280", "rgba(107, 114, 128, 0.15)"),  # Gray
    }
    
    text_color, bg_color = colors.get(status_lower, colors["unknown"])
    
    sizes = {
        "small": ("0.75rem", "2px 6px"),
        "normal": ("0.85rem", "4px 10px"),
        "large": ("1rem", "6px 14px"),
    }
    font_size, padding = sizes.get(size, sizes["normal"])
    
    icons = {
        "approved": "✅",
        "rejected": "❌",
        "pending": "⏳",
        "passed": "✓",
        "failed": "✗",
        "regenerating": "🔄",
    }
    icon = icons.get(status_lower, "•")
    
    return f"""
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: {bg_color};
        color: {text_color};
        padding: {padding};
        border-radius: 9999px;
        font-size: {font_size};
        font-weight: 600;
        border: 1px solid {text_color};
    ">
        {icon} {status.title() if status else 'Unknown'}
    </span>
    """


def render_mobile_button(
    label: str,
    key: str,
    type: str = "secondary",
    disabled: bool = False,
    icon: str = "",
    full_width: bool = True,
) -> bool:
    """Render a mobile-friendly button with large touch target.
    
    Args:
        label: Button label
        key: Unique key for the button
        type: Button type (primary, secondary)
        disabled: Whether button is disabled
        icon: Optional emoji icon prefix
        full_width: Whether button spans full width
        
    Returns:
        True if button was clicked
    """
    button_label = f"{icon} {label}" if icon else label
    
    return st.button(
        button_label,
        key=key,
        type="primary" if type == "primary" else "secondary",
        disabled=disabled,
        use_container_width=full_width,
    )


def render_version_selector(
    versions: list,
    current_version: int,
    key: str,
) -> int:
    """Render a dropdown to select a version.
    
    Args:
        versions: List of VersionInfo objects or version numbers
        current_version: Currently selected version
        key: Unique key for the selector
        
    Returns:
        Selected version number
    """
    if not versions:
        st.caption("No versions available")
        return 0
    
    # Build options
    options = []
    for v in versions:
        if hasattr(v, 'version'):
            version_num = v.version
            version_type = getattr(v, 'version_type', None)
            type_str = f" ({version_type.value})" if version_type else ""
            options.append(f"v{version_num}{type_str}")
        else:
            options.append(f"v{v}")
    
    # Find current index
    current_idx = 0
    for i, v in enumerate(versions):
        version_num = getattr(v, 'version', v)
        if version_num == current_version:
            current_idx = i
            break
    
    selected = st.selectbox(
        "Version",
        options=options,
        index=current_idx,
        key=key,
        label_visibility="collapsed",
    )
    
    # Extract version number from selection
    if selected:
        # Parse "v0 (original)" -> 0
        version_str = selected.split()[0].replace("v", "")
        try:
            return int(version_str)
        except ValueError:
            pass
    
    return current_version


def render_collapsible_section(
    title: str,
    key: str,
    expanded: bool = False,
    icon: str = "",
):
    """Render a collapsible section header.
    
    Args:
        title: Section title
        key: Unique key for the expander
        expanded: Whether section is initially expanded
        icon: Optional emoji icon
        
    Returns:
        Streamlit expander context manager
    """
    full_title = f"{icon} {title}" if icon else title
    return st.expander(full_title, expanded=expanded)


def render_metadata_row(label: str, value: str, icon: str = ""):
    """Render a metadata label-value row.
    
    Args:
        label: Metadata label
        value: Metadata value
        icon: Optional emoji icon
    """
    col1, col2 = st.columns([1, 2])
    with col1:
        st.caption(f"{icon} {label}:" if icon else f"{label}:")
    with col2:
        st.write(value)


def render_action_buttons(
    item_key: str,
    on_regenerate_script: Optional[Callable] = None,
    on_regenerate_audio: Optional[Callable] = None,
    on_regenerate_both: Optional[Callable] = None,
    script_disabled: bool = False,
    audio_disabled: bool = False,
) -> Optional[str]:
    """Render regeneration action buttons in a row.
    
    Args:
        item_key: Unique key prefix for buttons
        on_regenerate_script: Callback for regenerate script
        on_regenerate_audio: Callback for regenerate audio
        on_regenerate_both: Callback for regenerate both
        script_disabled: Disable script regeneration
        audio_disabled: Disable audio regeneration
        
    Returns:
        Action that was clicked, or None
    """
    col1, col2, col3 = st.columns(3)
    
    action = None
    
    with col1:
        if st.button(
            "📝 Script",
            key=f"{item_key}_regen_script",
            disabled=script_disabled,
            use_container_width=True,
        ):
            action = "script"
            if on_regenerate_script:
                on_regenerate_script()
    
    with col2:
        if st.button(
            "🔊 Audio",
            key=f"{item_key}_regen_audio",
            disabled=audio_disabled,
            use_container_width=True,
        ):
            action = "audio"
            if on_regenerate_audio:
                on_regenerate_audio()
    
    with col3:
        if st.button(
            "♻️ Both",
            key=f"{item_key}_regen_both",
            disabled=script_disabled or audio_disabled,
            use_container_width=True,
            type="primary",
        ):
            action = "both"
            if on_regenerate_both:
                on_regenerate_both()
    
    return action


def inject_mobile_styles():
    """Inject global CSS styles for mobile-first design."""
    st.markdown("""
    <style>
    /* ========================================
       MOBILE-FIRST BASE STYLES
       ======================================== */
    
    /* Touch-friendly minimum sizes */
    .stButton > button {
        min-height: 48px !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        min-height: 48px !important;
    }
    
    /* Prevent zoom on input focus (iOS) */
    input, textarea, select {
        font-size: 16px !important;
    }
    
    /* ========================================
       RESPONSIVE BREAKPOINTS
       ======================================== */
    
    /* Mobile (default) */
    .main .block-container {
        padding: 0.5rem 1rem 4rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* Tablet */
    @media (min-width: 768px) {
        .main .block-container {
            padding: 1rem 2rem 4rem 2rem !important;
        }
    }
    
    /* Desktop */
    @media (min-width: 1024px) {
        .main .block-container {
            max-width: 1200px !important;
            padding: 2rem 3rem 4rem 3rem !important;
        }
    }
    
    /* ========================================
       DARK/LIGHT MODE SUPPORT
       ======================================== */
    
    @media (prefers-color-scheme: dark) {
        .card-container {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    }
    
    @media (prefers-color-scheme: light) {
        .card-container {
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
    }
    
    .card-container {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    /* ========================================
       AUDIO PLAYER STYLES
       ======================================== */
    
    audio {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 8px !important;
    }
    
    /* ========================================
       DIFF STYLES
       ======================================== */
    
    .diff-inline {
        background: rgba(128, 128, 128, 0.05);
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
    }
    
    /* HtmlDiff table styling */
    table.diff {
        width: 100%;
        border-collapse: collapse;
        font-family: monospace;
        font-size: 0.85rem;
    }
    
    table.diff td {
        padding: 2px 8px;
        vertical-align: top;
    }
    
    table.diff .diff_add {
        background: rgba(34, 197, 94, 0.2);
    }
    
    table.diff .diff_sub {
        background: rgba(239, 68, 68, 0.2);
    }
    
    table.diff .diff_chg {
        background: rgba(245, 158, 11, 0.2);
    }
    
    </style>
    """, unsafe_allow_html=True)
