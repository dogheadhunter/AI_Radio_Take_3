# Checkpoint 4.2: Lyrics Context Extraction

## Status
**NOT STARTED** ⬜

## Goal
Create meaningful context summaries from lyrics that can be used in generation prompts without reproducing full lyrics text.

## Why Context Extraction?

### The Challenge
- **Full lyrics are too long** - Can't fit in prompts efficiently
- **Copyright concerns** - Don't want to reproduce lyrics verbatim
- **Relevance** - DJs reference themes, not specific lines
- **TTS limitations** - Can't read lyrics aloud anyway

### The Solution
Extract brief **thematic summaries** that capture:
1. What the song is about (theme)
2. Emotional tone (mood)
3. Notable elements (interesting details)

## Tasks

### 1. Define Context Types
- [ ] Theme - What the song is about
- [ ] Mood - Emotional tone
- [ ] Notable Element - Interesting or memorable aspect
- [ ] Create examples for each type

### 2. Implement Context Extraction
- [ ] Create `extract_lyrics_context()` function
- [ ] Generate 1-3 sentence summaries
- [ ] Avoid reproducing lyrics verbatim
- [ ] Capture essence without details

### 3. Handle Special Cases
- [ ] Instrumental songs - "An instrumental piece"
- [ ] Missing lyrics - Return None gracefully
- [ ] Very short lyrics - Summarize appropriately
- [ ] Narrative vs. abstract lyrics

### 4. Test Context Quality
- [ ] Generate contexts for sample songs
- [ ] Human review of 10+ contexts
- [ ] Verify brevity (1-3 sentences)
- [ ] Verify usefulness in prompts
- [ ] Refine extraction approach

### 5. Optimize for Prompts
- [ ] Format context for prompt injection
- [ ] Keep under 200 characters when possible
- [ ] Make context actionable for DJ voice
- [ ] Test in actual generation prompts

## Context Types

### 1. Mood
**Description:** Overall emotional tone of the song

**Examples:**
- "A melancholic love ballad"
- "An upbeat, energetic dance number"
- "A reflective, nostalgic piece"
- "A playful, humorous song"

### 2. Theme
**Description:** What the song is about

**Examples:**
- "About finding true love"
- "About heartbreak and loss"
- "About the difficulty of finding a good romantic partner"
- "About freedom and independence"
- "About memories of home"

### 3. Notable Element
**Description:** Something interesting or memorable

**Examples:**
- "Features a memorable chorus"
- "Tells a story about traveling"
- "Contains clever wordplay"
- "Has a distinctive instrumental break"

## Context Format

### Template
```
This song is about [theme]. The mood is [mood]. [Optional: Notable element].
```

### Examples

**Good Context (Balanced):**
```
"This song is about the difficulty of finding a good romantic partner. 
The mood is playful and humorous despite the serious topic."
```

**Good Context (Brief):**
```
"A melancholic ballad about lost love and regret."
```

**Good Context (With Detail):**
```
"This song is about homesickness and longing for simpler times. 
The mood is bittersweet and nostalgic. It features vivid imagery 
of rural life."
```

**Bad Context (Too Specific):**
```
"The song talks about how men are hard to find and when you find 
one he's either married or too wild. The singer says she's had 
good men and bad men..."
```
*(Too detailed, reproduces lyrics structure)*

**Bad Context (Too Vague):**
```
"A song about relationships."
```
*(Not useful, too generic)*

## Implementation

### File: `src/ai_radio/generation/lyrics_parser.py` (add to existing)

```python
def extract_lyrics_context(lyrics_data: LyricsData, max_length: int = 200) -> Optional[str]:
    """
    Extract a brief context summary from lyrics.
    
    This is what gets passed to the prompt - not the full lyrics,
    but a summary of themes, mood, or notable lines.
    
    Args:
        lyrics_data: Parsed lyrics data
        max_length: Maximum length of context string
        
    Returns:
        Brief context string or None if unavailable
    """
    # Handle instrumental
    if lyrics_data.is_instrumental:
        return "An instrumental piece with no vocals."
    
    # Handle missing lyrics
    if not lyrics_data.has_lyrics():
        return None
    
    # TODO: Implement context extraction
    # For now, simple implementation:
    # 1. Get first few lines
    # 2. Identify mood words
    # 3. Identify theme words
    # 4. Generate summary
    
    # Simple version (to be improved):
    lyrics_lower = lyrics_data.lyrics.lower()
    
    # Detect mood
    mood = detect_mood(lyrics_lower)
    
    # Detect theme
    theme = detect_theme(lyrics_lower)
    
    # Build context
    if theme and mood:
        context = f"A {mood} song about {theme}."
    elif theme:
        context = f"A song about {theme}."
    elif mood:
        context = f"A {mood} piece."
    else:
        # Fallback: generic description
        return None
    
    # Truncate if needed
    if len(context) > max_length:
        context = context[:max_length-3] + "..."
    
    return context


def detect_mood(lyrics: str) -> Optional[str]:
    """
    Detect mood from lyrics using keyword matching.
    
    Returns mood descriptor or None.
    """
    mood_keywords = {
        'melancholic': ['sad', 'cry', 'tears', 'lonely', 'blue', 'sorrow'],
        'upbeat': ['happy', 'joy', 'dance', 'fun', 'celebrate', 'party'],
        'romantic': ['love', 'heart', 'kiss', 'forever', 'together', 'darling'],
        'nostalgic': ['remember', 'memories', 'past', 'yesterday', 'used to'],
        'rebellious': ['fight', 'rebel', 'free', 'break', 'wild', 'run'],
        'playful': ['laugh', 'play', 'silly', 'tease', 'joke', 'fun'],
    }
    
    # Count keyword matches
    mood_scores = {}
    for mood, keywords in mood_keywords.items():
        score = sum(1 for kw in keywords if kw in lyrics)
        if score > 0:
            mood_scores[mood] = score
    
    # Return top mood if any
    if mood_scores:
        return max(mood_scores, key=mood_scores.get)
    
    return None


def detect_theme(lyrics: str) -> Optional[str]:
    """
    Detect theme from lyrics using keyword matching.
    
    Returns theme descriptor or None.
    """
    theme_keywords = {
        'love and romance': ['love', 'heart', 'kiss', 'romance', 'darling'],
        'heartbreak': ['broke', 'hurt', 'cry', 'left', 'goodbye', 'tears'],
        'freedom': ['free', 'fly', 'wild', 'run', 'escape', 'break'],
        'home and belonging': ['home', 'belong', 'family', 'roots', 'place'],
        'life journey': ['road', 'journey', 'travel', 'miles', 'going'],
        'hope and dreams': ['dream', 'hope', 'wish', 'someday', 'believe'],
    }
    
    # Count keyword matches
    theme_scores = {}
    for theme, keywords in theme_keywords.items():
        score = sum(1 for kw in keywords if kw in lyrics)
        if score > 0:
            theme_scores[theme] = score
    
    # Return top theme if any
    if theme_scores:
        return max(theme_scores, key=theme_scores.get)
    
    return None
```

## Refinement Strategy

### Version 1: Simple (Initial Implementation)
- Keyword-based mood and theme detection
- Template-based context generation
- Fallback to generic descriptions

### Version 2: Improved (After Testing)
- Better keyword dictionaries
- Weighted scoring
- More nuanced mood/theme combinations
- Handle edge cases better

### Version 3: Advanced (Future)
- LLM-based context extraction (optional)
- Semantic analysis
- Custom contexts per song
- Human-curated contexts for popular songs

## Testing Approach

### Manual Review Process
1. Extract contexts for 20 sample songs
2. Review each for:
   - Accuracy (matches song content)
   - Brevity (1-3 sentences, <200 chars)
   - Usefulness (helpful for DJ script)
   - Naturalness (not robotic)
3. Score each context (1-10)
4. Identify patterns in low scores
5. Refine extraction logic
6. Repeat until >7/10 average

### Test Cases

```python
def test_extract_context_normal_song():
    """Test context extraction for normal song."""
    lyrics_data = LyricsData(
        title="Test Song",
        artist="Test Artist",
        lyrics="I love you darling, you're my heart and soul...",
        is_instrumental=False,
    )
    
    context = extract_lyrics_context(lyrics_data)
    
    assert context is not None
    assert len(context) < 200
    assert 'love' in context.lower() or 'romantic' in context.lower()


def test_extract_context_instrumental():
    """Test context for instrumental."""
    lyrics_data = LyricsData(
        title="Instrumental",
        artist="Test",
        lyrics="",
        is_instrumental=True,
    )
    
    context = extract_lyrics_context(lyrics_data)
    
    assert "instrumental" in context.lower()


def test_extract_context_missing_lyrics():
    """Test handling missing lyrics."""
    lyrics_data = LyricsData(
        title="No Lyrics",
        artist="Test",
        lyrics="",
        is_instrumental=False,
    )
    
    context = extract_lyrics_context(lyrics_data)
    
    assert context is None
```

## Integration with Prompts

### Updated Prompt Builder

```python
def build_song_intro_prompt_v2(
    dj: str,
    artist: str,
    title: str,
    lyrics_context: Optional[str] = None,
) -> str:
    """
    Build prompt for song intro generation.
    
    Args:
        dj: DJ name ('julie' or 'mr_new_vegas')
        artist: Song artist
        title: Song title
        lyrics_context: Optional context from lyrics
    """
    prompt = f"""Generate a radio intro for {dj}.

Song: {artist} - {title}
"""
    
    # Add lyrics context if available
    if lyrics_context:
        prompt += f"\nContext: {lyrics_context}\n"
    
    prompt += """
[Rest of prompt...]
"""
    
    return prompt
```

## Success Criteria

| Criterion | Validation Method | Status |
|-----------|-------------------|--------|
| Context summaries are 1-3 sentences | Automated check | ⬜ |
| Summaries <200 characters | Automated check | ⬜ |
| Summaries capture essence without reproducing lyrics | Human review | ⬜ |
| Instrumental songs get appropriate context | Unit test | ⬜ |
| Context is usable in prompts | Integration test | ⬜ |
| Human quality rating >7/10 | Manual review of 20 samples | ⬜ |

## Quality Review Checklist

When reviewing generated contexts:

- [ ] **Accuracy** - Context matches song content
- [ ] **Brevity** - 1-3 sentences, <200 chars
- [ ] **Usefulness** - Helpful for DJ script generation
- [ ] **Naturalness** - Not robotic or template-y
- [ ] **Avoids reproduction** - Doesn't copy lyrics verbatim
- [ ] **Appropriate level** - Not too vague, not too specific

## Next Steps
Once complete, proceed to Checkpoint 4.3 to integrate lyrics into the generation pipeline.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 4 specification |
