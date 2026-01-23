# Checkpoint 2.7: Batch Weather Announcements Generation

#### Checkpoint 2.7: Batch Weather Announcements Generation
**Implement batch generation for weather announcements at configured times.**

## Overview
Generate weather announcements for specific times of day (configured in `WEATHER_TIMES`) for both DJs. This requires integration with the WeatherService to fetch real weather data.

## Tasks

### Task 1: Extend Generation Pipeline for Weather Announcements
- [ ] Add `generate_weather_announcement()` method to `GenerationPipeline`
- [ ] Create output structure: `data/generated/weather/<dj>/<HH-MM>/`
- [ ] Save both text script and audio file with weather data
- [ ] Handle voice reference if available

### Task 2: Implement Batch Weather Generation Iterator
- [ ] Create `generate_batch_weather_announcements()` function
- [ ] Generate for configured times from `config.WEATHER_TIMES`
- [ ] Integrate with `WeatherService` to fetch current conditions
- [ ] Support resume mode (skip existing files)
- [ ] Add progress callback support
- [ ] Handle both DJs (julie, mr_new_vegas)

### Task 3: Update Generation Script
- [ ] Implement `--weather-announcements` flag in `scripts/generate_content.py`
- [ ] Add `--location` argument for weather location
- [ ] Display progress during generation
- [ ] Show success/failure counts
- [ ] Support `--resume` for interrupted generation

### Task 4: Test Weather Announcement Generation
- [ ] Test dry-run mode shows correct count (weather times × DJs)
- [ ] Test generation creates proper directory structure
- [ ] Test resume mode skips existing files
- [ ] Verify weather data is included in scripts
- [ ] Verify audio files are valid and playable

## Implementation Details

**File: `src/ai_radio/generation/pipeline.py`**

Add method to `GenerationPipeline` class:

```python
def generate_weather_announcement(
    self,
    hour: int,
    minute: int,
    dj: str,
    weather_data: Optional[Dict] = None,
) -> GenerationResult:
    """Generate a weather announcement.
    
    Args:
        hour: Hour (0-23)
        minute: Minute (usually 0)
        dj: DJ personality name
        weather_data: Optional weather data dict from WeatherService
        
    Returns:
        GenerationResult with paths to text and audio files
    """
    from ai_radio.generation.prompts import build_weather_prompt
    
    # Build prompt with weather data
    prompt = build_weather_prompt(hour, minute, dj, weather_data)
    
    # Generate text with LLM
    response = self.llm_client.generate(prompt)
    script = response.strip()
    
    # Create output directory
    time_str = f"{hour:02d}-{minute:02d}"
    output_dir = self.output_dir / "weather" / dj / time_str
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save script with metadata
    script_path = output_dir / f"{dj}_0.txt"
    script_path.write_text(script, encoding="utf-8")
    
    # Save weather metadata
    if weather_data:
        import json
        metadata_path = output_dir / "weather_data.json"
        metadata_path.write_text(json.dumps(weather_data, indent=2), encoding="utf-8")
    
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
        weather_data=weather_data,
    )
```

Add batch generation function:

```python
def generate_batch_weather_announcements(
    pipeline: GenerationPipeline,
    dj: str,
    weather_times: List[int],
    location: Optional[str] = None,
    resume: bool = False,
    progress_callback: Optional[Callable] = None,
) -> Iterator[GenerationResult]:
    """Generate weather announcements for configured times.
    
    Args:
        pipeline: GenerationPipeline instance
        dj: DJ personality name
        weather_times: List of hours to generate weather for (e.g., [6, 12, 17])
        location: Optional location for weather (uses config default if not provided)
        resume: Skip existing files if True
        progress_callback: Optional callback(progress_info)
        
    Yields:
        GenerationResult for each weather announcement
    """
    from ai_radio.services.weather import WeatherService
    
    # Initialize weather service
    weather_service = WeatherService(location=location)
    
    total = len(weather_times)
    completed = 0
    failed = 0
    
    for hour in weather_times:
        minute = 0  # Weather announcements at top of hour
        time_str = f"{hour:02d}-{minute:02d}"
        
        # Check if already generated (resume mode)
        output_dir = pipeline.output_dir / "weather" / dj / time_str
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
            # Fetch current weather
            weather_data = weather_service.get_current_weather()
            
            # Generate announcement
            result = pipeline.generate_weather_announcement(
                hour, minute, dj, weather_data
            )
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
            logger.error(f"Failed to generate weather announcement {time_str} for {dj}: {e}")
            
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

Add `--weather-announcements` and `--location` arguments:

```python
parser.add_argument("--weather-announcements", action="store_true", 
                   help="Generate weather announcements")
parser.add_argument("--location", type=str, 
                   help="Location for weather (e.g., 'New York, NY')")
```

Update the weather announcements implementation:

```python
if args.weather_announcements:
    from ai_radio.config import WEATHER_TIMES
    from ai_radio.generation.pipeline import generate_batch_weather_announcements
    
    print(f"Generating weather announcements for configured times...")
    print(f"Weather times: {WEATHER_TIMES} (hours)")
    print(f"Location: {args.location or 'default from config'}")
    print(f"DJ: {args.dj}")
    print(f"Resume mode: {args.resume}")
    print("-" * 50)
    
    pipeline = GenerationPipeline(output_dir=GENERATED_DIR)
    djs = ["julie", "mr_new_vegas"] if args.dj == "all" else [args.dj]
    
    for dj in djs:
        print(f"\n=== Generating {dj.upper()} weather announcements ===\n")
        
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
        
        for result in generate_batch_weather_announcements(
            pipeline,
            dj=dj,
            weather_times=WEATHER_TIMES,
            location=args.location,
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
- [ ] `generate_weather_announcement()` creates text + audio files
- [ ] Batch generation produces announcements for each configured time
- [ ] Output structure: `data/generated/weather/<dj>/<HH-MM>/<dj>_0.txt` and `.wav`
- [ ] Weather metadata saved as JSON alongside scripts
- [ ] Resume mode skips existing files correctly
- [ ] Progress display shows current time slot and percentage

### Quality
- [ ] Generated scripts include actual weather data (temp, conditions, etc.)
- [ ] Scripts use proper DJ personality
- [ ] Audio files are clear and properly formatted
- [ ] Weather data is relevant and accurate
- [ ] Files are organized in logical directory structure

### Testing
- [ ] Dry-run shows correct count (weather times × DJs)
- [ ] `--dj julie --weather-announcements` generates for all weather times
- [ ] `--location "Las Vegas, NV"` uses specified location
- [ ] Interrupted generation can be resumed with `--resume`
- [ ] ContentSelector can find and use generated announcements

## Validation Commands

```bash
# Test dry-run
python scripts/generate_content.py --weather-announcements --dj julie --dry-run

# Generate for one DJ with custom location
python scripts/generate_content.py --weather-announcements --dj julie --location "Las Vegas, NV"

# Verify file structure
ls data/generated/weather/julie/
ls data/generated/weather/julie/06-00/
ls data/generated/weather/julie/12-00/

# Check weather metadata
cat data/generated/weather/julie/06-00/weather_data.json

# Test resume mode (run twice, second should skip)
python scripts/generate_content.py --weather-announcements --dj julie --resume

# Generate for all DJs
python scripts/generate_content.py --weather-announcements --dj all

# Test that station can use announcements
python -c "
from src.ai_radio.dj.content import ContentSelector
from src.ai_radio.config import GENERATED_DIR
selector = ContentSelector(GENERATED_DIR)
result = selector.get_weather_announcement('julie', 12, 0)
print(f'Found: {result}')
assert result is not None
"
```

## Anti-Regression Tests

```python
# tests/test_generation_pipeline.py

def test_generate_weather_announcement(pipeline):
    """Test weather announcement generation."""
    weather_data = {
        "temperature": 72,
        "condition": "Sunny",
        "humidity": 45,
    }
    
    result = pipeline.generate_weather_announcement(
        hour=12,
        minute=0,
        dj="julie",
        weather_data=weather_data,
    )
    
    assert result.success
    assert result.time_slot == "12-00"
    assert result.dj == "julie"
    assert Path(result.script_path).exists()
    assert Path(result.audio_path).exists()
    assert result.weather_data == weather_data


def test_batch_weather_announcements(pipeline, mock_weather_service):
    """Test batch weather announcement generation."""
    weather_times = [6, 12, 17]
    
    results = list(generate_batch_weather_announcements(
        pipeline,
        dj="julie",
        weather_times=weather_times,
        resume=False,
    ))
    
    # Should generate for each weather time
    assert len(results) == 3
    
    # All should succeed
    success_count = sum(1 for r in results if r.success)
    assert success_count == 3


def test_weather_announcement_resume(pipeline):
    """Test resume mode skips existing files."""
    weather_times = [6, 12, 17]
    
    # Generate once
    list(generate_batch_weather_announcements(
        pipeline, dj="julie", weather_times=weather_times, resume=False
    ))
    
    # Generate again with resume
    results = list(generate_batch_weather_announcements(
        pipeline, dj="julie", weather_times=weather_times, resume=True
    ))
    
    # All should be skipped
    skip_count = sum(1 for r in results if r.skipped)
    assert skip_count == 3
```

## Git Commit

```bash
git add src/ai_radio/generation/pipeline.py
git add scripts/generate_content.py
git add tests/test_generation_pipeline.py
git commit -m "feat(generation): add batch weather announcement generation

- Add generate_weather_announcement() to GenerationPipeline
- Implement generate_batch_weather_announcements() iterator
- Update scripts/generate_content.py with --weather-announcements flag
- Integrate with WeatherService for current conditions
- Generate for configured WEATHER_TIMES (default: 6 AM, 12 PM, 5 PM)
- Support custom location with --location flag
- Save weather metadata alongside scripts
- Support resume mode to skip existing files
"
```

## Dependencies
- **Requires**: Checkpoint 2.2 (Prompt Templates) - `build_weather_prompt()` must exist
- **Requires**: Checkpoint 2.4 (Generation Pipeline) - `GenerationPipeline` class
- **Requires**: Checkpoint 6.2 (Weather Service) - `WeatherService` for fetching data
- **Requires**: Checkpoint 4.3 (Content Selector) - Must support finding weather announcements

## Notes
- Weather announcements generated using **current** weather at generation time
- For realistic 24-hour broadcast, consider:
  - Generating weather at actual broadcast times (not pre-generation)
  - Or implementing weather forecast announcements for future times
- Default weather times from `config.WEATHER_TIMES`: [6, 12, 17] (6 AM, noon, 5 PM)
- Each DJ generates N announcements where N = len(WEATHER_TIMES)
- Weather data cached by WeatherService to avoid excessive API calls
- Consider adding `--forecast` flag for future enhancement (next-day weather)
