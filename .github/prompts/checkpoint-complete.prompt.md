---
description: 'Complete a checkpoint and prepare for audit'
---

# Checkpoint Complete

Before marking a checkpoint complete, follow this protocol to ensure quality and proper handoff.

## Pre-Completion Checklist

Work through this checklist before declaring a checkpoint complete:

### 1. Success Criteria Verification

- [ ] ALL success criteria checkboxes in checkpoint file are checked
- [ ] No partial completions - if criteria not met, don't check the box
- [ ] If success criteria can't be met, document why and get approval to modify

### 2. Testing Verification

Run relevant tests based on checkpoint type:

**Code checkpoints:**
```bash
# Run specific tests for the files you changed
pytest tests/generation/test_file_name.py -v

# Or run all tests in relevant area
pytest tests/generation/ -v
```

**Documentation checkpoints:**
- Verify all required files exist
- Check that cross-references are correct
- Ensure examples are accurate

### 3. Quality Checks

- [ ] Code follows project conventions
- [ ] Documentation is clear and complete
- [ ] No TODO or FIXME comments left unresolved
- [ ] All output files in correct locations
- [ ] File names match specifications

### 4. Update Documentation

Update these files:

**A. Checkpoint File Itself**
```markdown
## Status
**✅ COMPLETE** - [brief note on completion]
```

**B. CURRENT_STATUS.md**
```markdown
**Current Phase:** Phase X
**Current Checkpoint:** X.Y - [Name]

Progress:
- [x] Task 1 completed
- [x] Task 2 completed
- [x] All success criteria met

**Status:** Checkpoint X.Y complete. Ready for checkpoint X.Y+1.
```

### 5. Commit Changes

Create a descriptive commit:

```bash
git add .
git commit -m "checkpoint X.Y: [description of what was accomplished]"
```

**Commit message format:**
- Start with `checkpoint X.Y:`
- Brief description of deliverable
- Examples:
  - `checkpoint 2.2: create Julie prompt template with validation`
  - `checkpoint 3.1: design multi-stage validation architecture`
  - `checkpoint 4.3: integrate lyrics into generation pipeline`

### 6. Declare Completion

State clearly:

```
✅ Checkpoint X.Y complete and ready for audit.

Deliverables:
- [file 1]
- [file 2]
- [etc]

Tests: [PASS/status]
Success Criteria: [All met/X of Y met]
```

## Audit Readiness

A checkpoint is ready for audit when:

- ✅ All success criteria met
- ✅ All tests passing (or documented why skipped)
- ✅ All deliverables created and in correct locations
- ✅ Documentation updated (checkpoint file + CURRENT_STATUS.md)
- ✅ Changes committed with clear message
- ✅ You can explain what was done and why

## What Happens Next

After declaring checkpoint complete:

1. **Auditor Agent** (or human) reviews the work
2. They verify success criteria are genuinely met
3. They check tests pass
4. They validate deliverables

If audit passes:
- Checkpoint officially marked complete
- Move to next checkpoint

If audit finds issues:
- Issues documented
- You address them
- Checkpoint re-submitted for audit

## Common Mistakes to Avoid

❌ **Checking success criteria boxes without actually completing them**  
Fix: Only check boxes for truly complete items

❌ **Skipping tests because "they'll probably pass"**  
Fix: Always run tests before declaring complete

❌ **Forgetting to update CURRENT_STATUS.md**  
Fix: Make this a required step, not optional

❌ **Vague commit messages like "updates" or "fixes"**  
Fix: Use checkpoint X.Y format with specific description

❌ **Moving to next checkpoint without audit**  
Fix: Wait for audit confirmation before proceeding

## Example Completion Flow

```
# After completing all tasks in checkpoint 2.3

1. Check all success criteria: ✅ All 6 criteria met
2. Run tests: pytest tests/generation/test_prompts_v2.py -v ✅ PASS
3. Update checkpoint_2_3.md: Status → ✅ COMPLETE
4. Update CURRENT_STATUS.md: Checkpoint 2.3 done, ready for 2.4
5. Commit: "checkpoint 2.3: create Mr. New Vegas prompt template"
6. Declare: "Checkpoint 2.3 ready for audit"
```

## Remember

Quality over speed. A well-executed checkpoint that passes audit on first try is better than rushing through and needing multiple revision cycles.

Take the time to verify everything is complete before declaring done.
