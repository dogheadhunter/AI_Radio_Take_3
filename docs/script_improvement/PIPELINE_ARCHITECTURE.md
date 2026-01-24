# Pipeline Architecture: Batch Generation with Audit

## Overview

This document describes the complete pipeline for generating, auditing, and producing audio for AI Radio scripts. The pipeline is designed for GPU efficiency by loading models sequentially and supports checkpointing for resume capability.

## Pipeline Stages

### Stage 1: GENERATE SCRIPTS

**Objective:** Generate text scripts for all songs using the Writer LLM

**Process:**
```
1. Load Song Catalog (data/catalog.json)
2. Load Lyrics Data (music_with_lyrics/*.txt)
3. Initialize Writer Model (Stheno 8B via Ollama)
4. For each song × DJ combination:
   a. Match lyrics to song (if available)
   b. Extract lyrics context (themes, mood, key phrases)
   c. Build prompt with lyrics context (prompts_v2)
   d. Generate script text
   e. Sanitize script (remove meta-commentary, fix punctuation)
   f. Truncate after song introduction
   g. Save to data/generated/intros/{dj}/{artist-title}/{dj}_0.txt
5. Unload Writer Model
6. Save checkpoint to data/pipeline_state.json
```

**Outputs:**
- Text files: `data/generated/intros/{dj}/{artist-title}/{dj}_0.txt`
- Checkpoint: `data/pipeline_state.json` with `generate_completed: true`

**Key Components:**
- `GenerationPipeline` from `src.ai_radio.generation.pipeline`
- `build_song_intro_prompt_v2` from `src.ai_radio.generation.prompts_v2`
- `LLMClient` using model: `fluffy/l3-8b-stheno-v3.2`
- Lyrics matching via `src.ai_radio.generation.lyrics_parser`

**GPU Memory Management:**
- LLM loaded once for all generations
- Models unloaded before next stage
- Text-only generation (no TTS in this stage)

---

### Stage 2: AUDIT SCRIPTS

**Objective:** Evaluate all generated scripts for quality and character accuracy

**Process:**
```
1. Load all text scripts from Stage 1
2. Initialize Auditor Model (Dolphin-Llama3 via Ollama)
3. For each script:
   a. Build audit prompt with script and DJ character reference
   b. Call Auditor LLM
   c. Parse JSON response with criteria scores
   d. Calculate weighted score
   e. Determine pass/fail (threshold: 6.0)
   f. Save result to:
      - data/audit/{dj}/passed/{artist-title}_audit.json (if passed)
      - data/audit/{dj}/failed/{artist-title}_audit.json (if failed)
4. Unload Auditor Model
5. Generate summary report (data/audit/summary.json)
6. Update checkpoint (audit_completed: true)
```

**Outputs:**
- Audit results: `data/audit/{dj}/{passed|failed}/{artist-title}_audit.json`
- Summary: `data/audit/summary.json`
- Updated checkpoint: `data/pipeline_state.json`

**Key Components:**
- `audit_batch` from `src.ai_radio.generation.auditor`
- Auditor LLM model (via Ollama, configured in LLMClient)
- Scoring criteria: character_voice, era_appropriateness, forbidden_elements, natural_flow, length

**Audit Criteria Weights:**
```python
{
    "character_voice": 0.30,        # Matches DJ personality
    "era_appropriateness": 0.25,    # No anachronisms or modern slang
    "forbidden_elements": 0.20,     # No emojis, dates, meta-commentary
    "natural_flow": 0.15,           # Reads naturally, appropriate length
    "length": 0.10                  # Ends with song intro, not too long
}
```

**Pass/Fail Logic:**
- Each criterion scored 1-10
- Weighted average calculated
- Pass threshold: >= 6.0
- Failed scripts are NOT processed in Stage 3

---

### Stage 3: GENERATE AUDIO (Passed Scripts Only)

**Objective:** Generate audio files for scripts that passed the audit

**Process:**
```
1. Filter to passed scripts only (from Stage 2 results)
2. Load Chatterbox TTS Model (Chatterbox-Turbo)
3. Load voice references:
   - assets/voice_references/Julie/julie.wav
   - assets/voice_references/Mister_New_Vegas/mr_new_vegas.wav
4. For each passed script:
   a. Read text from data/generated/intros/{dj}/{artist-title}/{dj}_0.txt
   b. Generate audio using TTS + voice reference
   c. Save to data/generated/intros/{dj}/{artist-title}/{dj}_0.wav
5. Unload TTS Model
6. Update checkpoint (audio_completed: true)
7. Mark pipeline as complete
```

**Outputs:**
- Audio files: `data/generated/intros/{dj}/{artist-title}/{dj}_0.wav`
- Final checkpoint: `data/pipeline_state.json`

**Key Components:**
- `TTSClient` from `src.ai_radio.generation.tts_client`
- Chatterbox-Turbo model (loaded locally, not via server)
- Voice cloning with reference audio

**GPU Memory Management:**
- TTS model loaded once for all audio generation
- No other models loaded during this stage
- Efficient batch processing

---

## Checkpoint System

### Checkpoint File: `data/pipeline_state.json`

**Purpose:** Enable resume capability after interruption

**Structure:**
```json
{
  "timestamp": "2026-01-24T12:00:00",
  "run_id": "20260124_120000",
  "config": {
    "content_types": ["intros"],
    "djs": ["julie", "mr_new_vegas"],
    "song_limit": 100,
    "test_mode": false
  },
  "stages": {
    "generate": {
      "status": "completed",
      "completed_at": "2026-01-24T12:15:00",
      "scripts_generated": 200,
      "songs_processed": ["1", "2", "3", ...]
    },
    "audit": {
      "status": "in_progress",
      "completed_at": null,
      "scripts_audited": 150,
      "passed": 120,
      "failed": 30
    },
    "audio": {
      "status": "not_started",
      "completed_at": null,
      "audio_files_generated": 0
    }
  }
}
```

**Resume Logic:**
- If `generate.status == "completed"`, skip Stage 1
- If `audit.status == "completed"`, skip Stages 1 & 2
- If `audio.status == "completed"`, pipeline is fully complete
- Within each stage, check for existing files to skip individual items

---

## CLI Interface

### Command-Line Options

```bash
# Content type selection
--intros          Generate song intros
--outros          Generate song outros
--time            Generate time announcements
--weather         Generate weather announcements
--all-content     Generate everything

# DJ selection
--dj julie|mr_new_vegas|all

# Mode selection
--test            Test mode (uses FakeAuditorClient, limit 10)
--limit N         Process only N items
--random          Random selection (for testing)
--same-set        Use same N items as last --test run

# Stage control
--stage generate|audit|audio|all
--skip-audio      Generate and audit but skip audio
--resume          Resume from last checkpoint

# Output
--dry-run         Show what would be generated
--verbose         Detailed logging
```

### Usage Examples

```bash
# Full production run with both DJs
python scripts/generate_with_audit.py --intros --dj all

# Test run with 10 songs
python scripts/generate_with_audit.py --intros --dj julie --test --limit 10

# Resume interrupted run
python scripts/generate_with_audit.py --resume

# Generate and audit only (no audio)
python scripts/generate_with_audit.py --intros --dj all --skip-audio

# Run specific stage only
python scripts/generate_with_audit.py --stage audit

# Dry run to see what would happen
python scripts/generate_with_audit.py --intros --dj all --limit 20 --dry-run
```

---

## Data Flow Diagram

```
[catalog.json] ──┐
                 ├──> STAGE 1: Generate Scripts ──> [.txt files]
[lyrics/*.txt] ──┘                                        │
                                                           v
                                     STAGE 2: Audit ──> [passed/] [failed/]
                                                           │
                                                           v
                                                   STAGE 3: Audio
                                                           │
                                                           v
                                                      [.wav files]
```

---

## Error Handling

### Stage 1 Errors
- **LLM unavailable:** Fail fast, report error
- **Single song fails:** Log warning, continue to next song
- **Lyrics missing:** Generate without lyrics context (graceful degradation)
- **Sanitization failure:** Skip script, log error

### Stage 2 Errors
- **Auditor unavailable:** Fail fast, report error
- **JSON parse error:** Mark as failed audit, continue
- **Single audit fails:** Mark as failed, continue to next

### Stage 3 Errors
- **TTS unavailable:** Fail fast, report error
- **Single audio fails:** Log error, continue to next
- **Voice reference missing:** Generate without voice reference (fallback)

### Resume Capability
- All stages can be resumed after interruption
- Completed items are skipped based on file existence
- Checkpoint file tracks overall progress

---

## Performance Characteristics

### Estimated Timing (100 songs, 2 DJs = 200 scripts)

| Stage | Time per Item | Total Time | GPU Usage |
|-------|---------------|------------|-----------|
| Generate Scripts | 3-5 sec | 10-17 min | High (LLM) |
| Audit Scripts | 2-3 sec | 7-10 min | High (Auditor) |
| Generate Audio | 5-8 sec | 14-21 min (passed only) | High (TTS) |
| **Total Pipeline** | - | **31-48 min** | Sequential |

**Notes:**
- Audio generation only for passed scripts (~80% = 160 scripts)
- GPU memory never exceeds single model's requirement
- All stages can be interrupted and resumed

---

## Testing Strategy

### Unit Tests
- Each stage function independently testable
- Mock LLM/TTS clients for fast tests
- Checkpoint save/load logic

### Integration Tests
- Full pipeline with `--test --limit 10`
- Resume capability (interrupt and resume)
- Error handling for each stage
- Dry-run mode validation

### Validation Criteria (Phase 5 Gate)
- [ ] Pipeline completes successfully with `--limit 10`
- [ ] Checkpoint system works (interrupt and resume)
- [ ] GPU memory managed (no OOM errors)
- [ ] Pass rate >= 80% in audit stage
- [ ] All test modes work (`--test`, `--same-set`, `--dry-run`)

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-24 | 1.0 | Initial architecture specification |

