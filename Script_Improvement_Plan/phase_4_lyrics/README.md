# Phase 4: Lyrics Integration

## Phase Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | Parse lyrics files and integrate them into script generation for richer context |
| **Duration** | 1-2 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 2 complete (prompts support lyrics context) |
| **Outputs** | `lyrics_parser.py`, lyrics integration in pipeline |
| **Status** | ⬜ Not Started |

---

## Why This Phase Matters

Lyrics provide rich context that can make intros more meaningful and authentic:

### Benefits of Lyrics Integration
1. **Deeper connections** - Reference specific themes or emotions from the song
2. **Authentic insights** - Connect songs to listener experiences based on actual content
3. **Interesting details** - Provide facts about what the song is actually about
4. **Better intros** - More substance beyond just artist/title announcements

### Current State
- Lyrics files exist in `music_with_lyrics/` directory
- Format: Metadata header + lyrics text
- Not currently used in script generation
- Prompts already support `lyrics_context` parameter (Phase 2)

### Target State
- Parser extracts lyrics and metadata
- Context summaries generated from lyrics
- Summaries integrated into generation prompts
- Graceful handling when lyrics unavailable

---

## Checkpoints

- [ ] **Checkpoint 4.1** - Lyrics File Parser
- [ ] **Checkpoint 4.2** - Lyrics Context Extraction  
- [ ] **Checkpoint 4.3** - Pipeline Integration

---

## Deliverables

### Code
- `src/ai_radio/generation/lyrics_parser.py` - Parser implementation
- `tests/generation/test_lyrics_parser.py` - Parser tests
- Updated `prompts_v2.py` - Lyrics context integration

### Documentation
- Lyrics file format documented
- Context extraction approach documented
- Integration points documented

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Lyrics files parsed | >90% |
| Matching to catalog | >85% |
| Context quality (human review) | >7/10 |
| Generation with lyrics | Works seamlessly |
| Graceful degradation | No failures when lyrics missing |

---

## Dependencies

### Input
- Lyrics files in `music_with_lyrics/`
- Song catalog for matching
- Updated prompts from Phase 2

### Output
- Lyrics data structure
- Context summaries
- Integrated generation pipeline

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Lyrics missing for many songs | Medium | Low | Graceful degradation |
| Matching failures | Medium | Medium | Fuzzy matching, manual fallback |
| Poor context extraction | Low | Medium | Human review and refinement |
| Slows down generation | Low | Low | Cache parsed lyrics |

---

## Timeline Estimate

| Checkpoint | Estimated Time |
|------------|----------------|
| 4.1 - Parser | 2-3 hours |
| 4.2 - Context Extraction | 2-3 hours |
| 4.3 - Pipeline Integration | 1-2 hours |
| **Total** | **5-8 hours (1-2 sessions)** |

---

## Phase Status

**Current Status:** ⬜ Not Started

**Blockers:** None (Phase 2 complete)

**Next Action:** Begin Checkpoint 4.1 - Lyrics File Parser

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Phase 4 README created from Phase 4 specification |
