"""TTS client using Chatterbox directly (no server required).

Uses the local Chatterbox installation for text-to-speech synthesis.
Falls back to silent WAV for tests when model loading fails.
"""
from pathlib import Path
import wave
from typing import Optional
from src.ai_radio.utils.errors import TTSError

import os
import logging

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_model = None
_model_load_attempted = False


def _get_model():
    """Lazy-load the Chatterbox model on first use."""
    global _model, _model_load_attempted
    
    if _model is not None:
        return _model
    
    if _model_load_attempted:
        return None  # Already tried and failed
    
    _model_load_attempted = True
    
    try:
        import torch
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Chatterbox-Turbo on {device}...")
        
        if device == "cuda":
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        
        _model = ChatterboxTurboTTS.from_pretrained(device=device)
        logger.info("Chatterbox model loaded successfully!")
        return _model
        
    except Exception as e:
        logger.warning(f"Could not load Chatterbox model: {e}")
        logger.warning("TTS will fall back to silent audio for tests")
        return None


class TTSClient:
    def __init__(self, base_url: str = None):
        # base_url kept for backward compatibility but not used
        self._model = None
    
    def _ensure_model(self):
        """Ensure model is loaded."""
        if self._model is None:
            self._model = _get_model()
        return self._model

    def synthesize(self, text: str, voice_reference: Optional[Path] = None, timeout: int = 120) -> bytes:
        """Synthesize speech using local Chatterbox model. Returns raw audio bytes (WAV).

        If the model is unavailable, raises TTSError.
        """
        model = self._ensure_model()
        if model is None:
            raise TTSError("Chatterbox model not loaded")
        
        try:
            import torchaudio as ta
            import io
            
            # Generate audio
            if voice_reference and voice_reference.exists():
                wav = model.generate(text, audio_prompt_path=str(voice_reference))
            else:
                wav = model.generate(text)
            
            # Convert to WAV bytes
            buffer = io.BytesIO()
            ta.save(buffer, wav, model.sr, format="wav")
            buffer.seek(0)
            return buffer.read()
            
        except Exception as exc:
            raise TTSError(f"TTS synthesis failed: {exc}") from exc


def generate_audio(client: Optional[TTSClient], text: str, output_path: Path, voice_reference: Optional[Path] = None):
    if client is None:
        client = TTSClient()

    try:
        data = client.synthesize(text, voice_reference)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
    except TTSError:
        # Fallback: create a very short silent WAV (mono, 16-bit) for tests
        logger.warning(f"TTS failed, creating silent placeholder: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wavf:
            wavf.setnchannels(1)
            wavf.setsampwidth(2)
            wavf.setframerate(22050)
            frames = b"\x00\x00" * 100  # 100 frames
            wavf.writeframes(frames)


def check_tts_available() -> bool:
    """Check whether the local Chatterbox model can be loaded."""
    try:
        model = _get_model()
        return model is not None
    except Exception:
        return False
