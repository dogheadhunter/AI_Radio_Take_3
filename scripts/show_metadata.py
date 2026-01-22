import sys
from pathlib import Path

# Ensure src is importable when running script directly
ROOT = Path(__file__).resolve().parent.parent
proj_root = str(ROOT)
print('DEBUG sys.path before insert:', sys.path[0:3])
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
print('DEBUG sys.path after insert:', sys.path[0:3])

from src.ai_radio.library.metadata import read_metadata

p = Path('music')
mp3s = sorted(list(p.glob('**/*.mp3')))
if not mp3s:
    print('No mp3 files found in music/')
else:
    f = mp3s[0]
    m = read_metadata(f)
    print('File:', f)
    print('Artist:', m.artist)
    print('Title:', m.title)
    print('Album:', m.album)
    print('Year:', m.year)
    print('Duration (s):', m.duration_seconds)
