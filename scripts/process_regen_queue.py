"""
Process items in the regeneration queue.

Reads data/regeneration_queue.json and regenerates scripts/audio
based on reviewer feedback, then clears the queue.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.prompts import DJ


REGEN_QUEUE_FILE = Path("data/regeneration_queue.json")
LOG_FILE = Path("logs/regeneration_log.txt")


def log_message(message: str):
    """Log a message to both console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")


def get_next_version_number(folder_path: Path, dj: str, content_type: str = None) -> int:
    """Determine the next version number for regeneration."""
    # Find all existing versions
    # Handle different naming conventions for outros vs other types
    if content_type == "outros":
        # Outros use: julie_outro.txt, julie_outro_1.txt, etc.
        existing_files = list(folder_path.glob(f"{dj}_outro*.txt")) + list(folder_path.glob(f"{dj}_outro*.wav"))
    else:
        # Other types use: julie_0.txt, julie_1.txt, etc.
        existing_files = list(folder_path.glob(f"{dj}_*.txt")) + list(folder_path.glob(f"{dj}_*.wav"))
    
    if not existing_files:
        return 0
    
    max_version = 0
    for file_path in existing_files:
        try:
            stem_parts = file_path.stem.split('_')
            if content_type == "outros":
                # julie_outro or julie_outro_1
                if len(stem_parts) > 2:
                    version = int(stem_parts[-1])
                    max_version = max(max_version, version)
                # else version 0 (julie_outro)
            else:
                # julie_0 or julie_1
                version = int(stem_parts[-1])
                max_version = max(max_version, version)
        except (ValueError, IndexError):
            pass
    
    return max_version + 1


def parse_song_info_from_folder(folder_name: str) -> tuple:
    """Extract artist and title from folder name (format: Artist-Title)."""
    parts = folder_name.split('-', 1)
    if len(parts) == 2:
        artist = parts[0].replace('_', ' ').strip()
        title = parts[1].replace('_', ' ').strip()
        return artist, title
    return "Unknown", "Unknown"


def parse_time_info_from_folder(folder_name: str) -> tuple:
    """Extract hour and minute from time folder name (format: HH-MM)."""
    parts = folder_name.split('-')
    if len(parts) == 2:
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            return hour, minute
        except ValueError:
            pass
    return 0, 0


def regenerate_song_intro(pipeline: GenerationPipeline, item: Dict[str, Any], next_version: int) -> bool:
    """Regenerate a song intro."""
    folder_path = Path(item['folder_path'])
    dj = item['dj']
    
    # Parse song info from folder name
    artist, title = parse_song_info_from_folder(folder_path.name)
    song_id = f"{artist}-{title}"
    
    # Determine what to regenerate
    text_only = item['regenerate_type'] == 'script'
    audio_only = item['regenerate_type'] == 'audio'
    
    log_message(f"Regenerating intro for {song_id} ({dj}), type: {item['regenerate_type']}")
    
    try:
        # Update pipeline output to use the existing folder
        # We need to manually handle version numbering
        result = pipeline.generate_song_intro(
            song_id=song_id,
            artist=artist,
            title=title,
            dj=dj,
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=item['feedback']
        )
        
        if result.success:
            # Rename files to next version
            if not audio_only and result.text:
                old_script = folder_path / f"{dj}_0.txt"
                new_script = folder_path / f"{dj}_{next_version}.txt"
                if old_script.exists():
                    old_script.rename(new_script)
            
            if not text_only and result.audio_path:
                old_audio = folder_path / f"{dj}_0.wav"
                new_audio = folder_path / f"{dj}_{next_version}.wav"
                if old_audio.exists() and old_audio != result.audio_path:
                    old_audio.rename(new_audio)
            
            log_message(f"✓ Successfully regenerated {song_id}")
            return True
        else:
            log_message(f"✗ Failed to regenerate {song_id}: {result.error}")
            return False
    except Exception as e:
        log_message(f"✗ Exception regenerating {song_id}: {e}")
        return False


def regenerate_song_outro(pipeline: GenerationPipeline, item: Dict[str, Any], next_version: int) -> bool:
    """Regenerate a song outro."""
    folder_path = Path(item['folder_path'])
    dj = item['dj']
    
    # Parse song info from folder name
    artist, title = parse_song_info_from_folder(folder_path.name)
    song_id = f"{artist}-{title}"
    
    # Determine what to regenerate
    text_only = item['regenerate_type'] == 'script'
    audio_only = item['regenerate_type'] == 'audio'
    
    log_message(f"Regenerating outro for {song_id} ({dj}), type: {item['regenerate_type']}")
    
    try:
        result = pipeline.generate_song_outro(
            song_id=song_id,
            artist=artist,
            title=title,
            dj=dj,
            text_only=text_only,
            audio_only=audio_only,
            audit_feedback=item['feedback']
        )
        
        if result.success:
            # Rename files to next version
            # Outros use different naming: julie_outro.txt -> julie_outro_1.txt
            if not audio_only and result.text:
                old_script = folder_path / f"{dj}_outro.txt"
                if next_version == 1:
                    new_script = folder_path / f"{dj}_outro_1.txt"
                else:
                    new_script = folder_path / f"{dj}_outro_{next_version}.txt"
                if old_script.exists():
                    old_script.rename(new_script)
            
            if not text_only and result.audio_path:
                old_audio = folder_path / f"{dj}_outro.wav"
                if next_version == 1:
                    new_audio = folder_path / f"{dj}_outro_1.wav"
                else:
                    new_audio = folder_path / f"{dj}_outro_{next_version}.wav"
                if old_audio.exists() and old_audio != result.audio_path:
                    old_audio.rename(new_audio)
            
            log_message(f"✓ Successfully regenerated {song_id}")
            return True
        else:
            log_message(f"✗ Failed to regenerate {song_id}: {result.error}")
            return False
    except Exception as e:
        log_message(f"✗ Exception regenerating {song_id}: {e}")
        return False


def regenerate_time_announcement(pipeline: GenerationPipeline, item: Dict[str, Any], next_version: int) -> bool:
    """Regenerate a time announcement."""
    folder_path = Path(item['folder_path'])
    dj = item['dj']
    
    # Parse time info from folder name
    hour, minute = parse_time_info_from_folder(folder_path.name)
    
    # Determine what to regenerate
    text_only = item['regenerate_type'] == 'script'
    audio_only = item['regenerate_type'] == 'audio'
    
    log_message(f"Regenerating time announcement for {hour:02d}:{minute:02d} ({dj}), type: {item['regenerate_type']}")
    
    try:
        result = pipeline.generate_time_announcement(
            hour=hour,
            minute=minute,
            dj=dj,
            text_only=text_only,
            audio_only=audio_only
        )
        
        if result.success:
            # Rename files to next version
            if not audio_only and result.text:
                old_script = folder_path / f"{dj}_0.txt"
                new_script = folder_path / f"{dj}_{next_version}.txt"
                if old_script.exists():
                    old_script.rename(new_script)
            
            if not text_only and result.audio_path:
                old_audio = folder_path / f"{dj}_0.wav"
                new_audio = folder_path / f"{dj}_{next_version}.wav"
                if old_audio.exists() and old_audio != result.audio_path:
                    old_audio.rename(new_audio)
            
            log_message(f"✓ Successfully regenerated time announcement")
            return True
        else:
            log_message(f"✗ Failed to regenerate time announcement: {result.error}")
            return False
    except Exception as e:
        log_message(f"✗ Exception regenerating time announcement: {e}")
        return False


def regenerate_weather_announcement(pipeline: GenerationPipeline, item: Dict[str, Any], next_version: int) -> bool:
    """Regenerate a weather announcement."""
    folder_path = Path(item['folder_path'])
    dj = item['dj']
    
    # Parse hour and minute from folder name (format: HH-MM)
    parts = folder_path.name.split('-')
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except (ValueError, IndexError):
        hour, minute = 12, 0  # Default fallback
    
    # Determine what to regenerate
    text_only = item['regenerate_type'] == 'script'
    audio_only = item['regenerate_type'] == 'audio'
    
    log_message(f"Regenerating weather announcement for {folder_path.name} ({dj}), type: {item['regenerate_type']}")
    
    try:
        # For weather, we pass hour and minute (not condition)
        # The pipeline will handle weather data fetching internally
        result = pipeline.generate_weather_announcement(
            hour=hour,
            minute=minute,
            dj=dj,
            weather_data=None,  # Let pipeline handle weather data
            text_only=text_only,
            audio_only=audio_only
        )
        
        if result.success:
            # Rename files to next version
            if not audio_only and result.text:
                old_script = folder_path / f"{dj}_0.txt"
                new_script = folder_path / f"{dj}_{next_version}.txt"
                if old_script.exists():
                    old_script.rename(new_script)
            
            if not text_only and result.audio_path:
                old_audio = folder_path / f"{dj}_0.wav"
                new_audio = folder_path / f"{dj}_{next_version}.wav"
                if old_audio.exists() and old_audio != result.audio_path:
                    old_audio.rename(new_audio)
            
            log_message(f"✓ Successfully regenerated weather announcement")
            return True
        else:
            log_message(f"✗ Failed to regenerate weather announcement: {result.error}")
            return False
    except Exception as e:
        log_message(f"✗ Exception regenerating weather announcement: {e}")
        return False


def process_queue():
    """Process all items in the regeneration queue."""
    if not REGEN_QUEUE_FILE.exists():
        log_message("No regeneration queue found.")
        return
    
    # Load queue
    try:
        queue = json.loads(REGEN_QUEUE_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        log_message(f"Error loading queue: {e}")
        return
    
    if not queue:
        log_message("Regeneration queue is empty.")
        return
    
    log_message(f"Processing {len(queue)} items in regeneration queue...")
    
    # Initialize pipeline with v2 prompts
    pipeline = GenerationPipeline(
        output_dir=Path("data/generated"),
        prompt_version="v2"
    )
    
    success_count = 0
    fail_count = 0
    
    for item in queue:
        content_type = item['content_type']
        folder_path = Path(item['folder_path'])
        dj = item['dj']
        
        # Get next version number
        next_version = get_next_version_number(folder_path, dj, content_type)
        
        # Process based on content type
        success = False
        if content_type == 'intros':
            success = regenerate_song_intro(pipeline, item, next_version)
        elif content_type == 'outros':
            success = regenerate_song_outro(pipeline, item, next_version)
        elif content_type == 'time':
            success = regenerate_time_announcement(pipeline, item, next_version)
        elif content_type == 'weather':
            success = regenerate_weather_announcement(pipeline, item, next_version)
        else:
            log_message(f"Unknown content type: {content_type}")
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    # Clear queue after processing
    REGEN_QUEUE_FILE.write_text("[]", encoding='utf-8')
    
    log_message(f"\nRegeneration complete: {success_count} succeeded, {fail_count} failed")
    log_message("Queue cleared.")


def main():
    """Main entry point."""
    log_message("=" * 60)
    log_message("AI Radio Regeneration Queue Processor")
    log_message("=" * 60)
    
    try:
        process_queue()
    except Exception as e:
        log_message(f"Fatal error: {e}")
        import traceback
        log_message(traceback.format_exc())
        sys.exit(1)
    
    log_message("Done.")


if __name__ == "__main__":
    main()
