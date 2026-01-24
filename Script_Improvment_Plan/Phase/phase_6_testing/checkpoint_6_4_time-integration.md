# Checkpoint 6.4: Time Announcement Pipeline Integration

#### Checkpoint 6.4: Time Announcement Pipeline Integration
**Wire up `--time` flag to existing time announcement generator.**

## Overview
Time announcements are different from songs—they're based on 48 time slots (every 30 min × 24 hours), not the song catalog. This checkpoint integrates time generation into the audit pipeline.

## Current State

**What exists:**
- `prompts_v2.py`: `build_time_prompt_v2()` ✅
- `pipeline.py`: `generate_time_announcement()` ✅
- `pipeline.py`: `generate_batch_time_announcements()` ✅

**What's different from songs:**
- No song catalog lookup needed
- 48 fixed time slots instead of 131 songs
- Format: `{hour:02d}-{minute:02d}` (e.g., "08-30" for 8:30 AM)
- Output structure: `data/generated/time/{dj}/{HH-MM}/`

## Tasks

### Task 1: Remove Blocking Error (for time)
- [x] Modify line 1047 to allow `--time`
- [x] Keep weather blocked until its checkpoint

### Task 2: Add Time Slot Generation
- [x] Create time slot list: 00:00, 00:30, 01:00, ..., 23:30
- [x] Add time content type to config handling
- [x] Integrate time announcement generation logic
- [x] Set output path to `data/generated/time/{dj}/{HH-MM}/`

### Task 3: Handle --limit for Time
- [x] `--limit N` generates first N slots in sequence for predictable testing
- [x] Document behavior in help text

### Task 4: Add Time Audit Support
- [x] Verify auditor works with time scripts
- [x] Time scripts work with existing auditor (no adjustments needed)
- [x] Regeneration loop supports time announcements

## Time Slot Structure

```python
# 48 time slots
TIME_SLOTS = [(h, m) for h in range(24) for m in [0, 30]]

# Examples:
# (0, 0)   -> "00-00" -> Midnight
# (8, 30)  -> "08-30" -> 8:30 AM
# (17, 0)  -> "17-00" -> 5:00 PM
# (23, 30) -> "23-30" -> 11:30 PM
```

**Output Structure:**
```
data/generated/time/
├── julie/
│   ├── 00-00/
│   │   └── julie_0.txt
│   ├── 00-30/
│   ├── 01-00/
│   └── ...
└── mr_new_vegas/
    ├── 00-00/
    └── ...
```

## Implementation Notes

**Key Differences:**
- Time prompts include hour/minute context
- Scripts should mention time naturally ("It's quarter past ten...")
- Very short output (1 sentence typical)
- No song/artist context needed

**Auditor Adjustments:**
- Length criteria may need relaxing (time scripts are short)
- Character voice still important
- Era appropriateness still applies

## Success Criteria

| Criterion | Target |
|-----------|--------|
| `--time` flag accepted | No error on CLI |
| Time scripts generated | Files in `data/generated/time/` |
| Correct folder structure | `{dj}/{HH-MM}/` |
| Audit works | Results in `data/audit/` |

## Validation

```powershell
# Should NOT error after integration
python scripts/generate_with_audit.py --time --dj julie --limit 3 --skip-audio

# Verify structure
Get-ChildItem data\generated\time\julie\ -Directory

# Should see folders like: 00-00, 00-30, 01-00, etc.
```

## Implementation Summary

**Status: ✅ COMPLETE**

### Changes Made

**File Modified:** `scripts/generate_with_audit.py`

**New Functions Added:**
- `get_time_script_path(hour, minute, dj)` - Path helper for time scripts
- `get_time_audio_path(hour, minute, dj)` - Path helper for time audio
- `get_time_audit_path(hour, minute, dj, passed)` - Path helper for time audits

**Functions Updated:**
- `run_pipeline()` - Added time slot generation logic (48 slots)
- `stage_generate()` - Added time announcement generation loop
- `stage_audit()` - Added time announcement audit support
- `stage_regenerate()` - Added time announcement regeneration and re-audit
- `main()` - Updated help text and validation

### Key Features

✅ **48 Time Slots**: Generates announcements for every 30 minutes (00:00-23:30)  
✅ **`--limit` Support**: With `--limit N`, generates first N time slots for testing  
✅ **Full Pipeline**: Generation → Audit → Regeneration all working  
✅ **Multi-DJ**: Works with both julie and mr_new_vegas  
✅ **Proper Paths**: `data/generated/time/{dj}/{HH-MM}/`

### Test Results

```powershell
# Test with 3 time slots
python scripts/generate_with_audit.py --time --dj julie --limit 3 --skip-audio
# ✅ Generated 3 scripts, audited, regenerated failures

# Test with both DJs, 5 slots
python scripts/generate_with_audit.py --time --dj all --limit 5 --skip-audio
# ✅ Generated 10 scripts (5 × 2 DJs), full pipeline working
```

### Output Structure

```
data/generated/time/
├── julie/
│   ├── 00-00/julie_0.txt
│   ├── 00-30/julie_0.txt
│   ├── 01-00/julie_0.txt
│   └── ...
└── mr_new_vegas/
    ├── 00-00/mr_new_vegas_0.txt
    └── ...

data/audit/
├── julie/
│   ├── passed/
│   │   ├── 00-00_time_announcement_audit.json
│   │   └── ...
│   └── failed/
│       └── ...
└── mr_new_vegas/
    └── ...
```

### Next Steps

Ready for **Checkpoint 6.5: Weather Announcement Integration** when needed.
