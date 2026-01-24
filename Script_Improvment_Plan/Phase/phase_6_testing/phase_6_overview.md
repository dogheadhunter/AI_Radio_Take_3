# Phase 6 Overview

## Phase 6: Script Quality Testing

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Validate script generation quality across all content types |
| **Duration** | 2-3 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 5 complete (intro pipeline working) |
| **Focus** | Scripts only — no audio testing |

### Important Note on Testing
- Use `--skip-audio` flag for all tests to focus on script quality
- Run small batches first (5→10→20→full)
- Check `data/audit/summary.json` after each run
- Review failed scripts in `data/audit/{dj}/failed/`

### Content Types to Validate

| Type | Count | Data Source |
|------|-------|-------------|
| Song Intros | 131 songs × 2 DJs = 262 | `data/catalog.json` |
| Song Outros | 131 songs × 2 DJs = 262 | `data/catalog.json` |
| Time Announcements | 48 slots × 2 DJs = 96 | Every 30 min × 24 hrs |
| Weather Announcements | 3 times × 2 DJs = 6 | 6 AM, 12 PM, 5 PM |

### Testing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│              PROGRESSIVE TESTING STRATEGY                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  For each content type:                                      │
│                                                              │
│  1. INTEGRATION (if needed)                                  │
│     └── Wire up CLI flag to existing generator               │
│                                                              │
│  2. SMOKE TEST (5 items)                                     │
│     └── Verify generation and audit work                     │
│                                                              │
│  3. CHARACTER TEST (10 items per DJ)                         │
│     └── Verify DJ voice consistency                          │
│                                                              │
│  4. SCALE TEST (20-50 items)                                 │
│     └── Verify pass rate >70%                                │
│                                                              │
│  5. FULL RUN (all items)                                     │
│     └── Verify pass rate >95% after regeneration             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What's Already Working

**Song Intros (fully tested in Phase 5):**
- Prompts: `build_song_intro_prompt_v2()` ✅
- Generator: `generate_song_intro()`, `generate_batch_intros()` ✅
- Pipeline: `--intros` flag working ✅
- Auto-regeneration: 50% → 100% pass rate achieved ✅

### What Needs Integration

**Song Outros:**
- Prompts: `build_song_outro_prompt_v2()` exists ✅
- Generator: `generate_song_outro()`, `generate_batch_outros()` exists ✅
- Pipeline: `--outros` blocked by error ❌ → needs wiring

**Time Announcements:**
- Prompts: `build_time_prompt_v2()` exists ✅
- Generator: `generate_time_announcement()`, `generate_batch_time_announcements()` exists ✅
- Pipeline: `--time` blocked by error ❌ → needs wiring
- Note: Different structure — 48 time slots, not songs

**Weather Announcements:**
- Prompts: `build_weather_prompt_v2()` exists ✅
- Generator: `generate_weather_announcement()`, `generate_batch_weather_announcements()` exists ✅
- Pipeline: `--weather` blocked by error ❌ → needs wiring
- Note: Only 3 times × 2 DJs = 6 total
