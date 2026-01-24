# 📋 PHASE 6: Testing & Refinement

## Checkpoints

### Checkpoint 6.1: Initial Test Run 

**Review Template :**
```markdown
### Audit Accuracy
- Scripts auditor passed that you'd fail: X/Y
- Scripts auditor failed that you'd pass: X/Y
- Agreement rate: X%

### Common Issues Observed
1. 
2. 
3. 

### Overall Assessment
- Julie baseline quality: X/10
- Mr. New Vegas baseline quality: X/10
- Ready for refinement: Y/N
```

**Success Criteria:**
- [ ] 10 songs processed through full pipeline
- [ ] All outputs reviewed and scored
- [ ] Baseline quality scores established
- [ ] Issue patterns identified
- [ ] Ready for refinement phase

---

### Checkpoint 6.2: Prompt Refinement Cycle

**Goal:** Improve prompts based on test results

**Refinement Process:**

```
┌─────────────────────────────────────────────────────────────┐
│                  REFINEMENT CYCLE                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. IDENTIFY ISSUES                                          │
│     └── Review failed scripts and low-scoring passes         │
│                                                              │
│  2. DIAGNOSE ROOT CAUSE                                      │
│     ├── Prompt too vague?                                    │
│     ├── Examples not representative?                         │
│     ├── Missing constraints?                                 │
│     └── Wrong emphasis?                                      │
│                                                              │
│  3. MODIFY PROMPT                                            │
│     └── Make ONE change at a time                            │
│                                                              │
│  4. TEST WITH SAME SONGS                                     │
│     └── Use --same-set to compare directly                   │
│                                                              │
│  5. COMPARE RESULTS                                          │
│     ├── Did quality improve?                                 │
│     ├── Any regressions?                                     │
│     └── Keep or revert change?                               │
│                                                              │
│  6. REPEAT until quality target met                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Common Issues and Fixes:**

| Issue | Possible Cause | Fix to Try |
|-------|----------------|------------|
| Too generic | Not enough examples | Add 2-3 more examples |
| Wrong vocabulary | Era constraints too weak | Add specific forbidden words |
| Forced catchphrases | Examples overweight catchphrases | Replace with varied examples |
| Too long | No length guidance | Add explicit length constraint |
| Too short | Length constraint too tight | Relax or remove constraint |
| Wrong character | Examples not distinct enough | Add differentiation instructions |
| Clunky flow | Prompt too prescriptive | Reduce constraints, more natural examples |

**Refinement Log Template:**
```markdown
## Refinement Log

### Iteration 1
**Date:**
**Issue identified:** 
**Root cause hypothesis:** 
**Change made:** 
**Test results:** 
- Before: X/10 average
- After: Y/10 average
**Decision:** Keep / Revert

### Iteration 2
...
```

**Success Criteria:**
- [ ] At least 2 refinement cycles completed
- [ ] Each change tested with `--same-set`
- [ ] Refinement log maintained
- [ ] Quality improving or stable

---

### Checkpoint 6.3: Auditor Calibration

**Goal:** Ensure auditor is accurately identifying quality issues

**Calibration Process:**
1. Review all auditor decisions from test runs
2. Identify false positives (passed but bad)
3. Identify false negatives (failed but good)
4. Adjust auditor prompt if needed

**False Positive Analysis:**
- Scripts that passed audit but you'd reject
- Why did auditor miss the issue?
- What should auditor look for?

**False Negative Analysis:**
- Scripts that failed audit but are actually fine
- Why did auditor flag it incorrectly?
- Is the auditor too strict on certain criteria?

**Calibration Adjustments:**

| Problem | Adjustment |
|---------|------------|
| Too many false positives | Add specific issues to check for |
| Too many false negatives | Relax overly strict criteria |
| Wrong scoring weights | Adjust criteria weights |
| Inconsistent scores | Add more examples to auditor prompt |

**Success Criteria:**
- [ ] False positive rate < 10%
- [ ] False negative rate < 20%
- [ ] Auditor prompt refined if needed
- [ ] Calibration documented

---

### Checkpoint 6.4: Extended Test Run

**Goal:** Validate system at larger scale before full generation

**Tasks:**
1. Run pipeline on 50 songs (random selection)
2. Review audit results and statistics
3. Spot-check 10 random scripts manually
4. Verify pass rate meets target (>80%)
5. Identify any new issue patterns

**Test Command:**
```bash
python scripts/generate_with_audit.py --intros --dj all --limit 50
```

**Expected Results:**
- ~100 scripts generated (50 each DJ)
- >80 scripts pass audit
- <20 scripts in failed folder
- Audio generated for passed scripts

**Spot-Check Protocol:**
1. Randomly select 5 passed Julie scripts
2. Randomly select 5 passed Mr. NV scripts
3. Review each for quality
4. All should be acceptable (minor issues OK)

**Success Criteria:**
- [ ] 50 songs processed successfully
- [ ] Pass rate >80%
- [ ] Spot-check: 8/10 acceptable or better
- [ ] No new systematic issues discovered
- [ ] GPU memory managed correctly throughout

---

### Checkpoint 6.5: Full Content Generation

**Goal:** Generate all content for the radio station

**Generation Plan:**

| Content Type | Count | Estimated Time |
|--------------|-------|----------------|
| Song Intros (Julie) | ~700 | 2-3 hours |
| Song Intros (Mr. NV) | ~700 | 2-3 hours |
| Song Outros (Julie) | ~700 | 1-2 hours |
| Song Outros (Mr. NV) | ~700 | 1-2 hours |
| Time Announcements | 96 | 30 min |
| Weather Templates | 40 | 20 min |
| **Total** | ~2900+ | 8-12 hours |

**Execution Strategy:**
1. Run overnight for song intros
2. Review audit summary in morning
3. Run outros during day
4. Run time/weather when monitoring
5. Review failed scripts after each batch

**Commands:**
```bash
# Night 1: Intros
python scripts/generate_with_audit.py --intros --dj all

# Day 1: Review, then outros
python scripts/generate_with_audit.py --outros --dj all

# Day 2: Time and weather
python scripts/generate_with_audit.py --time --dj all
python scripts/generate_with_audit.py --weather --dj all
```

**Post-Generation Review:**
1. Check audit summaries for each batch
2. Review common failure reasons
3. Decide: regenerate failed scripts or manual edit?
4. Verify audio files exist for all passed scripts

**Success Criteria:**
- [ ] All content types generated
- [ ] Overall pass rate >80%
- [ ] Audio files exist for passed scripts
- [ ] Failed scripts documented for later attention
- [ ] System ran without crashes

---

### Checkpoint 6.6: Failed Script Handling

**Goal:** Address scripts that failed audit

**Options for Failed Scripts:**

**Option A: Regenerate with Adjusted Prompt**
- Review failure reasons
- Tweak prompt for specific issues
- Regenerate just the failed scripts
- Re-audit

**Option B: Manual Edit**
- For scripts close to passing
- Quick fixes (remove one bad word, etc.)
- Mark as manually edited

**Option C: Accept and Skip**
- For songs where generation consistently fails
- Skip intro entirely (just play song)
- Document for future improvement

**Failed Script Review Process:**
1. Group failures by reason
2. Identify patterns
3. Decide approach per pattern
4. Execute fixes
5. Update pass rate

**Success Criteria:**
- [ ] All failed scripts reviewed
- [ ] Decision made for each failure category
- [ ] High-value failures addressed
- [ ] Final pass rate documented
- [ ] Remaining failures acceptable

---

## Phase 6 Gate: Refinement Complete

### All Criteria Must Pass

| Criterion | Validation Method |
|-----------|-------------------|
| Initial test completed | 10 songs reviewed |
| Refinement cycles done | At least 2 iterations |
| Auditor calibrated | False positive <10%, false negative <20% |
| Extended test passed | 50 songs, >80% pass |
| Full generation complete | All content types done |
| Failed scripts addressed | Review complete, decisions made |
| Quality target met | Human satisfaction confirmed |

### Required Artifacts

1. `docs/script_improvement/REFINEMENT_LOG.md`
2. `data/audit/summary.json` (final statistics)
3. Updated `prompts_v2.py` (with refinements)
4. Updated `auditor.py` (if calibrated)
5. Generated content in `data/generated/`

### Final Quality Validation

**Human Review Checklist:**
- [ ] Listened to 10 random Julie intros - sound like Julie?
- [ ] Listened to 10 random Mr. NV intros - sound like Mr. New Vegas?
- [ ] Scripts and audio match (no weird TTS issues)?
- [ ] No scripts have emojis or obviously wrong content?
- [ ] Overall satisfied with quality?

**Sign-Off:**
```markdown
## Quality Sign-Off

**Date:** 
**Reviewer:** 

**Julie Quality:** X/10
**Mr. New Vegas Quality:** X/10

**Issues Remaining:**
- 

**Approved for Production:** Y/N

**Notes:**
```

**Git Commit:** `feat(generation): complete script generation refinement`

**Git Tag:** `v1.0.0-scripts`

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Phase 6 specification created |

---
---
---

# 📋 Script Improvement — Quick Reference

## Phase Summary

| Phase | Name | Status | Gate Passed |
|-------|------|--------|-------------|
| 1 | Style Guide Extraction | Not Started | ⬜ |
| 2 | Prompt Engineering | Not Started | ⬜ |
| 3 | Auditor System | Not Started | ⬜ |
| 4 | Lyrics Integration | Not Started | ⬜ |
| 5 | Batch Pipeline | Not Started | ⬜ |
| 6 | Testing & Refinement | Not Started | ⬜ |

## Key Commands

```bash
# Phase 1: Extract style patterns
python scripts/extract_style_patterns.py

# Phase 2-4: Test new prompts (manual with Ollama)
ollama run fluffy/I3-8b-stheno-v3.2

# Phase 5: Run pipeline
python scripts/generate_with_audit.py --intros --dj all --test --limit 10

# Phase 6: Full generation
python scripts/generate_with_audit.py --intros --dj all
```

## File Locations

| Purpose | Location |
|---------|----------|
| Master Plan | `docs/script_improvement/MASTER_PLAN.md` |
| Phase Specs | `docs/script_improvement/PHASE_X_*.md` |
| Style Guides | `docs/script_improvement/STYLE_GUIDE_*.md` |
| New Prompts | `src/ai_radio/generation/prompts_v2.py` |
| Auditor | `src/ai_radio/generation/auditor.py` |
| Lyrics Parser | `src/ai_radio/generation/lyrics_parser.py` |
| Pipeline Script | `scripts/generate_with_audit.py` |
| Audit Results | `data/audit/` |
| Generated Content | `data/generated/` |

## Models

| Role | Model | Purpose |
|------|-------|---------|
| Writer | fluffy/I3-8b-stheno-v3.2 | Generate scripts |
| Auditor | dolphin-llama3 | Validate scripts |
| TTS | Chatterbox | Generate audio |

## Quality Targets

| Metric | Target |
|--------|--------|
| Audit Pass Rate | >80% |
| Character Recognition | >90% |
| Era Appropriateness | >95% |
| Human Satisfaction | >7/10 |

## Git Tags

| Tag | Milestone |
|-----|-----------|
| `v0.9.1-style-guides` | Phase 1 complete |
| `v0.9.2-prompts` | Phase 2 complete |
| `v0.9.3-auditor` | Phase 3 complete |
| `v0.9.4-lyrics` | Phase 4 complete |
| `v0.9.5-pipeline` | Phase 5 complete |
| `v1.0.0-scripts` | Phase 6 complete, production ready |

---

## Session Start Protocol

When starting work on script improvement:

1. **Read the relevant phase document** (PHASE_X_*.md)
2. **Check current status** in this quick reference
3. **Review any previous session outputs**
4. **Run tests** to confirm baseline: `pytest tests/generation/ -v`
5. **Begin work** on current checkpoint

## Session End Protocol

When ending a work session:

1. **Commit all changes** with descriptive messages
2. **Update status** in this quick reference
3. **Note any incomplete work** for next session
4. **Push to GitHub** if checkpoint complete

---

## Troubleshooting

### GPU Memory Issues
```bash
# Check GPU memory
nvidia-smi

# Force unload models in Ollama
ollama stop fluffy/I3-8b-stheno-v3.2
ollama stop dolphin-llama3
```

### Pipeline Resume
```bash
# Resume from last checkpoint
python scripts/generate_with_audit.py --resume

# Check pipeline state
cat data/pipeline_state.json
```

### Audit Review
```bash
# View failed scripts
ls data/audit/julie/failed/
ls data/audit/mr_new_vegas/failed/

# View audit summary
cat data/audit/summary.json
```

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-23 | Complete script improvement plan created |

---

*This document serves as the master reference for the script improvement project. Individual phase specifications contain detailed checkpoints and success criteria.*