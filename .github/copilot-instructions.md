- This project is scaffolded for quick Python development using pytest.
- To get started, create a venv, install requirements, and open the project in VS Code.
- Use the `Python: Debug Tests` launch configuration to run tests with the debugger.
- **Testing**: Use mock tests by default (`pytest` or `TEST_MODE=mock pytest`). Only run integration tests (`TEST_MODE=integration pytest`) when testing full end-to-end integration with real services (Ollama + TTS), and ask the user first before doing so. See `tests/TESTING_MODES.md` for full details on the dual testing system, `docs/TESTING_QUICK_REF.md` for quick reference, and `docs/MOCK_TESTING_SETUP.md` for implementation details.
- If a shell command isn't working as expected, confirm you're not inside the Python REPL (you'll see the `>>>` prompt). Exit the REPL with `exit()` or `quit()`, or use Ctrl+Z then Enter on Windows (Ctrl+D on macOS/Linux), then run the command in your terminal.

## AI Radio Development Workflow

This project uses a phased checkpoint system. Follow these rules:

### Context Management
- **ALWAYS** start by reading `Script_Improvement_Plan/STATUS.md`
- **ONLY** load the current checkpoint file, not completed ones
- **NEVER** read archived documentation unless explicitly asked
- If you feel lost, ask the user to clarify the current checkpoint

### Checkpoint Discipline
- Complete ALL success criteria before moving on
- Run the Auditor agent to verify completion
- Update STATUS.md after each checkpoint
- Commit with descriptive messages

### Avoiding Context Rot
- Keep responses focused on the current task
- Do not reference completed phases unless relevant
- If context seems stale, re-read STATUS.md and CONTEXT.md
- Ask clarifying questions rather than guessing

### File Locations
| Purpose | Path |
|---------|------|
| Current status | `Script_Improvement_Plan/STATUS.md` |
| Essential context | `Script_Improvement_Plan/CONTEXT.md` |
| Current checkpoint | `Script_Improvement_Plan/phase_6_testing/checkpoint_6_8_*.md` |
| Archived phases | `archive/` |
