"""GUI utilities for AI Radio Streamlit application.

This package provides reusable utilities for the Review GUI including:
- Diff rendering with color highlighting
- Version management for content items
- Mobile-first Streamlit components
"""

from src.ai_radio.gui.diff import render_diff, render_inline_diff
from src.ai_radio.gui.version import (
    VersionInfo,
    VersionManager,
    get_version_info,
    create_new_version,
)
from src.ai_radio.gui.components import (
    render_audio_player,
    render_script_editor,
    render_status_badge,
    render_mobile_button,
)

__all__ = [
    # Diff rendering
    "render_diff",
    "render_inline_diff",
    # Version management
    "VersionInfo",
    "VersionManager",
    "get_version_info",
    "create_new_version",
    # Components
    "render_audio_player",
    "render_script_editor",
    "render_status_badge",
    "render_mobile_button",
]
