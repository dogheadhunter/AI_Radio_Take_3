"""Tests for GUI utility modules.

Tests diff rendering, version management, and component helpers.
"""
import pytest
import json
from pathlib import Path
from datetime import datetime

from src.ai_radio.gui.diff import render_diff, render_inline_diff, get_diff_stats
from src.ai_radio.gui.version import (
    VersionInfo,
    VersionMetadata,
    VersionManager,
    VersionType,
    get_version_info,
    create_new_version,
)


class TestDiffRendering:
    """Test diff rendering utilities."""
    
    @pytest.mark.mock
    def test_render_diff_basic(self):
        """Test basic diff rendering produces HTML."""
        old = "Hello world\nThis is a test"
        new = "Hello world\nThis is modified"
        
        html = render_diff(old, new)
        
        assert "<table" in html
        assert "Previous Version" in html
        assert "Current Version" in html
    
    @pytest.mark.mock
    def test_render_diff_identical(self):
        """Test diff rendering with identical text."""
        text = "Same text\nNo changes"
        
        html = render_diff(text, text)
        
        # Should still produce valid HTML
        assert "<table" in html
    
    @pytest.mark.mock
    def test_render_inline_diff_additions(self):
        """Test inline diff shows additions in green."""
        old = "Line 1"
        new = "Line 1\nLine 2"
        
        html = render_inline_diff(old, new)
        
        assert "+Line 2" in html
        assert "16a34a" in html  # Green color code (text color for additions)
    
    @pytest.mark.mock
    def test_render_inline_diff_deletions(self):
        """Test inline diff shows deletions in red."""
        old = "Line 1\nLine 2"
        new = "Line 1"
        
        html = render_inline_diff(old, new)
        
        assert "-Line 2" in html
        assert "dc2626" in html  # Red color code (text color for deletions)
    
    @pytest.mark.mock
    def test_get_diff_stats(self):
        """Test diff statistics calculation."""
        old = "Line 1\nLine 2\nLine 3"
        new = "Line 1\nModified\nLine 3\nLine 4"
        
        additions, deletions = get_diff_stats(old, new)
        
        # "Line 2" deleted, "Modified" and "Line 4" added
        assert additions == 2
        assert deletions == 1
    
    @pytest.mark.mock
    def test_get_diff_stats_no_changes(self):
        """Test diff stats with no changes."""
        text = "Same text"
        
        additions, deletions = get_diff_stats(text, text)
        
        assert additions == 0
        assert deletions == 0


class TestVersionInfo:
    """Test VersionInfo dataclass."""
    
    @pytest.mark.mock
    def test_version_info_creation(self):
        """Test creating a VersionInfo object."""
        info = VersionInfo(
            version=0,
            version_type=VersionType.ORIGINAL,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        
        assert info.version == 0
        assert info.version_type == VersionType.ORIGINAL
        assert info.script_path is None
        assert info.audio_path is None
    
    @pytest.mark.mock
    def test_version_info_to_dict(self):
        """Test converting VersionInfo to dict."""
        info = VersionInfo(
            version=1,
            version_type=VersionType.MANUAL_EDIT,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
            notes="Test edit",
        )
        
        data = info.to_dict()
        
        assert data["version"] == 1
        assert data["type"] == "manual_edit"
        assert "2026-01-01" in data["created_at"]
        assert data["notes"] == "Test edit"
    
    @pytest.mark.mock
    def test_version_info_from_dict(self):
        """Test creating VersionInfo from dict."""
        data = {
            "version": 2,
            "type": "regenerated",
            "created_at": "2026-01-01T12:00:00",
            "notes": "Regenerated with feedback",
        }
        
        info = VersionInfo.from_dict(data)
        
        assert info.version == 2
        assert info.version_type == VersionType.REGENERATED
        assert info.notes == "Regenerated with feedback"


class TestVersionMetadata:
    """Test VersionMetadata dataclass."""
    
    @pytest.mark.mock
    def test_metadata_creation(self):
        """Test creating VersionMetadata."""
        metadata = VersionMetadata()
        
        assert metadata.versions == []
        assert metadata.current_version == 0
        assert metadata.status == "pending"
    
    @pytest.mark.mock
    def test_metadata_to_dict(self):
        """Test converting VersionMetadata to dict."""
        info = VersionInfo(
            version=0,
            version_type=VersionType.ORIGINAL,
            created_at=datetime.now(),
        )
        metadata = VersionMetadata(
            versions=[info],
            current_version=0,
            status="approved",
        )
        
        data = metadata.to_dict()
        
        assert len(data["versions"]) == 1
        assert data["current_version"] == 0
        assert data["status"] == "approved"
    
    @pytest.mark.mock
    def test_metadata_from_dict(self):
        """Test creating VersionMetadata from dict."""
        data = {
            "versions": [
                {
                    "version": 0,
                    "type": "original",
                    "created_at": "2026-01-01T10:00:00",
                },
                {
                    "version": 1,
                    "type": "manual_edit",
                    "created_at": "2026-01-01T11:00:00",
                },
            ],
            "current_version": 1,
            "status": "pending",
        }
        
        metadata = VersionMetadata.from_dict(data)
        
        assert len(metadata.versions) == 2
        assert metadata.current_version == 1
        assert metadata.versions[1].version_type == VersionType.MANUAL_EDIT


class TestVersionManager:
    """Test VersionManager class."""
    
    @pytest.fixture
    def version_manager(self, tmp_path):
        """Create a VersionManager with a test folder."""
        folder = tmp_path / "test_item"
        folder.mkdir()
        
        # Create initial version files
        (folder / "julie_0.txt").write_text("Original script", encoding='utf-8')
        (folder / "julie_0.wav").write_bytes(b"RIFF....WAVEfmt ")
        
        return VersionManager(folder, "julie", "intros")
    
    @pytest.mark.mock
    def test_load_metadata_detects_versions(self, version_manager):
        """Test loading metadata detects existing files."""
        metadata = version_manager.load_metadata()
        
        assert len(metadata.versions) == 1
        assert metadata.versions[0].version == 0
        assert metadata.current_version == 0
    
    @pytest.mark.mock
    def test_create_version(self, version_manager):
        """Test creating a new version."""
        version_info = version_manager.create_version(
            script_text="Edited script content",
            version_type=VersionType.MANUAL_EDIT,
            notes="Manual edit by user",
        )
        
        assert version_info.version == 1
        assert version_info.version_type == VersionType.MANUAL_EDIT
        assert version_info.script_path.exists()
        assert version_info.script_path.read_text() == "Edited script content"
    
    @pytest.mark.mock
    def test_create_version_preserves_history(self, version_manager):
        """Test that creating versions preserves history."""
        # Create first edit
        version_manager.create_version("Edit 1", VersionType.MANUAL_EDIT)
        
        # Create second edit
        version_manager.create_version("Edit 2", VersionType.MANUAL_EDIT)
        
        # Verify all versions exist
        versions = version_manager.list_versions()
        assert len(versions) == 3  # Original + 2 edits
        
        # Verify files exist
        assert (version_manager.folder_path / "julie_0.txt").exists()
        assert (version_manager.folder_path / "julie_1.txt").exists()
        assert (version_manager.folder_path / "julie_2.txt").exists()
    
    @pytest.mark.mock
    def test_get_script_path(self, version_manager):
        """Test getting script path for version."""
        path_v0 = version_manager.get_script_path(0)
        path_v1 = version_manager.get_script_path(1)
        
        assert path_v0.name == "julie_0.txt"
        assert path_v1.name == "julie_1.txt"
    
    @pytest.mark.mock
    def test_get_current_version(self, version_manager):
        """Test getting current version info."""
        current = version_manager.get_current_version()
        
        assert current is not None
        assert current.version == 0
    
    @pytest.mark.mock
    def test_outro_naming_convention(self, tmp_path):
        """Test version manager handles outro naming."""
        folder = tmp_path / "outro_item"
        folder.mkdir()
        
        # Create outro files with different naming
        (folder / "julie_outro.txt").write_text("Outro v0", encoding='utf-8')
        (folder / "julie_outro_1.txt").write_text("Outro v1", encoding='utf-8')
        
        manager = VersionManager(folder, "julie", "outros")
        metadata = manager.load_metadata()
        
        assert len(metadata.versions) == 2
        assert metadata.current_version == 1


class TestVersionHelperFunctions:
    """Test convenience functions."""
    
    @pytest.mark.mock
    def test_get_version_info(self, tmp_path):
        """Test get_version_info helper."""
        folder = tmp_path / "item"
        folder.mkdir()
        (folder / "mr_new_vegas_0.txt").write_text("Test", encoding='utf-8')
        
        metadata = get_version_info(folder, "mr_new_vegas", "intros")
        
        assert metadata.current_version == 0
        assert len(metadata.versions) == 1
    
    @pytest.mark.mock
    def test_create_new_version_helper(self, tmp_path):
        """Test create_new_version helper."""
        folder = tmp_path / "item"
        folder.mkdir()
        (folder / "julie_0.txt").write_text("Original", encoding='utf-8')
        
        version_info = create_new_version(
            folder,
            "julie",
            "intros",
            "New content",
            VersionType.MANUAL_EDIT,
            "User edit",
        )
        
        assert version_info.version == 1
        assert version_info.notes == "User edit"
        assert (folder / "julie_1.txt").read_text() == "New content"


class TestVersionManagerEdgeCases:
    """Test edge cases in version management."""
    
    @pytest.mark.mock
    def test_empty_folder(self, tmp_path):
        """Test version manager with empty folder."""
        folder = tmp_path / "empty"
        folder.mkdir()
        
        manager = VersionManager(folder, "julie", "intros")
        metadata = manager.load_metadata()
        
        assert len(metadata.versions) == 0
        assert metadata.current_version == 0
    
    @pytest.mark.mock
    def test_save_and_reload_metadata(self, tmp_path):
        """Test metadata survives save/reload cycle."""
        folder = tmp_path / "item"
        folder.mkdir()
        (folder / "julie_0.txt").write_text("Script", encoding='utf-8')
        
        manager = VersionManager(folder, "julie", "intros")
        
        # Create a version
        manager.create_version("Edit", VersionType.MANUAL_EDIT, "Note")
        
        # Create new manager instance and reload
        manager2 = VersionManager(folder, "julie", "intros")
        metadata = manager2.load_metadata()
        
        assert len(metadata.versions) == 2
        assert metadata.current_version == 1
        assert metadata.versions[1].notes == "Note"
    
    @pytest.mark.mock
    def test_legacy_metadata_conversion(self, tmp_path):
        """Test loading legacy format metadata."""
        folder = tmp_path / "item"
        folder.mkdir()
        (folder / "julie_0.txt").write_text("Script", encoding='utf-8')
        
        # Write legacy format metadata
        legacy_data = {
            "status": "approved",
            "reviewed_at": "2026-01-01T12:00:00",
            "reviewer_notes": "Good script",
        }
        (folder / "review_status.json").write_text(
            json.dumps(legacy_data), encoding='utf-8'
        )
        
        manager = VersionManager(folder, "julie", "intros")
        metadata = manager.load_metadata()
        
        # Should detect file-based version and preserve legacy status
        assert len(metadata.versions) >= 1
        assert metadata.status == "approved"
