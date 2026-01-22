"""Run the mock TTS server directly (no Docker required)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dev.mock_tts import app

if __name__ == '__main__':
    app.app.run(host='0.0.0.0', port=3000)
