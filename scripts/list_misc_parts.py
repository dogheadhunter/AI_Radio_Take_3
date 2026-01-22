"""
List misc parts detected by the splitter and print a short preview for each.
"""
import re
from pathlib import Path

SPLIT_RE = re.compile(r"^\s*---\s*$", flags=re.MULTILINE)
CHECKPOINT_RE = re.compile(r"Checkpoint\s+(\d+)\.(\d+):\s*(.+)", re.IGNORECASE)
PHASE_RE = re.compile(r"Phase\s+(\d+):\s*(.+)", re.IGNORECASE)

source = Path("plan's/Detailed_Plan.md")
if not source.exists():
    raise SystemExit(f"Source not found: {source}")

text = source.read_text(encoding='utf-8')
parts = SPLIT_RE.split(text)

misc = []
for idx, chunk in enumerate(parts[1:], start=1):
    s = chunk.strip()
    if not s:
        continue
    if CHECKPOINT_RE.search(s) or PHASE_RE.search(s):
        continue
    misc.append((idx, s))

if not misc:
    print("No misc parts found.")
else:
    for idx, s in misc:
        lines = s.splitlines()
        preview = "\n".join(lines[:10])
        print(f"--- MISC PART #{idx} (first 10 lines) ---")
        print(preview)
        print("[... truncated ...]\n")

print(f"Found {len(misc)} misc parts")
