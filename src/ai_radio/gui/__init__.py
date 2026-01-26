"""GUI utilities for AI Radio Streamlit application.

This package provides reusable utilities for the Review GUI including:
- Diff rendering with color highlighting
- Version management for content items
- Mobile-first Streamlit components
- Backend service layer using API

IMPORTANT: The GUI should use the backend module for all data operations
to ensure content goes through the proper pipeline with lyrics, validation,
and audit loop.
"""

from src.ai_radio.gui.diff import render_diff, render_inline_diff
from src.ai_radio.gui.version import (
    VersionInfo,
    VersionManager,
    VersionType,
    get_version_info,
    create_new_version,
)
from src.ai_radio.gui.components import (
    render_audio_player,
    render_script_editor,
    render_status_badge,
    render_mobile_button,
    inject_mobile_styles,
)
from src.ai_radio.gui import backend

__all__ = [
    # Diff rendering
    "render_diff",
    "render_inline_diff",
    # Version management
    "VersionInfo",
    "VersionManager",
    "VersionType",
    "get_version_info",
    "create_new_version",
    # Components
    "render_audio_player",
    "render_script_editor",
    "render_status_badge",
    "render_mobile_button",
    "inject_mobile_styles",
    # Backend
    "backend",
]
