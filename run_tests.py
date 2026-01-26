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

    # In integration mode, do a preflight service check and fail fast on missing services
    if mode == 'integration':
        # Lazy import of check functions to avoid importing heavy modules in mock mode
        from src.ai_radio.generation.llm_client import check_ollama_available
        from src.ai_radio.generation.tts_client import check_tts_available
        print("Performing preflight checks for required services...")

        if not check_ollama_available():
            print("ERROR: Ollama LLM service not available at http://localhost:11434")
            print("Start Ollama (e.g., `ollama serve`) and try again.")
            return 2

        # Run TTS availability check with a short timeout to avoid long model loads
        import multiprocessing, queue

        def _check_tts(q):
            try:
                ok = check_tts_available()
            except Exception:
                ok = False
            q.put(bool(ok))

        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=_check_tts, args=(q,))
        p.start()
        p.join(10)  # 10 second timeout for TTS check
        tts_ok = False
        try:
            tts_ok = q.get_nowait()
        except queue.Empty:
            tts_ok = False
        finally:
            if p.is_alive():
                p.terminate()
                p.join()

        if not tts_ok:
            print("WARNING: TTS model not available (local Chatterbox model could not be loaded)")
            print("TTS-dependent integration tests will be skipped or may fail.")
            print("If you intended to run full TTS integration tests, start the Chatterbox server or ensure local model loads quickly.")
            print("Continuing test run, but beware some tests may be skipped or fall back to silent audio.")
            print()

    cmd = [sys.executable, '-m', 'pytest'] + args

    print(f"Running: {' '.join(cmd)}")
    print(f"TEST_MODE={mode}")
    print("-" * 60)

    result = subprocess.run(cmd, env=env)
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
