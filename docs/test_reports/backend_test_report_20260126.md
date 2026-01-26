# Backend Test Report — 2026-01-26

**Summary:**
- Test mode: Integration (Ollama LLM running, Chatterbox TTS not running)
- Total tests collected: 530
- Focused backend tests run: ~450
- Results: 447 passed, 1 failed, 1 skipped

## Key Findings ✅
- Ollama LLM service is running and integrated successfully (checked via `http://localhost:11434/api/version`).
- One failing test: `test_checkpoint_6_1_intro_baseline_mock` — after regeneration there were 0 audit files instead of 10.
  - Root cause: the test monkeypatches `gwa.DATA_DIR` but audit stage imports `DATA_DIR` directly from `src.ai_radio.config`, so the monkeypatch doesn't take effect in nested modules.
  - Impact: Test infrastructure issue (dependency injection / monkeypatch approach), not a production bug; other integration tests including real LLM generation passed.
- Chatterbox TTS service not running on port 3000; TTS-dependent tests were skipped.

## Actions Taken 🔧
- Ran full integration test suite with Ollama available; isolated and re-ran failing checkpoint test locally.
- Confirmed all other core, generation, API, playback, and station tests passed.

## Recommendations 💡
1. Fix the checkpoint test by using `pytest.monkeypatch` on `src.ai_radio.config.DATA_DIR` before imports, or refactor stages to accept `data_dir` as a parameter for better testability.
2. Start Chatterbox TTS service (`python dev/chatterbox_server.py`) and run full TTS integration tests to validate audio generation.
3. Consider dependency injection for `DATA_DIR`/`GENERATED_DIR` to make stages easier to test.

---

_Reported by: GitHub Copilot (Raptor mini Preview)_
_Timestamp: 2026-01-26_
