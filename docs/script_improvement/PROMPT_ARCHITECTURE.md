# Prompt Architecture (Phase 2)

## Overview

This document records the prompt architecture used for improved prompt templates (v2).

## Structure

SYSTEM PROMPT
1. Role Definition (who you are)
2. Character Voice Summary (how you speak)
3. Era Constraints (vocabulary rules)
4. Forbidden Elements (what to never do)
5. Few-Shot Examples (3-5 actual character lines)

USER PROMPT
1. Content Type (intro, outro, time, weather)
2. Song Information (artist, title, year)
3. Lyrics Context (if available)
4. Specific Instructions (length, formatting)

## Example Selection Strategy
- Select 3-5 exemplar lines that represent the full variety of the persona (intro types, outros, weather phrasing, time announcements).
- Prefer short, self-contained lines (1-2 sentences) that highlight key traits (e.g., warmth for Julie; suavity for Mr. New Vegas).
- Pick examples that avoid rare edge-cases or references; if a rare turn-of-phrase is useful, retain only one such example.
- Ensure that the set includes both short (1 sentence) and slightly longer (2-3 sentence) examples so the model learns acceptable length variation.

## Content-type planning
- Song intros: include artist-specific context and optional lyrics context.
- Outros: short, one-line transitions that optionally tease the next song.
- Time: concise single-sentence announcements that fit the DJ persona.
- Weather: 2-3 sentence summaries with time-of-day context when available.

## Token Budget Recommendations
- System prompt: ~500-800 tokens
- User prompt: ~200-400 tokens
- Leave room for generation: ~500-1000 tokens

## Files
- `src/ai_radio/generation/prompts_v2.py`: Implementation of v2 prompt builders.
- `tests/generation/test_prompts_v2.py`: Unit tests verifying presence of system/user prompts, examples, and forbidden words.

## Notes
- `prompts_v2` functions return a dict with `system` and `user` keys to support LLMs that accept a system+user message separation.
- `GenerationPipeline` supports `prompt_version='v1'` (default) and `prompt_version='v2'` to switch behavior.
