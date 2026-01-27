# Cherry Picker Integration Plan

This document outlines how to integrate the cherry picker module into the AI Radio pipeline.

## Current Status

- **Module**: `src/ai_radio/cherry_picker.py` (standalone, not integrated)
- **Tests**: `tests/cherry_picker/test_cherry_picker.py` (27 tests, all passing)
- **Design**: Modular, extensible, ready for integration

## Integration Points

### Option 1: Regeneration Stage Enhancement

The most natural integration point is in `src/ai_radio/stages/regenerate.py`, replacing "last-pass-wins" logic with intelligent selection.

#### Current Behavior
```python
# stages/regenerate.py (current)
# After max_retries, if multiple versions exist (v0, v1, v2...),
# the last version that passed audit is used
```

#### Enhanced Behavior
```python
# stages/regenerate.py (with cherry picker)
from src.ai_radio.cherry_picker import CherryPicker, SelectionGuidelines

# After regeneration loop completes:
# 1. Find all versions for each script (v0, v1, v2...)
# 2. Load audit results for each version
# 3. Use cherry picker to select best
# 4. Keep only the winner, archive others

picker = CherryPicker()
guidelines = SelectionGuidelines(
    require_audit_pass=True,
    style_weight=2.0,  # Emphasize character voice
    tts_safety_weight=1.5
)

for script_item in scripts_with_multiple_versions:
    versions = find_all_versions(script_item)  # [v0.txt, v1.txt, v2.txt]
    audit_results = load_audit_results(versions)
    
    result = picker.pick_best(versions, audit_results, guidelines, dj=dj)
    
    # Keep winner, archive others
    winner_version = result.winner_path
    for version in versions:
        if version != winner_version:
            archive_version(version)
```

**Pros:**
- Natural fit (regeneration already creates multiple versions)
- Minimal changes to pipeline flow
- Immediate value (better final scripts)

**Cons:**
- Adds complexity to regeneration stage
- Requires tracking all versions (currently only keeps latest)

### Option 2: New Pipeline Stage

Add a new stage between regeneration and audio generation.

```python
# New stage: src/ai_radio/stages/select.py

def stage_select(songs, djs, checkpoint, guidelines=None):
    """Stage 3.5: Select best script from multiple versions."""
    logger.info("STAGE 3.5: SELECT BEST SCRIPTS")
    
    picker = CherryPicker()
    guidelines = guidelines or SelectionGuidelines()
    
    for dj in djs:
        for song in songs:
            versions = find_all_versions(song, dj)
            if len(versions) > 1:
                audit_results = load_audit_results(versions)
                result = picker.pick_best(versions, audit_results, guidelines, dj=dj)
                
                # Save selection metadata
                save_selection_result(result)
                
                # Archive non-winners
                for version in versions:
                    if version != result.winner_path:
                        archive_version(version)
    
    checkpoint.mark_stage_completed("select")
```

**Pros:**
- Clean separation of concerns
- Optional (can be skipped)
- Easy to test in isolation

**Cons:**
- Adds another stage to pipeline
- Requires modification to checkpoint system

### Option 3: Post-Processing Tool

Create a standalone script for post-pipeline selection.

```bash
# scripts/select_best_versions.py
python scripts/select_best_versions.py --dj all --content-type intros
```

**Pros:**
- No pipeline modification
- Can be run anytime
- Easy to experiment with

**Cons:**
- Manual step (not automatic)
- Less integrated with workflow

## Recommended Approach

**Start with Option 3** (standalone tool), then migrate to **Option 1** (regeneration enhancement).

### Phase 1: Standalone Tool (Week 1)

Create `scripts/select_best_versions.py`:
- Find all scripts with multiple versions
- Run cherry picker on each
- Generate selection report
- Optionally archive non-winners

### Phase 2: Regeneration Integration (Week 2-3)

Enhance `stages/regenerate.py`:
- Track all versions during regeneration
- After max retries, run cherry picker
- Keep only winner
- Log selection rationale

### Phase 3: Refinement (Week 4+)

- Tune guideline weights based on real data
- Add external feedback (user reviews, TTS quality metrics)
- Extend with new selection criteria

## Code Changes Required

### Phase 1: Standalone Tool

```python
# scripts/select_best_versions.py
from pathlib import Path
from src.ai_radio.cherry_picker import CherryPicker, SelectionGuidelines
from src.ai_radio.core.paths import get_script_path, get_audit_path
import json

def find_script_versions(song, dj, content_type):
    """Find all versions of a script (v0, v1, v2...)."""
    versions = []
    for i in range(10):  # Max 10 versions
        path = get_script_path(song, dj, content_type, version=i)
        if path.exists():
            versions.append(path)
        else:
            break
    return versions

def load_audit_results(versions):
    """Load audit results for each version."""
    results = {}
    for version in versions:
        audit_path = version.with_suffix('.json')  # Assuming audit stored alongside
        if audit_path.exists():
            with open(audit_path) as f:
                results[version] = json.load(f)
    return results

def main():
    picker = CherryPicker()
    guidelines = SelectionGuidelines(style_weight=2.0)
    
    # For each song/dj/content_type with multiple versions
    for song in songs:
        for dj in djs:
            versions = find_script_versions(song, dj, content_type)
            if len(versions) <= 1:
                continue
            
            audit_results = load_audit_results(versions)
            result = picker.pick_best(versions, audit_results, guidelines, dj=dj)
            
            print(f"Selected {result.winner_path}")
            print(f"  Rationale: {result.selection_rationale}")
```

### Phase 2: Regeneration Integration

```python
# src/ai_radio/stages/regenerate.py (additions)

from src.ai_radio.cherry_picker import CherryPicker, SelectionGuidelines

def stage_regenerate(...):
    # ... existing regeneration logic ...
    
    # NEW: After max_retries loop, select best versions
    logger.info("\nSelecting best script versions...")
    picker = CherryPicker()
    guidelines = SelectionGuidelines(
        require_audit_pass=True,
        style_weight=2.0,
        tts_safety_weight=1.5
    )
    
    for song in songs:
        for dj in djs:
            versions = _find_all_versions(song, dj, content_type)
            if len(versions) <= 1:
                continue
            
            audit_results = _load_audit_results(versions)
            result = picker.pick_best(versions, audit_results, guidelines, dj=dj)
            
            # Archive non-winners
            for version in versions:
                if version != result.winner_path:
                    _archive_version(version)
            
            # Log selection
            logger.info(f"  {song['title']}: selected {result.winner_path.name}")
            logger.debug(f"    {result.selection_rationale}")
```

## Configuration

Add cherry picker configuration to pipeline config:

```json
{
  "cherry_picker": {
    "enabled": true,
    "guidelines": {
      "require_audit_pass": true,
      "clarity_weight": 1.0,
      "style_weight": 2.0,
      "creativity_weight": 1.2,
      "conciseness_weight": 1.0,
      "tts_safety_weight": 1.5,
      "novelty_weight": 0.8
    }
  }
}
```

## Testing Strategy

### Unit Tests
- Already complete (`tests/cherry_picker/test_cherry_picker.py`)
- 27 tests covering all features

### Integration Tests
- Test standalone tool with real data
- Test regeneration integration
- Verify correct winner selection in practice

### Manual Testing
- Run on sample batch (5-10 songs)
- Compare selections to human judgment
- Tune weights based on results

## Success Metrics

- **Selection accuracy**: Winner matches human judgment >80%
- **Performance**: <1 second per batch of 5 versions
- **Audit pass rate**: No decrease from current 99.5%
- **Style consistency**: Improved character voice scores

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Selection disagrees with humans | Medium | Tunable weights, forced picks |
| Performance overhead | Low | Fast scoring (<1s per batch) |
| Over-optimization | Medium | Balance multiple criteria, user override |
| Regression in quality | High | Require audit pass, monitor metrics |

## Timeline

- **Week 1**: Create standalone tool, test on sample data
- **Week 2**: Tune weights, validate selections
- **Week 3**: Integrate into regeneration stage
- **Week 4**: Monitor production, refine

## Future Extensions

1. **External feedback integration**: User reviews, TTS quality scores
2. **Machine learning**: Learn optimal weights from labeled data
3. **Voice synthesis preview**: Test actual TTS output before selection
4. **A/B testing**: Compare cherry picker vs. last-pass-wins
5. **Multi-objective optimization**: Pareto frontier for conflicting criteria
6. **Explainable AI**: Visualize why each script ranked as it did

## Contact

For questions or feedback on cherry picker integration, see the project maintainers.

---

**Status**: Design complete, ready for Phase 1 implementation
**Last Updated**: January 2026
