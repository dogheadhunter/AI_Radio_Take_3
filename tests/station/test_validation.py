"""
Test the 24-hour validation infrastructure.
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.ai_radio.station.validation import ValidationCheckpoint, ValidationReport, ValidationRunner
from src.ai_radio.station.controller import StationController


class TestValidationCheckpoint:
    """Test validation checkpoint data structure."""

    def test_checkpoint_creation(self):
        """Test creating a checkpoint."""
        checkpoint = ValidationCheckpoint(
            timestamp=datetime(2026, 1, 22, 12, 0, 0),
            hours_elapsed=4.0,
            status="running",
            songs_played=48,
            errors_count=0,
            current_dj="julie",
            current_song="Test Song",
            notes="All good"
        )
        
        assert checkpoint.hours_elapsed == 4.0
        assert checkpoint.status == "running"
        assert checkpoint.songs_played == 48
        assert checkpoint.current_dj == "julie"


class TestValidationReport:
    """Test validation report functionality."""

    def test_report_creation(self):
        """Test creating a validation report."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        report = ValidationReport(start_time=start)
        
        assert report.start_time == start
        assert report.end_time is None
        assert len(report.checkpoints) == 0
        assert len(report.issues) == 0

    def test_add_checkpoint(self):
        """Test adding checkpoints to report."""
        report = ValidationReport(start_time=datetime.now())
        
        checkpoint = ValidationCheckpoint(
            timestamp=datetime.now(),
            hours_elapsed=1.0,
            status="running",
            songs_played=12,
            errors_count=0,
            current_dj="julie"
        )
        
        report.add_checkpoint(checkpoint)
        assert len(report.checkpoints) == 1
        assert report.checkpoints[0] == checkpoint

    def test_add_issue(self):
        """Test adding issues to report."""
        report = ValidationReport(start_time=datetime.now())
        
        report.add_issue("Test issue 1")
        report.add_issue("Test issue 2")
        
        assert len(report.issues) == 2
        assert "Test issue 1" in report.issues

    def test_complete_report(self):
        """Test completing a report."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        end = datetime(2026, 1, 23, 8, 0, 0)
        
        report = ValidationReport(start_time=start)
        report.complete(end)
        
        assert report.end_time == end

    def test_duration_calculation(self):
        """Test actual duration calculation."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        end = datetime(2026, 1, 23, 8, 0, 0)
        
        report = ValidationReport(start_time=start)
        
        # Before completion
        assert report.get_actual_duration_hours() is None
        
        # After completion
        report.complete(end)
        assert report.get_actual_duration_hours() == 24.0

    def test_pass_result(self):
        """Test pass result determination."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        end = start + timedelta(hours=24.5)  # Ran longer than 24h
        
        report = ValidationReport(start_time=start, target_duration_hours=24.0)
        
        # Add successful checkpoints
        for i in range(5):
            checkpoint = ValidationCheckpoint(
                timestamp=start + timedelta(hours=i*6),
                hours_elapsed=i*6.0,
                status="running",
                songs_played=i*72,
                errors_count=0,
                current_dj="julie"
            )
            report.add_checkpoint(checkpoint)
        
        report.complete(end)
        
        result = report.get_result()
        assert result == "PASS"

    def test_fail_stopped_early(self):
        """Test fail result when stopped early."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        end = start + timedelta(hours=12)  # Only ran 12 hours
        
        report = ValidationReport(start_time=start, target_duration_hours=24.0)
        report.complete(end)
        
        result = report.get_result()
        assert "FAIL" in result

    def test_fail_station_stopped(self):
        """Test fail result when station stopped."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        end = start + timedelta(hours=24.5)
        
        report = ValidationReport(start_time=start, target_duration_hours=24.0)
        
        # Add checkpoints with stopped status at the end
        for i in range(4):
            checkpoint = ValidationCheckpoint(
                timestamp=start + timedelta(hours=i*6),
                hours_elapsed=i*6.0,
                status="running",
                songs_played=i*72,
                errors_count=0,
                current_dj="julie"
            )
            report.add_checkpoint(checkpoint)
        
        # Last checkpoint shows stopped
        final = ValidationCheckpoint(
            timestamp=end,
            hours_elapsed=24.5,
            status="stopped",
            songs_played=300,
            errors_count=0,
            current_dj="julie"
        )
        report.add_checkpoint(final)
        
        report.complete(end)
        
        result = report.get_result()
        assert "FAIL" in result

    def test_to_dict(self):
        """Test converting report to dictionary."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        report = ValidationReport(start_time=start)
        
        checkpoint = ValidationCheckpoint(
            timestamp=start,
            hours_elapsed=0.0,
            status="running",
            songs_played=0,
            errors_count=0,
            current_dj="julie"
        )
        report.add_checkpoint(checkpoint)
        report.add_issue("Test issue")
        
        data = report.to_dict()
        
        assert 'start_time' in data
        assert 'checkpoints' in data
        assert 'issues' in data
        assert len(data['checkpoints']) == 1
        assert len(data['issues']) == 1

    def test_save_report(self, tmp_path):
        """Test saving report to file."""
        start = datetime(2026, 1, 22, 8, 0, 0)
        report = ValidationReport(start_time=start)
        
        report_path = tmp_path / "test_report.json"
        report.save(report_path)
        
        assert report_path.exists()
        
        # Verify it's valid JSON
        with open(report_path) as f:
            data = json.load(f)
        
        assert 'start_time' in data


class TestValidationRunner:
    """Test validation runner functionality."""

    def test_runner_creation(self):
        """Test creating a validation runner."""
        controller = StationController()
        runner = ValidationRunner(controller, duration_hours=1.0, checkpoint_interval_minutes=15.0)
        
        assert runner.duration_hours == 1.0
        assert runner.checkpoint_interval_minutes == 15.0
        assert runner.controller == controller

    def test_runner_short_duration(self):
        """Test running a very short validation (< 1 minute)."""
        import time
        
        controller = StationController()
        runner = ValidationRunner(
            controller,
            duration_hours=0.01,  # ~36 seconds
            checkpoint_interval_minutes=0.1  # 6 seconds
        )
        
        report = runner.run()
        
        # Should have completed
        assert report.end_time is not None
        
        # Should have at least initial and final checkpoints
        assert len(report.checkpoints) >= 2
        
        # Controller should be stopped
        assert controller.is_stopped

    def test_runner_creates_checkpoints(self):
        """Test that runner creates periodic checkpoints."""
        controller = StationController()
        runner = ValidationRunner(
            controller,
            duration_hours=0.005,  # ~18 seconds
            checkpoint_interval_minutes=0.05  # 3 seconds
        )
        
        report = runner.run()
        
        # Should have multiple checkpoints
        assert len(report.checkpoints) >= 2
        
        # Checkpoints should have increasing hours_elapsed
        for i in range(len(report.checkpoints) - 1):
            assert report.checkpoints[i+1].hours_elapsed >= report.checkpoints[i].hours_elapsed
