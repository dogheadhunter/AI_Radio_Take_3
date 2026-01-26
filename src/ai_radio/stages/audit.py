"""Stage 2: Audit all generated scripts.

This module contains the audit stage of the pipeline, responsible for
evaluating the quality of generated scripts using the auditor client.
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

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
from src.ai_radio.core.checkpoint import PipelineCheckpoint
from src.ai_radio.stages.utils import FakeAuditorClient

logger = logging.getLogger(__name__)


def stage_audit(songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint, test_mode: bool = False) -> Dict[str, int]:
    """Stage 2: Audit all generated scripts, processing each DJ separately."""
    logger.info("\n" + "=" * 60)
    logger.info("STAGE 2: AUDIT SCRIPTS")
    logger.info("=" * 60)
    
    if checkpoint.is_stage_completed("audit"):
        logger.info("Stage 2 already completed, skipping...")
        stats = checkpoint.state["stages"]["audit"]
        return {"passed": stats["passed"], "failed": stats["failed"]}
    
    checkpoint.mark_stage_started("audit")
    
    # Process each DJ separately to avoid cross-contamination
    total_audit_results = {"passed": 0, "failed": 0}
    
    for dj in djs:
        logger.info(f"\nAuditing scripts for {dj.upper()}...")
        
        # Prepare audit client for this DJ
        if test_mode:
            client = FakeAuditorClient()
        else:
            # Use Dolphin model for auditing (different from Stheno used for generation)
            client = LLMClient(model="dolphin-llama3")
        
        # Collect scripts for this DJ (support intros and outros)
        content_types = checkpoint.state.get("config", {}).get("content_types", [])
        scripts_to_audit = []
        for song in songs:
            if "intros" in content_types:
                script_path = get_script_path(song, dj, content_type='intros')
                if script_path.exists():
                    script_id = f"{song['id']}_{dj}_intro"
                    content = script_path.read_text(encoding='utf-8')
                    scripts_to_audit.append({
                        "script_id": script_id,
                        "script_content": content,
                        "dj": dj,
                        "content_type": "song_intro",
                        "song": song
                    })
            if "outros" in content_types:
                script_path = get_script_path(song, dj, content_type='outros')
                if script_path.exists():
                    script_id = f"{song['id']}_{dj}_outro"
                    content = script_path.read_text(encoding='utf-8')
                    scripts_to_audit.append({
                        "script_id": script_id,
                        "script_content": content,
                        "dj": dj,
                        "content_type": "song_outro",
                        "song": song
                    })
        
        # Time announcements
        if "time" in content_types:
            time_slots = checkpoint.state.get("config", {}).get("time_slots", [])
            for hour, minute in time_slots:
                script_path = get_time_script_path(hour, minute, dj)
                if script_path.exists():
                    time_id = f"{hour:02d}-{minute:02d}"
                    script_id = f"{time_id}_{dj}_time"
                    content = script_path.read_text(encoding='utf-8')
                    scripts_to_audit.append({
                        "script_id": script_id,
                        "script_content": content,
                        "dj": dj,
                        "content_type": "time_announcement",
                        "time_slot": (hour, minute)
                    })
        
        # Weather announcements
        if "weather" in content_types:
            from src.ai_radio.config import WEATHER_TIMES
            for hour in WEATHER_TIMES:
                script_path = get_weather_script_path(hour, dj)
                if script_path.exists():
                    time_id = f"{hour:02d}-00"
                    script_id = f"{time_id}_{dj}_weather"
                    content = script_path.read_text(encoding='utf-8')
                    scripts_to_audit.append({
                        "script_id": script_id,
                        "script_content": content,
                        "dj": dj,
                        "content_type": "weather_announcement",
                        "weather_hour": hour
                    })
        
        if not scripts_to_audit:
            logger.info(f"No scripts found for {dj}")
            continue
        
        # Run audits for this DJ
        for i, script in enumerate(scripts_to_audit, 1):
            ctype = script['content_type']
            
            # Determine audit paths and display name based on content type
            if ctype == "time_announcement":
                hour, minute = script['time_slot']
                audit_path_passed = get_time_audit_path(hour, minute, dj, passed=True)
                audit_path_failed = get_time_audit_path(hour, minute, dj, passed=False)
                display_name = f"{hour:02d}:{minute:02d}"
            elif ctype == "weather_announcement":
                hour = script['weather_hour']
                audit_path_passed = get_weather_audit_path(hour, dj, passed=True)
                audit_path_failed = get_weather_audit_path(hour, dj, passed=False)
                display_name = f"{hour:02d}:00"
            else:
                song = script['song']
                audit_path_passed = get_audit_path(song, dj, passed=True, content_type=ctype)
                audit_path_failed = get_audit_path(song, dj, passed=False, content_type=ctype)
                display_name = song['title']
            
            if audit_path_passed.exists() or audit_path_failed.exists():
                # Already audited, count it
                if audit_path_passed.exists():
                    total_audit_results["passed"] += 1
                else:
                    total_audit_results["failed"] += 1
                logger.debug(f"  [{i}/{len(scripts_to_audit)}] Skipping {display_name} (already audited for {ctype})")
                continue
            
            try:
                result = audit_script(
                    client=client,
                    script_content=script['script_content'],
                    script_id=script['script_id'],
                    dj=dj,
                    content_type=ctype
                )
                
                # Save audit result (different path for time/weather vs songs)
                if ctype == "time_announcement":
                    hour, minute = script['time_slot']
                    audit_path = get_time_audit_path(hour, minute, dj, passed=result.passed)
                elif ctype == "weather_announcement":
                    hour = script['weather_hour']
                    audit_path = get_weather_audit_path(hour, dj, passed=result.passed)
                else:
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
                    total_audit_results["passed"] += 1
                    logger.info(f"  [{i}/{len(scripts_to_audit)}] ✓ {display_name} - Score: {result.score:.1f}")
                else:
                    total_audit_results["failed"] += 1
                    logger.info(f"  [{i}/{len(scripts_to_audit)}] ✗ {display_name} - Score: {result.score:.1f}")
            
            except Exception as e:
                logger.error(f"  [{i}/{len(scripts_to_audit)}] ERROR auditing {display_name}: {e}")
                total_audit_results["failed"] += 1
    
    # Generate summary
    total_scripts = sum(len(list((DATA_DIR / "audit" / dj / "passed").glob("*.json"))) + 
                       len(list((DATA_DIR / "audit" / dj / "failed").glob("*.json"))) 
                       for dj in djs 
                       if (DATA_DIR / "audit" / dj).exists())
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_scripts": total_scripts,
        "passed": total_audit_results["passed"],
        "failed": total_audit_results["failed"],
        "pass_rate": total_audit_results["passed"] / total_scripts if total_scripts else 0,
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
                                   scripts_audited=total_scripts,
                                   passed=total_audit_results["passed"],
                                   failed=total_audit_results["failed"])
    
    logger.info(f"\n✓ Stage 2 complete: {total_audit_results['passed']} passed, {total_audit_results['failed']} failed")
    logger.info(f"  Pass rate: {summary['pass_rate']:.1%}")
    
    return total_audit_results
