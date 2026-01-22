# Checkpoint 3.1: Basic Audio Player

#### Checkpoint 3.1: Basic Audio Player
**Play a single audio file.**

**Tasks:**
1. Create `src/ai_radio/playback/player.py`
2. Play MP3 and WAV files
3. Provide callbacks for play completion
4. Handle errors gracefully

**Tests First:**
```python
# tests/playback/test_player.py
"""Tests for audio player."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.ai_radio.playback.player import (
    AudioPlayer,
    play_file,
    stop_playback,
    is_playing,
    get_current_position,
    PlayerState,
)


class TestAudioPlayer: 
    """Test basic player operations."""
    
    def test_play_changes_state_to_playing(self, mock_pygame, sample_audio):
        """Playing must change state to PLAYING."""
        player = AudioPlayer()
        play_file(player, sample_audio)
        assert player.state == PlayerState. PLAYING
    
    def test_stop_changes_state_to_stopped(self, mock_pygame, sample_audio):
        """Stopping must change state to STOPPED."""
        player = AudioPlayer()
        play_file(player, sample_audio)
        stop_playback(player)
        assert player.state == PlayerState.STOPPED
    
    def test_is_playing_returns_correct_state(self, mock_pygame, sample_audio):
        """is_playing must reflect actual state."""
        player = AudioPlayer()
        assert not is_playing(player)
        play_file(player, sample_audio)
        assert is_playing(player)
    
    def test_raises_for_nonexistent_file(self, mock_pygame):
        """Must raise AudioFileError for missing files."""
        from src.ai_radio.utils.errors import AudioFileError
        player = AudioPlayer()
        with pytest.raises(AudioFileError):
            play_file(player, Path("/nonexistent/file.mp3"))
    
    def test_calls_completion_callback(self, mock_pygame, sample_audio):
        """Must call callback when playback completes."""
        player = AudioPlayer()
        callback = Mock()
        play_file(player, sample_audio, on_complete=callback)
        
        # Simulate playback completion
        player._simulate_complete()
        
        callback.assert_called_once()


class TestPlayerIntegration:
    """Integration tests with real audio. 
    
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    def test_plays_real_audio(self, real_audio_file):
        """Actually play an audio file."""
        player = AudioPlayer()
        play_file(player, real_audio_file)
        
        # Wait a moment
        import time
        time.sleep(0.5)
        
        assert is_playing(player) or player.state == PlayerState.COMPLETED
        stop_playback(player)
```

**Success Criteria:**
- [ ] All player tests pass
- [ ] Can play an actual MP3 file
- [ ] Completion callback fires when file ends
- [ ] Errors are handled gracefully

**Git Commit:** `feat(playback): add basic audio player`


**Progress:**
- Implemented `AudioPlayer` (test-friendly) and a `PygameAudioPlayer` for real playback.
- Added an integration test `tests/playback/test_player_integration_real.py` that plays a WAV file using `pygame` (marked `integration`).
- Note: Real playback requires `pygame` to be installed in the test environment; MP3 playback depends on system decoders/SDL_mixer support. Run `pytest -m integration` after installing `pygame` to verify real playback.

