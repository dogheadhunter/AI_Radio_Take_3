"""Stage: Regenerate failed scripts with feedback.

This module handles regenerating scripts that failed audit, using the
audit feedback to improve the output.
"""
import logging
import json
from pathlib import Path
from typing import List, Dict

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.auditor import audit_script
from src.ai_radio.generation.llm_client import LLMClient
from src.ai_radio.config import DATA_DIR
from src.ai_radio.core.paths import (
    get_script_path,
    get_audit_path,
    get_time_script_path,
    get_time_audit_path,
    get_weather_script_path,
    get_weather_audit_path
)
from src.ai_radio.core.sanitizer import sanitize_script, truncate_after_song_intro
from src.ai_radio.core.checkpoint import PipelineCheckpoint
from src.ai_radio.stages.utils import FakeAuditorClient, get_lyrics_for_song

logger = logging.getLogger(__name__)


def stage_regenerate(pipeline: GenerationPipeline, songs: List[Dict], djs: List[str], max_retries: int = 5, test_mode: bool = False) -> int:
    """Regenerate failed scripts up to max_retries times, processing each DJ separately."""
    logger.info("\n" + "=" * 60)
    logger.info(f"REGENERATION LOOP (max {max_retries} retries)")
    logger.info("=" * 60)
    
    total_regenerated = 0
    
    # Get content types from checkpoint (needed for time announcements)
    checkpoint_file = DATA_DIR / "pipeline_state.json"
    checkpoint = PipelineCheckpoint(checkpoint_file)
    content_types = checkpoint.state.get("config", {}).get("content_types", [])
    time_slots = checkpoint.state.get("config", {}).get("time_slots", [])
    
    for retry in range(max_retries):
        # Check if there are any failed scripts across all DJs
        total_failed = sum(
            len(list((DATA_DIR / "audit" / dj / "failed").glob("*.json")))
            for dj in djs
            if (DATA_DIR / "audit" / dj / "failed").exists()
        )
        
        if total_failed == 0:
            logger.info("No failed scripts to regenerate!")
            return total_regenerated
        
        logger.info(f"\n--- Retry {retry + 1}/{max_retries} ---")
        logger.info(f"Total failed scripts: {total_failed}")
        
        # Process each DJ separately
        for dj in djs:
            # Identify failed scripts for this DJ (support intros, outros, and time)
            failed_scripts = []  # list of {'song': song, 'failed_types': [..]} or {'time_slot': (h,m), 'failed_types': ['time_announcement']}
            
            # Check song-based content (intros, outros)
            for song in songs:
                failed_types = []
                if get_audit_path(song, dj, passed=False, content_type='song_intro').exists():
                    failed_types.append('song_intro')
                if get_audit_path(song, dj, passed=False, content_type='song_outro').exists():
                    failed_types.append('song_outro')
                if failed_types:
                    failed_scripts.append({'song': song, 'failed_types': failed_types})
            
            # Check time announcements
            if "time" in content_types:
                for hour, minute in time_slots:
                    if get_time_audit_path(hour, minute, dj, passed=False).exists():
                        failed_scripts.append({'time_slot': (hour, minute), 'failed_types': ['time_announcement']})
            
            if not failed_scripts:
                logger.debug(f"No failed scripts for {dj}")
                continue
            
            logger.info(f"\nRegenerating {len(failed_scripts)} failed scripts for {dj.upper()}...")
            
            # Helper to extract feedback from failed audit JSON
            def extract_audit_feedback(audit_path: Path) -> str:
                """Read audit JSON and format issues/notes as feedback string."""
                if not audit_path.exists():
                    return None
                try:
                    with open(audit_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    issues = data.get("issues", [])
                    notes = data.get("notes", "")
                    criteria = data.get("criteria_scores", {})
                    
                    feedback_parts = []
                    if issues:
                        feedback_parts.append("Issues: " + "; ".join(issues))
                    if notes:
                        feedback_parts.append("Notes: " + notes)
                    # Add low-scoring criteria
                    low_scores = [f"{k}={v}" for k, v in criteria.items() if isinstance(v, (int, float)) and v < 8]
                    if low_scores:
                        feedback_parts.append("Low scores: " + ", ".join(low_scores))
                    
                    return " | ".join(feedback_parts) if feedback_parts else None
                except Exception as e:
                    logger.warning(f"Could not read audit feedback: {e}")
                    return None
            
            # Regenerate scripts for this DJ (extract feedback, delete, regenerate in one pass)
            regenerated = 0
            for i, entry in enumerate(failed_scripts, 1):
                for ctype in entry['failed_types']:
                    try:
                        # Get paths and extract feedback BEFORE deleting
                        audit_feedback = None
                        if ctype == 'time_announcement':
                            hour, minute = entry['time_slot']
                            script_path = get_time_script_path(hour, minute, dj)
                            audit_path_failed = get_time_audit_path(hour, minute, dj, passed=False)
                            audit_feedback = extract_audit_feedback(audit_path_failed)
                        else:
                            song = entry['song']
                            if ctype == 'song_intro':
                                script_path = get_script_path(song, dj, content_type='intros')
                            else:
                                script_path = get_script_path(song, dj, content_type='outros')
                            audit_path_failed = get_audit_path(song, dj, passed=False, content_type=ctype)
                            audit_feedback = extract_audit_feedback(audit_path_failed)
                        
                        # Delete old script and audit
                        if script_path.exists():
                            script_path.unlink()
                        if audit_path_failed.exists():
                            audit_path_failed.unlink()
                        
                        # Log feedback if present
                        if audit_feedback:
                            logger.debug(f"  Feedback for regen: {audit_feedback[:100]}...")
                        
                        # Regenerate with feedback
                        if ctype == 'time_announcement':
                            hour, minute = entry['time_slot']
                            result = pipeline.generate_time_announcement(
                                hour=hour,
                                minute=minute,
                                dj=dj,
                                text_only=True
                            )
                            
                            if result.success and result.text:
                                sanitized = sanitize_script(result.text)
                                if sanitized:
                                    script_path.parent.mkdir(parents=True, exist_ok=True)
                                    script_path.write_text(sanitized, encoding='utf-8')
                                    regenerated += 1
                                    logger.debug(f"  [{i}/{len(failed_scripts)}] ✓ Regenerated time {hour:02d}:{minute:02d}")
                        elif ctype == 'song_intro':
                            song = entry['song']
                            script_path = get_script_path(song, dj, content_type='intros')
                            # Get lyrics for feedback loop
                            lyrics_context = get_lyrics_for_song(song['artist'], song['title'])
                            result = pipeline.generate_song_intro(
                                song_id=song['id'],
                                artist=song['artist'],
                                title=song['title'],
                                dj=dj,
                                text_only=True,
                                lyrics_context=lyrics_context,
                                audit_feedback=audit_feedback
                            )
                            
                            if result.success and result.text:
                                # Sanitize and truncate
                                sanitized = sanitize_script(result.text)
                                truncated = truncate_after_song_intro(sanitized, song['artist'], song['title'])
                                
                                if truncated:
                                    script_path.parent.mkdir(parents=True, exist_ok=True)
                                    script_path.write_text(truncated, encoding='utf-8')
                                    regenerated += 1
                                    logger.debug(f"  [{i}/{len(failed_scripts)}] ✓ Regenerated intro {song['title']}")
                        elif ctype == 'song_outro':
                            song = entry['song']
                            script_path = get_script_path(song, dj, content_type='outros')
                            # Get lyrics for feedback loop
                            lyrics_context = get_lyrics_for_song(song['artist'], song['title'])
                            result = pipeline.generate_song_outro(
                                song_id=song['id'],
                                artist=song['artist'],
                                title=song['title'],
                                dj=dj,
                                text_only=True,
                                lyrics_context=lyrics_context,
                                audit_feedback=audit_feedback
                            )
                            
                            if result.success and result.text:
                                sanitized = sanitize_script(result.text)
                                if sanitized:
                                    script_path.parent.mkdir(parents=True, exist_ok=True)
                                    script_path.write_text(sanitized, encoding='utf-8')
                                    regenerated += 1
                                    logger.debug(f"  [{i}/{len(failed_scripts)}] ✓ Regenerated outro {song['title']}")
                    except Exception as e:
                        display_name = f"{entry['time_slot'][0]:02d}:{entry['time_slot'][1]:02d}" if ctype == 'time_announcement' else entry['song']['title']
                        logger.error(f"  [{i}/{len(failed_scripts)}] ✗ Error regenerating {display_name} ({ctype}): {e}")
            
            logger.info(f"Regenerated {regenerated} scripts for {dj}")
            total_regenerated += regenerated
            
            # Re-audit regenerated scripts for this DJ
            if regenerated > 0:
                logger.info(f"Re-auditing regenerated scripts for {dj.upper()}...")
                
                # Prepare audit client
                if test_mode:
                    client = FakeAuditorClient()
                else:
                    client = LLMClient(model="dolphin-llama3")
                
                new_passed = 0
                new_failed = 0
                
                for i, entry in enumerate(failed_scripts, 1):
                    for ctype in entry['failed_types']:
                        if ctype == 'time_announcement':
                            hour, minute = entry['time_slot']
                            script_path = get_time_script_path(hour, minute, dj)
                            
                            if not script_path.exists():
                                continue
                            
                            try:
                                content = script_path.read_text(encoding='utf-8')
                                time_id = f"{hour:02d}-{minute:02d}"
                                script_id = f"{time_id}_{dj}_time"
                                
                                result = audit_script(
                                    client=client,
                                    script_content=content,
                                    script_id=script_id,
                                    dj=dj,
                                    content_type=ctype
                                )
                                
                                # Save audit result
                                audit_path = get_time_audit_path(hour, minute, dj, passed=result.passed)
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
                                    new_passed += 1
                                    logger.info(f"  [{i}/{len(failed_scripts)}] ✓ {hour:02d}:{minute:02d} - Score: {result.score:.1f}")
                                else:
                                    new_failed += 1
                                    logger.debug(f"  [{i}/{len(failed_scripts)}] ✗ {hour:02d}:{minute:02d} - Score: {result.score:.1f}")
                            
                            except Exception as e:
                                logger.error(f"  [{i}/{len(failed_scripts)}] ERROR re-auditing {hour:02d}:{minute:02d}: {e}")
                        else:
                            song = entry['song']
                            script_path = get_script_path(song, dj, content_type='intros' if ctype == 'song_intro' else 'outros')
                        
                            if not script_path.exists():
                                continue
                            
                            try:
                                content = script_path.read_text(encoding='utf-8')
                                script_id = f"{song['id']}_{dj}_intro" if ctype == 'song_intro' else f"{song['id']}_{dj}_outro"
                                
                                result = audit_script(
                                    client=client,
                                    script_content=content,
                                    script_id=script_id,
                                    dj=dj,
                                    content_type=ctype
                                )
                                
                                # Save audit result
                                audit_path = get_audit_path(song, dj, passed=result.passed, content_type=ctype)
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
                                    new_passed += 1
                                    logger.info(f"  [{i}/{len(failed_scripts)}] ✓ {song['title']} - Score: {result.score:.1f}")
                                else:
                                    new_failed += 1
                                    logger.debug(f"  [{i}/{len(failed_scripts)}] ✗ {song['title']} - Score: {result.score:.1f}")
                            
                            except Exception as e:
                                logger.error(f"  [{i}/{len(failed_scripts)}] ERROR re-auditing {song['title']}: {e}")
                
                logger.info(f"Re-audit complete for {dj}: {new_passed} passed, {new_failed} failed")
        
        # Check if all scripts passed after this retry
        total_failed_after = sum(
            len(list((DATA_DIR / "audit" / dj / "failed").glob("*.json")))
            for dj in djs
            if (DATA_DIR / "audit" / dj / "failed").exists()
        )
        
        if total_failed_after == 0:
            logger.info(f"\n✓ All scripts passed after {retry + 1} retries!")
            return total_regenerated
    
    logger.info(f"\n✓ Regeneration complete after {max_retries} retries")
    return total_regenerated
