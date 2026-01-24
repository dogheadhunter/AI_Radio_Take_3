#!/usr/bin/env python3
"""Helper script to run tests in different modes.

Usage:
    python run_tests.py               # Mock mode (default, fast)
    python run_tests.py --integration # Integration mode (real services)
    python run_tests.py --help        # Show help
"""
import sys
import os
import subprocess
from pathlib import Path


def main():
    args = sys.argv[1:]
    
    # Determine mode
    if '--integration' in args or '-i' in args:
        mode = 'integration'
        args = [a for a in args if a not in ('--integration', '-i')]
        print("🔍 Running INTEGRATION tests (requires services)")
        print("   - Ollama should be running on localhost:11434")
        print("   - TTS service should be available")
        print()
    else:
        mode = 'mock'
        print("⚡ Running MOCK tests (fast, no services needed)")
        print()
    
    # Handle help
    if '--help' in args or '-h' in args:
        print(__doc__)
        print("\nPytest options can be passed through:")
        print("  python run_tests.py -v              # Verbose mode")
        print("  python run_tests.py -k weather      # Run only weather tests")
        print("  python run_tests.py --integration -v # Integration tests, verbose")
        print()
        print("Environment variable method:")
        print("  TEST_MODE=mock pytest")
        print("  TEST_MODE=integration pytest")
        return 0
    
    # Set environment and run pytest
    env = os.environ.copy()
    env['TEST_MODE'] = mode
    
    cmd = [sys.executable, '-m', 'pytest'] + args
    
    print(f"Running: {' '.join(cmd)}")
    print(f"TEST_MODE={mode}")
    print("-" * 60)
    
    result = subprocess.run(cmd, env=env)
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
