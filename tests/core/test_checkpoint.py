"""Tests for pipeline checkpoint system."""
import pytest
import json
from pathlib import Path
from src.ai_radio.core.checkpoint import PipelineCheckpoint


class TestPipelineCheckpoint:
    """Test checkpoint save/load functionality."""
    
    def test_creates_new_checkpoint(self, tmp_path):
        """New checkpoint should have initial state."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        assert checkpoint.state is not None
        assert "stages" in checkpoint.state
        assert "generate" in checkpoint.state["stages"]
        assert "audit" in checkpoint.state["stages"]
        assert "audio" in checkpoint.state["stages"]
    
    def test_initial_stages_not_started(self, tmp_path):
        """Initial stages should be 'not_started'."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        assert checkpoint.state["stages"]["generate"]["status"] == "not_started"
        assert checkpoint.state["stages"]["audit"]["status"] == "not_started"
        assert checkpoint.state["stages"]["audio"]["status"] == "not_started"
    
    def test_is_stage_completed_false_initially(self, tmp_path):
        """Initially no stages should be completed."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        assert not checkpoint.is_stage_completed("generate")
        assert not checkpoint.is_stage_completed("audit")
        assert not checkpoint.is_stage_completed("audio")
    
    def test_mark_stage_started(self, tmp_path):
        """Marking stage as started should update status."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        checkpoint.mark_stage_started("generate")
        assert checkpoint.state["stages"]["generate"]["status"] == "in_progress"
        assert not checkpoint.is_stage_completed("generate")
    
    def test_mark_stage_completed(self, tmp_path):
        """Marking stage as completed should update status."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        checkpoint.mark_stage_completed("generate", scripts_generated=100)
        
        assert checkpoint.is_stage_completed("generate")
        assert checkpoint.state["stages"]["generate"]["status"] == "completed"
        assert checkpoint.state["stages"]["generate"]["scripts_generated"] == 100
        assert checkpoint.state["stages"]["generate"]["completed_at"] is not None
    
    def test_update_stage_progress(self, tmp_path):
        """Updating progress should save counters."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        checkpoint.update_stage_progress("audit", scripts_audited=50, passed=45, failed=5)
        
        assert checkpoint.state["stages"]["audit"]["scripts_audited"] == 50
        assert checkpoint.state["stages"]["audit"]["passed"] == 45
        assert checkpoint.state["stages"]["audit"]["failed"] == 5
    
    def test_saves_to_disk(self, tmp_path):
        """Checkpoint should be saved to disk."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        checkpoint.mark_stage_completed("generate", scripts_generated=100)
        
        # File should exist
        assert checkpoint_file.exists()
        
        # Should be valid JSON
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            assert data["stages"]["generate"]["scripts_generated"] == 100
    
    def test_loads_from_disk(self, tmp_path):
        """Checkpoint should load existing state from disk."""
        checkpoint_file = tmp_path / "checkpoint.json"
        
        # Create first checkpoint
        checkpoint1 = PipelineCheckpoint(checkpoint_file)
        checkpoint1.mark_stage_completed("generate", scripts_generated=100)
        
        # Load second checkpoint
        checkpoint2 = PipelineCheckpoint(checkpoint_file)
        
        assert checkpoint2.is_stage_completed("generate")
        assert checkpoint2.state["stages"]["generate"]["scripts_generated"] == 100
    
    def test_has_run_id(self, tmp_path):
        """Checkpoint should have a run ID."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        assert "run_id" in checkpoint.state
        assert checkpoint.state["run_id"]
    
    def test_has_timestamp(self, tmp_path):
        """Checkpoint should have a timestamp."""
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        assert "timestamp" in checkpoint.state
        assert checkpoint.state["timestamp"]
    
    def test_creates_parent_directory(self, tmp_path):
        """Should create parent directories if they don't exist."""
        checkpoint_file = tmp_path / "nested" / "dir" / "checkpoint.json"
        checkpoint = PipelineCheckpoint(checkpoint_file)
        
        checkpoint.save()
        
        assert checkpoint_file.exists()
        assert checkpoint_file.parent.exists()
