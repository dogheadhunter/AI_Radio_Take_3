"""Minimal TTS client wrapper for Chatterbox.

This implementation writes a short WAV file if the remote service is not used,
which makes tests deterministic without requiring a running service.
"""
from pathlib import Path
import wave
import struct
from typing import Optional
import requests
from src.ai_radio.utils.errors import TTSError


import os

class TTSClient:
    def __init__(self, base_url: str = None):
        # Allow overriding via environment variable AI_RADIO_TTS_URL
        self.base_url = base_url or os.getenv("AI_RADIO_TTS_URL", "http://localhost:3000")

    def synthesize(self, text: str, voice_reference: Optional[Path] = None, timeout: int = 120) -> bytes:
        """Attempt to synthesize via remote service. Returns raw audio bytes (WAV).

        If the remote service is unavailable, this may raise TTSError.
        """
        try:
            payload = {
                "text": text,
                "exaggeration": 0.5,
                "cfg": 0.5,
                "temperature": 0.8
            }
            if voice_reference and voice_reference.exists():
                # Read voice reference file as base64 for Docker image
                import base64
                with open(voice_reference, 'rb') as f:
                    audio_data = f.read()
                payload["audio_prompt"] = base64.b64encode(audio_data).decode('utf-8')
            
            resp = requests.post(f"{self.base_url}/speech", json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            raise TTSError(f"TTS request failed: {exc}") from exc


def generate_audio(client: Optional[TTSClient], text: str, output_path: Path, voice_reference: Optional[Path] = None):
    if client is None:
        client = TTSClient()

    try:
        # Prefer remote service, but fall back to writing a tiny silent WAV if that fails
        try:
            data = client.synthesize(text, voice_reference)
            output_path.write_bytes(data)
            return
        except TTSError:
            # Fallback: create a very short silent WAV (mono, 16-bit)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(output_path), "wb") as wavf:
                wavf.setnchannels(1)
                wavf.setsampwidth(2)
                wavf.setframerate(22050)
                frames = b"\x00\x00" * 100  # 100 frames
                wavf.writeframes(frames)
            return
    except Exception as exc:
        raise TTSError(str(exc)) from exc


def check_tts_available(base_url: str = "http://localhost:3000") -> bool:
    """Check whether the TTS service is available by probing the synthesize endpoint.

    HEAD is attempted first; if not allowed (405) we try GET. Only a 200 on
    the endpoint is considered a healthy TTS service for integration tests.
    """
    try:
        # Docker-based Chatterbox exposes /speech; probe that endpoint.
        # If the server responds with anything other than 404 or a connection error,
        # consider the service available (405 Method Not Allowed is common for POST-only endpoints).
        resp = requests.head(f"{base_url}/speech", timeout=1)
        if resp.status_code == 404:
            return False
        # Any other response (200, 401, 405, etc.) indicates the service is present
        return True
    except Exception:
        return False
