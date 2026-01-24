# Checkpoint 6.6: Weather Announcement Pipeline Integration

#### Checkpoint 6.6: Weather Announcement Pipeline Integration
**Wire up `--weather` flag to existing weather announcement generator.**

## Overview
Weather announcements are the smallest content type—only 3 times × 2 DJs = 6 total. They require weather condition data to be meaningful.

## Current State

**What exists:**
- `prompts_v2.py`: `build_weather_prompt_v2()` ✅
- `pipeline.py`: `generate_weather_announcement()` ✅
- `pipeline.py`: `generate_batch_weather_announcements()` ✅
- `config.py`: Weather times defined (6 AM, 12 PM, 5 PM)

**What's different:**
- Only 3 time slots (not 48)
- Requires weather condition input
- More substantive than time announcements
- May include Fallout-themed wasteland weather

## Weather Times

From `config.py`:
```python
WEATHER_ANNOUNCEMENT_TIMES = [
    (6, 0),   # 6:00 AM - Morning weather
    (12, 0),  # 12:00 PM - Midday weather
    (17, 0),  # 5:00 PM - Evening weather
]
```

## Tasks

### Task 1: Remove Blocking Error (for weather)
- [ ] Modify line 947 to allow `--weather`
- [ ] All content types now unblocked

### Task 2: Define Weather Data Structure
- [ ] Determine weather input format
- [ ] Options:
  - Hardcoded test conditions
  - Weather templates (sunny, rainy, rad storm, etc.)
  - API integration (future)
- [ ] For testing, use sample weather summaries

### Task 3: Add Weather Generation Logic
- [ ] Add weather content type to config handling
- [ ] Integrate `generate_batch_weather_announcements()` call
- [ ] Pass weather summary to generator
- [ ] Set output path to `data/generated/weather/{dj}/{HH-MM}/`

### Task 4: Add Weather Audit Support
- [ ] Verify auditor works with weather scripts
- [ ] Weather scripts are 2-3 sentences
- [ ] Era-appropriate weather vocabulary

## Weather Data Options

**For Testing (hardcoded):**
```python
SAMPLE_WEATHER = [
    "Clear skies, temperature around 75 degrees.",
    "Partly cloudy with a chance of radiation showers.",
    "Dust storm moving in from the west.",
    "Fog rolling in from the river.",
    "Hot and dry, stay hydrated out there.",
]
```

**Fallout-Themed Weather:**
- Rad storms
- Dust storms
- Acid rain
- Nuclear winter
- Clear wasteland skies

## Output Structure

```
data/generated/weather/
├── julie/
│   ├── 06-00/
│   │   └── julie_0.txt
│   ├── 12-00/
│   └── 17-00/
└── mr_new_vegas/
    ├── 06-00/
    ├── 12-00/
    └── 17-00/
```

## Success Criteria

| Criterion | Target |
|-----------|--------|
| `--weather` flag accepted | No error on CLI |
| Weather scripts generated | 6 files total |
| Weather summary incorporated | References conditions |
| Audit works | Results in `data/audit/` |

## Validation

```powershell
# Should NOT error after integration
python scripts/generate_with_audit.py --weather --dj all --skip-audio

# Verify structure
Get-ChildItem data\generated\weather\ -Recurse

# Should see 6 files: 3 times × 2 DJs
```

## Notes

Implementation decisions needed:
```
Weather data source:
- [ ] Hardcoded test data
- [ ] Weather templates file
- [ ] Live API (future)

Template approach:
- 
```
