from pathlib import Path
from src.ai_radio.library.scanner import scan_library
p = Path('/nonexistent/directory')
print('Calling scan_library with:', p)
try:
    r = scan_library(p)
    print('Returned:', r)
except Exception as e:
    print('Raised:', type(e), e)
