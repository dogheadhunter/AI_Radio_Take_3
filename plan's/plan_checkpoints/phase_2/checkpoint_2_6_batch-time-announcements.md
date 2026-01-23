# Checkpoint 2.6: Batch Time Announcements Generation

#### Checkpoint 2.6: Batch Time Announcements Generation
**Implement batch generation for time announcements to pre-generate all 24-hour time slots.**

## Overview
Generate all time announcements for a 24-hour period (48 announcements at 30-minute intervals) for both DJs. This enables the station to run without real-time LLM/TTS dependencies.

## Tasks

### Task 1: Extend Generation Pipeline for Time Announcements
- [x] Add `generate_time_announcement()` method to `GenerationPipeline`
- [x] Create output structure: `data/generated/time/<dj>/<HH-MM>/`
- [x] Save both text script and audio file
- [x] Handle voice reference if available

### Task 2: Implement Batch Time Generation Iterator
- [x] Create `generate_batch_time_announcements()` function
- [x] Generate for all 48 time slots (00:00, 00:30, 01:00, ... 23:30)
- [x] Support resume mode (skip existing files)
- [x] Add progress callback support
- [x] Handle both DJs (julie, mr_new_vegas)

### Task 3: Update Generation Script
- [x] Implement `--time-announcements` flag in `scripts/generate_content.py`
- [x] Display progress during generation
- [x] Show success/failure counts
- [x] Support `--resume` for interrupted generation

### Task 4: Test Time Announcement Generation
- [x] Test dry-run mode shows correct count (48 × DJs)
- [x] Test generation creates proper directory structure
- [x] Test resume mode skips existing files
- [x] Verify audio files are valid and playable

## Implementation Details

**File: `src/ai_radio/generation/pipeline.py`**

Add method to `GenerationPipeline` class:

```python
def generate_time_announcement(
    self,
    hour: int,
    minute: int,
    dj: str,
) -> GenerationResult:
    """Generate a time announcement.
    
    Args:
        hour: Hour (0-23)
        minute: Minute (0, 30)
        dj: DJ personality name
        
    Returns:
        GenerationResult with paths to text and audio files
    """
    from ai_radio.generation.prompts import build_time_announcement_prompt
    
    # Build prompt
    prompt = build_time_announcement_prompt(hour, minute, dj)
    
    # Generate text with LLM
    response = self.llm_client.generate(prompt)
    script = response.strip()
    
    # Create output directory
    time_str = f"{hour:02d}-{minute:02d}"
    output_dir = self.output_dir / "time" / dj / time_str
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save script
    script_path = output_dir / f"{dj}_0.txt"
    script_path.write_text(script, encoding="utf-8")
    
    # Generate audio
    audio_path = output_dir / f"{dj}_0.wav"
    voice_ref = self._get_voice_reference(dj)
    self.tts_client.generate_audio(script, str(audio_path), voice_reference=voice_ref)
    
    return GenerationResult(
        success=True,
        time_slot=time_str,
        dj=dj,
        script_path=str(script_path),
        audio_path=str(audio_path),
    )
```

Add batch generation function:

```python
def generate_batch_time_announcements(
    pipeline: GenerationPipeline,
    dj: str,
    resume: bool = False,
    progress_callback: Optional[Callable] = None,
) -> Iterator[GenerationResult]:
    """Generate all time announcements for 24 hours.
    
    Generates 48 announcements (every 30 minutes) for the specified DJ.
    
    Args:
        pipeline: GenerationPipeline instance
        dj: DJ personality name
        resume: Skip existing files if True
        progress_callback: Optional callback(progress_info)
        
    Yields:
        GenerationResult for each time announcement
    """
    # Generate all time slots
    time_slots = []
    for hour in range(24):
        for minute in [0, 30]:
            time_slots.append((hour, minute))
    
    total = len(time_slots)
    completed = 0
    failed = 0
    
    for hour, minute in time_slots:
        time_str = f"{hour:02d}-{minute:02d}"
        
        # Check if already generated (resume mode)
        output_dir = pipeline.output_dir / "time" / dj / time_str
        audio_path = output_dir / f"{dj}_0.wav"
        
        if resume and audio_path.exists():
            # Skip existing, but yield skipped result
            completed += 1
            if progress_callback:
                progress_callback({
                    "total": total,
                    "completed": completed,
                    "failed": failed,
                    "percent": (completed / total) * 100,
                    "current_slot": time_str,
                    "skipped": True,
                })
            yield GenerationResult(
                success=True,
                time_slot=time_str,
                dj=dj,
                skipped=True,
            )
            continue
        
        try:
            result = pipeline.generate_time_announcement(hour, minute, dj)
            completed += 1
            
            if progress_callback:
                progress_callback({
                    "total": total,
                    "completed": completed,
                    "failed": failed,
                    "percent": (completed / total) * 100,
                    "current_slot": time_str,
                })
            
            yield result
            
        except Exception as e:
            failed += 1
            logger.error(f"Failed to generate time announcement {time_str} for {dj}: {e}")
            
            if progress_callback:
                progress_callback({
                    "total": total,
                    "completed": completed,
                    "failed": failed,
                    "percent": (completed / total) * 100,
                    "current_slot": time_str,
                })
            
            yield GenerationResult(
                success=False,
                time_slot=time_str,
                dj=dj,
                error=str(e),
            )
```

**File: `scripts/generate_content.py`**

Update the `--time-announcements` implementation:

```python
if args.time_announcements:
    print(f"Generating time announcements for 24 hours...")
    print(f"DJ: {args.dj}")
    print(f"Resume mode: {args.resume}")
    print("-" * 50)
    
    from ai_radio.generation.pipeline import generate_batch_time_announcements
    
    pipeline = GenerationPipeline(output_dir=GENERATED_DIR)
    djs = ["julie", "mr_new_vegas"] if args.dj == "all" else [args.dj]
    
    for dj in djs:
        print(f"\n=== Generating {dj.upper()} time announcements ===\n")
        
        start_time = datetime.now()
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        def progress_callback(progress):
            elapsed = datetime.now() - start_time
            skipped_marker = " [SKIP]" if progress.get("skipped") else ""
            print(f"\r[{progress['percent']:.1f}%] {progress['completed']}/{progress['total']} "
                  f"({progress['failed']} failed) - {progress['current_slot']}{skipped_marker}...", 
                  end="", flush=True)
        
        for result in generate_batch_time_announcements(
            pipeline,
            dj=dj,
            resume=args.resume,
            progress_callback=progress_callback,
        ):
            if result.success:
                if result.skipped:
                    skip_count += 1
                else:
                    success_count += 1
            else:
                fail_count += 1
                logger.warning(f"Failed: {result.time_slot} - {result.error}")
        
        elapsed = datetime.now() - start_time
        print(f"\n\nCompleted in {elapsed}")
        print(f"Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")
```

## Success Criteria

### Functionality
- [x] `generate_time_announcement()` creates text + audio files
- [x] Batch generation produces 48 time slots per DJ
- [x] Output structure: `data/generated/time/<dj>/<HH-MM>/<dj>_0.txt` and `.wav`
- [x] Resume mode skips existing files correctly
- [x] Progress display shows current time slot and percentage

### Quality
- [ ] Generated scripts use proper DJ personality
- [ ] Audio files are clear and properly formatted
- [ ] Time is announced correctly (e.g., "3:30 AM", "12:00 PM", "11:30 PM")
- [ ] Files are organized in logical directory structure

### Testing
- [ ] Dry-run shows 48 × number of DJs to generate
- [ ] `--dj julie --time-announcements` generates 48 announcements
- [ ] `--dj all --time-announcements` generates 96 announcements (48 × 2)
- [ ] Interrupted generation can be resumed with `--resume`
- [ ] ContentSelector can find and use generated announcements

## Validation Commands

```bash
# Test dry-run
python scripts/generate_content.py --time-announcements --dj julie --dry-run

# Generate for one DJ
python scripts/generate_content.py --time-announcements --dj julie

# Verify file structure
ls data/generated/time/julie/
ls data/generated/time/julie/00-00/
ls data/generated/time/julie/12-00/

# Test resume mode (run twice, second should skip)
python scripts/generate_content.py --time-announcements --dj julie --resume

# Generate for all DJs
python scripts/generate_content.py --time-announcements --dj all

# Test that station can use announcements
python -c "
from src.ai_radio.dj.content import ContentSelector
from src.ai_radio.config import GENERATED_DIR
selector = ContentSelector(GENERATED_DIR)
result = selector.get_time_announcement('julie', 12, 0)
print(f'Found: {result}')
assert result is not None
"
```

## Anti-Regression Tests

```python
# tests/test_generation_pipeline.py

def test_generate_time_announcement(pipeline):
    """Test time announcement generation."""
    result = pipeline.generate_time_announcement(
        hour=12,
        minute=30,
        dj="julie"
    )
    
    assert result.success
    assert result.time_slot == "12-30"
    assert result.dj == "julie"
    assert Path(result.script_path).exists()
    assert Path(result.audio_path).exists()


def test_batch_time_announcements(pipeline):
    """Test batch time announcement generation."""
    results = list(generate_batch_time_announcements(
        pipeline,
        dj="julie",
        resume=False,
    ))
    
    # Should generate 48 time slots
    assert len(results) == 48
    
    # All should succeed
    success_count = sum(1 for r in results if r.success)
    assert success_count == 48


def test_time_announcement_resume(pipeline):
    """Test resume mode skips existing files."""
    # Generate once
    list(generate_batch_time_announcements(pipeline, dj="julie", resume=False))
    
    # Generate again with resume
    results = list(generate_batch_time_announcements(pipeline, dj="julie", resume=True))
    
    # All should be skipped
    skip_count = sum(1 for r in results if r.skipped)
    assert skip_count == 48
```

## Git Commit

```bash
git add src/ai_radio/generation/pipeline.py
git add scripts/generate_content.py
git add tests/test_generation_pipeline.py
git commit -m "feat(generation): add batch time announcement generation

- Add generate_time_announcement() to GenerationPipeline
- Implement generate_batch_time_announcements() iterator
- Update scripts/generate_content.py with --time-announcements flag
- Generate 48 time slots (every 30 min) for 24 hours
- Support resume mode to skip existing files
- Add progress tracking and display
"
```

## Dependencies
- **Requires**: Checkpoint 2.2 (Prompt Templates) - `build_time_announcement_prompt()` must exist
- **Requires**: Checkpoint 2.4 (Generation Pipeline) - `GenerationPipeline` class
- **Requires**: Checkpoint 4.3 (Content Selector) - Must support finding time announcements

## Notes
- Each DJ generates 48 announcements (24 hours × 2 per hour = 48)
- Time format follows 12-hour clock with AM/PM in prompts
- File naming uses 24-hour format for directory structure (00-00 to 23-30)
- Consider implementing `--specific-time HH:MM` flag for regenerating single time slots
- Future enhancement: Add `--weather-announcements` using similar pattern
