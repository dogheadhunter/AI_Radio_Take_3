# AI Radio (minimal)

A minimal Python package for signal detection along with pytest configuration and VS Code debug setup.

## Setup

- Create a virtual environment:

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  pip install -r requirements.txt
  ```

- Run tests:

  ```powershell
  # Fast mock tests (default, no services needed)
  .\.venv\Scripts\pytest -q
  
  # Or using make:
  make test
  
  # Run integration tests (requires services)
  $env:TEST_MODE="integration"; .\.venv\Scripts\pytest -q
  
  # Or using make:
  make test-integration
  ```

- **See [tests/TESTING_MODES.md](tests/TESTING_MODES.md) for detailed testing documentation**

## Testing Strategy

This project uses a **dual testing approach**:

- **Mock Tests** (default): Fast tests using mocked services - perfect for development
- **Integration Tests**: Full end-to-end tests with real services - for validation

```powershell
# Daily development - fast mock tests
pytest                           # or: make test-mock

# Before deployment - full integration tests  
$env:TEST_MODE="integration"
pytest                           # or: make test-integration
```

Read [tests/TESTING_MODES.md](tests/TESTING_MODES.md) for complete details on the testing system.


## Services Setup

### Required Services for Content Generation

AI Radio requires two external services to generate content:

1. **Ollama (LLM Service)** - Port 11434
   - Download from: https://ollama.ai
   - Install and run: `ollama serve`
   - Pull required model: `ollama pull llama2`

2. **Chatterbox (TTS Service)** - Port 3000
   - Located in: `dev/chatterbox_server.py`
   - Start with: `python dev/chatterbox_server.py`
   - Uses voice references from: `assets/voice_references/`

### Verify Services are Running

```powershell
# Check Ollama (LLM)
Test-NetConnection localhost -Port 11434

# Check Chatterbox (TTS)
Test-NetConnection localhost -Port 3000
```

### Generate Content

```powershell
# Generate all time announcements (48 slots)
python scripts/generate_content.py --time-announcements --dj julie

# Generate weather announcements
python scripts/generate_content.py --weather-announcements --dj julie

# Generate song intros
python scripts/generate_content.py --intros --dj julie --limit 5

# Generate song outros
python scripts/generate_content.py --outros --dj julie --limit 5
```

## Debugging in VS Code

Open the workspace in VS Code. Use the `Run and Debug` view and pick `Python: Debug Tests` to run pytest with the debugger attached.
