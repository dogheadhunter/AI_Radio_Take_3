"""Checkpoint system for AI Radio generation pipeline.

This module manages pipeline state to enable resuming interrupted runs
and tracking progress across multiple stages (generate, audit, audio).
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json


class PipelineCheckpoint:
    """Manages pipeline state for resume capability."""
    
    def __init__(self, state_file: Path):
        """Initialize checkpoint manager.
        
        Args:
            state_file: Path to checkpoint JSON file
        """
        self.state_file = state_file
        self.state = self._load_or_init()
    
    def _load_or_init(self) -> Dict[str, Any]:
        """Load existing checkpoint or initialize new one."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "timestamp": datetime.now().isoformat(),
            "run_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "config": {},
            "stages": {
                "generate": {"status": "not_started", "completed_at": None, "scripts_generated": 0},
                "audit": {"status": "not_started", "completed_at": None, "scripts_audited": 0, "passed": 0, "failed": 0},
                "audio": {"status": "not_started", "completed_at": None, "audio_files_generated": 0}
            }
        }
    
    def save(self):
        """Save checkpoint to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def is_stage_completed(self, stage: str) -> bool:
        """Check if a stage is completed.
        
        Args:
            stage: Stage name ('generate', 'audit', or 'audio')
            
        Returns:
            True if stage has completed status
        """
        return self.state["stages"].get(stage, {}).get("status") == "completed"
    
    def mark_stage_started(self, stage: str):
        """Mark stage as in progress.
        
        Args:
            stage: Stage name to mark as started
        """
        self.state["stages"][stage]["status"] = "in_progress"
        self.save()
    
    def mark_stage_completed(self, stage: str, **kwargs):
        """Mark stage as completed with additional data.
        
        Args:
            stage: Stage name to mark as completed
            **kwargs: Additional data to store (e.g., scripts_generated=100)
        """
        self.state["stages"][stage]["status"] = "completed"
        self.state["stages"][stage]["completed_at"] = datetime.now().isoformat()
        for key, value in kwargs.items():
            self.state["stages"][stage][key] = value
        self.save()
    
    def update_stage_progress(self, stage: str, **kwargs):
        """Update progress counters for a stage.
        
        Args:
            stage: Stage name to update
            **kwargs: Progress data to update (e.g., scripts_audited=50)
        """
        for key, value in kwargs.items():
            self.state["stages"][stage][key] = value
        self.save()
