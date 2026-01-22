"""Batch content generation script for Phase 2."""
import sys
from pathlib import Path
from datetime import datetime

# Ensure the repository root is on sys.path so internal `src` package imports work
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai_radio.library.catalog import load_catalog
from src.ai_radio.generation.pipeline import GenerationPipeline, generate_batch_intros
from src.ai_radio.config import CATALOG_FILE, GENERATED_DIR
from src.ai_radio.utils.logging import setup_logging


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate radio content")
    parser.add_argument("--intros", action="store_true", help="Generate song intros")
    parser.add_argument("--time-announcements", action="store_true", help="Generate time announcements")
    parser.add_argument("--dj", choices=["julie", "mr_new_vegas", "all"], default="all")
    parser.add_argument("--limit", type=int, help="Limit number of songs")
    parser.add_argument("--resume", action="store_true", help="Resume interrupted generation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    args = parser.parse_args()

    logger = setup_logging("generate_content")

    if not CATALOG_FILE.exists():
        print(f"Error: Catalog not found at {CATALOG_FILE}")
        print("Run 'python scripts/scan_library.py' first.")
        return 1

    catalog = load_catalog(CATALOG_FILE)
    # catalog._songs maps id -> SongMetadata; convert to simple dicts used by pipeline
    songs = [{"id": str(song_id), "artist": s.artist, "title": s.title} for song_id, s in catalog._songs.items()]

        songs = songs[: args.limit]
        print(f"Limited to {args.limit} songs for testing")

    if args.dry_run:
        print(f"Would generate content for {len(songs)} songs")
        print(f"DJs: {args.dj}")
        print(f"Output directory: {GENERATED_DIR}")
        return 0

    if args.intros:
        print(f"Generating intros for {len(songs)} songs...")
        print(f"DJ: {args.dj}")
        print(f"Resume mode: {args.resume}")
        print("-" * 50)

        pipeline = GenerationPipeline(output_dir=GENERATED_DIR)

        djs = ["julie", "mr_new_vegas"] if args.dj == "all" else [args.dj]

        for dj in djs:
            print(f"\n=== Generating {dj.upper()} intros ===\n")

            start_time = datetime.now()
            success_count = 0
            fail_count = 0

            def progress_callback(progress):
                elapsed = datetime.now() - start_time
                print(
                    f"\r[{progress.percent:.1f}%] {progress.completed}/{progress.total} "
                    f"({progress.failed} failed) - {progress.current_song[:40]}...",
                    end="",
                    flush=True,
                )

            for result in generate_batch_intros(
                pipeline,
                [{"id": s.id, "artist": s.artist, "title": s.title} for s in songs],
                dj=dj,
                resume=args.resume,
                progress_callback=progress_callback,
            ):
                if result.success:
                    success_count += 1
                else:
                    fail_count += 1
                    logger.warning(f"Failed: {result.song_id} - {result.error}")

            elapsed = datetime.now() - start_time
            print(f"\n\nCompleted in {elapsed}")
            print(f"Success: {success_count}, Failed: {fail_count}")

    if args.time_announcements:
        print("Generating time announcements...")
        # Implementation for time announcements
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
