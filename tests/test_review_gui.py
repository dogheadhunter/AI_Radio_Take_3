"""
Tests for the Review GUI module (review_gui.py).

These tests verify the core functionality of the review interface including:
- Scanning and discovering generated content
- Filtering and pagination
- Review status management
- Regeneration queue management
- CSV export
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
from review_gui import (
    ReviewItem,
    scan_generated_content,
    filter_items,
    load_review_status,
    save_review_status,
    get_audit_status,
    add_to_regen_queue,
    get_regen_queue_count,
    clear_regen_queue,
    export_reviews_to_csv,
    SCRIPT_ISSUES,
    AUDIO_ISSUES
)


@pytest.fixture
def sample_generated_content(tmp_path):
    """Create sample generated content structure for testing."""
    data_dir = tmp_path / "data"
    generated_dir = data_dir / "generated"
    audit_dir = data_dir / "audit"
    
    # Create intro
    intro_folder = generated_dir / "intros" / "julie" / "Test_Artist-Test_Song"
    intro_folder.mkdir(parents=True)
    (intro_folder / "julie_0.txt").write_text("Test intro script", encoding='utf-8')
    (intro_folder / "julie_0.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create outro
    outro_folder = generated_dir / "outros" / "mr_new_vegas" / "Other_Artist-Other_Song"
    outro_folder.mkdir(parents=True)
    (outro_folder / "mr_new_vegas_outro.txt").write_text("Test outro script", encoding='utf-8')
    (outro_folder / "mr_new_vegas_outro.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create time announcement
    time_folder = generated_dir / "time" / "julie" / "12-00"
    time_folder.mkdir(parents=True)
    (time_folder / "julie_0.txt").write_text("Test time script", encoding='utf-8')
    (time_folder / "julie_0.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create weather with multiple versions
    weather_folder = generated_dir / "weather" / "mr_new_vegas" / "06-00"
    weather_folder.mkdir(parents=True)
    (weather_folder / "mr_new_vegas_0.txt").write_text("Test weather v0", encoding='utf-8')
    (weather_folder / "mr_new_vegas_0.wav").write_bytes(b"RIFF....WAVEfmt ")
    (weather_folder / "mr_new_vegas_1.txt").write_text("Test weather v1", encoding='utf-8')
    (weather_folder / "mr_new_vegas_1.wav").write_bytes(b"RIFF....WAVEfmt ")
    
    # Create audit results
    audit_passed = audit_dir / "julie" / "passed"
    audit_passed.mkdir(parents=True)
    (audit_passed / "Test_Artist-Test_Song_intro_audit.json").write_text(
        json.dumps({"score": 8.5, "passed": True}), encoding='utf-8'
    )
    
    audit_failed = audit_dir / "julie" / "failed"
    audit_failed.mkdir(parents=True)
    (audit_failed / "12-00_time_audit.json").write_text(
        json.dumps({"score": 5.0, "passed": False}), encoding='utf-8'
    )
    
    # Create regeneration queue
    queue_file = data_dir / "regeneration_queue.json"
    queue_file.write_text("[]", encoding='utf-8')
    
    return {
        "data_dir": data_dir,
        "generated_dir": generated_dir,
        "audit_dir": audit_dir,
        "queue_file": queue_file
    }


@pytest.mark.mock
def test_scan_generated_content(sample_generated_content, monkeypatch):
    """Test scanning generated content directories."""
    # Patch the module-level constants
    import review_gui
    monkeypatch.setattr(review_gui, 'DATA_DIR', sample_generated_content['data_dir'])
    monkeypatch.setattr(review_gui, 'GENERATED_DIR', sample_generated_content['generated_dir'])
    monkeypatch.setattr(review_gui, 'AUDIT_DIR', sample_generated_content['audit_dir'])
    
    items = scan_generated_content()
    
    # Should find 4 items: intro, outro, time, weather
    assert len(items) == 4
    
    # Check item types
    content_types = [item.content_type for item in items]
    assert "intros" in content_types
    assert "outros" in content_types
    assert "time" in content_types
    assert "weather" in content_types
    
    # Check DJs
    djs = [item.dj for item in items]
    assert "julie" in djs
    assert "mr_new_vegas" in djs
    
    # Find weather item and check versions
    weather_item = next(item for item in items if item.content_type == "weather")
    assert weather_item.latest_version == 1
    assert len(weather_item.script_versions) == 2
    assert len(weather_item.audio_versions) == 2


@pytest.mark.mock
def test_review_item_version_paths(sample_generated_content, monkeypatch):
    """Test ReviewItem version path retrieval."""
    import review_gui
    monkeypatch.setattr(review_gui, 'DATA_DIR', sample_generated_content['data_dir'])
    monkeypatch.setattr(review_gui, 'GENERATED_DIR', sample_generated_content['generated_dir'])
    monkeypatch.setattr(review_gui, 'AUDIT_DIR', sample_generated_content['audit_dir'])
    
    items = scan_generated_content()
    weather_item = next(item for item in items if item.content_type == "weather")
    
    # Test getting specific versions
    v0_script = weather_item.get_script_path(0)
    v1_script = weather_item.get_script_path(1)
    
    assert v0_script is not None
    assert v1_script is not None
    assert v0_script.exists()
    assert v1_script.exists()
    assert "mr_new_vegas_0.txt" in str(v0_script)
    assert "mr_new_vegas_1.txt" in str(v1_script)
    
    # Test getting latest version (default)
    latest_script = weather_item.get_script_path()
    assert latest_script == v1_script


@pytest.mark.mock
def test_filter_items(sample_generated_content, monkeypatch):
    """Test item filtering functionality."""
    import review_gui
    monkeypatch.setattr(review_gui, 'DATA_DIR', sample_generated_content['data_dir'])
    monkeypatch.setattr(review_gui, 'GENERATED_DIR', sample_generated_content['generated_dir'])
    monkeypatch.setattr(review_gui, 'AUDIT_DIR', sample_generated_content['audit_dir'])
    
    # Mock session state
    class SessionState:
        filter_content_type = "All"
        filter_dj = "All"
        filter_audit_status = "All"
        filter_review_status = "All"
        search_query = ""
    
    import streamlit as st
    monkeypatch.setattr(st, 'session_state', SessionState())
    
    items = scan_generated_content()
    
    # Test no filtering
    filtered = filter_items(items)
    assert len(filtered) == 4
    
    # Test content type filter
    st.session_state.filter_content_type = "intros"
    filtered = filter_items(items)
    assert len(filtered) == 1
    assert filtered[0].content_type == "intros"
    
    # Test DJ filter
    st.session_state.filter_content_type = "All"
    st.session_state.filter_dj = "julie"
    filtered = filter_items(items)
    assert all(item.dj == "julie" for item in filtered)
    
    # Test audit status filter
    st.session_state.filter_dj = "All"
    st.session_state.filter_audit_status = "Passed"
    filtered = filter_items(items)
    assert all(item.audit_status == "passed" for item in filtered)
    
    # Test search query
    st.session_state.filter_audit_status = "All"
    st.session_state.search_query = "Test_Artist"
    filtered = filter_items(items)
    assert len(filtered) == 1
    assert "Test_Artist" in filtered[0].item_id


@pytest.mark.mock
def test_load_save_review_status(tmp_path):
    """Test loading and saving review status."""
    folder = tmp_path / "test_folder"
    folder.mkdir()
    
    # Test loading non-existent status (should return default)
    status = load_review_status(folder)
    assert status["status"] == "pending"
    assert status["reviewed_at"] is None
    assert status["script_issues"] == []
    assert status["audio_issues"] == []
    
    # Test saving status
    new_status = {
        "status": "rejected",
        "reviewed_at": datetime.now().isoformat(),
        "reviewer_notes": "Test notes",
        "script_issues": ["Character voice mismatch"],
        "audio_issues": ["Pacing issues"]
    }
    save_review_status(folder, new_status)
    
    # Test loading saved status
    loaded_status = load_review_status(folder)
    assert loaded_status["status"] == "rejected"
    assert loaded_status["reviewer_notes"] == "Test notes"
    assert "Character voice mismatch" in loaded_status["script_issues"]
    assert "Pacing issues" in loaded_status["audio_issues"]


@pytest.mark.mock
def test_get_audit_status(sample_generated_content, monkeypatch):
    """Test audit status retrieval."""
    import review_gui
    monkeypatch.setattr(review_gui, 'AUDIT_DIR', sample_generated_content['audit_dir'])
    
    # Test passed audit
    status = get_audit_status("intros", "julie", "Test_Artist-Test_Song")
    assert status == "passed"
    
    # Test failed audit
    status = get_audit_status("time", "julie", "12-00")
    assert status == "failed"
    
    # Test no audit (should return None)
    status = get_audit_status("outros", "mr_new_vegas", "Other_Artist-Other_Song")
    assert status is None


@pytest.mark.mock
def test_regeneration_queue(sample_generated_content, monkeypatch):
    """Test regeneration queue management."""
    import review_gui
    monkeypatch.setattr(review_gui, 'DATA_DIR', sample_generated_content['data_dir'])
    monkeypatch.setattr(review_gui, 'REGEN_QUEUE_FILE', sample_generated_content['queue_file'])
    
    # Test initial empty queue
    count = get_regen_queue_count()
    assert count == 0
    
    # Test adding items to queue
    item = ReviewItem(
        content_type="intros",
        dj="julie",
        item_id="Test_Artist-Test_Song",
        folder_path=Path("/test/path"),
        script_versions=[],
        audio_versions=[],
        latest_version=0
    )
    
    add_to_regen_queue(item, "script", "Test feedback")
    count = get_regen_queue_count()
    assert count == 1
    
    # Verify queue contents
    queue_data = json.loads(sample_generated_content['queue_file'].read_text())
    assert len(queue_data) == 1
    assert queue_data[0]["content_type"] == "intros"
    assert queue_data[0]["dj"] == "julie"
    assert queue_data[0]["regenerate_type"] == "script"
    assert queue_data[0]["feedback"] == "Test feedback"
    
    # Test adding another item
    add_to_regen_queue(item, "audio", "Audio feedback")
    count = get_regen_queue_count()
    assert count == 2
    
    # Test clearing queue
    clear_regen_queue()
    count = get_regen_queue_count()
    assert count == 0


@pytest.mark.mock
def test_export_reviews_to_csv(sample_generated_content, monkeypatch):
    """Test CSV export functionality."""
    import review_gui
    monkeypatch.setattr(review_gui, 'DATA_DIR', sample_generated_content['data_dir'])
    monkeypatch.setattr(review_gui, 'GENERATED_DIR', sample_generated_content['generated_dir'])
    monkeypatch.setattr(review_gui, 'AUDIT_DIR', sample_generated_content['audit_dir'])
    
    items = scan_generated_content()
    
    # Add some review status to items
    for item in items[:2]:
        status = {
            "status": "approved",
            "reviewed_at": datetime.now().isoformat(),
            "reviewer_notes": "Test approval",
            "script_issues": [],
            "audio_issues": []
        }
        save_review_status(item.folder_path, status)
    
    # Export to CSV
    df = export_reviews_to_csv(items)
    
    # Verify DataFrame structure
    assert len(df) == 4
    assert "content_type" in df.columns
    assert "dj" in df.columns
    assert "item_id" in df.columns
    assert "review_status" in df.columns
    assert "audit_status" in df.columns
    assert "script_issues" in df.columns
    assert "audio_issues" in df.columns
    assert "reviewer_notes" in df.columns
    
    # Verify data
    approved_count = (df["review_status"] == "approved").sum()
    assert approved_count == 2


@pytest.mark.mock
def test_failure_reason_categories():
    """Test that failure reason categories are properly defined."""
    # Verify script issues for each content type
    assert "intros" in SCRIPT_ISSUES
    assert "outros" in SCRIPT_ISSUES
    assert "time" in SCRIPT_ISSUES
    assert "weather" in SCRIPT_ISSUES
    
    # Verify each has reasonable issues
    assert len(SCRIPT_ISSUES["intros"]) > 0
    assert len(SCRIPT_ISSUES["time"]) > 0
    
    # Verify common issues exist
    assert "Character voice mismatch" in SCRIPT_ISSUES["intros"]
    assert "Character voice mismatch" in SCRIPT_ISSUES["time"]
    
    # Verify audio issues
    assert len(AUDIO_ISSUES) > 0
    assert "Garbled/distorted audio" in AUDIO_ISSUES
    assert "Pacing issues" in AUDIO_ISSUES


@pytest.mark.mock
def test_outro_naming_convention(sample_generated_content, monkeypatch):
    """Test that outro files with different naming convention are handled correctly."""
    import review_gui
    monkeypatch.setattr(review_gui, 'DATA_DIR', sample_generated_content['data_dir'])
    monkeypatch.setattr(review_gui, 'GENERATED_DIR', sample_generated_content['generated_dir'])
    monkeypatch.setattr(review_gui, 'AUDIT_DIR', sample_generated_content['audit_dir'])
    
    items = scan_generated_content()
    outro_item = next(item for item in items if item.content_type == "outros")
    
    # Verify outro files are found with _outro naming
    assert len(outro_item.script_versions) > 0
    assert len(outro_item.audio_versions) > 0
    
    script_path = outro_item.get_script_path(0)
    assert script_path is not None
    assert "mr_new_vegas_outro.txt" in str(script_path)


@pytest.mark.mock
def test_review_status_persistence(tmp_path):
    """Test that review status persists across multiple loads."""
    folder = tmp_path / "test_item"
    folder.mkdir()
    
    # Save initial status
    status1 = {
        "status": "rejected",
        "reviewed_at": "2026-01-25T10:00:00",
        "reviewer_notes": "First review",
        "script_issues": ["Issue 1"],
        "audio_issues": []
    }
    save_review_status(folder, status1)
    
    # Load and verify
    loaded1 = load_review_status(folder)
    assert loaded1["status"] == "rejected"
    assert loaded1["reviewer_notes"] == "First review"
    
    # Update status
    status2 = {
        "status": "approved",
        "reviewed_at": "2026-01-25T11:00:00",
        "reviewer_notes": "Second review - approved",
        "script_issues": [],
        "audio_issues": []
    }
    save_review_status(folder, status2)
    
    # Load and verify updated status
    loaded2 = load_review_status(folder)
    assert loaded2["status"] == "approved"
    assert loaded2["reviewer_notes"] == "Second review - approved"
    assert len(loaded2["script_issues"]) == 0
