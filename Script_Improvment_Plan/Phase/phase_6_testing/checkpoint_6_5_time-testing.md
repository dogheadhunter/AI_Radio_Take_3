# Checkpoint 6.5: Time Announcement Quality Testing

#### Checkpoint 6.5: Time Announcement Quality Testing
**Validate time announcement quality through progressive testing.**

## Overview
Time announcements are simpler than song intros but have unique requirements—natural time expression, varied phrasing to avoid repetition across 48 slots.

## Prerequisites
- [ ] Checkpoint 6.4 complete (time integration done)
- [ ] `--time` flag works without errors

## Tasks

### Task 1: Smoke Test (3 slots)
- [ ] Run `--time --dj all --limit 3 --skip-audio`
- [ ] Verify 6 scripts generated (3 × 2 DJs)
- [ ] Check that time is mentioned naturally
- [ ] Verify no obvious issues

### Task 2: Character Test (6 slots per DJ)
- [ ] Run `--time --dj julie --limit 6 --skip-audio`
- [ ] Run `--time --dj mr_new_vegas --limit 6 --skip-audio`
- [ ] Verify Julie's casual, personal style
- [ ] Verify Mr. NV's smooth, romantic style
- [ ] Check variety in phrasing

### Task 3: Edge Time Tests
- [ ] Test midnight (00:00) - handle "midnight" vs "12 AM"
- [ ] Test noon (12:00) - handle "noon" vs "12 PM"
- [ ] Test half hours - natural phrasing ("half past", "30")
- [ ] Verify no anachronistic time formats

### Task 4: Full Slot Test (all 48)
- [ ] Run `--time --dj all --skip-audio` (no limit)
- [ ] Verify 96 scripts generated (48 × 2 DJs)
- [ ] Check pass rate
- [ ] Review variety across time slots

## Commands

```powershell
# Clean time data
Remove-Item -Path "data\generated\time\*" -Recurse -Force -ErrorAction SilentlyContinue

# Smoke test
python scripts/generate_with_audit.py --time --dj all --limit 3 --skip-audio

# Character tests
python scripts/generate_with_audit.py --time --dj julie --limit 6 --skip-audio
python scripts/generate_with_audit.py --time --dj mr_new_vegas --limit 6 --skip-audio

# Full test
python scripts/generate_with_audit.py --time --dj all --skip-audio

# Check results
Get-Content data\audit\summary.json
```

## Time-Specific Quality Checks

### Natural Time Expression
- [ ] "It's ten o'clock" ✅
- [ ] "The time is 10:00 AM" ❌ (too robotic)
- [ ] "Quarter past eight" ✅
- [ ] "It's 8:15 AM" ❌ (too digital)

### Era-Appropriate Phrasing
- [ ] No "24-hour time" unless contextual
- [ ] Natural radio DJ phrasing
- [ ] Variety: "The time is...", "It's...", "Just about..."

### Character Voice
**Julie:**
- Casual, personal ("Hey, it's about 3 o'clock...")
- May comment on time of day
- Friendly, conversational

**Mr. New Vegas:**
- Smooth, polished ("The time is...")
- May add romantic touch
- Professional but warm

## Expected Quality Metrics

| Test | Initial Pass Rate | Final Pass Rate |
|------|-------------------|-----------------|
| Smoke (6 scripts) | >70% | >95% |
| Julie (6 scripts) | >70% | >95% |
| Mr. NV (6 scripts) | >70% | >95% |
| Full (96 scripts) | >70% | >95% |

## Success Criteria

| Criterion | Target |
|-----------|--------|
| All 48 slots generate | 96 scripts total |
| Natural time expression | No robotic phrasing |
| Character consistency | Matches DJ personality |
| Variety | No identical scripts |
| Pass rate | >95% after regen |

## Validation Checklist

- [ ] Smoke test completes without errors
- [ ] Both DJs have appropriate time phrasing
- [ ] Midnight/noon handled correctly
- [ ] Half hours sound natural
- [ ] Full 48-slot run succeeds
- [ ] Ready to proceed to weather integration

## Notes

Document time-specific observations:
```
Date: 
Time Expression Quality:
- 

Variety Assessment:
- 

Prompt Adjustments Needed:
- 
```
