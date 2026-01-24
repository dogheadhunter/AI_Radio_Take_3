# Checkpoint 2.5: Prompt Integration

## Goal
Integrate new prompts into the generation system

## Tasks

1. Create `prompts_v2.py` with all new prompt functions
2. Maintain backward compatibility with existing system
3. Add configuration to switch between old/new prompts
4. Create tests for new prompt functions

## File Structure

```python
# src/ai_radio/generation/prompts_v2.py

"""
Improved prompt templates for DJ personalities.
Version 2: Uses extracted style guides and few-shot examples.
"""

from enum import Enum
from typing import Optional, Dict, Any

class DJ(Enum):
    JULIE = "julie"
    MR_NEW_VEGAS = "mr_new_vegas"

# Style guide content (extracted from Phase 1)
JULIE_EXAMPLES = [...]
MR_NV_EXAMPLES = [...]
FORBIDDEN_WORDS = [...]

def build_song_intro_prompt_v2(
    dj: DJ,
    artist: str,
    title: str,
    year: Optional[int] = None,
    lyrics_context: Optional[str] = None,
) -> Dict[str, str]:
    """Build improved song intro prompt."""
    pass
```

## Test File

`tests/generation/test_prompts_v2.py`

## Success Criteria

- [x] `prompts_v2.py` created with all functions
- [x] All functions return proper prompt structure
- [x] Tests verify prompt content includes examples
- [x] Tests verify forbidden words are mentioned
- [x] No breaking changes to existing generation

## Note

Pipeline supports `prompt_version='v2'` and generator tests pass. See `tests/generation/test_prompts_v2.py`.

## Status

**✅ COMPLETE** - Integration verified
