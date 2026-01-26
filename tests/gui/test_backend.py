"""Tests for GUI backend service layer."""
import pytest
import json
from pathlib import Path

from src.ai_radio.gui.backend import (
    load_catalog,
    get_song_generation_status,
    regenerate_content,
    save_manual_edit,
    get_version_metadata,
    get_script_text,
    get_audit_status,
    _parse_song_from_item_id,
    _parse_time_from_item_id,
)
from src.ai_radio.api.schemas import SongInfo


class TestParseFunctions:
    """Test parsing helper functions."""
    
    @pytest.mark.mock
    def test_parse_song_from_item_id(self):
        """Test parsing song info from item_id."""
        artist, title = _parse_song_from_item_id("Johnny_Cash-Ring_of_Fire")
        
        assert artist == "Johnny Cash"
        assert title == "Ring of Fire"
    
    @pytest.mark.mock
    def test_parse_song_with_spaces(self):
        """Test parsing song with underscores as spaces."""
        artist, title = _parse_song_from_item_id("The_Rolling_Stones-Paint_It_Black")
        
        assert artist == "The Rolling Stones"
        assert title == "Paint It Black"
    
    @pytest.mark.mock
    def test_parse_song_no_dash(self):
        """Test parsing when no dash in item_id."""
        artist, title = _parse_song_from_item_id("Unknown_Song")
        
        assert artist == "Unknown Song"
        assert title == ""
    
    @pytest.mark.mock
    def test_parse_time_from_item_id(self):
        """Test parsing time from item_id."""
        hour, minute = _parse_time_from_item_id("12-30")
        
        assert hour == 12
        assert minute == 30
    
    @pytest.mark.mock
    def test_parse_time_zero_padded(self):
        """Test parsing zero-padded time."""
        hour, minute = _parse_time_from_item_id("08-00")
        
        assert hour == 8
        assert minute == 0
    
    @pytest.mark.mock
    def test_parse_time_invalid(self):
        """Test parsing invalid time."""
        hour, minute = _parse_time_from_item_id("not-a-time")
        
        assert hour is None
        assert minute is None


class TestSaveManualEdit:
    """Test manual edit saving."""
    
    @pytest.mark.mock
    def test_save_manual_edit_creates_version(self, tmp_path):
        """Test that manual edit creates a new version."""
        folder = tmp_path / "test_song"
        folder.mkdir()
        
        # Create initial version
        (folder / "julie_0.txt").write_text("Original script", encoding='utf-8')
        
        # Save manual edit
        success, version_info = save_manual_edit(
            folder, "julie", "intros", "Edited script", "User edit"
        )
        
        assert success is True
        assert version_info is not None
        assert version_info.version == 1
        
        # Verify file was created
        assert (folder / "julie_1.txt").exists()
        assert (folder / "julie_1.txt").read_text() == "Edited script"
    
    @pytest.mark.mock
    def test_save_manual_edit_preserves_original(self, tmp_path):
        """Test that original version is preserved."""
        folder = tmp_path / "test_song"
        folder.mkdir()
        
        original = "Original script content"
        (folder / "julie_0.txt").write_text(original, encoding='utf-8')
        
        # Save edit
        save_manual_edit(folder, "julie", "intros", "New content", "")
        
        # Original should still exist and be unchanged
        assert (folder / "julie_0.txt").read_text() == original


class TestGetVersionMetadata:
    """Test version metadata retrieval."""
    
    @pytest.mark.mock
    def test_get_version_metadata(self, tmp_path):
        """Test getting version metadata."""
        folder = tmp_path / "test_song"
        folder.mkdir()
        
        (folder / "julie_0.txt").write_text("V0", encoding='utf-8')
        (folder / "julie_1.txt").write_text("V1", encoding='utf-8')
        
        metadata = get_version_metadata(folder, "julie", "intros")
        
        assert len(metadata.versions) == 2
        assert metadata.current_version == 1


class TestGetScriptText:
    """Test script text retrieval."""
    
    @pytest.mark.mock
    def test_get_script_text(self, tmp_path):
        """Test getting script text for version."""
        folder = tmp_path / "test_song"
        folder.mkdir()
        
        (folder / "julie_0.txt").write_text("Version 0 content", encoding='utf-8')
        
        text = get_script_text(folder, "julie", "intros", 0)
        
        assert text == "Version 0 content"
    
    @pytest.mark.mock
    def test_get_script_text_not_found(self, tmp_path):
        """Test getting script text for non-existent version."""
        folder = tmp_path / "test_song"
        folder.mkdir()
        
        text = get_script_text(folder, "julie", "intros", 99)
        
        assert text is None


class TestGetAuditStatus:
    """Test audit status retrieval."""
    
    @pytest.mark.mock
    def test_get_audit_status_passed(self, tmp_path, monkeypatch):
        """Test getting passed audit status."""
        from src.ai_radio import config
        monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
        
        # Create passed audit file
        audit_dir = tmp_path / "audit" / "julie" / "passed"
        audit_dir.mkdir(parents=True)
        (audit_dir / "Test_Song_intro_audit.json").write_text('{"passed": true}')
        
        status = get_audit_status("intros", "julie", "Test_Song")
        
        assert status == "passed"
    
    @pytest.mark.mock
    def test_get_audit_status_failed(self, tmp_path, monkeypatch):
        """Test getting failed audit status."""
        from src.ai_radio import config
        monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
        
        # Create failed audit file
        audit_dir = tmp_path / "audit" / "julie" / "failed"
        audit_dir.mkdir(parents=True)
        (audit_dir / "Test_Song_intro_audit.json").write_text('{"passed": false}')
        
        status = get_audit_status("intros", "julie", "Test_Song")
        
        assert status == "failed"
    
    @pytest.mark.mock
    def test_get_audit_status_none(self, tmp_path, monkeypatch):
        """Test getting audit status when no audit exists."""
        from src.ai_radio import config
        monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
        
        status = get_audit_status("intros", "julie", "No_Audit")
        
        assert status is None
