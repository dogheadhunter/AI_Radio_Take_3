# Checkpoint 2.3: TTS Client

#### Checkpoint 2.3: TTS Client
**Interface with Chatterbox for voice synthesis.**

**Tasks:**
1. Create `src/ai_radio/generation/tts_client.py`
2. Generate audio from text
3. Support voice cloning with reference audio

**Tests First:**
```python
# tests/generation/test_tts_client.py
"""Tests for TTS client."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.ai_radio. generation.tts_client import (
    TTSClient,
    generate_audio,
    check_tts_available,
)


class TestTTSClient: 
    """Test TTS client operations."""
    
    def test_generate_creates_file(self, mock_chatterbox, tmp_path):
        """Generate must create an audio file."""
        client = TTSClient()
        output_path = tmp_path / "output. wav"
        generate_audio(
            client,
            text="Hello world",
            output_path=output_path,
        )
        assert output_path.exists()
    
    def test_generate_with_voice_reference(self, mock_chatterbox, tmp_path, voice_sample):
        """Generate must accept voice reference for cloning."""
        client = TTSClient()
        output_path = tmp_path / "output.wav"
        # Should not raise
        generate_audio(
            client,
            text="Hello world",
            output_path=output_path,
            voice_reference=voice_sample,
        )
    
    def test_raises_on_tts_error(self, mock_chatterbox_error, tmp_path):
        """Must raise TTSError when TTS fails."""
        from src.ai_radio.utils.errors import TTSError
        client = TTSClient()
        with pytest.raises(TTSError):
            generate_audio(
                client,
                text="Hello world",
                output_path=tmp_path / "output.wav",
            )


class TestTTSClientIntegration: 
    """Integration tests that call real Chatterbox. 
    
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_generation(self, tmp_path):
        """Actually call Chatterbox and generate audio."""
        if not check_tts_available():
            pytest.skip("Chatterbox not available")
        
        client = TTSClient()
        output_path = tmp_path / "test_output.wav"
        generate_audio(client, "Hello, this is a test.", output_path)
        
        assert output_path.exists()
        assert output_path. stat().st_size > 0
```

**Success Criteria:**
- [x] Unit tests pass with mocking
- [x] Integration test generates actual audio file
- [x] Voice cloning with reference audio works

**Git Commit:** `feat(generation): add TTS client`
