from pathlib import Path
from src.ai_radio.library.scanner import scan_library
p = Path('/nonexistent/directory')
print('p:', p)
print('exists:', p.exists())
print('is_dir:', p.is_dir())
try:
    scan_library(p)
    print('scan_library returned (did not raise)')
except Exception as e:
    print('scan_library raised:', type(e), e)
