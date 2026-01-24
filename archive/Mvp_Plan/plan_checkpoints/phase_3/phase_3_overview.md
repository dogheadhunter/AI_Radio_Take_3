# Phase 3 Overview

## Phase 3: Audio Playback Engine

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | Play audio files with queue management |
| **Duration** | 2-3 sessions |
| **Complexity** | Medium |
| **Dependencies** | Phase 0 complete |

### Technology Decision
Before implementing, we need to choose an audio library.  This is an **Architecture Decision Record (ADR)**.

**File:  `docs/decisions/ADR-001-audio-library.md`**
```markdown
# ADR-001: Audio Playback Library

## Status
Proposed

## Context
We need to play MP3 and WAV files for the radio station. 
Requirements:
- Play audio files sequentially
- Control volume
- Know when a file finishes playing
- Work on Windows 11
- Be reliable for 24-hour operation

## Options Considered

### Option A: pygame. mixer
- Pros: Well-documented, cross-platform, easy to use
- Cons: Requires pygame installation, may be overkill

### Option B: playsound
- Pros: Very simple, minimal dependencies
- Cons: Limited features, no callbacks for completion

### Option C:  python-vlc
- Pros: Powerful, uses VLC backend
- Cons:  Requires VLC installation, complex

### Option D: pydub + simpleaudio
- Pros: Good audio manipulation, lightweight playback
- Cons: Two libraries to manage

## Decision
**Option A:  pygame.mixer**

Rationale:
- Most documented for this use case
- Provides completion callbacks
- Handles common audio formats
- Cross-platform

## Consequences
- Must add pygame to requirements. txt
- Initialize pygame.mixer at startup
- Use pygame.mixer.music for longer files (songs)
- Use pygame.mixer.Sound for short files (intros, time announcements)
```
