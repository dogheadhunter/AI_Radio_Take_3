- This project is scaffolded for quick Python development using pytest.
- To get started, create a venv, install requirements, and open the project in VS Code.
- Use the `Python: Debug Tests` launch configuration to run tests with the debugger.
- **Testing**: Use mock tests by default (`pytest` or `TEST_MODE=mock pytest`). Only run integration tests (`TEST_MODE=integration pytest`) when testing full end-to-end integration with real services (Ollama + TTS), and ask the user first before doing so. See `tests/TESTING_MODES.md` for full details on the dual testing system, `docs/TESTING_QUICK_REF.md` for quick reference, and `docs/MOCK_TESTING_SETUP.md` for implementation details.
- If a shell command isn't working as expected, confirm you're not inside the Python REPL (you'll see the `>>>` prompt). Exit the REPL with `exit()` or `quit()`, or use Ctrl+Z then Enter on Windows (Ctrl+D on macOS/Linux), then run the command in your terminal.

## Script Improvement Plan Workflow

This project uses a checkpoint-based workflow to prevent context rot during LLM execution.

### Key Files (Read Every Session)

- `Script_Improvement_Plan/CURRENT_STATUS.md` - Single source of truth for where we are
- `Script_Improvement_Plan/CRITICAL_CONTEXT.md` - Hard-won learnings that MUST carry forward

### Workflow Rules

1. **Work on ONE checkpoint at a time** - Don't jump ahead or work on multiple checkpoints
2. **Read only the checkpoint file you're working on** - Avoid loading entire phase files (causes context rot)
3. **Complete ALL success criteria** before moving on - No partial completions
4. **Use checkpoint-executor agent** for focused execution of individual checkpoints
5. **Update CURRENT_STATUS.md at session end** - Keep status current

### Session Start Protocol

1. Read `Script_Improvement_Plan/CURRENT_STATUS.md` - Know where we are
2. Read `Script_Improvement_Plan/CRITICAL_CONTEXT.md` - Load key learnings
3. Read the specific checkpoint file (e.g., `phase_2_prompts/checkpoint_2_3.md`)
4. Confirm understanding before starting work

### Session End Protocol

1. Update checkbox status in checkpoint file
2. Update `Script_Improvement_Plan/CURRENT_STATUS.md` with progress
3. Commit with message: `checkpoint X.Y: [description]`
4. State "Checkpoint X.Y ready for audit"

### DO NOT

- Load entire phase files (too much context)
- Skip success criteria to "move faster"
- Move to next checkpoint without audit verification
- Forget to read CRITICAL_CONTEXT.md
- Work on multiple checkpoints simultaneously

### Critical Learnings

**Voice-First Prompting (Phase 2):**
- Teach voice through authentic examples, not restriction lists
- LLM learns from "sound like this" not "don't say that"

**Batch Ordering (Phase 3):**
- Generate ALL Julie scripts, THEN all Mr. NV scripts
- Character bleed drops from 78% to 20% with correct ordering

**Multi-Stage Validation (Phase 3):**
- Stage 1: Rule-based (fast, deterministic)
- Stage 2: LLM character validation (subjective)
- Stage 3: Human calibration

### Agents and Prompts

- Use `checkpoint-executor.agent.md` for focused checkpoint work
- Use `session-start.prompt.md` to properly load context
- Use `checkpoint-complete.prompt.md` before declaring done
