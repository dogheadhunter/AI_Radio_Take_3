"""Version management utilities for AI Radio content.

Provides helpers for managing script and audio versions with metadata,
supporting the versioned file naming convention: {dj}_{version}.txt/wav
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class VersionType(str, Enum):
    """Type of content version."""
    ORIGINAL = "original"
    REGENERATED = "regenerated"
    MANUAL_EDIT = "manual_edit"
    AUDIO_ONLY = "audio_only"


@dataclass
class VersionInfo:
    """Information about a content version.
    
    Attributes:
        version: Version number (0, 1, 2, ...)
        version_type: How this version was created
        created_at: When this version was created
        script_path: Path to script file (if exists)
        audio_path: Path to audio file (if exists)
        notes: Optional notes about this version
    """
    version: int
    version_type: VersionType
    created_at: datetime
    script_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    notes: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "type": self.version_type.value,
            "created_at": self.created_at.isoformat(),
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VersionInfo":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            version_type=VersionType(data.get("type", "original")),
            created_at=datetime.fromisoformat(data["created_at"]),
            notes=data.get("notes", ""),
        )


@dataclass
class VersionMetadata:
    """Metadata for all versions of a content item.
    
    Stored in review_status.json alongside version files.
    """
    versions: List[VersionInfo] = field(default_factory=list)
    current_version: int = 0
    status: str = "pending"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "versions": [v.to_dict() for v in self.versions],
            "current_version": self.current_version,
            "status": self.status,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VersionMetadata":
        """Create from dictionary."""
        versions = [
            VersionInfo.from_dict(v)
            for v in data.get("versions", [])
        ]
        return cls(
            versions=versions,
            current_version=data.get("current_version", 0),
            status=data.get("status", "pending"),
        )


class VersionManager:
    """Manages versions for a content item folder.
    
    Handles reading/writing version metadata and creating new versions
    while preserving the full version history.
    """
    
    def __init__(self, folder_path: Path, dj: str, content_type: str = "intros"):
        """Initialize version manager for a content folder.
        
        Args:
            folder_path: Path to the content item folder
            dj: DJ name (julie, mr_new_vegas)
            content_type: Content type (intros, outros, time, weather)
        """
        self.folder_path = Path(folder_path)
        self.dj = dj
        self.content_type = content_type
        self._metadata_path = self.folder_path / "review_status.json"
    
    def load_metadata(self) -> VersionMetadata:
        """Load version metadata from file."""
        if not self._metadata_path.exists():
            # Initialize with detected versions
            return self._detect_versions()
        
        try:
            with open(self._metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if has new version format
            if "versions" in data:
                metadata = VersionMetadata.from_dict(data)
            else:
                # Legacy format - convert
                metadata = self._detect_versions()
                metadata.status = data.get("status", "pending")
            
            return metadata
        except (json.JSONDecodeError, KeyError):
            return self._detect_versions()
    
    def save_metadata(self, metadata: VersionMetadata):
        """Save version metadata to file."""
        self.folder_path.mkdir(parents=True, exist_ok=True)
        
        # Merge with existing review_status.json if present
        existing = {}
        if self._metadata_path.exists():
            try:
                with open(self._metadata_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Update with version info while preserving other fields
        existing.update(metadata.to_dict())
        
        with open(self._metadata_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    
    def _detect_versions(self) -> VersionMetadata:
        """Detect versions from existing files in folder."""
        versions = []
        max_version = -1
        
        if not self.folder_path.exists():
            return VersionMetadata()
        
        # Scan for script files
        pattern = f"{self.dj}_*.txt" if self.content_type != "outros" else f"{self.dj}_outro*.txt"
        script_files = list(self.folder_path.glob(pattern))
        
        for script_path in script_files:
            version_num = self._extract_version_from_path(script_path)
            if version_num is not None:
                # Check for corresponding audio
                audio_path = self._get_audio_path_for_version(version_num)
                
                version = VersionInfo(
                    version=version_num,
                    version_type=VersionType.ORIGINAL if version_num == 0 else VersionType.REGENERATED,
                    created_at=datetime.fromtimestamp(script_path.stat().st_mtime),
                    script_path=script_path,
                    audio_path=audio_path if audio_path and audio_path.exists() else None,
                )
                versions.append(version)
                max_version = max(max_version, version_num)
        
        versions.sort(key=lambda v: v.version)
        
        return VersionMetadata(
            versions=versions,
            current_version=max_version if max_version >= 0 else 0,
        )
    
    def _extract_version_from_path(self, path: Path) -> Optional[int]:
        """Extract version number from file path."""
        stem = path.stem
        parts = stem.split('_')
        
        if self.content_type == "outros":
            # outro naming: dj_outro, dj_outro_1, dj_outro_2
            if len(parts) >= 2 and parts[-1] == "outro":
                return 0
            elif len(parts) >= 3 and parts[-2] == "outro":
                try:
                    return int(parts[-1])
                except ValueError:
                    return None
        else:
            # Standard naming: dj_0, dj_1, dj_2
            try:
                return int(parts[-1])
            except ValueError:
                return None
        
        return None
    
    def _get_audio_path_for_version(self, version: int) -> Optional[Path]:
        """Get the audio file path for a specific version."""
        if self.content_type == "outros":
            if version == 0:
                candidates = [
                    self.folder_path / f"{self.dj}_outro.wav",
                    self.folder_path / f"{self.dj}_0_full.wav",
                    self.folder_path / f"{self.dj}_0.wav",
                ]
            else:
                candidates = [
                    self.folder_path / f"{self.dj}_outro_{version}.wav",
                    self.folder_path / f"{self.dj}_{version}_full.wav",
                    self.folder_path / f"{self.dj}_{version}.wav",
                ]
        else:
            candidates = [
                self.folder_path / f"{self.dj}_{version}_full.wav",
                self.folder_path / f"{self.dj}_{version}.wav",
            ]
        
        for path in candidates:
            if path.exists():
                return path
        return None
    
    def get_script_path(self, version: int) -> Path:
        """Get the script file path for a specific version."""
        if self.content_type == "outros":
            if version == 0:
                return self.folder_path / f"{self.dj}_outro.txt"
            else:
                return self.folder_path / f"{self.dj}_outro_{version}.txt"
        else:
            return self.folder_path / f"{self.dj}_{version}.txt"
    
    def get_audio_path(self, version: int) -> Path:
        """Get the audio file path for a specific version."""
        # Return the "full" audio path for new versions
        return self.folder_path / f"{self.dj}_{version}_full.wav"
    
    def get_current_version(self) -> Optional[VersionInfo]:
        """Get the current (latest) version info."""
        metadata = self.load_metadata()
        for v in metadata.versions:
            if v.version == metadata.current_version:
                return v
        return None
    
    def get_version(self, version: int) -> Optional[VersionInfo]:
        """Get info for a specific version."""
        metadata = self.load_metadata()
        for v in metadata.versions:
            if v.version == version:
                return v
        return None
    
    def list_versions(self) -> List[VersionInfo]:
        """Get all versions in order."""
        metadata = self.load_metadata()
        return sorted(metadata.versions, key=lambda v: v.version)
    
    def create_version(
        self,
        script_text: str,
        version_type: VersionType,
        notes: str = "",
    ) -> VersionInfo:
        """Create a new version with the given script text.
        
        Args:
            script_text: The script content for the new version
            version_type: How this version was created
            notes: Optional notes about this version
            
        Returns:
            VersionInfo for the newly created version
        """
        metadata = self.load_metadata()
        
        # Determine next version number
        new_version = metadata.current_version + 1
        
        # Create script file
        script_path = self.get_script_path(new_version)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script_text, encoding='utf-8')
        
        # Create version info
        version_info = VersionInfo(
            version=new_version,
            version_type=version_type,
            created_at=datetime.now(),
            script_path=script_path,
            notes=notes,
        )
        
        # Update metadata
        metadata.versions.append(version_info)
        metadata.current_version = new_version
        self.save_metadata(metadata)
        
        return version_info
    
    def set_audio_path(self, version: int, audio_path: Path):
        """Set the audio path for a version after audio generation."""
        metadata = self.load_metadata()
        
        for v in metadata.versions:
            if v.version == version:
                v.audio_path = audio_path
                break
        
        self.save_metadata(metadata)


def get_version_info(folder_path: Path, dj: str, content_type: str = "intros") -> VersionMetadata:
    """Convenience function to get version metadata for a folder.
    
    Args:
        folder_path: Path to the content item folder
        dj: DJ name
        content_type: Content type
        
    Returns:
        VersionMetadata with all version information
    """
    manager = VersionManager(folder_path, dj, content_type)
    return manager.load_metadata()


def create_new_version(
    folder_path: Path,
    dj: str,
    content_type: str,
    script_text: str,
    version_type: VersionType = VersionType.MANUAL_EDIT,
    notes: str = "",
) -> VersionInfo:
    """Convenience function to create a new version.
    
    Args:
        folder_path: Path to the content item folder
        dj: DJ name
        content_type: Content type
        script_text: Script content for new version
        version_type: How this version was created
        notes: Optional notes
        
    Returns:
        VersionInfo for the newly created version
    """
    manager = VersionManager(folder_path, dj, content_type)
    return manager.create_version(script_text, version_type, notes)
