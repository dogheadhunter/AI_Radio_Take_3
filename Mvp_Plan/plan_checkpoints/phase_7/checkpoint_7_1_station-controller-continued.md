# Checkpoint 7.1: Station Controller (Continued)

## Phase 7: Integration (Continued)

#### Checkpoint 7.1: Station Controller (Continued)

**Tests First (Continued):**
```python
# tests/station/test_controller.py (continued)

    def test_uses_correct_dj(self, controller_with_content):
        """Must use correct DJ for time of day."""
        controller = controller_with_content
        
        with patch_current_time(datetime(2026, 1, 22, 10, 0)):
            current_dj = controller.get_current_dj()
            assert current_dj. name == "julie"
        
        with patch_current_time(datetime(2026, 1, 22, 22, 0)):
            current_dj = controller.get_current_dj()
            assert current_dj.name == "mr_new_vegas"
    
    def test_handles_dj_handoff(self, controller_with_content):
        """Must handle DJ transition at 7 PM."""
        controller = controller_with_content
        
        with patch_current_time(datetime(2026, 1, 22, 19, 0)):
            items = controller._get_next_items()
        
        types = [item.item_type for item in items]
        assert "dj_handoff" in types


class TestStationRecovery:
    """Test error recovery."""
    
    def test_continues_on_song_error(self, controller_with_content, corrupt_song):
        """Must skip corrupt songs and continue."""
        controller = controller_with_content
        controller.queue_song(corrupt_song)
        
        # Should not raise
        controller._play_next()
        
        # Should have moved on
        assert controller. current_item != corrupt_song
    
    def test_logs_errors(self, controller_with_content, corrupt_song, caplog):
        """Must log errors for review."""
        controller = controller_with_content
        controller.queue_song(corrupt_song)
        
        controller._play_next()
        
        assert "error" in caplog. text. lower()
    
    def test_plays_recovery_line(self, controller_with_content, corrupt_song):
        """Must play DJ recovery line on error."""
        controller = controller_with_content
        
        played = []
        controller.on_item_started = lambda item: played.append(item. item_type)
        
        controller.queue_song(corrupt_song)
        controller._play_next()
        
        assert "error_recovery" in played
```

**Implementation Specification:**
```python
# src/ai_radio/station/controller.py
"""
Station controller - the brain of the radio station. 

Orchestrates all subsystems: 
- Music library and rotation
- Content playback
- DJ scheduling
- Information services (weather, time)
- Radio shows
- Error recovery

This is the main entry point for running the station.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Callable
from pathlib import Path

from src.ai_radio.library.catalog import SongCatalog, load_catalog
from src.ai_radio.library. rotation import RotationManager, get_next_song
from src.ai_radio.playback. controller import PlaybackController
from src.ai_radio. dj.scheduler import DJScheduler, get_current_dj
from src.ai_radio. dj.content import ContentSelector, get_intro_for_song
from src.ai_radio.services. clock import ClockService, is_announcement_time
from src.ai_radio. services.weather import WeatherService, is_weather_time
from src.ai_radio.shows.show_manager import ShowManager, get_next_episode
from src.ai_radio.utils.logging import setup_logging, log_error_with_context
from src.ai_radio. utils.errors import AIRadioError, PlaybackError
from src.ai_radio. config import (
    CATALOG_FILE,
    RADIO_SHOW_HOUR,
    DJ_HANDOFF_HOUR,
)


class StationState(Enum):
    """Station operational states."""
    INITIALIZING = auto()
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass
class StationStatus:
    """Current station status for display."""
    state: StationState
    current_song: Optional[str]
    current_dj: str
    next_up: Optional[str]
    uptime_seconds: float
    songs_played: int
    errors_count: int


class StationController: 
    """
    Master controller for the AI Radio Station. 
    
    Coordinates all subsystems and makes decisions about
    what to play next based on time, DJ, and programming.
    """
    
    def __init__(self, config_overrides: dict = None):
        self.logger = setup_logging("station. controller")
        self.state = StationState. INITIALIZING
        
        # Subsystems (initialized in start())
        self.catalog:  Optional[SongCatalog] = None
        self.rotation: Optional[RotationManager] = None
        self.playback: Optional[PlaybackController] = None
        self. dj_scheduler: Optional[DJScheduler] = None
        self.content: Optional[ContentSelector] = None
        self.clock: Optional[ClockService] = None
        self.weather: Optional[WeatherService] = None
        self.shows: Optional[ShowManager] = None
        
        # Statistics
        self.start_time:  Optional[datetime] = None
        self. songs_played: int = 0
        self.errors_count: int = 0
        
        # Callbacks
        self.on_song_change: Optional[Callable] = None
        self.on_dj_change: Optional[Callable] = None
        self. on_error: Optional[Callable] = None
    
    def _initialize_subsystems(self) -> None:
        """Initialize all subsystems."""
        self. logger.info("Initializing subsystems...")
        
        # Load catalog
        self. catalog = load_catalog(CATALOG_FILE)
        self.logger.info(f"Loaded {len(self.catalog)} songs")
        
        # Initialize rotation
        self.rotation = RotationManager(self.catalog)
        
        # Initialize playback
        self.playback = PlaybackController()
        self.playback.on_item_complete = self._on_playback_complete
        
        # Initialize DJ system
        self. dj_scheduler = DJScheduler()
        self.content = ContentSelector()
        
        # Initialize services
        self.clock = ClockService()
        self.weather = WeatherService()
        
        # Initialize shows
        self.shows = ShowManager()
        
        self.logger.info("All subsystems initialized")
    
    def _decide_next_content(self) -> List['QueueItem']:
        """
        Decide what to play next based on current time and state.
        
        Priority order:
        1. DJ Handoff (if transition time)
        2. Radio Show (if 8 PM)
        3. Weather (if weather time)
        4. Time announcement (if announcement time)
        5. Next song with intro
        """
        now = datetime.now()
        items = []
        current_dj = get_current_dj(self.dj_scheduler, now)
        
        # Check for DJ handoff
        if now.hour == DJ_HANDOFF_HOUR and now.minute < 5:
            handoff = self._get_handoff_content()
            if handoff:
                items. extend(handoff)
        
        # Check for radio show time
        if now.hour == RADIO_SHOW_HOUR and not self._show_played_today():
            show_items = self._get_show_content()
            if show_items:
                items.extend(show_items)
                return items  # Show takes priority
        
        # Check for weather
        if is_weather_time(self.weather, now):
            weather_item = self._get_weather_content(current_dj)
            if weather_item:
                items. append(weather_item)
        
        # Check for time announcement
        if is_announcement_time(self.clock, now):
            time_item = self._get_time_content(current_dj, now)
            if time_item: 
                items.append(time_item)
        
        # Always queue next song
        song_items = self._get_next_song_content(current_dj)
        items.extend(song_items)
        
        return items
    
    # Additional implementation methods...
```

**Success Criteria:**
- [x] All controller tests pass
- [x] Station starts and initializes all subsystems
- [x] Correct content decisions based on time
- [x] DJ handoff works at 7 PM
- [x] Radio shows play at 8 PM
- [x] Weather plays at scheduled times
- [x] Time announcements play every 30 minutes
- [x] Errors are caught and recovered from

**Validation:**
```bash
# Human runs: 
pytest tests/station/test_controller. py -v
```

**Git Commit:** `feat(station): add station controller`
