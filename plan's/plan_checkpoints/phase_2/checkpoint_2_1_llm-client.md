# Checkpoint 2.1: LLM Client

#### Checkpoint 2.1: LLM Client
**Interface with Ollama for text generation.**

**Tasks:**
1. Create `src/ai_radio/generation/llm_client.py`
2. Create synchronous interface to Ollama
3. Handle errors and timeouts

**Tests First (With Mocking):**
```python
# tests/generation/test_llm_client.py
"""Tests for LLM client."""
import pytest
from unittest. mock import Mock, patch
from src.ai_radio.generation.llm_client import (
    LLMClient,
    generate_text,
    check_ollama_available,
)


class TestLLMClient:
    """Test LLM client operations."""
    
    def test_generate_returns_string(self, mock_ollama):
        """Generate must return a string."""
        client = LLMClient()
        result = generate_text(client, "Test prompt")
        assert isinstance(result, str)
    
    def test_generate_returns_nonempty(self, mock_ollama):
        """Generate must return non-empty string."""
        mock_ollama.return_value = "Generated response"
        client = LLMClient()
        result = generate_text(client, "Test prompt")
        assert len(result) > 0
    
    def test_raises_on_ollama_error(self, mock_ollama_error):
        """Must raise LLMError when Ollama fails."""
        from src.ai_radio.utils.errors import LLMError
        client = LLMClient()
        with pytest.raises(LLMError):
            generate_text(client, "Test prompt")
    
    def test_check_available_returns_bool(self):
        """Availability check must return boolean."""
        result = check_ollama_available()
        assert isinstance(result, bool)


class TestLLMClientIntegration:
    """Integration tests that call real Ollama. 
    
    These tests are marked slow and require Ollama running.
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_generation(self):
        """Actually call Ollama and get a response."""
        if not check_ollama_available():
            pytest.skip("Ollama not available")
        
        client = LLMClient()
        result = generate_text(client, "Say 'hello' and nothing else.")
        assert len(result) > 0
```

**Success Criteria:**
- [ ] Unit tests pass with mocking
- [ ] Integration test passes when Ollama is running
- [ ] Errors are caught and wrapped in `LLMError`

**Git Commit:** `feat(generation): add LLM client`
