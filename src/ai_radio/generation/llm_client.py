"""Minimal LLM client wrapper for Ollama.

This implementation is intentionally small and test-friendly. Unit tests should mock
network calls; integration tests can hit a real Ollama instance.
"""
from typing import Optional
import requests
from src.ai_radio.utils.errors import LLMError


import os
import json as json_module

class LLMClient:
    def __init__(self, base_url: str = None, model: str = None):
        # Allow overriding via environment variables
        self.base_url = base_url or os.getenv("AI_RADIO_LLM_URL", "http://localhost:11434")
        self.model = model or os.getenv("AI_RADIO_LLM_MODEL", "dolphin-llama3:latest")

    def generate(self, prompt: str, timeout: int = 30) -> str:
        """Call Ollama and return generated text.

        Ollama returns streaming NDJSON; we accumulate the response.
        Raises LLMError on failure.
        """
        try:
            payload = {"model": self.model, "prompt": prompt, "stream": False}
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # Ollama returns {'response': '...'}
            text = data.get("response", "")
            if not text:
                raise LLMError("Empty response from LLM")
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
    """Check if the Ollama service appears available by checking the base URL."""
    try:
        resp = requests.get(base_url, timeout=2)
        return resp.status_code == 200
    except Exception:
        return False
