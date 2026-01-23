"""
24-Hour Validation Mode - Automated test runner and logger.

This module provides the infrastructure for running and logging 24-hour validation tests.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
import json
import time

from src.ai_radio.utils.logging import setup_logging


@dataclass
class ValidationCheckpoint:
    """A checkpoint in the 24-hour validation."""
    timestamp: datetime
    hours_elapsed: float
    status: str  # "running", "stopped", "error"
    songs_played: int
    errors_count: int
    current_dj: str
    current_song: Optional[str] = None
    notes: str = ""


@dataclass
class ValidationReport:
    """Complete report of a 24-hour validation run."""
    start_time: datetime
    end_time: Optional[datetime] = None
    target_duration_hours: float = 24.0
    checkpoints: List[ValidationCheckpoint] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    
    def add_checkpoint(self, checkpoint: ValidationCheckpoint):
        """Add a checkpoint to the report."""
        self.checkpoints.append(checkpoint)
    
    def add_issue(self, issue: str):
        """Add an issue to the report."""
        self.issues.append(issue)
    
    def complete(self, end_time: datetime):
        """Mark the validation as complete."""
        self.end_time = end_time
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'target_duration_hours': self.target_duration_hours,
            'actual_duration_hours': self.get_actual_duration_hours(),
            'total_checkpoints': len(self.checkpoints),
            'total_issues': len(self.issues),
            'checkpoints': [
                {
                    'timestamp': cp.timestamp.isoformat(),
                    'hours_elapsed': cp.hours_elapsed,
                    'status': cp.status,
                    'songs_played': cp.songs_played,
                    'errors_count': cp.errors_count,
                    'current_dj': cp.current_dj,
                    'current_song': cp.current_song,
                    'notes': cp.notes,
                }
                for cp in self.checkpoints
            ],
            'issues': self.issues,
            'result': self.get_result(),
        }
    
    def get_actual_duration_hours(self) -> Optional[float]:
        """Get actual duration in hours."""
        if self.end_time is None:
            return None
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600
    
    def get_result(self) -> str:
        """Determine pass/fail result."""
        if self.end_time is None:
            return "INCOMPLETE"
        
        # Check if we ran for target duration
        actual_hours = self.get_actual_duration_hours()
        if actual_hours < self.target_duration_hours * 0.95:  # Allow 5% tolerance
            return "FAIL - Stopped early"
        
        # Check if any checkpoint shows stopped/error status
        final_statuses = [cp.status for cp in self.checkpoints[-3:]]  # Last 3 checkpoints
        if 'stopped' in final_statuses or 'error' in final_statuses:
            return "FAIL - Station stopped"
        
        # Check error count
        if self.checkpoints:
            final_errors = self.checkpoints[-1].errors_count
            if final_errors > 10:  # Arbitrary threshold
                return "PASS with warnings - High error count"
        
        return "PASS"
    
    def save(self, path: Path):
        """Save report to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class ValidationRunner:
    """Runs a 24-hour validation test with periodic checkpoints."""
    
    def __init__(self, controller, duration_hours: float = 24.0, checkpoint_interval_minutes: float = 60.0):
        self.controller = controller
        self.duration_hours = duration_hours
        self.checkpoint_interval_minutes = checkpoint_interval_minutes
        self.logger = setup_logging("validation")
        self.report = ValidationReport(
            start_time=datetime.now(),
            target_duration_hours=duration_hours
        )
    
    def run(self) -> ValidationReport:
        """
        Run the validation test.
        Returns the validation report.
        """
        self.logger.info(f"Starting {self.duration_hours}-hour validation test")
        self.logger.info(f"Checkpoints every {self.checkpoint_interval_minutes} minutes")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=self.duration_hours)
        next_checkpoint = start_time
        
        try:
            # Start the station
            self.controller.start()
            self.logger.info("Station started")
            
            # Create initial checkpoint
            self._create_checkpoint(start_time)
            
            # Run until duration expires
            while datetime.now() < end_time:
                # Check if station is still running
                if not self.controller.is_running:
                    self.report.add_issue("Station stopped running")
                    self.logger.error("Station stopped running!")
                    break
                
                # Create checkpoint if interval elapsed
                now = datetime.now()
                if now >= next_checkpoint:
                    self._create_checkpoint(now)
                    next_checkpoint = now + timedelta(minutes=self.checkpoint_interval_minutes)
                
                # Sleep briefly
                time.sleep(10)  # Check every 10 seconds
            
            # Final checkpoint
            self._create_checkpoint(datetime.now())
            
        except Exception as e:
            self.logger.exception(f"Validation test failed with exception: {e}")
            self.report.add_issue(f"Exception: {str(e)}")
        
        finally:
            # Stop the station
            if self.controller.is_running:
                self.controller.stop()
            
            # Complete the report
            self.report.complete(datetime.now())
            self.logger.info(f"Validation test complete: {self.report.get_result()}")
        
        return self.report
    
    def _create_checkpoint(self, timestamp: datetime):
        """Create a checkpoint at the given timestamp."""
        status = self.controller.get_status()
        hours_elapsed = (timestamp - self.report.start_time).total_seconds() / 3600
        
        checkpoint = ValidationCheckpoint(
            timestamp=timestamp,
            hours_elapsed=hours_elapsed,
            status=status.state.name.lower(),
            songs_played=status.songs_played,
            errors_count=status.errors_count,
            current_dj=status.current_dj,
            current_song=status.current_song,
        )
        
        self.report.add_checkpoint(checkpoint)
        self.logger.info(
            f"Checkpoint @ {hours_elapsed:.1f}h: "
            f"status={checkpoint.status}, "
            f"songs={checkpoint.songs_played}, "
            f"errors={checkpoint.errors_count}, "
            f"dj={checkpoint.current_dj}"
        )
