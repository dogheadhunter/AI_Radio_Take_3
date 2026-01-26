- This project is scaffolded for quick Python development using pytest.
- To get started, create a venv, install requirements, and open the project in VS Code.
- Use the `Python: Debug Tests` launch configuration to run tests with the debugger.
- **Testing**: Use mock tests by default (`pytest` or `TEST_MODE=mock pytest`). Only run integration tests (`TEST_MODE=integration pytest`) when testing full end-to-end integration with real services (Ollama + TTS), and ask the user first before doing so. See `tests/TESTING_MODES.md` for full details on the dual testing system, `docs/TESTING_QUICK_REF.md` for quick reference, and `docs/MOCK_TESTING_SETUP.md` for implementation details.
- If a shell command isn't working as expected, confirm you're not inside the Python REPL (you'll see the `>>>` prompt). Exit the REPL with `exit()` or `quit()`, or use Ctrl+Z then Enter on Windows (Ctrl+D on macOS/Linux), then run the command in your terminal.

## AI Radio Development Workflow

This project uses a modular architecture. Follow these rules:

### Context Management
- **ALWAYS** start by reading `docs/LLM_CONTEXT.md` for quick project overview
- For detailed architecture, see `docs/ARCHITECTURE.md`
- **NEVER** read archived documentation unless explicitly asked
- If you feel lost, ask the user for clarification

### Code Organization
- Core utilities are in `src/ai_radio/core/`
- Pipeline stages are in `src/ai_radio/stages/`
- Generation backend is in `src/ai_radio/generation/`
- Tests mirror the source structure in `tests/`

### Testing Discipline
- Run tests after making changes: `pytest`
- Use mock tests for fast iteration (default)
- Only use integration tests with user permission

### File Locations
| Purpose | Path |
|---------|------|
| LLM context | `docs/LLM_CONTEXT.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Main README | `README.md` |
| Archived docs | `archive/` |
