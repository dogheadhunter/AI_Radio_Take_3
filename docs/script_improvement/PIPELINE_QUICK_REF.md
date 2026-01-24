# Pipeline Quick Reference

Quick reference for using the complete generation pipeline.

---

## Common Commands

### Basic Usage

```bash
# Full production run (all songs, both DJs)
python scripts/generate_with_audit.py --intros --dj all

# Test with 10 songs
python scripts/generate_with_audit.py --intros --dj julie --limit 10 --test

# Specific DJ only
python scripts/generate_with_audit.py --intros --dj julie
python scripts/generate_with_audit.py --intros --dj mr_new_vegas
```

### Stage Control

```bash
# Generate and audit only (skip audio)
python scripts/generate_with_audit.py --intros --dj all --skip-audio

# Run specific stage only
python scripts/generate_with_audit.py --stage generate
python scripts/generate_with_audit.py --stage audit
python scripts/generate_with_audit.py --stage audio
```

### Resume & Recovery

```bash
# Resume interrupted run
python scripts/generate_with_audit.py --resume

# Check what would be done without doing it
python scripts/generate_with_audit.py --intros --dj all --dry-run
```

### Testing & Debugging

```bash
# Test mode with fake auditor (fast)
python scripts/generate_with_audit.py --intros --dj all --limit 10 --test

# Verbose output for debugging
python scripts/generate_with_audit.py --intros --dj julie --limit 5 --verbose

# Random sample for testing
python scripts/generate_with_audit.py --intros --dj all --limit 20 --random
```

---

## Output Locations

### Generated Scripts
```
data/generated/intros/
├── julie/
│   └── {Artist-Title}/
│       └── julie_0.txt
└── mr_new_vegas/
    └── {Artist-Title}/
        └── mr_new_vegas_0.txt
```

### Audit Results
```
data/audit/
├── julie/
│   ├── passed/{Artist-Title}_audit.json
│   └── failed/{Artist-Title}_audit.json
├── mr_new_vegas/
│   ├── passed/{Artist-Title}_audit.json
│   └── failed/{Artist-Title}_audit.json
└── summary.json
```

### Audio Files
```
data/generated/intros/
├── julie/
│   └── {Artist-Title}/
│       └── julie_0.wav
└── mr_new_vegas/
    └── {Artist-Title}/
        └── mr_new_vegas_0.wav
```

### Checkpoint
```
data/pipeline_state.json
```

---

## Troubleshooting

### Pipeline Stuck or Interrupted

```bash
# Check checkpoint status
cat data/pipeline_state.json

# Resume from last checkpoint
python scripts/generate_with_audit.py --resume

# Clear checkpoint and start fresh
rm data/pipeline_state.json
python scripts/generate_with_audit.py --intros --dj all
```

### Audit Results Review

```bash
# View summary
cat data/audit/summary.json

# Count passed/failed
ls data/audit/julie/passed/ | wc -l
ls data/audit/julie/failed/ | wc -l

# Review failed scripts
cat data/audit/julie/failed/Artist-Song_audit.json
```

### GPU Memory Issues

```bash
# Check GPU memory
nvidia-smi

# Stop Ollama if needed
ollama stop fluffy/l3-8b-stheno-v3.2
ollama stop dolphin-llama3

# Kill any stuck Python processes
taskkill /F /IM python.exe /T
```

### Re-run Specific Stage

```bash
# Delete audit results and re-audit
rm -r data/audit/
python scripts/generate_with_audit.py --stage audit

# Regenerate audio for passed scripts
rm data/generated/intros/julie/*/julie_0.wav
python scripts/generate_with_audit.py --stage audio
```

---

## Pipeline Flow

```
1. Load catalog.json
2. Load lyrics (if available)
3. STAGE 1: Generate Scripts
   - For each song × DJ
   - Generate text with Writer LLM
   - Sanitize and truncate
   - Save to .txt file
4. STAGE 2: Audit
   - For each script
   - Run through Auditor LLM
   - Calculate score
   - Save to passed/ or failed/
5. STAGE 3: Audio
   - For passed scripts only
   - Load TTS model
   - Generate audio with voice cloning
   - Save to .wav file
6. Done!
```

---

## Expected Performance

### Small Test (10 songs, 2 DJs, test mode)
- Scripts: instant (test mode)
- Audit: < 1 second (fake auditor)
- Audio: ~5 minutes (20 files @ 15 sec each)
- **Total: ~5 minutes**

### Medium Run (50 songs, 2 DJs)
- Scripts: ~5-8 minutes
- Audit: ~3-5 minutes  
- Audio: ~12-18 minutes (80 files @ 15 sec)
- **Total: ~20-31 minutes**

### Full Catalog (100+ songs, 2 DJs)
- Scripts: ~10-17 minutes
- Audit: ~7-10 minutes
- Audio: ~25-35 minutes (160 files @ 15 sec)
- **Total: ~42-62 minutes**

---

## Quality Checks

After running the pipeline:

```bash
# Check pass rate
cat data/audit/summary.json | grep pass_rate

# Count outputs
find data/generated/intros/ -name "*.txt" | wc -l
find data/generated/intros/ -name "*.wav" | wc -l

# Verify no errors
ls data/audit/julie/failed/
ls data/audit/mr_new_vegas/failed/
```

Expected results:
- Pass rate: 80%+ for production
- All passed scripts should have audio
- Failed scripts should NOT have audio

---

## See Also

- [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md) - Complete architecture documentation
- [PHASE_5_COMPLETE.md](PHASE_5_COMPLETE.md) - Implementation validation report
- [Phase_five.md](../../Script_Improvment_Plan/Phase/Phase_five.md) - Original specification

