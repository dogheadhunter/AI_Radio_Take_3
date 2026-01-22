"""
Split Detailed_Plan.md into per-checkpoint markdown files organized by phase.

This script is non-destructive: it reads the source file and writes copies into
an output directory. It will never modify the original file.

Behavior
- Splits the input file on lines that contain only `---` (whitespace allowed).
- For each segment that contains a `Checkpoint X.Y: Title` heading, creates
  `OUTPUT_DIR/phase_X/checkpoint_X_Y-title-slug.md` containing the segment.
- If a segment contains a `Phase X: Title` heading but no checkpoint, the
  segment is written to `OUTPUT_DIR/phase_X/phase_X-overview.md`.
- Any initial prelude (before first `---`) is written to `OUTPUT_DIR/README.md`.

Usage
    python scripts/split_checkpoints.py "plan's/Detailed_Plan.md"
    python scripts/split_checkpoints.py --output-dir plan_checkpoints --dry-run "plan's/Detailed_Plan.md"

"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Optional

CHECKPOINT_RE = re.compile(r"Checkpoint\s+(\d+)\.(\d+):\s*(.+)", re.IGNORECASE)
PHASE_RE = re.compile(r"Phase\s+(\d+):\s*(.+)", re.IGNORECASE)
SPLIT_RE = re.compile(r"^\s*---\s*$", flags=re.MULTILINE)


def slugify(s: str) -> str:
    s = s.strip().lower()
    # replace spaces with hyphens, remove forbidden characters
    s = re.sub(r"[^a-z0-9\-\s_]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def find_checkpoint_info(text: str) -> Optional[tuple[int, int, str]]:
    m = CHECKPOINT_RE.search(text)
    if m:
        phase = int(m.group(1))
        minor = int(m.group(2))
        title = m.group(3).strip()
        return phase, minor, title
    return None


def find_phase_info(text: str) -> Optional[tuple[int, str]]:
    m = PHASE_RE.search(text)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return None


def write_segment(output_dir: Path, phase: Optional[int], filename: str, content: str, dry_run: bool) -> Path:
    if phase is not None:
        dest_dir = output_dir / f"phase_{phase}"
    else:
        dest_dir = output_dir

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    if dry_run:
        print(f"[DRY-RUN] Would write: {dest_path}")
    else:
        dest_path.write_text(content, encoding="utf-8")
        print(f"Wrote: {dest_path}")
    return dest_path


def split_checkpoints(source: Path, output_dir: Path, dry_run: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    text = source.read_text(encoding="utf-8")

    # Split on lines that are only '---' (multiline)
    parts = SPLIT_RE.split(text)

    # If the file starts with a prelude (no preceding '---'), it will be parts[0]
    # We'll write that to README.md in the output dir if non-empty.
    if parts:
        prelude = parts[0].strip()
        if prelude:
            write_segment(output_dir, None, "README.md", prelude + "\n", dry_run)

    checkpoint_count = 0
    phase_overviews: dict[int, str] = {}

    # process the following parts (they represent chunks following each '---')
    for idx, chunk in enumerate(parts[1:], start=1):
        chunk_str = chunk.strip()
        if not chunk_str:
            continue

        # Skip continuation markers (just headers like "## Roadmap (Continued)")
        lines = [line for line in chunk_str.split('\n') if line.strip()]
        if len(lines) <= 2 and any('continued' in line.lower() for line in lines):
            continue

            # 1) Check for explicit checkpoint
        cp = find_checkpoint_info(chunk_str)
        if cp:
            phase, minor, title = cp
            checkpoint_count += 1
            slug = slugify(title) or f"checkpoint-{phase}-{minor}"
            filename = f"checkpoint_{phase}_{minor}_{slug}.md"
            # include a heading line at the top to make file self-contained
            content = f"# Checkpoint {phase}.{minor}: {title}\n\n" + chunk_str + "\n"
            write_segment(output_dir, phase, filename, content, dry_run)
            continue

        # 2) Check for a Phase Gate (e.g., "Phase 1 Gate: Music Library Complete")
        PHASE_GATE_RE = re.compile(r"Phase\s+(\d+)\s+Gate(?::\s*(.+))?", re.IGNORECASE)
        pg = PHASE_GATE_RE.search(chunk_str)
        if pg:
            phase_num = int(pg.group(1))
            gate_title = (pg.group(2) or "Phase Gate").strip()
            filename = f"phase_{phase_num}_gate.md"
            content = f"# Phase {phase_num} Gate: {gate_title}\n\n" + chunk_str + "\n"
            write_segment(output_dir, phase_num, filename, content, dry_run)
            continue

        # 3) Check for 'Phase X: Title' overviews
        ph = find_phase_info(chunk_str)
        if ph:
            phase_num, phase_title = ph
            # store/append as overview; if multiple chunks belong to same phase, append
            existing = phase_overviews.get(phase_num, "")
            combined = existing + ("\n" + chunk_str if existing else chunk_str)
            phase_overviews[phase_num] = combined
            continue

        # 4) Known top-level sections: map them to descriptive files rather than misc parts
        # Extract first header line if present
        first_header = None
        for line in chunk_str.splitlines():
            if line.strip().startswith("#"):
                first_header = line.strip().lstrip("#").strip()
                break

        TOP_LEVEL_MAP = {
            "development philosophy": "development_philosophy.md",
            "anti-corruption safeguards": "anti_corruption_safeguards.md",
            "refactoring guidelines": "refactoring_guidelines.md",
            "appendix:  test templates": "appendix_test_templates.md",
            "appendix: test templates": "appendix_test_templates.md",
            "quick reference": "quick_reference.md",
            "document history": "document_history.md",
            "context management": "context_management.md",
        }
        if first_header and first_header.lower() in TOP_LEVEL_MAP:
            filename = TOP_LEVEL_MAP[first_header.lower()]

            # Special handling: if Appendix contains "Test Templates", split into
            # Fixture, Unit, and Integration templates and assign them to phases.
            if first_header.lower().startswith("appendix") and "test templates" in first_header.lower():
                # Look for sub-sections starting with '###'
                sections = re.split(r"(?m)^###\s*", chunk_str)
                # The first element before any '###' is heading/intro; keep it as appendix file
                intro = sections[0].strip()
                if intro:
                    write_segment(output_dir, None, filename, f"# {first_header}\n\n" + intro + "\n", dry_run)

                # Patterns to find the specific templates
                patterns = [
                    (re.compile(r"###\s*Fixture Template.*?(?=\n###|\Z)", re.S|re.I), 0, "fixture_template.md"),
                    (re.compile(r"###\s*Unit Test Template.*?(?=\n###|\Z)", re.S|re.I), 0, "unit_test_template.md"),
                    (re.compile(r"###\s*Integration Test Template.*?(?=\n###|\Z)", re.S|re.I), 7, "integration_test_template.md"),
                ]

                for patt, phase_num, fn in patterns:
                    m = patt.search(chunk_str)
                    if m:
                        snippet = m.group(0).strip()
                        # Ensure it has a top-level header
                        if not snippet.startswith('#'):
                            snippet = '# ' + snippet
                        write_segment(output_dir, phase_num, fn, snippet + "\n", dry_run)
                continue

            # Default write for other top-level mapped sections
            content = f"# {first_header}\n\n" + chunk_str + "\n"
            write_segment(output_dir, None, filename, content, dry_run)
            continue

        # fallback: write to miscellaneous file
        filename = f"misc_part_{idx}.md"
        content = chunk_str + "\n"
        write_segment(output_dir, None, filename, content, dry_run)

    # write phase overviews
    for phase_num, overview in phase_overviews.items():
        filename = f"phase_{phase_num}_overview.md"
        content = f"# Phase {phase_num} Overview\n\n" + overview + "\n"
        write_segment(output_dir, phase_num, filename, content, dry_run)

    print("Done. Checkpoints processed:", checkpoint_count)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Split Detailed_Plan.md into per-checkpoint files organized by phase.")
    p.add_argument("source", help="Path to Detailed_Plan.md")
    p.add_argument("--output-dir", default="plan_checkpoints", help="Output directory for split checkpoints")
    p.add_argument("--dry-run", action="store_true", help="Show what would be written without writing files")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.source)
    output_dir = Path(args.output_dir)
    try:
        split_checkpoints(source, output_dir, dry_run=args.dry_run)
    except Exception as e:
        print("Error:", e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
