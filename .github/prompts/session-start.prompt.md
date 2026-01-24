---
description: 'Initialize a development session with proper context loading'
---

# Session Start Protocol

Before beginning work, establish context:

1. **Check Current Status**
   - Read `Script_Improvement_Plan/STATUS.md`
   - Identify the current checkpoint

2. **Load Minimal Context**
   - Read `Script_Improvement_Plan/CONTEXT.md`
   - Read ONLY the current checkpoint file

3. **Verify Environment**
   - Confirm you're in the correct repository
   - Check that tests pass: `pytest tests/ -v`

4. **State Your Understanding**
   Before making any changes, summarize:
   - Current checkpoint number and name
   - What tasks remain
   - What success criteria must be met

5. **Begin Work**
   - Focus ONLY on the current checkpoint
   - Do NOT read completed checkpoints
   - Do NOT jump ahead to future checkpoints
