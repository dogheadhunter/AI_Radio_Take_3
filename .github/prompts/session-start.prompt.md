---
description: 'Initialize a development session with proper context loading'
---

# Session Start Protocol

Before beginning work, establish context:

1. **Check Documentation**
   - Read `docs/LLM_CONTEXT.md` for project overview
   - For detailed architecture, see `docs/ARCHITECTURE.md`

2. **Understand Project Structure**
   - Core utilities: `src/ai_radio/core/`
   - Pipeline stages: `src/ai_radio/stages/`
   - Generation backend: `src/ai_radio/generation/`

3. **Verify Environment**
   - Confirm you're in the correct repository
   - Check that tests pass: `pytest`

4. **State Your Understanding**
   Before making any changes, summarize:
   - What you understand about the task
   - Which modules you expect to modify
   - How you'll test your changes

5. **Begin Work**
   - Focus on the specific task requested
   - Use mock tests for fast iteration
   - Commit changes with descriptive messages
