# Testing Quick Reference

## Run Tests

```powershell
# Default: Fast mock tests (recommended for development)
pytest

# Integration tests (requires Ollama + TTS services)
$env:TEST_MODE="integration"; pytest

# Run specific test file
pytest tests/generation/test_pipeline_mock.py

# Verbose output
pytest -v

# Stop at first failure
pytest -x
```

## Make Commands

```powershell
make test              # Default tests
make test-mock         # Explicitly run mock tests
make test-integration  # Run integration tests
make test-all          # Run everything with verbose output
```

## Python Helper Script

```powershell
# Mock mode (fast)
python run_tests.py

# Integration mode (requires services)
python run_tests.py --integration

# With pytest options
python run_tests.py -v -k weather
python run_tests.py --integration -x
```

## Test Markers

```python
@pytest.mark.mock                # Mock/fast test
@pytest.mark.integration         # Integration test (auto-skipped in mock mode)
@pytest.mark.requires_services   # Needs external services
@pytest.mark.slow                # Slow test
```

## Common Patterns

### Writing a Mock Test
```python
@pytest.mark.mock
def test_something(tmp_path, mock_services):
    pipeline = GenerationPipeline(output_dir=tmp_path)
    result = pipeline.do_something()
    assert result.success
```

### Writing an Integration Test
```python
@pytest.mark.integration
@pytest.mark.requires_services
def test_something_integration(tmp_path):
    if not check_ollama_available():
        pytest.skip("Ollama not available")
    
    pipeline = GenerationPipeline(output_dir=tmp_path)
    result = pipeline.do_something()
    assert result.success
```

## Environment Variables

```powershell
# Set test mode
$env:TEST_MODE="mock"         # or "integration"

# Check current mode
python -c "from tests.test_modes import get_test_mode; print(get_test_mode())"
```

## Troubleshooting

**Tests running slow?**
- Check that `TEST_MODE=mock` (default)
- Look for warnings about model loading

**Integration tests skipped?**
- This is normal in mock mode
- Set `TEST_MODE=integration` to run them

**Need to test both modes?**
```powershell
# Run mock tests
$env:TEST_MODE="mock"; pytest tests/generation/

# Then run integration tests
$env:TEST_MODE="integration"; pytest tests/generation/
```

## File Locations

- Mock tests: `tests/generation/test_pipeline_mock.py`
- Integration tests: `tests/generation/test_pipeline_integration.py`
- Fixtures: `tests/conftest.py`
- Documentation: `tests/TESTING_MODES.md`
- This reference: `docs/TESTING_QUICK_REF.md`
