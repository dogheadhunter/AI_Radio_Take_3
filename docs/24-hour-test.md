# 24-Hour Validation Test Guide

## Overview
This guide walks you through running a 24-hour validation test of the AI Radio Station to verify it can run continuously without manual intervention.

## Pre-Flight Checklist

Before starting the 24-hour test, verify:

### Content Verification
- [ ] Catalog contains all songs (`python scripts/scan_library.py <music_path>`)
- [ ] All songs have at least one generated intro (Julie and Mr. New Vegas)
- [ ] Time announcements generated for all 48 slots (every 30 min × 2 DJs)
- [ ] Weather templates generated (if weather enabled)
- [ ] At least one radio show episode ready (if shows enabled)
- [ ] DJ handoff audio generated

### System Verification
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Station starts without errors: `python -m ai_radio --dry-run`
- [ ] Ollama is not needed during playback (all content pre-generated)
- [ ] Chatterbox is not needed during playback (all content pre-generated)
- [ ] Log directory has write permissions
- [ ] Adequate disk space for 24 hours of logs

### Configuration Verification
- [ ] Music library path is correct
- [ ] Weather API key is configured (or weather disabled with `--no-weather`)
- [ ] Shows directory contains episode(s) (or shows disabled with `--no-shows`)

### Environmental Verification
- [ ] Computer will not sleep during test
- [ ] Screen saver won't interfere
- [ ] No scheduled restarts or updates
- [ ] Audio output is configured correctly

## Running the Test

### Option 1: Automated Validation Mode (Recommended)

Run the built-in validation mode:

```bash
python -m ai_radio --validate-24h
```

This will:
- Start the station
- Create checkpoints every hour
- Log all activity
- Generate a validation report at the end
- Save results to `logs/validation_YYYYMMDD_HHMMSS.json`

**Custom duration:**
```bash
# Run for 12 hours instead
python -m ai_radio --validate-24h --duration 12.0

# Run with checkpoints every 30 minutes
python -m ai_radio --validate-24h --checkpoint-interval 30.0
```

### Option 2: Manual Test with Helper Script

Use the helper script to run and monitor manually:

```bash
python scripts/24h_test.py
```

This script will:
- Prompt you through the pre-flight checklist
- Start the station
- Remind you to check in at intervals
- Help you log observations

### Option 3: Fully Manual Test

1. **Start the station** at a memorable time (e.g., 8:00 AM):
   ```bash
   python -m ai_radio
   ```

2. **Record start time and initial state** in a log file

3. **Check in at intervals:**
   - +1 hour: Still running?
   - +4 hours: Still running? Any errors in log?
   - +8 hours: Check log size, any issues?
   - +12 hours: Midpoint check
   - +24 hours: Final validation

4. **Log observations** using the template below

## Checkpoint Template

Copy this template to a file like `24h_test_log.md`:

```markdown
## 24-Hour Test Log

### Start
- Start time: ___________
- Initial song: ___________
- Initial DJ: ___________
- Start conditions: ___________

### +1 Hour Check
- Time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played: ___________
- Errors in log: ___________

### +4 Hour Check
- Time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played: ___________
- Errors in log: ___________

### +8 Hour Check
- Time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played: ___________
- Log file size: ___________

### +12 Hour Check
- Time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- DJ handoff observed: [ ] Yes [ ] No
- Radio show played: [ ] Yes [ ] No

### +24 Hour Final
- End time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Total songs played: ___________
- Total errors: ___________
- Final DJ: ___________

### Issues Observed
(List any issues)

### Overall Result
[ ] PASS - Ran 24 hours without manual intervention
[ ] FAIL - Reason: ___________
```

## Post-Test Analysis

After the test completes:

1. **Review the logs** in `logs/` directory
2. **Count errors** by category
3. **Identify patterns** in any issues
4. **Run the test suite** again to ensure stability:
   ```bash
   pytest tests/ -v
   ```

### Automated Report Analysis

If you used `--validate-24h`, review the JSON report:

```bash
# View the report
cat logs/validation_*.json

# Or use Python to parse it
python -c "import json; print(json.dumps(json.load(open('logs/validation_YYYYMMDD_HHMMSS.json')), indent=2))"
```

The report includes:
- Total duration
- Checkpoint timestamps
- Songs played count
- Error count at each checkpoint
- Issues encountered
- Pass/fail result

## Success Criteria

The test **passes** if:
- ✅ Station ran for full 24 hours
- ✅ No crashes or stops
- ✅ All major features worked (songs, intros, time announcements)
- ✅ Errors were recoverable (station kept running)
- ✅ All tests still pass after the run

## Troubleshooting

### Station Stops Early
- Check logs for error messages
- Verify no system sleep/hibernation occurred
- Check disk space

### High Error Count
- Review log files for patterns
- Check if errors are recoverable
- Verify all content is pre-generated

### Audio Issues
- Verify audio device didn't disconnect
- Check volume settings
- Review playback error logs

## Next Steps

After a successful 24-hour test:

1. **Document any issues** found during testing
2. **Create bug fix tickets** for critical issues
3. **Update documentation** based on learnings
4. **Tag the release:** `git tag v1.0.0-mvp`
5. **Celebrate!** 🎉 You've completed Phase 8!

## Quick Command Reference

```bash
# Pre-flight: Run tests
pytest tests/ -v

# Pre-flight: Verify config
python -m ai_radio --dry-run

# Run 24h validation (automated)
python -m ai_radio --validate-24h

# Run 12h validation (testing)
python -m ai_radio --validate-24h --duration 12.0

# Run with frequent checkpoints
python -m ai_radio --validate-24h --checkpoint-interval 15.0

# Normal station run (manual test)
python -m ai_radio

# View logs
tail -f logs/ai_radio_*.log  # Linux/Mac
Get-Content logs/ai_radio_*.log -Wait  # Windows PowerShell
```
