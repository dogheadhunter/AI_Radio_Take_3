# Checkpoint 7.3: Command Handler

#### Checkpoint 7.3: Command Handler
**Handle user input during playback.**

**Tasks:**
1. Create `src/ai_radio/station/commands.py`
2. Non-blocking keyboard input
3. Handle Q (quit), P (pause), S (skip), B (banish)
4. Handle flagging bad intros

**Tests First:**
```python
# tests/station/test_commands.py
"""Tests for command handler."""
import pytest
from unittest.mock import Mock
from src.ai_radio.station.commands import (
    CommandHandler,
    Command,
    parse_key,
    execute_command,
)


class TestParseKey:
    """Test key parsing."""
    
    def test_q_is_quit(self):
        """'q' key must map to QUIT command."""
        assert parse_key('q') == Command.QUIT
        assert parse_key('Q') == Command.QUIT
    
    def test_p_is_pause(self):
        """'p' key must map to PAUSE command."""
        assert parse_key('p') == Command.PAUSE
        assert parse_key('P') == Command.PAUSE
    
    def test_s_is_skip(self):
        """'s' key must map to SKIP command."""
        assert parse_key('s') == Command.SKIP
        assert parse_key('S') == Command.SKIP
    
    def test_b_is_banish(self):
        """'b' key must map to BANISH command."""
        assert parse_key('b') == Command.BANISH
        assert parse_key('B') == Command.BANISH
    
    def test_f_is_flag(self):
        """'f' key must map to FLAG command."""
        assert parse_key('f') == Command.FLAG
        assert parse_key('F') == Command.FLAG
    
    def test_unknown_key_is_none(self):
        """Unknown keys must return None."""
        assert parse_key('x') is None
        assert parse_key('1') is None


class TestExecuteCommand:
    """Test command execution."""
    
    def test_quit_stops_station(self, mock_controller):
        """QUIT must stop the station."""
        execute_command(Command. QUIT, mock_controller)
        mock_controller.stop. assert_called_once()
    
    def test_pause_pauses_playback(self, mock_controller):
        """PAUSE must pause playback."""
        execute_command(Command.PAUSE, mock_controller)
        mock_controller.pause.assert_called_once()
    
    def test_skip_advances_song(self, mock_controller):
        """SKIP must advance to next song."""
        execute_command(Command.SKIP, mock_controller)
        mock_controller.skip.assert_called_once()
    
    def test_banish_banishes_current_song(self, mock_controller):
        """BANISH must banish current song."""
        mock_controller.current_song_id = "song_123"
        execute_command(Command. BANISH, mock_controller)
        mock_controller.banish_song.assert_called_once_with("song_123")
    
    def test_flag_flags_current_intro(self, mock_controller):
        """FLAG must flag current intro for regeneration."""
        mock_controller.current_intro_path = "/path/to/intro.wav"
        execute_command(Command.FLAG, mock_controller)
        mock_controller.flag_intro. assert_called_once()
```

**Implementation Specification:**
```python
# src/ai_radio/station/commands.py
"""
Command handler for user input during playback.

Provides non-blocking keyboard input handling on Windows.
Supports: 
- Q:  Quit station
- P:  Pause/Resume
- S: Skip current song
- B:  Banish current song
- F: Flag current intro for regeneration
- +/-: Volume up/down (future)
"""
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
import sys
import threading

if TYPE_CHECKING: 
    from src. ai_radio.station.controller import StationController


class Command(Enum):
    """Available commands."""
    QUIT = auto()
    PAUSE = auto()
    RESUME = auto()
    SKIP = auto()
    BANISH = auto()
    FLAG = auto()
    PROMOTE = auto()
    VOLUME_UP = auto()
    VOLUME_DOWN = auto()


# Key mappings
KEY_MAP = {
    'q': Command. QUIT,
    'p': Command. PAUSE,
    's': Command.SKIP,
    'b': Command.BANISH,
    'f': Command.FLAG,
    'r': Command.PROMOTE,  # R for "really like this"
    '+':  Command.VOLUME_UP,
    '-': Command.VOLUME_DOWN,
}


def parse_key(key: str) -> Optional[Command]:
    """Parse a key press into a command."""
    return KEY_MAP.get(key.lower())


def execute_command(command: Command, controller: 'StationController') -> None:
    """Execute a command on the station controller."""
    from src.ai_radio.utils.logging import setup_logging
    logger = setup_logging("commands")
    
    if command == Command. QUIT:
        logger.info("Quit command received")
        controller. stop()
    
    elif command == Command.PAUSE: 
        if controller.is_playing: 
            logger.info("Pausing playback")
            controller.pause()
        else:
            logger.info("Resuming playback")
            controller.resume()
    
    elif command == Command. SKIP:
        logger.info(f"Skipping:  {controller.current_song_display}")
        controller. skip()
    
    elif command == Command.BANISH: 
        song_id = controller. current_song_id
        if song_id: 
            logger.info(f"Banishing: {controller.current_song_display}")
            controller.banish_song(song_id)
            controller.skip()
    
    elif command == Command.FLAG: 
        intro_path = controller. current_intro_path
        if intro_path:
            logger.info(f"Flagging intro for regeneration: {intro_path}")
            controller.flag_intro(intro_path)
    
    elif command == Command.PROMOTE:
        song_id = controller.current_song_id
        if song_id:
            logger. info(f"Promoting: {controller. current_song_display}")
            controller. promote_song(song_id)


class CommandHandler: 
    """
    Non-blocking keyboard input handler.
    
    Runs in a separate thread to avoid blocking playback.
    """
    
    def __init__(self, controller: 'StationController'):
        self.controller = controller
        self.running = False
        self.thread:  Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start listening for keyboard input."""
        self.running = True
        self.thread = threading.Thread(target=self._input_loop, daemon=True)
        self.thread. start()
    
    def stop(self) -> None:
        """Stop listening for keyboard input."""
        self.running = False
    
    def _input_loop(self) -> None:
        """Main input loop (runs in thread)."""
        # Windows-specific keyboard handling
        if sys.platform == 'win32': 
            import msvcrt
            while self. running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                    command = parse_key(key)
                    if command:
                        execute_command(command, self.controller)
        else:
            # Unix-like systems would need different handling
            # For MVP, focus on Windows
            pass
```

**Success Criteria:**
- [ ] All command tests pass
- [ ] Keys map to correct commands
- [ ] Commands execute correctly
- [ ] Non-blocking input works

**Git Commit:** `feat(station): add command handler`
