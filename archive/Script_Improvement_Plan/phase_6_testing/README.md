# 📋 Phase 6: Script Quality Testing

## Document Purpose
This plan provides a **step-by-step testing roadmap** for validating script generation quality across all content types before full production runs. Focus is exclusively on script generation and auditing—no audio testing in this phase.

## Current Status

| Content Type | Prompts | Generator | Pipeline | Tested |
|--------------|---------|-----------|----------|--------|
| Song Intros | ✅ | ✅ | ✅ | ✅ |
| Song Outros | ✅ | ✅ | ❌ | ❌ |
| Time Announcements | ✅ | ✅ | ❌ | ❌ |
| Weather Announcements | ✅ | ✅ | ❌ | ❌ |

## Key Finding
The **core generation code already exists** for all content types in `pipeline.py`. The blocker is in `generate_with_audit.py` line 947:
```python
if args.outros or args.time or args.weather or args.all_content:
    parser.error('Currently only --intros is supported')
```

## Phase Structure

| Checkpoint | Name | Status |
|------------|------|--------|
| 6.1 | Intro Baseline Validation | ⬜ Not Started |
| 6.2 | Outro Pipeline Integration | ⬜ Not Started |
| 6.3 | Outro Quality Testing | ⬜ Not Started |
| 6.4 | Time Pipeline Integration | ⬜ Not Started |
| 6.5 | Time Quality Testing | ⬜ Not Started |
| 6.6 | Weather Pipeline Integration | ⬜ Not Started |
| 6.7 | Weather Quality Testing | ⬜ Not Started |
| 6.8 | Full Scale Validation | ⬜ Not Started |

## Quick Commands

```bash
# Test intros (already working)
python scripts/generate_with_audit.py --intros --dj all --limit 5 --skip-audio

# After integration, test outros
python scripts/generate_with_audit.py --outros --dj all --limit 5 --skip-audio

# After integration, test time
python scripts/generate_with_audit.py --time --dj all --limit 3 --skip-audio

# After integration, test weather
python scripts/generate_with_audit.py --weather --dj all --skip-audio
```

## File Locations

| Purpose | Location |
|---------|----------|
| Pipeline Script | `scripts/generate_with_audit.py` |
| Generator Backend | `src/ai_radio/generation/pipeline.py` |
| Prompts (v2) | `src/ai_radio/generation/prompts_v2.py` |
| Auditor | `src/ai_radio/generation/auditor.py` |
| Audit Results | `data/audit/` |
| Generated Scripts | `data/generated/` |

## Quality Targets

| Metric | Target |
|--------|--------|
| Audit Pass Rate (initial) | >70% |
| Audit Pass Rate (after regen) | >95% |
| Character Recognition | >90% |
| Era Appropriateness | >95% |

## Git Tags

| Tag | Milestone |
|-----|-----------|
| `v0.9.5-pipeline` | Phase 5 complete (intros working) |
| `v0.9.6-outros` | Outro generation validated |
| `v0.9.7-time` | Time generation validated |
| `v0.9.8-weather` | Weather generation validated |
| `v1.0.0-scripts` | All script types production ready |
