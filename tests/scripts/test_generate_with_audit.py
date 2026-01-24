"""Tests for generate_with_audit.py pipeline script."""
from pathlib import Path
import json
import sys
import pytest

# Import the pipeline functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.generate_with_audit import (
    run_pipeline,
    PipelineCheckpoint,
    get_script_path,
    get_audit_path,
    get_audio_path
)


def test_checkpoint_system(tmp_path):
    """Test checkpoint save/load functionality."""
    checkpoint_file = tmp_path / "checkpoint.json"
    checkpoint = PipelineCheckpoint(checkpoint_file)
    
    # Initial state
    assert not checkpoint.is_stage_completed("generate")
    
    # Mark stage completed
    checkpoint.mark_stage_completed("generate", scripts_generated=100)
    assert checkpoint.is_stage_completed("generate")
    assert checkpoint.state["stages"]["generate"]["scripts_generated"] == 100
    
    # Load from file
    checkpoint2 = PipelineCheckpoint(checkpoint_file)
    assert checkpoint2.is_stage_completed("generate")
    assert checkpoint2.state["stages"]["generate"]["scripts_generated"] == 100


def test_path_helpers():
    """Test path generation helper functions."""
    song = {"id": 1, "artist": "Test Artist", "title": "Test Song"}
    
    script_path = get_script_path(song, "julie")
    assert "Test_Artist-Test_Song" in str(script_path)
    assert script_path.name == "julie_0.txt"
    
    audio_path = get_audio_path(song, "julie")
    assert "Test_Artist-Test_Song" in str(audio_path)
    assert audio_path.name == "julie_0.wav"
    
    audit_path = get_audit_path(song, "julie", passed=True)
    assert "passed" in str(audit_path)
    assert audit_path.name == "Test_Artist-Test_Song_song_intro_audit.json"

