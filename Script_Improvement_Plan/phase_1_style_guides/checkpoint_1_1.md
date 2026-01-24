# Checkpoint 1.1: Transcript Preprocessing

## Goal
Clean and prepare transcripts for analysis

## Tasks

1. Remove timestamps from Julie's transcript (`00:00:00 Speaker:` prefixes)
2. Split transcripts into individual lines/segments
3. Categorize segments by type (intro, outro, commentary, etc.)
4. Save cleaned transcripts for reference

## Input Files

- `assets/voice_references/Julie/Julie_Full_Voicelines_Script.txt`
- `assets/voice_references/Mister_New_Vegas/Mister_New_Vegas_Voice_Files_Script.txt`

## Output Files

- `data/style_analysis/julie_cleaned.txt`
- `data/style_analysis/mr_new_vegas_cleaned.txt`
- `data/style_analysis/julie_categorized.json`
- `data/style_analysis/mr_new_vegas_categorized.json`

## Success Criteria

- [x] Timestamps removed from all lines ✅
- [x] Each line is a complete thought/segment ✅
- [x] Categories identified: `song_intro`, `song_outro`, `commentary`, `time`, `weather`, `other` ✅
- [x] At least 20 segments categorized for each DJ ✅

## Validation

```bash
# Check cleaned file has no timestamps
grep -c "00:00:00" data/style_analysis/julie_cleaned.txt
# Expected: 0

# Check categorization file exists and has data
python -c "import json; d=json.load(open('data/style_analysis/julie_categorized.json')); print(f'Categories: {list(d.keys())}')"
```

## Transcript Format Handling

Julie's transcript has timestamps to remove:
```
00:00:00 Speaker: Now we've got Cass Daley...
```

Process:
1. Read each line
2. Strip timestamp prefix with regex: `^\d{2}:\d{2}:\d{2}\s+Speaker:\s*`
3. Keep the content

Mr. New Vegas's transcript may have similar formatting - verify and adjust.

## Categorization Heuristics

How to identify segment types:
- **Song Intro**: Contains artist name, song title, or "next song/tune"
- **Song Outro**: Follows a song, transitional language
- **Commentary**: General observations, stories, not about specific songs
- **Time**: Contains clock references
- **Weather**: Contains weather-related words
- **Other**: Doesn't fit above categories

## Status

**✅ COMPLETE** - All criteria met
