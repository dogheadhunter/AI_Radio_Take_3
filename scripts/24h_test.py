#!/usr/bin/env python
"""
24-Hour Test Helper Script

This script helps run and monitor a 24-hour validation test manually.
It guides you through the pre-flight checklist and creates a log file.
"""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def ask_yes_no(question):
    """Ask a yes/no question."""
    while True:
        response = input(f"{question} (y/n): ").strip().lower()
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print("Please answer 'y' or 'n'")


def run_pre_flight_checklist():
    """Run through the pre-flight checklist."""
    print_header("PRE-FLIGHT CHECKLIST")
    
    checks = [
        "Catalog contains all songs",
        "All songs have generated intros",
        "Time announcements generated",
        "Weather templates ready (if enabled)",
        "Radio show episodes ready (if enabled)",
        "All tests pass (pytest tests/ -v)",
        "Station starts without errors (--dry-run)",
        "Log directory has write permissions",
        "Adequate disk space available",
        "Computer won't sleep during test",
        "No scheduled restarts or updates",
        "Audio output configured correctly",
    ]
    
    all_passed = True
    for check in checks:
        if not ask_yes_no(f"✓ {check}?"):
            all_passed = False
            print(f"  ⚠️  Warning: '{check}' not ready")
    
    if not all_passed:
        print("\n⚠️  Some checks failed. Continue anyway?")
        if not ask_yes_no("Proceed with test"):
            print("Test aborted.")
            return False
    
    return True


def create_log_file():
    """Create a log file for manual observations."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = Path('logs') / f'24h_manual_test_{timestamp}.md'
    log_path.parent.mkdir(exist_ok=True)
    
    template = """# 24-Hour Test Log

## Test Information
- Start time: {start_time}
- Test date: {date}
- Tester: [Your name here]

## Pre-Flight Status
- All checks completed: ✓

## Checkpoints

### +1 Hour Check ({plus_1h})
- Time checked: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played (approx): ___________
- Errors in log: ___________
- Notes: ___________

### +4 Hour Check ({plus_4h})
- Time checked: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played (approx): ___________
- Errors in log: ___________
- Notes: ___________

### +8 Hour Check ({plus_8h})
- Time checked: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Songs played (approx): ___________
- Log file size: ___________
- Notes: ___________

### +12 Hour Check ({plus_12h})
- Time checked: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- DJ handoff observed: [ ] Yes [ ] No
- Radio show played: [ ] Yes [ ] No
- Notes: ___________

### +16 Hour Check ({plus_16h})
- Time checked: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Notes: ___________

### +20 Hour Check ({plus_20h})
- Time checked: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Notes: ___________

### +24 Hour Final ({plus_24h})
- End time: ___________
- Status: [ ] Running [ ] Stopped [ ] Error
- Total songs played: ___________
- Total errors: ___________
- Final DJ: ___________
- Notes: ___________

## Issues Observed
(List any issues below)

- 
- 
- 

## Overall Result
[ ] PASS - Ran 24 hours without manual intervention
[ ] FAIL - Reason: ___________

## Post-Test Notes
(Add any additional observations or recommendations)

"""
    
    start = datetime.now()
    content = template.format(
        start_time=start.strftime('%H:%M:%S'),
        date=start.strftime('%Y-%m-%d'),
        plus_1h=(start + timedelta(hours=1)).strftime('%H:%M'),
        plus_4h=(start + timedelta(hours=4)).strftime('%H:%M'),
        plus_8h=(start + timedelta(hours=8)).strftime('%H:%M'),
        plus_12h=(start + timedelta(hours=12)).strftime('%H:%M'),
        plus_16h=(start + timedelta(hours=16)).strftime('%H:%M'),
        plus_20h=(start + timedelta(hours=20)).strftime('%H:%M'),
        plus_24h=(start + timedelta(hours=24)).strftime('%H:%M'),
    )
    
    with open(log_path, 'w') as f:
        f.write(content)
    
    return log_path


def print_instructions(log_path):
    """Print instructions for the test."""
    print_header("24-HOUR TEST INSTRUCTIONS")
    
    print(f"Log file created: {log_path}")
    print()
    print("Now you should:")
    print("  1. Start the station:")
    print("     python -m ai_radio")
    print()
    print("  2. Let it run for 24 hours")
    print()
    print("  3. Check in at these times and update the log file:")
    
    start = datetime.now()
    checkpoints = [1, 4, 8, 12, 16, 20, 24]
    for hours in checkpoints:
        check_time = start + timedelta(hours=hours)
        print(f"     +{hours:2d} hours: {check_time.strftime('%H:%M')} ({check_time.strftime('%a %b %d')})")
    
    print()
    print("  4. After 24 hours, fill in the final results in the log file")
    print()
    print("  5. Run the test suite again to verify stability:")
    print("     pytest tests/ -v")
    print()
    print("TIP: Use automated mode instead:")
    print("     python -m ai_radio --validate-24h")
    print()


def main():
    """Main entry point."""
    print_header("24-HOUR VALIDATION TEST HELPER")
    
    print("This script will help you set up and run a 24-hour validation test.")
    print("You can also use the automated mode: python -m ai_radio --validate-24h")
    print()
    
    if not ask_yes_no("Continue with manual test setup"):
        print("Exiting. Use 'python -m ai_radio --validate-24h' for automated testing.")
        return 0
    
    # Run pre-flight checklist
    if not run_pre_flight_checklist():
        return 1
    
    print("\n✅ Pre-flight checks complete!")
    
    # Create log file
    log_path = create_log_file()
    
    # Print instructions
    print_instructions(log_path)
    
    print_header("READY TO START")
    print("Open the log file to track your progress:")
    print(f"  {log_path}")
    print()
    print("Good luck! 🎉")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
