"""Shared data types for AI Radio API.

This module defines the core data structures used throughout the API layer.
Uses Python dataclasses for lightweight, standard-library-based typing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class ContentType(str, Enum):
    """Types of radio content that can be generated."""
    INTRO = "intro"
    OUTRO = "outro"
    TIME = "time"
    WEATHER = "weather"


class DJ(str, Enum):
    """Available DJ personalities."""
    JULIE = "julie"
    MR_NEW_VEGAS = "mr_new_vegas"


class ReviewStatus(str, Enum):
    """Status of a content item in the review queue."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REGENERATING = "regenerating"


class AuditStatus(str, Enum):
    """Status of an audit result."""
    PASSED = "passed"
    FAILED = "failed"
    NOT_AUDITED = "not_audited"


@dataclass
class SongInfo:
    """Information about a song in the catalog."""
    id: str
    artist: str
    title: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility with existing code."""
        return {"id": self.id, "artist": self.artist, "title": self.title}


@dataclass
class ContentItem:
    """A piece of generated content (script or audio).
    
    Represents a single generated item such as a song intro script,
    time announcement, or weather report.
    """
    content_type: ContentType
    dj: DJ
    script_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    script_text: Optional[str] = None
    
    # For song-based content
    song: Optional[SongInfo] = None
    
    # For time announcements
    hour: Optional[int] = None
    minute: Optional[int] = None
    
    # For weather announcements
    weather_hour: Optional[int] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    version: int = 0
    
    @property
    def has_script(self) -> bool:
        """Check if script file exists."""
        return self.script_path is not None and self.script_path.exists()
    
    @property
    def has_audio(self) -> bool:
        """Check if audio file exists."""
        return self.audio_path is not None and self.audio_path.exists()
    
    @property
    def display_name(self) -> str:
        """Human-readable name for this content item."""
        if self.content_type == ContentType.TIME:
            return f"Time {self.hour:02d}:{self.minute:02d}"
        elif self.content_type == ContentType.WEATHER:
            return f"Weather {self.weather_hour:02d}:00"
        elif self.song:
            type_label = "Intro" if self.content_type == ContentType.INTRO else "Outro"
            return f"{type_label}: {self.song.artist} - {self.song.title}"
        return f"Unknown content"


@dataclass
class GenerationResult:
    """Result of a content generation operation.
    
    Contains the outcome of generating a script or audio file,
    including success/failure status, the generated text, and any errors.
    """
    success: bool
    content_type: ContentType
    dj: DJ
    text: Optional[str] = None
    audio_path: Optional[Path] = None
    script_path: Optional[Path] = None
    error: Optional[str] = None
    
    # For song-based content
    song: Optional[SongInfo] = None
    
    # For time/weather
    hour: Optional[int] = None
    minute: Optional[int] = None


@dataclass
class AuditResult:
    """Result of auditing a script.
    
    Contains the audit scores, issues found, and pass/fail status
    from the LLM auditor evaluation.
    """
    script_id: str
    dj: DJ
    content_type: ContentType
    passed: bool
    score: float
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    notes: str = ""
    audit_path: Optional[Path] = None
    audited_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], audit_path: Optional[Path] = None) -> "AuditResult":
        """Create AuditResult from dictionary (e.g., loaded from JSON)."""
        # Map string content type to enum
        content_type_str = data.get("content_type", "intro")
        if "intro" in content_type_str.lower():
            content_type = ContentType.INTRO
        elif "outro" in content_type_str.lower():
            content_type = ContentType.OUTRO
        elif "time" in content_type_str.lower():
            content_type = ContentType.TIME
        elif "weather" in content_type_str.lower():
            content_type = ContentType.WEATHER
        else:
            content_type = ContentType.INTRO
        
        # Map DJ string to enum
        dj_str = data.get("dj", "julie").lower()
        dj = DJ.JULIE if dj_str == "julie" else DJ.MR_NEW_VEGAS
        
        return cls(
            script_id=data.get("script_id", ""),
            dj=dj,
            content_type=content_type,
            passed=data.get("passed", False),
            score=data.get("score", 0.0),
            criteria_scores=data.get("criteria_scores", {}),
            issues=data.get("issues", []),
            notes=data.get("notes", ""),
            audit_path=audit_path,
        )


@dataclass
class ReviewItem:
    """An item in the review queue awaiting human approval.
    
    Contains a content item and its current review status for
    the human-in-the-loop approval workflow.
    """
    content: ContentItem
    audit_result: Optional[AuditResult] = None
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_notes: str = ""
    reviewed_at: Optional[datetime] = None
    regeneration_count: int = 0
    
    @property
    def needs_review(self) -> bool:
        """Check if this item needs human review."""
        return self.status == ReviewStatus.PENDING


@dataclass
class ContentFilter:
    """Filter parameters for content queries.
    
    Used to filter content listings by various criteria.
    """
    dj: Optional[DJ] = None
    content_type: Optional[ContentType] = None
    has_script: Optional[bool] = None
    has_audio: Optional[bool] = None
    audit_status: Optional[AuditStatus] = None
    
    # For song filtering
    artist: Optional[str] = None
    title: Optional[str] = None


@dataclass  
class AuditFilter:
    """Filter parameters for audit result queries."""
    dj: Optional[DJ] = None
    content_type: Optional[ContentType] = None
    passed: Optional[bool] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None


@dataclass
class PipelineStatus:
    """Current status of the generation pipeline.
    
    Provides an overview of what content has been generated,
    audited, and approved across all DJs and content types.
    """
    generate_completed: bool = False
    audit_completed: bool = False
    audio_completed: bool = False
    
    scripts_generated: int = 0
    scripts_audited: int = 0
    scripts_passed: int = 0
    scripts_failed: int = 0
    audio_files_generated: int = 0
    
    current_stage: Optional[str] = None
    run_id: Optional[str] = None
    last_updated: Optional[datetime] = None
