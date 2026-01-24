---
description: 'Start a new work session with proper context loading'
---

# Session Start

Before starting work on the Script Improvement Plan, load the required context.

## Context Loading Steps

Follow these steps IN ORDER:

### 1. Check Current Status
```
Read: Script_Improvement_Plan/CURRENT_STATUS.md
```

This tells you:
- Which phase we're in
- Which checkpoint we're working on
- What's been completed
- Any blockers

### 2. Load Critical Context
```
Read: Script_Improvement_Plan/CRITICAL_CONTEXT.md
```

This contains hard-won learnings that MUST carry forward:
- Voice-first prompting (teach by example, not restriction)
- Batch ordering matters (all Julie, then all Mr. NV)
- Multi-stage validation architecture
- Red flags by DJ character

**DO NOT skip this** - these learnings prevent repeating past mistakes.

### 3. Load Checkpoint File
```
Read: Script_Improvement_Plan/phase_X_name/checkpoint_X_Y.md
```

This contains:
- Goal for THIS checkpoint only
- Tasks to complete
- Success criteria
- Validation commands

### 4. Confirm Understanding

Before proceeding, confirm:
- ✅ I know which checkpoint I'm working on
- ✅ I've read the critical context
- ✅ I understand the goal and tasks
- ✅ I know what success looks like

## What NOT to Do

❌ **Don't read entire phase files** - they're too large and cause context rot  
❌ **Don't read other checkpoints** - stay focused on your current one  
❌ **Don't skip CRITICAL_CONTEXT.md** - those learnings must carry forward  
❌ **Don't start work before confirming the checkpoint** - make sure you're working on the right thing  

## Example Session Start

```
User: "Start work on the Script Improvement Plan"

Agent:
1. Reading Script_Improvement_Plan/CURRENT_STATUS.md...
   - Current Phase: Phase 4 - Lyrics Integration
   - Current Checkpoint: 4.2 - Lyrics Context Extraction
   
2. Reading Script_Improvement_Plan/CRITICAL_CONTEXT.md...
   - Key learnings noted: voice-first prompting, batch ordering, multi-stage validation
   
3. Reading Script_Improvement_Plan/phase_4_lyrics/checkpoint_4_2.md...
   - Goal: Create meaningful context summaries from lyrics
   - Tasks: Identify themes/mood, extract notable lines, create brief summaries, handle instrumental
   
4. Ready to begin checkpoint 4.2. Shall I proceed?
```

## Quick Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `CURRENT_STATUS.md` | Know where we are | Every session start |
| `CRITICAL_CONTEXT.md` | Key learnings | Every session start |
| `checkpoint_X_Y.md` | Current work | Every session start |
| `MASTER_PLAN.md` | Overall vision | Project start only |
| `README.md` (per phase) | Phase overview | When starting new phase |
| `GATE.md` (per phase) | Gate criteria | When completing phase |

## Ready to Work?

After loading context, you're ready to execute the checkpoint. Follow the tasks in order, complete all success criteria, run tests, and update status when done.

Good luck! 🎯
