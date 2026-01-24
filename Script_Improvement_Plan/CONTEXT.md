# Script Improvement Plan - Essential Context

This document provides the minimum context needed for an LLM to continue work on the Script Improvement Plan. Load this file at the start of each session.

## Project Overview

AI Radio Station generates DJ scripts (intros, outros, time announcements, weather) using two LLMs:
- **Writer Model**: Stheno 8B - generates scripts in DJ character voice
- **Auditor Model**: Dolphin-Llama3 - validates scripts for quality

## Two DJs

| DJ | Style | Era |
|----|-------|-----|
| Julie | Warm, personal, Appalachian | Fallout 76 |
| Mr. New Vegas | Smooth, romantic, polished | Fallout New Vegas |

## Content Types

| Type | Count | Source |
|------|-------|--------|
| Song Intros | 131 songs × 2 DJs = 262 | catalog.json |
| Song Outros | 131 songs × 2 DJs = 262 | catalog.json |
| Time Announcements | 48 slots × 2 DJs = 96 | Every 30 min |
| Weather Announcements | 3 times × 2 DJs = 6 | 6 AM, 12 PM, 5 PM |
| **Total** | **626 scripts** | |

## Key Files

| Purpose | Location |
|---------|----------|
| Main Pipeline Script | `scripts/generate_with_audit.py` |
| Prompts (v2) | `src/ai_radio/generation/prompts_v2.py` |
| Auditor | `src/ai_radio/generation/auditor.py` |
| Pipeline Backend | `src/ai_radio/generation/pipeline.py` |
| Generated Scripts | `data/generated/{type}/{dj}/` |
| Audit Results | `data/audit/{dj}/{passed|failed}/` |

## Quality Targets

| Metric | Target |
|--------|--------|
| Initial pass rate | >50% |
| Final pass rate (after regen) | >95% |
| Character recognition | >90% |
| Era appropriateness | >95% |

## Session Protocol

1. Load this file (CONTEXT.md)
2. Check STATUS.md for current checkpoint
3. Load only the current checkpoint file
4. Complete checkpoint tasks
5. Run Auditor agent to verify
6. Update STATUS.md
7. Commit with descriptive message

## Commands Reference

```powershell
# Generate intros
python scripts/generate_with_audit.py --intros --dj all --skip-audio

# Generate outros
python scripts/generate_with_audit.py --outros --dj all --skip-audio

# Generate time announcements
python scripts/generate_with_audit.py --time --dj all --skip-audio

# Generate weather
python scripts/generate_with_audit.py --weather --dj all --skip-audio

# Check audit results
Get-Content data\audit\summary.json

# Run tests
pytest tests/ -v
```
