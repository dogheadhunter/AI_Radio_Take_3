"""Complete generation pipeline with auditing.

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
import json
import logging
import re
import sys
from typing import List, Dict, Any, Optional

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

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.auditor import audit_batch, audit_script
from src.ai_radio.generation.llm_client import LLMClient
from src.ai_radio.generation.tts_client import TTSClient, generate_audio
from src.ai_radio.config import GENERATED_DIR, VOICE_REFERENCES_DIR, DATA_DIR


# ============================================================================
# CHECKPOINT SYSTEM
# ============================================================================

class PipelineCheckpoint:
    """Manages pipeline state for resume capability."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_or_init()
    
    def _load_or_init(self) -> Dict[str, Any]:
        """Load existing checkpoint or initialize new one."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "timestamp": datetime.now().isoformat(),
            "run_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "config": {},
            "stages": {
                "generate": {"status": "not_started", "completed_at": None, "scripts_generated": 0},
                "audit": {"status": "not_started", "completed_at": None, "scripts_audited": 0, "passed": 0, "failed": 0},
                "audio": {"status": "not_started", "completed_at": None, "audio_files_generated": 0}
            }
        }
    
    def save(self):
        """Save checkpoint to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def is_stage_completed(self, stage: str) -> bool:
        """Check if a stage is completed."""
        return self.state["stages"].get(stage, {}).get("status") == "completed"
    
    def mark_stage_started(self, stage: str):
        """Mark stage as in progress."""
        self.state["stages"][stage]["status"] = "in_progress"
        self.save()
    
    def mark_stage_completed(self, stage: str, **kwargs):
        """Mark stage as completed with additional data."""
        self.state["stages"][stage]["status"] = "completed"
        self.state["stages"][stage]["completed_at"] = datetime.now().isoformat()
        for key, value in kwargs.items():
            self.state["stages"][stage][key] = value
        self.save()
    
    def update_stage_progress(self, stage: str, **kwargs):
        """Update progress counters for a stage."""
        for key, value in kwargs.items():
            self.state["stages"][stage][key] = value
        self.save()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_catalog_songs(catalog_path: Path, limit: Optional[int] = None, random_sample: bool = False):
    """Load songs from catalog.json."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    songs = data.get('songs', [])
    
    # Convert to simpler format
    songs = [{"id": s['id'], "artist": s['artist'], "title": s['title']} for s in songs]
    
    # Apply random sampling if requested
    if random_sample and limit:
        import random
        songs = random.sample(songs, min(limit, len(songs)))
    elif limit:
        songs = songs[:limit]
    
    return songs
def load_catalog_songs(catalog_path: Path, limit: Optional[int] = None, random_sample: bool = False):
    """Load songs from catalog.json."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    songs = data.get('songs', [])
    
    # Convert to simpler format
    songs = [{"id": s['id'], "artist": s['artist'], "title": s['title']} for s in songs]
    
    # Apply random sampling if requested
    if random_sample and limit:
        import random
        songs = random.sample(songs, min(limit, len(songs)))
    elif limit:
        songs = songs[:limit]
    
    return songs


def sanitize_script(text: str) -> str:
    """Remove meta-commentary and sanitize TTS-breaking punctuation."""
    # Remove ALL parenthetical content (often meta-commentary)
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove dates/years
    text = re.sub(r'\b(19|20)\d{2}\b', '', text)  # Remove 4-digit years
    text = re.sub(r'\b\d{4}s\b', '', text)  # Remove decade references like "1940s"
    
    # Fix TTS-breaking punctuation
    text = text.replace('...', '…')  # Convert to single ellipsis character first
    text = re.sub(r'([?!]),', r'\1', text)  # Remove comma after ? or !
    text = re.sub(r'\s*-\s*', ' ', text)  # Remove dashes (often used for em-dash)
    
    # Fix common punctuation errors
    text = re.sub(r'(\w+)\s+(and)\s+(?:we|I|it|that)', r'\1, \2 ', text)
    text = re.sub(r'(\w+)\s+([A-Z][a-z]+\s+(?:is|are|was|were|has|have))', r'\1? \2', text)
    text = re.sub(r'(\w+)\s+(Here(?:\'s| is| are))', r'\1. \2', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix ellipsis at sentence boundaries
    text = re.sub(r'…\.', '.', text)
    text = re.sub(r'\.{2,}', '.', text)
    
    return text


def truncate_after_song_intro(text: str, artist: str, title: str) -> str:
    """Truncate any text that comes after the song introduction."""
    # Validate artist name appears correctly (catch typos/truncations)
    artist_parts = artist.split()
    if len(artist_parts) > 1:
        for part in artist_parts:
            if len(part) > 3:
                pattern = re.escape(part[:4])
                if re.search(r'\b' + pattern + r'[a-z]{0,2}\b', text, re.IGNORECASE):
                    if part.lower() not in text.lower():
                        logger.warning(f"Detected truncated artist name in script: expected '{artist}'")
                        return ""
    
    # Protect common abbreviations
    protected_text = text.replace('Mr.', 'Mr~').replace('Mrs.', 'Mrs~').replace('Ms.', 'Ms~').replace('Dr.', 'Dr~')
    
    sentences = re.split(r'([.!?])\s+', protected_text)
    result = []
    found_intro = False
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        sentence = sentences[i]
        punct = sentences[i+1] if i+1 < len(sentences) else '.'
        
        has_artist = artist.lower() in sentence.lower()
        has_title = title.lower() in sentence.lower()
        
        result.append(sentence + punct)
        
        if has_artist and has_title:
            found_intro = True
            break
        elif (has_artist or has_title) and len(result) > 1:
            found_intro = True
            break
    
    if found_intro:
        final_text = ' '.join(result).strip()
        final_text = final_text.replace('Mr~', 'Mr.').replace('Mrs~', 'Mrs~').replace('Ms~', 'Ms.').replace('Dr~', 'Dr.')
        return final_text
    
    # Restore protections and return original
    text = text.replace('Mr~', 'Mr.').replace('Mrs~', 'Mrs.').replace('Ms~', 'Ms.').replace('Dr~', 'Dr.')
    return text


# ============================================================================
# PIPELINE STAGES
# ============================================================================

def stage_generate(pipeline: GenerationPipeline, songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint, test_mode: bool = False) -> int:
    """Stage 1: Generate text scripts for all songs."""
    logger.info("=" * 60)
    logger.info("STAGE 1: GENERATE SCRIPTS")
    logger.info("=" * 60)
    
    if checkpoint.is_stage_completed("generate"):
        logger.info("Stage 1 already completed, skipping...")
        return checkpoint.state["stages"]["generate"]["scripts_generated"]
    
    checkpoint.mark_stage_started("generate")
    
    total_scripts = 0
    for dj in djs:
        logger.info(f"\nGenerating scripts for {dj.upper()}...")
        
        for i, song in enumerate(songs, 1):
            # Check if already exists (for resume within stage)
            script_path = get_script_path(song, dj)
            if script_path.exists():
                logger.debug(f"  [{i}/{len(songs)}] Skipping {song['title']} (already exists)")
                total_scripts += 1
                continue
            
            try:
                result = pipeline.generate_song_intro(
                    song_id=str(song['id']),
                    artist=song['artist'],
                    title=song['title'],
                    dj=dj,
                    text_only=True
                )
                
                if result.success and result.text:
                    # Sanitize and truncate
                    sanitized = sanitize_script(result.text)
                    truncated = truncate_after_song_intro(sanitized, song['artist'], song['title'])
                    
                    if truncated:
                        # Save the script
                        script_path.parent.mkdir(parents=True, exist_ok=True)
                        script_path.write_text(truncated, encoding='utf-8')
                        total_scripts += 1
                        logger.info(f"  [{i}/{len(songs)}] ✓ {song['title']}")
                    else:
                        logger.warning(f"  [{i}/{len(songs)}] ✗ {song['title']} (validation failed)")
                else:
                    logger.warning(f"  [{i}/{len(songs)}] ✗ {song['title']} (generation failed)")
            
            except Exception as e:
                logger.error(f"  [{i}/{len(songs)}] ✗ {song['title']} - Error: {e}")
    
    checkpoint.mark_stage_completed("generate", scripts_generated=total_scripts)
    logger.info(f"\n✓ Stage 1 complete: {total_scripts} scripts generated")
    return total_scripts


def stage_audit(songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint, test_mode: bool = False) -> Dict[str, int]:
    """Stage 2: Audit all generated scripts."""
    logger.info("\n" + "=" * 60)
    logger.info("STAGE 2: AUDIT SCRIPTS")
    logger.info("=" * 60)
    
    if checkpoint.is_stage_completed("audit"):
        logger.info("Stage 2 already completed, skipping...")
        stats = checkpoint.state["stages"]["audit"]
        return {"passed": stats["passed"], "failed": stats["failed"]}
    
    checkpoint.mark_stage_started("audit")
    
    # Prepare audit client
    if test_mode:
        client = FakeAuditorClient()
    else:
        client = None  # Will use default LLMClient in auditor
    
    # Collect all scripts to audit
    scripts_to_audit = []
    for dj in djs:
        for song in songs:
            script_path = get_script_path(song, dj)
            if script_path.exists():
                script_id = f"{song['id']}_{dj}"
                content = script_path.read_text(encoding='utf-8')
                scripts_to_audit.append({
                    "script_id": script_id,
                    "script_content": content,
                    "dj": dj,
                    "content_type": "song_intro",
                    "song": song
                })
    
    logger.info(f"Auditing {len(scripts_to_audit)} scripts...")
    
    # Run audits and organize by DJ
    audit_results = {"passed": 0, "failed": 0}
    
    for i, script in enumerate(scripts_to_audit, 1):
        dj = script['dj']
        song = script['song']
        
        # Check if already audited
        audit_path_passed = get_audit_path(song, dj, passed=True)
        audit_path_failed = get_audit_path(song, dj, passed=False)
        
        if audit_path_passed.exists() or audit_path_failed.exists():
            # Already audited, count it
            if audit_path_passed.exists():
                audit_results["passed"] += 1
            else:
                audit_results["failed"] += 1
            logger.debug(f"  [{i}/{len(scripts_to_audit)}] Skipping {song['title']} (already audited)")
            continue
        
        try:
            result = audit_script(
                client=client,
                script_content=script['script_content'],
                script_id=script['script_id'],
                dj=dj,
                content_type="song_intro"
            )
            
            # Save audit result
            audit_path = get_audit_path(song, dj, passed=result.passed)
            audit_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(audit_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "script_id": result.script_id,
                    "dj": result.dj,
                    "content_type": result.content_type,
                    "score": result.score,
                    "passed": result.passed,
                    "criteria_scores": result.criteria_scores,
                    "issues": result.issues,
                    "notes": result.notes
                }, f, indent=2, ensure_ascii=False)
            
            if result.passed:
                audit_results["passed"] += 1
                logger.info(f"  [{i}/{len(scripts_to_audit)}] ✓ {song['title']} ({dj}) - Score: {result.score:.1f}")
            else:
                audit_results["failed"] += 1
                logger.info(f"  [{i}/{len(scripts_to_audit)}] ✗ {song['title']} ({dj}) - Score: {result.score:.1f}")
        
        except Exception as e:
            logger.error(f"  [{i}/{len(scripts_to_audit)}] ERROR auditing {song['title']}: {e}")
            audit_results["failed"] += 1
    
    # Generate summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_scripts": len(scripts_to_audit),
        "passed": audit_results["passed"],
        "failed": audit_results["failed"],
        "pass_rate": audit_results["passed"] / len(scripts_to_audit) if scripts_to_audit else 0,
        "by_dj": {}
    }
    
    for dj in djs:
        dj_passed = len(list((DATA_DIR / "audit" / dj / "passed").glob("*.json"))) if (DATA_DIR / "audit" / dj / "passed").exists() else 0
        dj_failed = len(list((DATA_DIR / "audit" / dj / "failed").glob("*.json"))) if (DATA_DIR / "audit" / dj / "failed").exists() else 0
        summary["by_dj"][dj] = {"passed": dj_passed, "failed": dj_failed}
    
    # Save summary
    summary_path = DATA_DIR / "audit" / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    checkpoint.mark_stage_completed("audit", 
                                   scripts_audited=len(scripts_to_audit),
                                   passed=audit_results["passed"],
                                   failed=audit_results["failed"])
    
    logger.info(f"\n✓ Stage 2 complete: {audit_results['passed']} passed, {audit_results['failed']} failed")
    logger.info(f"  Pass rate: {summary['pass_rate']:.1%}")
    
    return audit_results


def stage_audio(songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint) -> int:
    """Stage 3: Generate audio for passed scripts only."""
    logger.info("\n" + "=" * 60)
    logger.info("STAGE 3: GENERATE AUDIO (Passed Scripts Only)")
    logger.info("=" * 60)
    
    if checkpoint.is_stage_completed("audio"):
        logger.info("Stage 3 already completed, skipping...")
        return checkpoint.state["stages"]["audio"]["audio_files_generated"]
    
    checkpoint.mark_stage_started("audio")
    
    # Collect passed scripts only
    passed_scripts = []
    for dj in djs:
        for song in songs:
            audit_path = get_audit_path(song, dj, passed=True)
            if audit_path.exists():
                passed_scripts.append({"song": song, "dj": dj})
    
    logger.info(f"Generating audio for {len(passed_scripts)} passed scripts...")
    
    # Initialize TTS
    tts_client = TTSClient()
    audio_generated = 0
    
    for i, item in enumerate(passed_scripts, 1):
        song = item['song']
        dj = item['dj']
        
        script_path = get_script_path(song, dj)
        audio_path = get_audio_path(song, dj)
        
        # Check if audio already exists
        if audio_path.exists():
            audio_generated += 1
            logger.debug(f"  [{i}/{len(passed_scripts)}] Skipping {song['title']} (audio exists)")
            continue
        
        try:
            # Read script
            script_text = script_path.read_text(encoding='utf-8')
            
            # Get voice reference
            dj_folder = "Julie" if dj == "julie" else "Mister_New_Vegas"
            voice_ref = VOICE_REFERENCES_DIR / dj_folder / f"{dj}.wav"
            if not voice_ref.exists():
                voice_ref = None
            
            # Generate audio
            generate_audio(tts_client, script_text, audio_path, voice_reference=voice_ref)
            audio_generated += 1
            logger.info(f"  [{i}/{len(passed_scripts)}] ✓ {song['title']} ({dj})")
        
        except Exception as e:
            logger.error(f"  [{i}/{len(passed_scripts)}] ✗ {song['title']} ({dj}) - Error: {e}")
    
    checkpoint.mark_stage_completed("audio", audio_files_generated=audio_generated)
    logger.info(f"\n✓ Stage 3 complete: {audio_generated} audio files generated")
    
    return audio_generated


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_script_path(song: Dict, dj: str) -> Path:
    """Get the path to a script file."""
    safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['artist'])
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['title'])
    safe_artist = safe_artist.strip().replace(' ', '_')
    safe_title = safe_title.strip().replace(' ', '_')
    folder_name = f"{safe_artist}-{safe_title}"
    return GENERATED_DIR / "intros" / dj / folder_name / f"{dj}_0.txt"


def get_audio_path(song: Dict, dj: str) -> Path:
    """Get the path to an audio file."""
    safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['artist'])
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['title'])
    safe_artist = safe_artist.strip().replace(' ', '_')
    safe_title = safe_title.strip().replace(' ', '_')
    folder_name = f"{safe_artist}-{safe_title}"
    return GENERATED_DIR / "intros" / dj / folder_name / f"{dj}_0.wav"


def get_audit_path(song: Dict, dj: str, passed: bool) -> Path:
    """Get the path to an audit result file."""
    safe_artist = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['artist'])
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in song['title'])
    safe_artist = safe_artist.strip().replace(' ', '_')
    safe_title = safe_title.strip().replace(' ', '_')
    folder_name = f"{safe_artist}-{safe_title}"
    status_folder = "passed" if passed else "failed"
    return DATA_DIR / "audit" / dj / status_folder / f"{folder_name}_audit.json"


class FakeAuditorClient:
    """Simple fake client for test mode."""
    def generate(self, prompt: str, *args, **kwargs) -> str:
        # Extract just the script portion (between the last '---')
        parts = prompt.split('---')
        script = parts[-1] if len(parts) > 1 else prompt
        script = script.lower()
        
        # Simple heuristics for pass/fail - be more lenient in test mode
        # Look for actual problematic content in the script
        if "awesome" in script or "😀" in script or "lol" in script or "omg" in script:
            return json.dumps({
                "criteria_scores": {"character_voice": 4, "era_appropriateness": 2, "forbidden_elements": 1, "natural_flow": 4, "length": 6},
                "issues": ["Uses modern slang or emoji"],
                "notes": "Contains modern slang"
            })
        elif "borderline" in script:
            return json.dumps({
                "criteria_scores": {"character_voice": 6, "era_appropriateness": 6, "forbidden_elements": 10, "natural_flow": 6, "length": 6},
                "issues": ["Slight character drift"],
                "notes": "Borderline but acceptable"
            })
        
        # Default: pass with good scores (for test mode)
        return json.dumps({
            "criteria_scores": {"character_voice": 8, "era_appropriateness": 8, "forbidden_elements": 10, "natural_flow": 8, "length": 8},
            "issues": [],
            "notes": "Good script"
        })


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
    logger.info(f"Loaded {len(songs)} songs from catalog")
    logger.info(f"DJs: {', '.join(djs)}")
    
    # Store configuration in checkpoint
    checkpoint.state["config"] = {
        "content_types": ["intros"] if args.intros or args.resume else [],
        "djs": djs,
        "song_limit": len(songs),
        "test_mode": test_mode
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
    """Remove meta-commentary and sanitize TTS-breaking punctuation."""
    # Remove ALL parenthetical content (often meta-commentary)
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove dates/years
    text = re.sub(r'\b(19|20)\d{2}\b', '', text)  # Remove 4-digit years
    text = re.sub(r'\b\d{4}s\b', '', text)  # Remove decade references like "1940s"
    
    # Fix TTS-breaking punctuation
    text = text.replace('...', '…')  # Convert to single ellipsis character first
    text = re.sub(r'([?!]),', r'\1', text)  # Remove comma after ? or !
    text = re.sub(r'\s*-\s*', ' ', text)  # Remove dashes (often used for em-dash)
        # Fix common punctuation errors
    # Add comma before "and" in certain contexts
    text = re.sub(r'(\w+)\s+(and)\s+(?:we|I|it|that)', r'\1, \2 ', text)
    # Fix run-on questions (add ? before new sentence starting with capital)
    text = re.sub(r'(\w+)\s+([A-Z][a-z]+\s+(?:is|are|was|were|has|have))', r'\1? \2', text)
    # Fix missing periods before "Here's" or "Here are" 
    text = re.sub(r'(\w+)\s+(Here(?:\'s| is| are))', r'\1. \2', text)
        # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix ellipsis at sentence boundaries (…. or ….)
    text = re.sub(r'…\.', '.', text)  # Ellipsis + period → single period
    text = re.sub(r'\.{2,}', '.', text)  # Multiple periods → single period
    
    return text


def truncate_after_song_intro(text: str, artist: str, title: str) -> str:
    """Truncate any text that comes after the song introduction."""
    # First, validate artist name appears correctly (catch typos/truncations)
    # Look for partial matches that might indicate truncation
    artist_parts = artist.split()
    if len(artist_parts) > 1:
        # Check if only part of the name appears (e.g., "Louie Armst" instead of "Louis Armstrong")
        for part in artist_parts:
            if len(part) > 3:  # Only check meaningful parts
                # Look for truncated versions (e.g., "Armst" from "Armstrong")
                pattern = re.escape(part[:4])  # First 4 chars
                if re.search(r'\b' + pattern + r'[a-z]{0,2}\b', text, re.IGNORECASE):
                    # Found potentially truncated name - might be incomplete
                    # Try to verify full name is NOT present
                    if part.lower() not in text.lower():
                        # Truncation detected - reject this script
                        logger.warning(f"Detected truncated artist name in script: expected '{artist}', found partial match")
                        # Return empty to flag for rejection
                        return ""
    
    # Split by sentence boundaries more carefully (avoid splitting on abbreviations like Mr. Mrs. Dr.)
    # Simple approach: protect common abbreviations before splitting
    protected_text = text.replace('Mr.', 'Mr~')
    protected_text = protected_text.replace('Mrs.', 'Mrs~')
    protected_text = protected_text.replace('Ms.', 'Ms~')
    protected_text = protected_text.replace('Dr.', 'Dr~')
    
    sentences = re.split(r'([.!?])\s+', protected_text)
    result = []
    found_intro = False
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        sentence = sentences[i]
        punct = sentences[i+1] if i+1 < len(sentences) else '.'
        
        # Check if this sentence contains artist or title
        has_artist = artist.lower() in sentence.lower()
        has_title = title.lower() in sentence.lower()
        
        result.append(sentence + punct)
        
        # If we found both artist and title in this sentence, stop here
        if has_artist and has_title:
            found_intro = True
            break
        # Or if we found just one and we've already accumulated some text
        elif (has_artist or has_title) and len(result) > 1:
            found_intro = True
            break
    
    if found_intro:
        # Restore protected abbreviations
        final_text = ' '.join(result).strip()
        final_text = final_text.replace('Mr~', 'Mr.')
        final_text = final_text.replace('Mrs~', 'Mrs.')
        final_text = final_text.replace('Ms~', 'Ms.')
        final_text = final_text.replace('Dr~', 'Dr.')
        return final_text
    
    # Fallback: return original if no clear intro found (also restore protections)
    text = text.replace('Mr~', 'Mr.')
    text = text.replace('Mrs~', 'Mrs.')
    text = text.replace('Ms~', 'Ms.')
    text = text.replace('Dr~', 'Dr.')


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
    parser.add_argument('--outros', action='store_true', help='Generate song outros (not yet implemented)')
    parser.add_argument('--time', action='store_true', help='Generate time announcements (not yet implemented)')
    parser.add_argument('--weather', action='store_true', help='Generate weather announcements (not yet implemented)')
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
    
    if args.outros or args.time or args.weather or args.all_content:
        parser.error('Currently only --intros is supported')
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run pipeline
    return run_pipeline(args)


if __name__ == '__main__':
    sys.exit(main())

