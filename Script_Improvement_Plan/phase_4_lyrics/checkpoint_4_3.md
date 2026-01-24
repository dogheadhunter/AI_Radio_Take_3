# Checkpoint 4.3: Pipeline Integration

## Status
**NOT STARTED** ⬜

## Goal
Integrate lyrics parsing and context extraction into the generation pipeline so that scripts benefit from lyrics context when available.

## Tasks

### 1. Load Lyrics at Pipeline Start
- [ ] Add lyrics loading to pipeline initialization
- [ ] Call `match_lyrics_to_catalog()` during setup
- [ ] Cache parsed lyrics for efficiency
- [ ] Log statistics (matched, unmatched, errors)

### 2. Update Generation Flow
- [ ] Pass lyrics context to prompt builder
- [ ] Handle missing lyrics gracefully
- [ ] Ensure generation works with or without lyrics
- [ ] Track which scripts used lyrics context

### 3. Integrate with Prompt Builder
- [ ] Update `build_song_intro_prompt_v2()`
- [ ] Add `lyrics_context` parameter
- [ ] Format context appropriately in prompt
- [ ] Test prompt quality with/without context

### 4. Test Integration
- [ ] Generate scripts with lyrics context
- [ ] Generate scripts without lyrics context
- [ ] Compare quality (human review)
- [ ] Verify no failures when lyrics missing

### 5. Monitor and Log
- [ ] Log lyrics usage per script
- [ ] Track success rates with/without lyrics
- [ ] Identify songs that benefit most from lyrics
- [ ] Document findings

## Integration Points

### 1. Pipeline Initialization

**File:** `src/ai_radio/generation/validated_pipeline.py`

```python
class ValidatedGenerationPipeline:
    """Pipeline with lyrics integration."""
    
    def __init__(
        self,
        catalog: SongCatalog,
        lyrics_dir: Optional[Path] = None,
    ):
        self.catalog = catalog
        
        # Load and match lyrics
        self.lyrics_data = {}
        if lyrics_dir and lyrics_dir.exists():
            self.lyrics_data = match_lyrics_to_catalog(
                lyrics_dir=lyrics_dir,
                catalog=catalog,
            )
            
            # Log statistics
            total_songs = len(catalog.songs)
            matched = len(self.lyrics_data)
            logger.info(f"Lyrics matched: {matched}/{total_songs} ({matched/total_songs*100:.1f}%)")
```

### 2. Script Generation

```python
def generate_intro(self, song: Song, dj: str) -> str:
    """Generate intro with optional lyrics context."""
    
    # Get lyrics context if available
    lyrics_context = None
    if song.id in self.lyrics_data:
        lyrics_context = extract_lyrics_context(
            self.lyrics_data[song.id]
        )
    
    # Build prompt
    prompt = build_song_intro_prompt_v2(
        dj=dj,
        artist=song.artist,
        title=song.title,
        lyrics_context=lyrics_context,
    )
    
    # Generate
    script = self.generator.generate(prompt)
    
    # Track whether lyrics were used
    if lyrics_context:
        logger.debug(f"Generated with lyrics context: {song.id}")
    
    return script
```

### 3. Prompt Integration

**File:** `src/ai_radio/generation/prompts_v2.py`

```python
def build_song_intro_prompt_v2(
    dj: str,
    artist: str,
    title: str,
    lyrics_context: Optional[str] = None,
) -> str:
    """
    Build song intro prompt with optional lyrics context.
    
    Args:
        dj: DJ name ('julie' or 'mr_new_vegas')
        artist: Song artist  
        title: Song title
        lyrics_context: Optional context from lyrics
    """
    
    # Base prompt
    prompt = f"""You are {dj}, generating a song introduction.

Song: {artist} - {title}
"""
    
    # Add lyrics context if available
    if lyrics_context:
        prompt += f"""
Song Context: {lyrics_context}

You may reference the song's theme or mood in your introduction,
but keep it natural and conversational. Don't force it if it 
doesn't fit your style.
"""
    
    # Rest of prompt (character description, examples, constraints)
    prompt += get_dj_prompt_section(dj)
    
    return prompt
```

## Graceful Degradation

### Handling Missing Lyrics

**Strategy:** System should work perfectly whether lyrics are available or not

```python
# Option 1: Lyrics available
lyrics_context = "A melancholic ballad about lost love."
# → Richer, more thematic intro

# Option 2: Lyrics not available
lyrics_context = None
# → Standard intro based on artist/title only

# Both should produce quality scripts!
```

### Error Handling

```python
try:
    lyrics_context = extract_lyrics_context(self.lyrics_data[song.id])
except Exception as e:
    # Log but don't fail
    logger.warning(f"Failed to extract lyrics context for {song.id}: {e}")
    lyrics_context = None

# Continue with generation regardless
```

## Testing Strategy

### Test Scenarios

1. **With lyrics context**
   - Generate 10 intros with lyrics available
   - Verify context is referenced appropriately
   - Check for quality improvement

2. **Without lyrics context**
   - Generate 10 intros without lyrics
   - Verify system still works
   - Compare quality to with-lyrics

3. **Mixed batch**
   - Generate 20 intros (some with, some without lyrics)
   - Verify no failures
   - Track statistics

4. **Edge cases**
   - Instrumental songs
   - Malformed lyrics
   - Very short/long lyrics
   - Missing lyrics files

### Quality Comparison

**Test Command:**
```bash
# Generate with lyrics
python scripts/generate_validated_batch.py \
    --intros --dj julie --limit 10 --lyrics-dir music_with_lyrics/

# Generate without lyrics (control group)
python scripts/generate_validated_batch.py \
    --intros --dj julie --limit 10 --no-lyrics
```

**Evaluation:**
- Human review of both sets
- Score quality (1-10)
- Identify differences
- Determine if lyrics help

## Monitoring and Metrics

### Statistics to Track

```python
# Pipeline statistics
stats = {
    'total_generated': 100,
    'with_lyrics': 75,
    'without_lyrics': 25,
    'lyrics_match_rate': 0.75,
    'pass_rate_with_lyrics': 0.92,
    'pass_rate_without_lyrics': 0.88,
}
```

### Logging

```python
# Log lyrics usage
logger.info(f"Generated intro for {song.id}")
logger.debug(f"  Artist: {song.artist}")
logger.debug(f"  Title: {song.title}")
logger.debug(f"  Lyrics context: {lyrics_context or 'None'}")
logger.debug(f"  Context length: {len(lyrics_context) if lyrics_context else 0} chars")
```

## CLI Updates

### Add Lyrics Option

```bash
# Enable lyrics (default if lyrics_dir exists)
python scripts/generate_with_audit.py --intros --dj julie --lyrics

# Disable lyrics (for comparison)
python scripts/generate_with_audit.py --intros --dj julie --no-lyrics

# Specify custom lyrics directory
python scripts/generate_with_audit.py --intros --dj julie --lyrics-dir /path/to/lyrics
```

## Expected Outcomes

### Quality Improvements
- **More specific intros** - Reference song themes
- **Better context** - Connect to listener experiences
- **Richer content** - More substance than just artist/title
- **Maintain character** - Still sounds like the DJ

### Performance
- **No slowdown** - Lyrics cached at startup
- **No failures** - Graceful handling of missing lyrics
- **Same pass rate** - Validation still works
- **Better scripts** - Higher human satisfaction

## Success Criteria

| Criterion | Validation Method | Status |
|-----------|-------------------|--------|
| Lyrics loaded at pipeline start | Unit test | ⬜ |
| Matching works for most songs | >85% match rate | ⬜ |
| Missing lyrics don't break generation | Integration test | ⬜ |
| Generated intros reference lyrics when appropriate | Human review | ⬜ |
| Quality improved with lyrics | A/B comparison | ⬜ |
| No performance degradation | Timing tests | ⬜ |
| Statistics logged correctly | Log verification | ⬜ |

## Quality Review

### Review 10 Scripts With Lyrics

For each script, evaluate:
- [ ] Does it reference the song's theme?
- [ ] Is the reference natural, not forced?
- [ ] Does it maintain DJ character?
- [ ] Is it better than a generic intro?
- [ ] Score: ___/10

**Target:** Average >7/10

### Review 10 Scripts Without Lyrics

For each script, evaluate:
- [ ] Is quality still acceptable?
- [ ] Does it work without context?
- [ ] No errors or issues?
- [ ] Score: ___/10

**Target:** Average >6/10 (slightly lower OK)

## Documentation Updates

- [ ] Update pipeline README with lyrics usage
- [ ] Document lyrics directory structure
- [ ] Add lyrics CLI options to help text
- [ ] Update examples to show lyrics integration

## Next Steps
Once complete, proceed to Phase 4 Gate validation to confirm all criteria met.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 4 specification |
