"""Clean slate - Remove all generated content and state files.

This script resets the AI Radio project to a clean state by removing:
- All generated content (scripts and audio)
- Pipeline checkpoint state
- Regeneration queue
"""
import shutil
from pathlib import Path
import sys

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai_radio.config import DATA_DIR, GENERATED_DIR


def clean_slate():
    """Remove all generated content and state files."""
    print("🧹 Cleaning slate...")
    
    # Remove all generated content
    if GENERATED_DIR.exists():
        print(f"  Removing {GENERATED_DIR}")
        shutil.rmtree(GENERATED_DIR)
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove state files
    state_files = [
        DATA_DIR / "pipeline_state.json",
        DATA_DIR / "regeneration_queue.json"
    ]
    
    for state_file in state_files:
        if state_file.exists():
            print(f"  Removing {state_file.name}")
            state_file.unlink()
    
    print("✅ Clean slate complete!")
    print("\nYou can now run a fresh 24-hour generation:")
    print("  .venv\\Scripts\\python scripts\\generate_with_audit.py --intros --outros --time --weather --dj mr_new_vegas")


if __name__ == '__main__':
    clean_slate()
