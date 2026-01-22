"""Minimal LLM client wrapper for Ollama.

This implementation is intentionally small and test-friendly. Unit tests should mock
network calls; integration tests can hit a real Ollama instance.
"""
from typing import Optional
import requests
from src.ai_radio.utils.errors import LLMError


import os

class LLMClient:
    def __init__(self, base_url: str = None):
        # Allow overriding via environment variable AI_RADIO_LLM_URL
        self.base_url = base_url or os.getenv("AI_RADIO_LLM_URL", "http://localhost:11434")

    def generate(self, prompt: str, timeout: int = 10) -> str:
        """Call Ollama (or any compatible service) and return generated text.

        Raises LLMError on failure.
        """
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json={"prompt": prompt}, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # Accept either {'text': '...'} or {'response': '...'}
            text = data.get("text") or data.get("response")
            if not isinstance(text, str):
                raise LLMError("Invalid response from LLM")
            return text
        except Exception as exc:
            raise LLMError(str(exc)) from exc


def generate_text(client: Optional[LLMClient], prompt: str) -> str:
    if client is None:
        client = LLMClient()
    try:
        return client.generate(prompt)
    except Exception as exc:
        # Ensure we always raise LLMError for consumers
        raise LLMError(str(exc)) from exc


def check_ollama_available(base_url: str = "http://localhost:11434") -> bool:
    """Check if the Ollama service appears available.

    This now requires the /api/generate endpoint to be present. HEAD/GET are
    attempted against that endpoint; a 200 means the endpoint is available.
    If HEAD is not allowed (405), a GET is tried. Any other status indicates
    the generation endpoint is not available and integration tests should skip.
    """
    try:
        resp = requests.head(f"{base_url}/api/generate", timeout=1)
        if resp.status_code == 200:
            return True
        if resp.status_code == 405:
            # HEAD not allowed; try GET on the generate endpoint
            resp2 = requests.get(f"{base_url}/api/generate", timeout=1)
            return resp2.status_code == 200
        # Any other code (404, 500, etc.) => not available
        return False
    except Exception:
        return False
