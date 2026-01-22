"""Environment validation script.

Run this to verify your setup is ready for AI Radio development.
Usage:  python -m scripts.validate_setup
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from typing import Callable

# Add src to path to ensure `src.ai_radio` imports work
ROOT = Path(__file__).parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


def check_python_version() -> bool:
    """Check Python version is 3.8+."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (need 3.8+)")
        return False


def check_import(module_name: str, package_name: str | None = None) -> bool:
    """Check if a Python module can be imported."""
    package_name = package_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {package_name} importable")
        return True
    except ImportError:
        print(f"❌ {package_name} not importable (pip install {package_name})")
        return False


def check_ollama() -> bool:
    """Check if Ollama is installed and responding."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama installed and responding")
            return True
        else:
            print("❌ Ollama installed but not responding")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama timeout (is it running?)")
        return False


def check_directory_structure() -> bool:
    """Check that project directories exist."""
    project_root = Path(__file__).parent.parent
    required_dirs = [
        "src/ai_radio",
        "tests",
        "data",
        "logs",
        "assets",
    ]
    missing = [d for d in required_dirs if not (project_root / d).exists()]
    if missing:
        print(f"❌ Missing directories: {', '.join(missing)}")
        return False
    print("✅ All required directories present")
    return True


def check_config_import() -> bool:
    """Check that config module can be imported.

    Tries `ai_radio.config` first and falls back to `src.ai_radio.config` for
    environments where `src` is the package root.
    """
    try:
        from ai_radio.config import PROJECT_ROOT  # type: ignore

        print("✅ ai_radio.config importable")
        return True
    except Exception:
        try:
            from src.ai_radio.config import PROJECT_ROOT  # type: ignore

            print("✅ src.ai_radio.config importable")
            return True
        except Exception as exc:  # pragma: no cover - diagnostic
            print(f"❌ ai_radio.config import failed: {exc}")
            return False


def run_all_checks(checks: list[Callable[[], bool]]) -> list[bool]:
    results = [check() for check in checks]
    return results


def main() -> int:
    print("=" * 60)
    print("AI Radio Station - Environment Validation")
    print("=" * 60)
    print()

    checks = [
        check_python_version,
        lambda: check_import("pytest"),
        lambda: check_import("mutagen"),
        check_ollama,
        check_directory_structure,
        check_config_import,
    ]

    results = run_all_checks(checks)

    print()
    print("=" * 60)
    if all(results):
        print("✅ All checks passed! Environment is ready.")
        return 0
    else:
        print("❌ Some checks failed. Fix issues above and re-run.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
