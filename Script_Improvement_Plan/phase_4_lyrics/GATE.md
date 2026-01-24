# Phase 4 Gate: Lyrics Integration Complete

## Gate Status
**NOT STARTED** ⬜

All criteria must pass to proceed to Phase 5.

---

## Gate Criteria

### 1. Parser Works ✅

**Criterion:** Lyrics parser successfully extracts metadata and lyrics from files

**Validation:**
- [ ] Unit tests pass
- [ ] Parser handles normal lyrics files correctly
- [ ] Parser handles instrumental files correctly
- [ ] Parser handles malformed files gracefully
- [ ] >90% of lyrics files parse successfully

**Test Command:**
```bash
pytest tests/generation/test_lyrics_parser.py -v
```

**Status:** ⬜ Not Started

---

### 2. Context Extraction Works ✅

**Criterion:** Context extraction creates meaningful summaries

**Validation:**
- [ ] Context summaries are 1-3 sentences
- [ ] Contexts are <200 characters
- [ ] Contexts capture essence without reproducing lyrics
- [ ] Manual review of 10 summaries shows quality >7/10
- [ ] Instrumental songs handled correctly

**Manual Review Process:**
1. Extract contexts for 10 diverse songs
2. Score each context (1-10) for:
   - Accuracy (matches song content)
   - Brevity (appropriate length)
   - Usefulness (helps DJ script)
   - Naturalness (not robotic)
3. Calculate average score
4. Target: >7/10 average

**Status:** ⬜ Not Started

---

### 3. Pipeline Integration Complete ✅

**Criterion:** Lyrics context integrated into generation pipeline

**Validation:**
- [ ] Lyrics loaded at pipeline start
- [ ] Context passed to prompt builder
- [ ] Generation uses lyrics when available
- [ ] Missing lyrics handled gracefully
- [ ] Statistics logged correctly

**Test Command:**
```bash
# Test with lyrics
python scripts/generate_validated_batch.py \
    --intros --dj julie --limit 5 --lyrics-dir music_with_lyrics/

# Test without lyrics
python scripts/generate_validated_batch.py \
    --intros --dj julie --limit 5 --no-lyrics
```

**Expected:**
- Both commands complete without errors
- With-lyrics: Context included in prompts
- Without-lyrics: Standard prompts used
- All scripts pass validation

**Status:** ⬜ Not Started

---

### 4. Graceful Degradation ✅

**Criterion:** System works perfectly with or without lyrics

**Validation:**
- [ ] Songs without lyrics still generate successfully
- [ ] No errors when lyrics missing
- [ ] No errors when lyrics malformed
- [ ] Quality acceptable in both cases

**Test Scenarios:**
1. Full batch with lyrics available
2. Full batch with no lyrics
3. Mixed batch (some with, some without)
4. Batch with malformed lyrics files

**Status:** ⬜ Not Started

---

## Required Artifacts

### Code ✅
1. [ ] `src/ai_radio/generation/lyrics_parser.py`
   - `LyricsData` dataclass
   - `parse_lyrics_file()` function
   - `extract_lyrics_context()` function
   - `match_lyrics_to_catalog()` function

2. [ ] Updated `src/ai_radio/generation/prompts_v2.py`
   - `lyrics_context` parameter added
   - Context integrated into prompts

3. [ ] Updated `src/ai_radio/generation/validated_pipeline.py`
   - Lyrics loading at initialization
   - Context extraction during generation

### Tests ✅
4. [ ] `tests/generation/test_lyrics_parser.py`
   - Parser tests
   - Context extraction tests
   - Matching tests
   - Edge case tests

### Documentation ✅
5. [ ] Lyrics file format documented
6. [ ] Context extraction approach documented  
7. [ ] Integration points documented
8. [ ] CLI usage updated

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Lyrics files parsed | >90% | ___ | ⬜ |
| Matching to catalog | >85% | ___ | ⬜ |
| Context quality (human review) | >7/10 | ___ | ⬜ |
| Generation with lyrics | Works seamlessly | ___ | ⬜ |
| Graceful degradation | No failures | ___ | ⬜ |

---

## Quality Validation

### Human Review of Contexts

**Sample Size:** 10 diverse songs

**Review Template:**
```markdown
## Context Review

**Song:** {artist} - {title}
**Lyrics Available:** Yes/No
**Generated Context:** "{context}"

### Scores (1-10)
- Accuracy: ___
- Brevity: ___
- Usefulness: ___
- Naturalness: ___

**Overall:** ___/10

**Notes:**
```

**Passing Criteria:**
- [ ] Average score >7/10
- [ ] No score below 5/10
- [ ] All contexts under 200 characters

---

## Integration Test

### Test Command
```bash
python scripts/generate_validated_batch.py \
    --intros --dj all --limit 10 \
    --lyrics-dir music_with_lyrics/
```

### Expected Results
- [ ] 20 scripts generated (10 per DJ)
- [ ] Lyrics context used where available
- [ ] No errors or failures
- [ ] Pass rate >80%
- [ ] Logs show lyrics statistics

### Verification
1. Check logs for lyrics matching stats
2. Review generated scripts
3. Verify context used appropriately
4. Confirm character voice maintained

---

## Performance Validation

### Timing Test

**Baseline (without lyrics):**
```bash
time python scripts/generate_validated_batch.py --intros --dj julie --limit 10 --no-lyrics
```

**With lyrics:**
```bash
time python scripts/generate_validated_batch.py --intros --dj julie --limit 10 --lyrics-dir music_with_lyrics/
```

**Acceptance:**
- [ ] Lyrics add <10% overhead
- [ ] No performance degradation in generation
- [ ] Caching works correctly

---

## Comparison Test

### A/B Quality Comparison

**Setup:**
1. Generate 10 scripts WITH lyrics context
2. Generate 10 scripts WITHOUT lyrics context (same songs)
3. Human review both sets blind (randomized order)
4. Score each script (1-10)
5. Compare averages

**Expected:**
- Scripts with lyrics: Average >7/10
- Scripts without lyrics: Average >6/10
- With-lyrics scripts reference song themes appropriately

---

## Edge Cases Verified

- [ ] Instrumental songs (no lyrics text)
- [ ] Missing lyrics files
- [ ] Malformed lyrics files
- [ ] Very short lyrics (<50 words)
- [ ] Very long lyrics (>500 words)
- [ ] Songs with no match in catalog
- [ ] Catalog songs with no lyrics files

---

## Git Tracking

**Commit Message:** `feat(generation): add lyrics integration`

**Git Tag:** `v0.9.4-lyrics`

**Files Changed:**
- `src/ai_radio/generation/lyrics_parser.py` (new)
- `src/ai_radio/generation/prompts_v2.py` (modified)
- `src/ai_radio/generation/validated_pipeline.py` (modified)
- `tests/generation/test_lyrics_parser.py` (new)

---

## Phase 4 Summary

### What Was Built
- Lyrics file parser with robust error handling
- Context extraction for thematic summaries
- Integration into generation pipeline
- Graceful degradation when lyrics unavailable

### Key Features
- **Efficient parsing** - Handles various file formats
- **Smart matching** - Fuzzy matching to catalog
- **Meaningful contexts** - Brief, actionable summaries
- **Seamless integration** - Works with existing pipeline
- **Graceful fallback** - No failures when lyrics missing

### Impact
- **Richer intros** - Can reference song themes
- **Better context** - More substance than artist/title only
- **Maintained quality** - Character voice still authentic
- **No performance hit** - Efficient caching and parsing

---

## Next Phase Readiness

### Prerequisites for Phase 5 ✅
- [ ] Lyrics parser working
- [ ] Context extraction producing quality summaries
- [ ] Integration tested and verified
- [ ] All tests passing

### Ready to Proceed?
**Status:** ⬜ Not Started

Once all gate criteria pass, proceed to **Phase 5: Batch Pipeline**.

---

## Sign-Off

**Phase Owner:** _________________  
**Date Completed:** _________________  
**Gate Status:** ⬜ **NOT STARTED**

**Reviewer Notes:**
_________________

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Gate document created from Phase 4 specification |
