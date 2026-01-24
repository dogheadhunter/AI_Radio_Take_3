"""Tests for LLM client."""
import pytest
from unittest.mock import patch
from src.ai_radio.generation.llm_client import LLMClient, generate_text, check_ollama_available
from src.ai_radio.utils.errors import LLMError


def test_generate_returns_string(monkeypatch):
    class Dummy:
        def generate(self, prompt, banned_phrases=None):
            return "Generated response"

    client = Dummy()
    result = generate_text(client, "Test prompt")
    assert isinstance(result, str)


def test_generate_raises_on_error(monkeypatch):
    class Broken:
        def generate(self, prompt):
            raise Exception("boom")

    with pytest.raises(LLMError):
        generate_text(Broken(), "Test prompt")


def test_check_available_returns_bool():
    assert isinstance(check_ollama_available(), bool)


import pytest

@pytest.mark.integration
@pytest.mark.slow
def test_real_generation_integration():
    """Call Ollama if available and assert non-empty response.

    Be defensive: if the generate endpoint returns 404 (service present but no
    generate route), skip the test instead of failing the suite.
    """
    if not check_ollama_available():
        pytest.skip("Ollama not available")

    client = LLMClient()
    try:
        result = generate_text(client, "Say 'hello' and nothing else.")
    except LLMError as exc:
        # If the remote service responded with 404 for the generate endpoint,
        # treat as unavailable for purposes of integration tests.
        msg = str(exc).lower()
        if "404" in msg or "not found" in msg:
            pytest.skip("Ollama generate endpoint not available (404)")
        raise

    assert isinstance(result, str)
    assert len(result) > 0
