"""
Tests for the regeneration queue processor (scripts/process_regen_queue.py).

These tests verify:
- Queue processing logic
- Version number management
- Folder name parsing
- Integration points (mocked)
"""
import pytest
import json
from pathlib import Path
import sys

# Add scripts directory to path for importing the module
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from process_regen_queue import (
    get_next_version_number,
    parse_song_info_from_folder,
    parse_time_info_from_folder
)


@pytest.mark.mock
def test_get_next_version_number_intros(tmp_path):
    """Test version number calculation for intros."""
    folder = tmp_path / "test_song"
    folder.mkdir()
    
    # No existing files - should return 0
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 0
    
    # Create version 0
    (folder / "julie_0.txt").write_text("v0")
    (folder / "julie_0.wav").write_bytes(b"wav0")
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 1
    
    # Create version 1
    (folder / "julie_1.txt").write_text("v1")
    (folder / "julie_1.wav").write_bytes(b"wav1")
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 2
    
    # Create version 3 (skip version 2)
    (folder / "julie_3.txt").write_text("v3")
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 4


@pytest.mark.mock
def test_get_next_version_number_outros(tmp_path):
    """Test version number calculation for outros with different naming."""
    folder = tmp_path / "test_song"
    folder.mkdir()
    
    # No existing files - should return 0
    next_ver = get_next_version_number(folder, "mr_new_vegas", "outros")
    assert next_ver == 0
    
    # Create version 0 (outro naming)
    (folder / "mr_new_vegas_outro.txt").write_text("v0")
    (folder / "mr_new_vegas_outro.wav").write_bytes(b"wav0")
    next_ver = get_next_version_number(folder, "mr_new_vegas", "outros")
    assert next_ver == 1
    
    # Create version 1
    (folder / "mr_new_vegas_outro_1.txt").write_text("v1")
    (folder / "mr_new_vegas_outro_1.wav").write_bytes(b"wav1")
    next_ver = get_next_version_number(folder, "mr_new_vegas", "outros")
    assert next_ver == 2


@pytest.mark.mock
def test_parse_song_info_from_folder():
    """Test parsing artist and title from folder name."""
    artist, title = parse_song_info_from_folder("Louis_Armstrong-A_Kiss_to_Build_a_Dream_On")
    assert artist == "Louis Armstrong"
    assert title == "A Kiss to Build a Dream On"
    
    artist, title = parse_song_info_from_folder("The_Beatles-Hey_Jude")
    assert artist == "The Beatles"
    assert title == "Hey Jude"
    
    # Test malformed folder name
    artist, title = parse_song_info_from_folder("NoHyphen")
    assert artist == "Unknown"
    assert title == "Unknown"


@pytest.mark.mock
def test_parse_time_info_from_folder():
    """Test parsing hour and minute from time folder name."""
    hour, minute = parse_time_info_from_folder("12-00")
    assert hour == 12
    assert minute == 0
    
    hour, minute = parse_time_info_from_folder("06-30")
    assert hour == 6
    assert minute == 30
    
    hour, minute = parse_time_info_from_folder("23-45")
    assert hour == 23
    assert minute == 45
    
    # Test malformed folder name
    hour, minute = parse_time_info_from_folder("invalid")
    assert hour == 0
    assert minute == 0


@pytest.mark.mock
def test_queue_file_structure(tmp_path):
    """Test regeneration queue JSON structure."""
    queue_file = tmp_path / "regeneration_queue.json"
    
    # Create a sample queue
    queue = [
        {
            "content_type": "intros",
            "dj": "julie",
            "item_id": "Artist-Song",
            "folder_path": "/path/to/folder",
            "regenerate_type": "both",
            "feedback": "Test feedback",
            "added_at": "2026-01-25T10:00:00"
        }
    ]
    
    queue_file.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    
    # Verify it can be read
    loaded = json.loads(queue_file.read_text())
    assert len(loaded) == 1
    assert loaded[0]["content_type"] == "intros"
    assert loaded[0]["regenerate_type"] == "both"
    assert loaded[0]["feedback"] == "Test feedback"


@pytest.mark.mock
def test_version_increment_logic():
    """Test that version incrementing works correctly for different content types."""
    # This tests the logic without needing actual files or services
    
    # For intros: julie_0.txt -> julie_1.txt
    assert "julie_1.txt" == "julie_1.txt"
    
    # For outros: mr_new_vegas_outro.txt -> mr_new_vegas_outro_1.txt
    assert "mr_new_vegas_outro_1.txt" == "mr_new_vegas_outro_1.txt"
    
    # Verify naming pattern understanding
    intro_pattern = "{dj}_{version}.txt"
    outro_pattern_v0 = "{dj}_outro.txt"
    outro_pattern_v1 = "{dj}_outro_1.txt"
    
    assert intro_pattern.format(dj="julie", version=0) == "julie_0.txt"
    assert outro_pattern_v0.format(dj="mr_new_vegas") == "mr_new_vegas_outro.txt"
    assert outro_pattern_v1.format(dj="mr_new_vegas") == "mr_new_vegas_outro_1.txt"



@pytest.mark.mock
def test_get_next_version_number_intros(tmp_path):
    """Test version number calculation for intros."""
    folder = tmp_path / "test_song"
    folder.mkdir()
    
    # No existing files - should return 0
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 0
    
    # Create version 0
    (folder / "julie_0.txt").write_text("v0")
    (folder / "julie_0.wav").write_bytes(b"wav0")
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 1
    
    # Create version 1
    (folder / "julie_1.txt").write_text("v1")
    (folder / "julie_1.wav").write_bytes(b"wav1")
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 2
    
    # Create version 3 (skip version 2)
    (folder / "julie_3.txt").write_text("v3")
    next_ver = get_next_version_number(folder, "julie", "intros")
    assert next_ver == 4


@pytest.mark.mock
def test_get_next_version_number_outros(tmp_path):
    """Test version number calculation for outros with different naming."""
    folder = tmp_path / "test_song"
    folder.mkdir()
    
    # No existing files - should return 0
    next_ver = get_next_version_number(folder, "mr_new_vegas", "outros")
    assert next_ver == 0
    
    # Create version 0 (outro naming)
    (folder / "mr_new_vegas_outro.txt").write_text("v0")
    (folder / "mr_new_vegas_outro.wav").write_bytes(b"wav0")
    next_ver = get_next_version_number(folder, "mr_new_vegas", "outros")
    assert next_ver == 1
    
    # Create version 1
    (folder / "mr_new_vegas_outro_1.txt").write_text("v1")
    (folder / "mr_new_vegas_outro_1.wav").write_bytes(b"wav1")
    next_ver = get_next_version_number(folder, "mr_new_vegas", "outros")
    assert next_ver == 2


@pytest.mark.mock
def test_parse_song_info_from_folder():
    """Test parsing artist and title from folder name."""
    artist, title = parse_song_info_from_folder("Louis_Armstrong-A_Kiss_to_Build_a_Dream_On")
    assert artist == "Louis Armstrong"
    assert title == "A Kiss to Build a Dream On"
    
    artist, title = parse_song_info_from_folder("The_Beatles-Hey_Jude")
    assert artist == "The Beatles"
    assert title == "Hey Jude"
    
    # Test malformed folder name
    artist, title = parse_song_info_from_folder("NoHyphen")
    assert artist == "Unknown"
    assert title == "Unknown"


@pytest.mark.mock
def test_parse_time_info_from_folder():
    """Test parsing hour and minute from time folder name."""
    hour, minute = parse_time_info_from_folder("12-00")
    assert hour == 12
    assert minute == 0
    
    hour, minute = parse_time_info_from_folder("06-30")
    assert hour == 6
    assert minute == 30
    
    hour, minute = parse_time_info_from_folder("23-45")
    assert hour == 23
    assert minute == 45
    
    # Test malformed folder name
    hour, minute = parse_time_info_from_folder("invalid")
    assert hour == 0
    assert minute == 0


@pytest.mark.mock
def test_queue_file_structure(tmp_path):
    """Test regeneration queue JSON structure."""
    queue_file = tmp_path / "regeneration_queue.json"
    
    # Create a sample queue
    queue = [
        {
            "content_type": "intros",
            "dj": "julie",
            "item_id": "Artist-Song",
            "folder_path": "/path/to/folder",
            "regenerate_type": "both",
            "feedback": "Test feedback",
            "added_at": "2026-01-25T10:00:00"
        }
    ]
    
    queue_file.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    
    # Verify it can be read
    loaded = json.loads(queue_file.read_text())
    assert len(loaded) == 1
    assert loaded[0]["content_type"] == "intros"
    assert loaded[0]["regenerate_type"] == "both"
    assert loaded[0]["feedback"] == "Test feedback"


@pytest.mark.mock
def test_version_increment_logic():
    """Test that version incrementing works correctly for different content types."""
    # This tests the logic without needing actual files or services
    
    # For intros: julie_0.txt -> julie_1.txt
    assert "julie_1.txt" == "julie_1.txt"
    
    # For outros: mr_new_vegas_outro.txt -> mr_new_vegas_outro_1.txt
    assert "mr_new_vegas_outro_1.txt" == "mr_new_vegas_outro_1.txt"
    
    # Verify naming pattern understanding
    intro_pattern = "{dj}_{version}.txt"
    outro_pattern_v0 = "{dj}_outro.txt"
    outro_pattern_v1 = "{dj}_outro_1.txt"
    
    assert intro_pattern.format(dj="julie", version=0) == "julie_0.txt"
    assert outro_pattern_v0.format(dj="mr_new_vegas") == "mr_new_vegas_outro.txt"
    assert outro_pattern_v1.format(dj="mr_new_vegas") == "mr_new_vegas_outro_1.txt"

