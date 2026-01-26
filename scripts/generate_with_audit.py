"""Complete generation pipeline with auditing.

This script has been refactored to use modular stage implementations.
The core logic is now in:
  - src/ai_radio/stages/generate.py
  - src/ai_radio/stages/audit.py
  - src/ai_radio/stages/audio.py
  - src/ai_radio/stages/regenerate.py
  - src/ai_radio/core/checkpoint.py
  - src/ai_radio/core/paths.py
  - src/ai_radio/core/sanitizer.py

Usage:
    # Full run
    python scripts/generate_with_audit.py --intros --dj all
    
    # Test run (10 songs)
    python scripts/generate_with_audit.py --intros --dj julie --test --limit 10
    
    # Resume interrupted run
    python scripts/generate_with_audit.py --resume
    
    # Specific stage only
    python scripts/generate_with_audit.py --stage generate
    python scripts/generate_with_audit.py --stage audit
    python scripts/generate_with_audit.py --stage audio
    
    # Generate and audit only (skip audio)
    python scripts/generate_with_audit.py --intros --dj all --skip-audio
"""
import argparse
from pathlib import Path
from datetime import datetime
import logging
import sys

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import from new modular structure
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.llm_client import LLMClient
from src.ai_radio.config import DATA_DIR

# Import from refactored modules
from src.ai_radio.core.checkpoint import PipelineCheckpoint
from src.ai_radio.stages import stage_generate, stage_audit, stage_regenerate, stage_audio
from src.ai_radio.stages.utils import load_catalog_songs, FakeAuditorClient


# ============================================================================
# MAIN PIPELINE
# ============================================================================
def run_pipeline(args):
    """Run the complete pipeline."""
    logger.info("AI Radio - Generation Pipeline with Audit")
    logger.info("=" * 60)
    
    # Initialize checkpoint first (in resume mode)
    checkpoint_file = DATA_DIR / "pipeline_state.json"
    checkpoint = PipelineCheckpoint(checkpoint_file)
    
    # In resume mode, restore configuration from checkpoint
    if args.resume and checkpoint_file.exists():
        logger.info("--- RESUME MODE ---")
        logger.info("Loading configuration from checkpoint...")
        config = checkpoint.state.get("config", {})
        
        # Restore DJs if not specified
        if args.dj == 'all' and config.get('djs'):
            djs = config['djs']
        else:
            djs = [args.dj] if args.dj != 'all' else ['julie', 'mr_new_vegas']
        
        # Restore test mode if not specified
        test_mode = config.get('test_mode', args.test)
        
        # Restore song limit
        limit = config.get('song_limit', args.limit)
        
        logger.info(f"Restored config: {len(djs)} DJ(s), {limit} songs, test_mode={test_mode}")
    else:
        djs = [args.dj] if args.dj != 'all' else ['julie', 'mr_new_vegas']
        test_mode = args.test
        limit = args.limit
    
    # Load songs
    catalog_path = DATA_DIR / "catalog.json"
    if not catalog_path.exists():
        logger.error(f"Catalog not found at {catalog_path}")
        logger.error("Run 'python scripts/scan_library.py' first.")
        return 1
    
    songs = load_catalog_songs(catalog_path, limit=limit, random_sample=args.random)
    
    # Prepare time slots if --time is specified
    time_slots = []
    if args.time or (args.resume and 'time' in checkpoint.state.get('config', {}).get('content_types', [])):
        # Generate all 48 time slots (every 30 minutes)
        all_time_slots = [(h, m) for h in range(24) for m in [0, 30]]
        
        if limit and args.time:  # Only apply limit if explicitly using --time (not in resume)
            # For predictable testing, take first N slots
            time_slots = all_time_slots[:limit]
        else:
            time_slots = all_time_slots
    
    logger.info(f"Loaded {len(songs)} songs from catalog")
    if time_slots:
        logger.info(f"Time slots: {len(time_slots)}")
    logger.info(f"DJs: {', '.join(djs)}")
    
    # Store configuration in checkpoint
    content_types = []
    if args.intros:
        content_types.append("intros")
    if args.outros:
        content_types.append("outros")
    if args.time:
        content_types.append("time")
    if args.weather:
        content_types.append("weather")
    if args.all_content:
        content_types = ["intros", "outros", "time", "weather"]
    checkpoint.state["config"] = {
        "content_types": content_types if (content_types or args.resume) else [],
        "djs": djs,
        "song_limit": len(songs),
        "test_mode": test_mode,
        "time_slots": time_slots
    }
    checkpoint.save()
    
    # Dry run mode
    if args.dry_run:
        logger.info("\n--- DRY RUN MODE ---")
        logger.info(f"Would generate scripts for {len(songs)} songs × {len(djs)} DJs = {len(songs) * len(djs)} scripts")
        logger.info(f"Stages to run: {args.stage or 'all'}")
        logger.info(f"Output directory: {GENERATED_DIR}")
        logger.info(f"Audit directory: {DATA_DIR / 'audit'}")
        return 0
    
    # Initialize pipeline
    lyrics_dir = Path("music_with_lyrics")
    pipeline = GenerationPipeline(
        output_dir=GENERATED_DIR,
        prompt_version='v2',
        lyrics_dir=lyrics_dir if lyrics_dir.exists() else None
    )
    
    # Determine which stages to run
    stages_to_run = []
    if args.stage:
        if args.stage == 'all':
            stages_to_run = ['generate', 'audit', 'audio']
        else:
            stages_to_run = [args.stage]
    else:
        # Default: run all stages (respecting --skip-audio)
        stages_to_run = ['generate', 'audit']
        if not args.skip_audio:
            stages_to_run.append('audio')
    
    # Resume mode: skip completed stages
    if args.resume:
        logger.info("")
        original_stages = stages_to_run.copy()
        stages_to_run = [s for s in stages_to_run if not checkpoint.is_stage_completed(s)]
        skipped = set(original_stages) - set(stages_to_run)
        if skipped:
            logger.info(f"Skipping completed stages: {', '.join(skipped)}")
        if not stages_to_run:
            logger.info("All stages already completed!")
            return 0
    
    # Run stages
    start_time = datetime.now()
    
    try:
        if 'generate' in stages_to_run:
            stage_generate(pipeline, songs, djs, checkpoint, test_mode=test_mode)
        
        if 'audit' in stages_to_run:
            stage_audit(songs, djs, checkpoint, test_mode=test_mode)
            
            # After audit, run regeneration loop (up to 5 retries)
            stage_regenerate(pipeline, songs, djs, max_retries=5, test_mode=test_mode)
        
        if 'audio' in stages_to_run:
            stage_audio(songs, djs, checkpoint)
        
        elapsed = datetime.now() - start_time
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total time: {elapsed}")
        logger.info(f"Checkpoint saved to: {checkpoint_file}")
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("\n\nPipeline interrupted by user")
        logger.info(f"Progress saved to: {checkpoint_file}")
        logger.info("Run with --resume to continue")
        return 130
    
    except Exception as e:
        logger.error(f"\n\nPipeline failed with error: {e}", exc_info=True)
        logger.info(f"Partial progress saved to: {checkpoint_file}")
        logger.info("Run with --resume to continue")
        return 1


def main():
    """Parse arguments and run pipeline."""
    parser = argparse.ArgumentParser(
        description="Complete generation pipeline with auditing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full production run
  python scripts/generate_with_audit.py --intros --dj all
  
  # Test run with 10 songs
  python scripts/generate_with_audit.py --intros --dj julie --test --limit 10
  
  # Resume interrupted run
  python scripts/generate_with_audit.py --resume
  
  # Generate and audit only (skip audio)
  python scripts/generate_with_audit.py --intros --dj all --skip-audio
  
  # Run specific stage
  python scripts/generate_with_audit.py --stage audit
        """
    )
    
    # Content type selection
    parser.add_argument('--intros', action='store_true', help='Generate song intros')
    parser.add_argument('--outros', action='store_true', help='Generate song outros')
    parser.add_argument('--time', action='store_true', help='Generate time announcements (48 slots, every 30 min). With --limit N, generates first N time slots.')
    parser.add_argument('--weather', action='store_true', help='Generate weather announcements (3 slots: 6 AM, 12 PM, 5 PM)')
    parser.add_argument('--all-content', action='store_true', help='Generate everything (not yet implemented)')
    
    # DJ selection
    parser.add_argument('--dj', choices=['julie', 'mr_new_vegas', 'all'], default='all', help='Which DJ(s) to generate for')
    
    # Mode selection
    parser.add_argument('--test', action='store_true', help='Test mode (uses fake auditor, limits output)')
    parser.add_argument('--limit', type=int, help='Limit number of songs to process')
    parser.add_argument('--random', action='store_true', help='Random selection when using --limit')
    
    # Stage control
    parser.add_argument('--stage', choices=['generate', 'audit', 'audio', 'all'], help='Run specific stage only')
    parser.add_argument('--skip-audio', action='store_true', help='Generate and audit but skip audio generation')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    
    # Output options
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without doing it')
    parser.add_argument('--verbose', action='store_true', help='Detailed logging')
    
    args = parser.parse_args()
    
    # Validation
    # Resume mode can work without content type (will use checkpoint config)
    if not args.resume:
        if not args.intros and not args.outros and not args.time and not args.weather and not args.all_content:
            parser.error('Must specify at least one content type (--intros, --outros, --time, --weather, or --all-content)')
    
    # Block unsupported content types (only --all-content not yet implemented)
    if args.all_content:
        parser.error('Currently only --intros, --outros, --time, and --weather are supported')
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run pipeline
    return run_pipeline(args)


if __name__ == '__main__':
    sys.exit(main())

