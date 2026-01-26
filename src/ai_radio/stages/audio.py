"""Stage 3: Generate audio for passed scripts.

This module contains the audio generation stage of the pipeline, responsible for
converting text scripts that passed audit into audio files using TTS.
"""
import logging
from pathlib import Path
from typing import List, Dict

from src.ai_radio.generation.tts_client import TTSClient, generate_audio
from src.ai_radio.config import VOICE_REFERENCES_DIR
from src.ai_radio.core.paths import get_script_path, get_audit_path, get_audio_path
from src.ai_radio.core.checkpoint import PipelineCheckpoint

logger = logging.getLogger(__name__)


def stage_audio(songs: List[Dict], djs: List[str], checkpoint: PipelineCheckpoint) -> int:
    """Stage 3: Generate audio for passed scripts only."""
    logger.info("\n" + "=" * 60)
    logger.info("STAGE 3: GENERATE AUDIO (Passed Scripts Only)")
    logger.info("=" * 60)
    
    if checkpoint.is_stage_completed("audio"):
        logger.info("Stage 3 already completed, skipping...")
        return checkpoint.state["stages"]["audio"]["audio_files_generated"]
    
    checkpoint.mark_stage_started("audio")
    
    # Collect passed scripts only (include intros and outros)
    passed_scripts = []
    for dj in djs:
        for song in songs:
            if get_audit_path(song, dj, passed=True, content_type='song_intro').exists():
                passed_scripts.append({"song": song, "dj": dj, "content_type": "song_intro"})
            if get_audit_path(song, dj, passed=True, content_type='song_outro').exists():
                passed_scripts.append({"song": song, "dj": dj, "content_type": "song_outro"})
    
    logger.info(f"Generating audio for {len(passed_scripts)} passed scripts...")
    
    # Initialize TTS
    tts_client = TTSClient()
    audio_generated = 0
    
    for i, item in enumerate(passed_scripts, 1):
        song = item['song']
        dj = item['dj']
        ctype = item.get('content_type', 'song_intro')
        
        script_path = get_script_path(song, dj, content_type='outros' if ctype == 'song_outro' else 'intros')
        audio_path = get_audio_path(song, dj, content_type='outros' if ctype == 'song_outro' else 'intros')        
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
