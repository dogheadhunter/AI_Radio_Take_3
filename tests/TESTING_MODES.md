# Testing Modes: Mock vs Integration

This project uses a dual testing strategy that allows you to switch between fast mock tests and comprehensive integration tests.

## Quick Start

### Run Fast Mock Tests (Default)
```bash
# Run all tests with mocks (fast, no external services needed)
pytest

# Or explicitly:
TEST_MODE=mock pytest
```

### Run Real Integration Tests
```bash
# Run all tests including integration tests (requires services)
TEST_MODE=integration pytest

# Run only integration tests
TEST_MODE=integration pytest -m integration
```

## Test Modes Explained

### Mock Mode (Default - Fast ⚡)
- **Speed**: Very fast (~seconds)
- **Requirements**: None - no external services needed
- **Coverage**: Tests all code paths and logic
- **Use when**:
  - Developing new features
  - Running tests in CI/CD
  - Quick verification during development
  - Testing on machines without GPU/services

**What's mocked**:
- LLM (Ollama) responses - returns realistic generated text
- TTS (Chatterbox) audio - creates valid WAV files with proper format
- Service availability checks

### Integration Mode (Thorough 🔍)
- **Speed**: Slower (~minutes)
- **Requirements**: 
  - Ollama running on localhost:11434
  - Chatterbox TTS model loaded (GPU recommended)
- **Coverage**: Tests real service integration
- **Use when**:
  - Verifying changes to LLM/TTS integration
  - Before deploying to production
  - Testing with actual models
  - Validating voice quality

**What's real**:
- Actual LLM text generation
- Real TTS audio synthesis
- Network calls to services
- Model inference

## Test Organization

### Mock Tests
- Location: `tests/generation/test_pipeline_mock.py`
- Markers: `@pytest.mark.mock`
- Focus: Logic, orchestration, error handling, file organization

### Integration Tests
- Location: `tests/generation/test_pipeline_integration.py`
- Markers: `@pytest.mark.integration`, `@pytest.mark.requires_services`
- Focus: End-to-end functionality, service communication

## Fixtures Available

### Mock Fixtures (from conftest.py)

```python
# Simple mocks
mock_llm          # Basic LLM mock
mock_tts          # Basic TTS mock

# Realistic mocks (recommended)
mock_llm_realistic     # Context-aware LLM responses
mock_tts_realistic     # Proper WAV file generation
mock_services          # Both LLM + TTS mocked
mock_service_checks    # Service availability returns True
```

### Example Test Usage

```python
@pytest.mark.mock
def test_my_feature(tmp_path, mock_services):
    """Mock test - fast, no services needed."""
    pipeline = GenerationPipeline(output_dir=tmp_path)
    result = pipeline.generate_song_intro(...)
    assert result.success

@pytest.mark.integration
@pytest.mark.requires_services
def test_my_feature_integration(tmp_path):
    """Integration test - requires real services."""
    if not check_ollama_available():
        pytest.skip("Ollama not available")
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    result = pipeline.generate_song_intro(...)
    assert result.success
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# Fast tests on every PR
- name: Run Tests
  run: |
    TEST_MODE=mock pytest tests/
  
# Nightly integration tests
- name: Integration Tests
  if: github.event_name == 'schedule'
  run: |
    # Start services
    docker-compose up -d
    # Run integration tests
    TEST_MODE=integration pytest tests/
```

## Environment Variables

- `TEST_MODE`: Controls test mode
  - `mock` (default): Fast tests with mocks
  - `integration`: Real tests with services

## Markers Reference

- `@pytest.mark.mock`: Mock/fast test
- `@pytest.mark.integration`: Integration test (auto-skipped in mock mode)
- `@pytest.mark.slow`: Slow test
- `@pytest.mark.requires_services`: Requires external services

## Benefits of This Approach

✅ **Fast Development Cycle**: Mock tests run in seconds
✅ **No Service Dependencies**: Can test without GPU or services
✅ **Same Coverage**: Mock tests verify all logic paths
✅ **Confidence Before Deploy**: Integration tests validate real behavior
✅ **Flexible**: Easy to toggle between modes
✅ **CI-Friendly**: Fast tests on every commit, integration tests nightly

## Common Workflows

### Daily Development
```bash
# Make changes
# Run fast tests
pytest
# If passing, commit
```

### Before Major Release
```bash
# Start all services
docker-compose up -d
# Run full integration suite
TEST_MODE=integration pytest tests/
# Verify everything works end-to-end
```

### Debugging Service Issues
```bash
# Run only integration tests to isolate service problems
TEST_MODE=integration pytest tests/generation/test_pipeline_integration.py -v
```

### Testing Specific Features
```bash
# Test only mock tests for a module
pytest tests/generation/test_pipeline_mock.py

# Test both mock and integration for a feature
TEST_MODE=integration pytest tests/generation/ -k "weather"
```

## Adding New Tests

When adding new functionality, create **both**:

1. **Mock test** (in `test_pipeline_mock.py`):
   - Use `@pytest.mark.mock`
   - Use `mock_services` fixture
   - Focus on logic and edge cases
   - Should be fast

2. **Integration test** (in `test_pipeline_integration.py`):
   - Use `@pytest.mark.integration` and `@pytest.mark.requires_services`
   - Check service availability
   - Focus on end-to-end behavior
   - Can be slower

## Troubleshooting

**Q: Tests are being skipped in mock mode**
- This is expected for `@pytest.mark.integration` tests
- Set `TEST_MODE=integration` to run them

**Q: Integration tests fail with "services not available"**
- Ensure Ollama is running: `curl http://localhost:11434`
- Ensure TTS is available: Check Docker container or local model
- Use mock mode if services aren't needed: `TEST_MODE=mock pytest`

**Q: Want to run integration tests for just one test**
```bash
TEST_MODE=integration pytest tests/generation/test_pipeline_integration.py::test_specific_test
```

## Test Cleanup Notes (January 2026)

As part of the pipeline refactor, the following test improvements were made:

### Mock Fixtures Fixed
- Fixed `mock_llm_realistic` fixture to patch `generate_text` in both `llm_client` and `pipeline` modules
- Fixed `mock_tts_realistic` fixture similarly for TTS
- Fixed `mock_llm_auditor_mixed` to correctly extract script content from audit prompts
- Updated `FakeAuditorClient` to use regex extraction for script content

### Voice Reference Files
The `mock_services` fixture now creates placeholder voice reference WAV files, since the pipeline checks for their existence before generating audio.

### Pipeline Tests Updated
- Tests updated to expect `_full.wav` files (dual audio support)
- `test_llm_called_before_tts` updated to allow multiple TTS calls

### Integration Tests Marked
The following tests require complex module patching or actual services:
- `test_checkpoint_6_1_intro_baseline.py` - marked as `@pytest.mark.integration`
- `test_checkpoint_6_2_outro_integration.py` - marked as `@pytest.mark.integration`

These are skipped in mock mode and should be run with `TEST_MODE=integration` when services are available.
