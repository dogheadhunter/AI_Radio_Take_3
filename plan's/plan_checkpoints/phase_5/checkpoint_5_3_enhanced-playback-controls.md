# Checkpoint 5.3: Enhanced Playback Controls

#### Checkpoint 5.3: Enhanced Playback Controls
**Implement true pause/resume and seek functionality for better playback control.**

## Overview
Currently, pause/resume restarts playback from the beginning. This checkpoint adds true pause/unpause functionality and optional seek/fast-forward/rewind capabilities using pygame.mixer features.

## Tasks

### Task 1: Implement True Pause/Resume in PygameAudioPlayer
- [ ] Add `pause()` method using `pygame.mixer.music.pause()`
- [ ] Add `unpause()` method using `pygame.mixer.music.unpause()`
- [ ] Add `is_paused()` method to check pause state
- [ ] Update `get_position()` to handle paused state correctly
- [ ] Add tests for pause/unpause functionality

### Task 2: Update PlaybackController for True Pause
- [ ] Update `pause_playback()` to use new `pause()` method
- [ ] Update `resume_playback()` to use new `unpause()` method
- [ ] Track pause state in controller
- [ ] Ensure pause state persists across playback items
- [ ] Add tests for controller pause/resume

### Task 3: Implement Seek Functionality (Optional)
- [ ] Add `seek(position_ms)` method to PygameAudioPlayer
- [ ] Use `pygame.mixer.music.set_pos()` for supported formats
- [ ] Handle formats that don't support seeking gracefully
- [ ] Add `get_duration()` method if not present
- [ ] Add validation for seek position bounds

### Task 4: Implement Fast-Forward/Rewind (Optional)
- [ ] Add `skip_forward(seconds)` method
- [ ] Add `skip_backward(seconds)` method
- [ ] Calculate new position based on current position
- [ ] Use seek functionality internally
- [ ] Add safeguards against seeking past boundaries

### Task 5: Update Command Handler for New Controls
- [ ] Add `seek <seconds>` command
- [ ] Add `ff` or `forward` command (skip forward 10s)
- [ ] Add `rw` or `rewind` command (skip backward 10s)
- [ ] Update help text with new commands
- [ ] Add tests for new commands

### Task 6: Update Terminal Display for Playback State
- [ ] Show paused indicator in status display
- [ ] Show current position / duration during playback
- [ ] Show seek position when seeking
- [ ] Add progress bar for current track (optional)

## Implementation Details

**File: `src/ai_radio/playback/player.py`**

Update `PygameAudioPlayer` class:

```python
class PygameAudioPlayer(AudioPlayer):
    """Real audio player using pygame.mixer."""
    
    def __init__(self):
        pygame.mixer.init()
        self._current_file: Optional[str] = None
        self._is_paused = False
    
    def play(self, file_path: str) -> None:
        """Start playing an audio file."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self._current_file = file_path
            self._is_paused = False
            logger.info(f"Playing: {file_path}")
        except Exception as e:
            logger.error(f"Failed to play {file_path}: {e}")
            raise
    
    def stop(self) -> None:
        """Stop playback."""
        pygame.mixer.music.stop()
        self._current_file = None
        self._is_paused = False
    
    def pause(self) -> None:
        """Pause playback without stopping."""
        if self.is_playing() and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            logger.info("Playback paused")
    
    def unpause(self) -> None:
        """Resume paused playback."""
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
            logger.info("Playback resumed")
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return pygame.mixer.music.get_busy()
    
    def is_paused(self) -> bool:
        """Check if audio is currently paused."""
        return self._is_paused
    
    def get_position(self) -> float:
        """Get current playback position in seconds."""
        if not self.is_playing() and not self._is_paused:
            return 0.0
        # pygame returns position in milliseconds
        pos_ms = pygame.mixer.music.get_pos()
        return pos_ms / 1000.0
    
    def seek(self, position_seconds: float) -> bool:
        """Seek to specific position in current track.
        
        Args:
            position_seconds: Target position in seconds
            
        Returns:
            True if seek successful, False if not supported/failed
        """
        if not self._current_file:
            logger.warning("Cannot seek: no file loaded")
            return False
        
        try:
            # pygame.mixer.music.set_pos() only works for certain formats
            # For MP3/OGG, position is in seconds
            pygame.mixer.music.set_pos(position_seconds)
            logger.info(f"Seeked to {position_seconds:.1f}s")
            return True
        except NotImplementedError:
            logger.warning(f"Seeking not supported for {self._current_file}")
            return False
        except Exception as e:
            logger.error(f"Seek failed: {e}")
            return False
    
    def skip_forward(self, seconds: float = 10.0) -> bool:
        """Skip forward by specified seconds."""
        current_pos = self.get_position()
        new_pos = current_pos + seconds
        return self.seek(new_pos)
    
    def skip_backward(self, seconds: float = 10.0) -> bool:
        """Skip backward by specified seconds."""
        current_pos = self.get_position()
        new_pos = max(0.0, current_pos - seconds)
        return self.seek(new_pos)
```

**File: `src/ai_radio/playback/controller.py`**

Update pause/resume functions:

```python
def pause_playback(controller: PlaybackController) -> None:
    """Pause current playback without stopping."""
    if controller.player.is_playing():
        controller.player.pause()
        controller.state.paused = True
        logger.info("Playback paused")
    else:
        logger.warning("Nothing playing to pause")


def resume_playback(controller: PlaybackController) -> None:
    """Resume paused playback."""
    if controller.state.paused:
        controller.player.unpause()
        controller.state.paused = False
        logger.info("Playback resumed")
    else:
        logger.warning("Playback not paused")


def seek_playback(controller: PlaybackController, position_seconds: float) -> bool:
    """Seek to specific position in current track."""
    if controller.player.is_playing() or controller.state.paused:
        success = controller.player.seek(position_seconds)
        if success:
            logger.info(f"Seeked to {position_seconds:.1f}s")
        return success
    else:
        logger.warning("Nothing playing to seek")
        return False


def skip_forward_playback(controller: PlaybackController, seconds: float = 10.0) -> bool:
    """Skip forward in current track."""
    return controller.player.skip_forward(seconds)


def skip_backward_playback(controller: PlaybackController, seconds: float = 10.0) -> bool:
    """Skip backward in current track."""
    return controller.player.skip_backward(seconds)
```

**File: `src/ai_radio/station/commands.py`**

Add new commands:

```python
class CommandHandler:
    """Handle user commands during station operation."""
    
    COMMANDS = {
        "help": "Show this help message",
        "pause": "Pause playback",
        "resume": "Resume playback",
        "skip": "Skip current track",
        "stop": "Stop the station",
        "status": "Show current status",
        "queue": "Show upcoming tracks",
        "ff": "Fast-forward 10 seconds",
        "rw": "Rewind 10 seconds",
        "seek <seconds>": "Seek to specific position",
    }
    
    def handle_command(self, command: str) -> bool:
        """Handle a user command.
        
        Returns:
            True if station should continue, False if should stop
        """
        cmd_parts = command.strip().lower().split()
        if not cmd_parts:
            return True
        
        cmd = cmd_parts[0]
        args = cmd_parts[1:]
        
        if cmd == "help":
            self._show_help()
        elif cmd == "pause":
            self._handle_pause()
        elif cmd == "resume":
            self._handle_resume()
        elif cmd == "skip":
            self._handle_skip()
        elif cmd == "stop":
            return False
        elif cmd == "status":
            self._show_status()
        elif cmd == "queue":
            self._show_queue()
        elif cmd == "ff" or cmd == "forward":
            self._handle_fast_forward()
        elif cmd == "rw" or cmd == "rewind":
            self._handle_rewind()
        elif cmd == "seek" and args:
            try:
                seconds = float(args[0])
                self._handle_seek(seconds)
            except ValueError:
                print("Invalid seek position. Use: seek <seconds>")
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")
        
        return True
    
    def _handle_fast_forward(self) -> None:
        """Fast-forward 10 seconds."""
        success = skip_forward_playback(self.controller, seconds=10.0)
        if success:
            print("⏩ Fast-forwarded 10 seconds")
        else:
            print("⚠️  Fast-forward not available")
    
    def _handle_rewind(self) -> None:
        """Rewind 10 seconds."""
        success = skip_backward_playback(self.controller, seconds=10.0)
        if success:
            print("⏪ Rewound 10 seconds")
        else:
            print("⚠️  Rewind not available")
    
    def _handle_seek(self, seconds: float) -> None:
        """Seek to specific position."""
        success = seek_playback(self.controller, seconds)
        if success:
            print(f"⏭️  Seeked to {seconds:.1f}s")
        else:
            print("⚠️  Seek not available")
```

## Success Criteria

### Functionality
- [ ] Pause command truly pauses playback (doesn't restart)
- [ ] Resume command continues from paused position
- [ ] Pause state survives between tracks in queue
- [ ] `is_paused()` correctly reports pause state
- [ ] Seek moves to specified position in track
- [ ] Fast-forward/rewind skip 10 seconds in either direction

### Quality
- [ ] Pause/resume is instant with no audio glitches
- [ ] Position tracking remains accurate during pause
- [ ] Seek works for MP3 files (most common format)
- [ ] Graceful degradation when seeking not supported
- [ ] Clear user feedback for all commands

### Testing
- [ ] Unit tests for all new player methods
- [ ] Unit tests for controller pause/resume/seek functions
- [ ] Integration tests for command handler
- [ ] Manual testing with actual audio files
- [ ] Test pause during intro, song, announcement

## Validation Commands

```bash
# Run unit tests
.venv/Scripts/pytest tests/test_playback_player.py::test_pause_unpause -v
.venv/Scripts/pytest tests/test_playback_player.py::test_seek -v
.venv/Scripts/pytest tests/test_playback_controller.py::test_pause_resume -v

# Manual testing
python src/ai_radio/main.py

# In running station:
> pause          # Should pause immediately
> status         # Should show "Paused: True"
> resume         # Should continue from same position
> ff             # Should skip ahead 10 seconds
> rw             # Should go back 10 seconds
> seek 30        # Should jump to 30 seconds into track
```

## Anti-Regression Tests

```python
# tests/test_playback_player.py

def test_pause_unpause(pygame_player):
    """Test true pause/unpause functionality."""
    # Play a file
    pygame_player.play("test.mp3")
    time.sleep(0.5)
    
    # Pause
    pygame_player.pause()
    assert pygame_player.is_paused()
    assert pygame_player.is_playing()  # Still "busy" when paused
    
    pos_at_pause = pygame_player.get_position()
    time.sleep(0.5)
    
    # Position shouldn't change while paused
    assert pygame_player.get_position() == pytest.approx(pos_at_pause, abs=0.1)
    
    # Unpause
    pygame_player.unpause()
    assert not pygame_player.is_paused()
    time.sleep(0.5)
    
    # Position should advance after unpause
    assert pygame_player.get_position() > pos_at_pause


def test_seek(pygame_player):
    """Test seeking to specific position."""
    pygame_player.play("test.mp3")
    time.sleep(0.5)
    
    # Seek to 10 seconds
    success = pygame_player.seek(10.0)
    
    if success:  # Only test if format supports seeking
        time.sleep(0.1)
        assert pygame_player.get_position() == pytest.approx(10.0, abs=1.0)


def test_skip_forward(pygame_player):
    """Test fast-forward functionality."""
    pygame_player.play("test.mp3")
    time.sleep(0.5)
    
    pos_before = pygame_player.get_position()
    success = pygame_player.skip_forward(10.0)
    
    if success:
        time.sleep(0.1)
        assert pygame_player.get_position() >= pos_before + 9.0


def test_skip_backward(pygame_player):
    """Test rewind functionality."""
    pygame_player.play("test.mp3")
    pygame_player.seek(20.0)
    time.sleep(0.5)
    
    pos_before = pygame_player.get_position()
    success = pygame_player.skip_backward(10.0)
    
    if success:
        time.sleep(0.1)
        assert pygame_player.get_position() <= pos_before - 9.0


# tests/test_playback_controller.py

def test_pause_resume_maintains_position(controller, sample_audio):
    """Test that pause/resume maintains playback position."""
    start_playback(controller, sample_audio)
    time.sleep(1.0)
    
    # Pause
    pause_playback(controller)
    assert controller.state.paused
    pos_at_pause = controller.player.get_position()
    
    time.sleep(1.0)
    
    # Position should not advance while paused
    assert controller.player.get_position() == pytest.approx(pos_at_pause, abs=0.1)
    
    # Resume
    resume_playback(controller)
    assert not controller.state.paused
    time.sleep(0.5)
    
    # Position should advance after resume
    assert controller.player.get_position() > pos_at_pause
```

## Git Commit

```bash
git add src/ai_radio/playback/player.py
git add src/ai_radio/playback/controller.py
git add src/ai_radio/station/commands.py
git add tests/test_playback_player.py
git add tests/test_playback_controller.py
git commit -m "feat(playback): add true pause/resume and seek controls

- Implement pause()/unpause() in PygameAudioPlayer
- Add is_paused() state tracking
- Implement seek(), skip_forward(), skip_backward() methods
- Update PlaybackController for true pause (no restart)
- Add ff/rw/seek commands to CommandHandler
- Add comprehensive tests for new functionality
"
```

## Dependencies
- **Requires**: Checkpoint 3.2 (Audio Player) - `PygameAudioPlayer` class exists
- **Requires**: Checkpoint 3.3 (Playback Controller) - Controller integration
- **Requires**: Checkpoint 7.3 (Command Handler) - Command system

## Notes
- **pygame.mixer.music.set_pos()** support varies by format:
  - ✅ MP3: Supported (position in seconds)
  - ✅ OGG: Supported (position in seconds)  
  - ❌ WAV: Not supported
  - ❌ FLAC: Not supported
- For unsupported formats, seek will fail gracefully
- Consider using `pydub` or `mutagen` to get accurate duration
- Future enhancement: Add visual progress bar in terminal display
- Future enhancement: Add keyboard shortcuts (space = pause, arrows = seek)
