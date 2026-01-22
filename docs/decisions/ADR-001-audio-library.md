# ADR-001: Audio Playback Library

## Status
Proposed

## Context
We need to play MP3 and WAV files for the radio station. Requirements:
- Play audio files sequentially
- Control volume
- Know when a file finishes playing
- Work on Windows 11
- Be reliable for 24-hour operation

## Decision
**Option A: pygame.mixer**

Rationale:
- Most documented for this use case
- Provides completion callbacks
- Handles common audio formats
- Cross-platform

## Consequences
- Add pygame to requirements
- Initialize pygame.mixer at startup when real playback is used
- Use pygame.mixer.music for longer files (songs)
- Use pygame.mixer.Sound for short files (intros, time announcements)
