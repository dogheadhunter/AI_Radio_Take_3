# AI Radio Review GUI

Comprehensive Streamlit-based review interface for manually reviewing, approving/rejecting, and regenerating AI-generated radio scripts and audio files.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [User Interface](#user-interface)
- [Workflow Guide](#workflow-guide)
- [Data Structure](#data-structure)
- [Regeneration System](#regeneration-system)
- [Export & Analysis](#export--analysis)
- [Troubleshooting](#troubleshooting)

## Overview

The Review GUI provides a complete quality control workflow for the AI Radio project's 630+ generated scripts and audio files. It integrates with the existing generation pipeline and audit system to allow:

- Manual review of scripts and audio
- Approval/rejection with structured feedback
- Version comparison and tracking
- Regeneration queueing with feedback
- Data export for analysis

### What It Reviews

| Content Type | Count | Description |
|--------------|-------|-------------|
| Song Intros | 264 | DJ introductions for 132 songs × 2 DJs |
| Song Outros | 264 | DJ outros for 132 songs × 2 DJs |
| Time Announcements | 96 | Time of day announcements (every 30 min × 2 DJs) |
| Weather Announcements | 6 | Weather reports (3 conditions × 2 DJs) |
| **Total** | **630** | |

## Installation

### Prerequisites

- Python 3.8+
- All AI Radio project dependencies installed
- Streamlit (added to requirements.txt)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit>=1.30.0` - Web UI framework
- `pandas>=1.5` - Data export and manipulation

## Quick Start

### Launch the Review GUI

```bash
# Method 1: Using the launcher script
python run_review_gui.py

# Method 2: Direct Streamlit command
streamlit run review_gui.py
```

The GUI will open in your default browser at `http://localhost:8501`.

### Basic Workflow

1. **Browse items** using filters and pagination
2. **Listen to audio** and read scripts
3. **Select issues** from predefined categories
4. **Approve or reject** items
5. **Queue regeneration** for items that need improvement
6. **Process queue** to regenerate content with feedback

## Features

### 1. Review Interface

- **Side-by-side display** of script text and audio player
- **Metadata display**: DJ, content type, audit status, review status
- **Version selector**: Switch between different versions
- **Audio playback**: HTML5 player for .wav files

### 2. Filtering & Search

Filter by:
- Content type (intros, outros, time, weather)
- DJ (Julie, Mr. New Vegas)
- Audit status (passed, failed)
- Review status (pending, approved, rejected)
- Item ID search

### 3. Approval/Rejection Workflow

**Status Options:**
- ✅ **Approved**: Item meets quality standards
- ❌ **Rejected**: Item has issues and needs regeneration
- ⚪ **Pending**: Not yet reviewed (default)

**Failure Reason Categories:**

**Script Issues (Intros/Outros):**
- Character voice mismatch
- Wrong era references
- Forbidden elements (swearing, modern references)
- Unnatural flow
- Wrong length
- Doesn't incorporate lyrics
- Factually incorrect

**Script Issues (Time):**
- Character voice mismatch
- Unnatural flow
- Wrong length
- Incorrect time

**Script Issues (Weather):**
- Character voice mismatch
- Doesn't incorporate weather data
- Unnatural flow
- Wrong length
- Factually incorrect

**Audio Issues (All Types):**
- Garbled/distorted audio
- Wrong voice
- Mispronunciation
- Pacing issues
- Volume issues
- Audio artifacts
- Unnatural intonation

### 4. Regeneration Options

- **🔄 Regen Script**: Regenerate text only (audio is good)
- **🔊 Regen Audio**: Regenerate audio only (script is good)
- **🔄🔊 Regen Both**: Regenerate both script and audio

Items are queued for batch processing with feedback from review.

### 5. Version Management

- Automatic version tracking (file_0.txt, file_1.txt, etc.)
- Version comparison viewer
- Latest version indicator
- Browse any historical version

### 6. Statistics Dashboard

Real-time metrics:
- Total items
- Filtered count
- Approved count
- Rejected count
- Regeneration queue size

### 7. CSV Export

Export review data including:
- Item metadata (type, DJ, ID)
- Audit status
- Review status
- Selected issues
- Reviewer notes
- Timestamps

## User Interface

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  🎙️ AI Radio Review GUI                                │
├──────────────┬──────────────────────────────────────────┤
│   SIDEBAR    │           MAIN AREA                      │
│              │                                           │
│  Filters:    │  Statistics (Total, Filtered, etc.)      │
│  - Content   │  [Export CSV Button]                     │
│  - DJ        │                                           │
│  - Audit     │  ┌────────────────────────────────────┐  │
│  - Review    │  │  Item: Artist-Song                 │  │
│  - Search    │  │  Type: intros  DJ: julie  Status:✅│  │
│              │  │  Version: [0 ▼]                    │  │
│  Items/page  │  │                                    │  │
│              │  │  ┌───────────┬──────────────────┐  │  │
│  Actions:    │  │  │ Script    │ Audio            │  │  │
│  🔄 Refresh  │  │  │ [text...] │ [▶️ player]      │  │  │
│              │  │  └───────────┴──────────────────┘  │  │
│  Regen Queue │  │                                    │  │
│  [5 items]   │  │  ✏️ Review Decision               │  │
│  🗑️ Clear    │  │  Script Issues: [checkboxes]      │  │
│              │  │  Audio Issues: [checkboxes]       │  │
│              │  │  Notes: [text area]               │  │
│              │  │  [✅ Approve] [❌ Reject] [🔄...]  │  │
│              │  └────────────────────────────────────┘  │
│              │                                           │
│              │  [⬅️ Previous]  Page 1 of 10  [Next ➡️] │
└──────────────┴──────────────────────────────────────────┘
```

### Status Indicators

- 🟢 **Green dot**: Passed audit / Approved
- 🔴 **Red dot**: Failed audit / Rejected
- ⚪ **White dot**: Pending review

## Workflow Guide

### Complete Review Workflow

```
┌────────────────────┐
│  Launch Review GUI │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────┐
│  Apply filters to   │
│  focus on specific  │
│  content/DJ/status  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  For each item:     │
│  1. Listen to audio │
│  2. Read script     │
│  3. Check versions  │
└─────────┬───────────┘
          │
          ▼
      ┌───┴───┐
      │ Good? │
      └───┬───┘
      Yes │ No
          │   │
          ▼   ▼
    ┌──────┐ ┌────────────────────┐
    │Approve│ │ Select issues &    │
    │       │ │ add notes          │
    └──────┘ ├────────────────────┤
             │ ✅ Reject OR        │
             │ 🔄 Queue regen      │
             └────────────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │ Regeneration     │
          │ Queue builds up  │
          └─────────┬────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ Run queue        │
          │ processor        │
          └─────────┬────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ New versions     │
          │ generated with   │
          │ feedback         │
          └──────────────────┘
```

### Example: Reviewing a Song Intro

1. **Open Review GUI** and filter to "intros"
2. **Select first item** in the list
3. **Play audio** - sounds good ✓
4. **Read script** - notice it uses modern slang ✗
5. **Select issue**: "Forbidden elements"
6. **Add note**: "Uses 'cool' which is too modern for the era"
7. **Click "Regen Script"** (audio is fine, only script needs fixing)
8. Item added to regeneration queue with feedback
9. Continue reviewing more items
10. When done, run `python scripts/process_regen_queue.py`
11. Return to GUI, refresh, and review new version

### Batch Review Tips

- Use **pagination** to work through items systematically
- Apply **filters** to focus on failed audit items first
- Use **CSV export** periodically to track progress
- Queue regenerations as you go, process in batches
- Review regenerated items with version comparison

## Data Structure

### File Organization

```
data/
├── generated/
│   ├── intros/
│   │   ├── julie/
│   │   │   └── Artist-Song/
│   │   │       ├── julie_0.txt        # Original script
│   │   │       ├── julie_0.wav        # Original audio
│   │   │       ├── julie_1.txt        # Regenerated script v1
│   │   │       ├── julie_1.wav        # Regenerated audio v1
│   │   │       └── review_status.json # Review metadata
│   │   └── mr_new_vegas/
│   ├── outros/
│   ├── time/
│   │   └── julie/
│   │       └── 00-00/                 # Hour-minute folders
│   │           ├── julie_0.txt
│   │           ├── julie_0.wav
│   │           └── review_status.json
│   └── weather/
└── regeneration_queue.json
```

### review_status.json Schema

```json
{
  "status": "approved|rejected|pending",
  "reviewed_at": "2026-01-25T10:30:00",
  "reviewer_notes": "Great script but audio has pacing issues",
  "script_issues": [
    "Character voice mismatch",
    "Wrong length"
  ],
  "audio_issues": [
    "Pacing issues"
  ]
}
```

### regeneration_queue.json Schema

```json
[
  {
    "content_type": "intros",
    "dj": "julie",
    "item_id": "Artist-Song",
    "folder_path": "/path/to/data/generated/intros/julie/Artist-Song",
    "regenerate_type": "script|audio|both",
    "feedback": "Script issues: Character voice mismatch. Audio issues: Pacing issues. Great script but audio has pacing issues",
    "added_at": "2026-01-25T10:35:00"
  }
]
```

## Regeneration System

### How It Works

1. **User queues items** via Review GUI buttons
2. **Feedback is compiled** from selected issues + notes
3. **Item added to queue** with regeneration type
4. **Batch processor** reads queue and calls generation pipeline
5. **New versions created** with incremented numbers
6. **Queue cleared** after processing

### Running the Processor

```bash
python scripts/process_regen_queue.py
```

**What it does:**
1. Reads `data/regeneration_queue.json`
2. For each item:
   - Determines next version number
   - Calls appropriate pipeline function with feedback
   - Saves new version (e.g., julie_1.txt, julie_1.wav)
3. Logs results to `logs/regeneration_log.txt`
4. Clears queue

### Integration with Pipeline

The processor uses the existing `GenerationPipeline` class:

```python
# For script-only regeneration
pipeline.generate_song_intro(
    song_id=song_id,
    artist=artist,
    title=title,
    dj=dj,
    text_only=True,
    audit_feedback=feedback  # Passed to LLM prompt
)

# For audio-only regeneration
pipeline.generate_song_intro(
    song_id=song_id,
    artist=artist,
    title=title,
    dj=dj,
    audio_only=True
)

# For both
pipeline.generate_song_intro(
    song_id=song_id,
    artist=artist,
    title=title,
    dj=dj,
    audit_feedback=feedback
)
```

### Feedback Integration

The `audit_feedback` parameter is passed through to prompt builders in `prompts_v2.py`, where it's incorporated into the system prompt to guide the LLM in addressing specific issues.

## Export & Analysis

### CSV Export

Click "📥 Export Reviews to CSV" to download review data.

**Exported Fields:**
- content_type
- dj
- item_id
- latest_version
- audit_status
- review_status
- reviewed_at
- script_issues (comma-separated)
- audio_issues (comma-separated)
- reviewer_notes

### Use Cases

1. **Quality Analysis**: Identify common failure patterns
2. **Prompt Improvement**: Use issue frequencies to refine prompts
3. **Model Training**: Export approved/rejected pairs for fine-tuning
4. **Progress Tracking**: Monitor review completion over time
5. **DJ Comparison**: Compare quality between Julie and Mr. New Vegas

### Example Analysis (using pandas)

```python
import pandas as pd

# Load exported CSV
df = pd.read_csv('review_export.csv')

# Most common script issues
df['script_issues'].str.split(', ').explode().value_counts()

# Approval rate by DJ
df.groupby('dj')['review_status'].value_counts(normalize=True)

# Audit vs review correlation
pd.crosstab(df['audit_status'], df['review_status'])
```

## Troubleshooting

### GUI Won't Start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

**Error**: `FileNotFoundError: review_gui.py not found`

**Solution**: Run from project root
```bash
cd /path/to/AI_Radio_Take_3
python run_review_gui.py
```

### No Items Showing

**Problem**: GUI shows "No items found"

**Possible Causes:**
1. No content generated yet
2. Wrong working directory
3. Filters too restrictive

**Solutions:**
1. Generate content first: `python scripts/generate_with_audit.py --intros --dj all --skip-audio`
2. Check that `data/generated/` exists and has content
3. Reset all filters to "All"

### Audio Won't Play

**Problem**: Audio player shows but no sound

**Solutions:**
1. Check browser console for errors
2. Verify .wav files exist in folders
3. Try different browser (Chrome/Firefox recommended)
4. Check file permissions

### Regeneration Queue Not Processing

**Problem**: Running `process_regen_queue.py` doesn't regenerate

**Check:**
1. Queue file exists: `data/regeneration_queue.json`
2. Queue has items (not empty array)
3. Ollama/LLM services are running
4. Check logs: `logs/regeneration_log.txt`

**Common Errors:**
- `LLM not available`: Start Ollama service
- `TTS not available`: Start Chatterbox TTS
- `Permission denied`: Check file permissions

### Version Numbers Wrong

**Problem**: Versions don't increment properly

**Cause**: File naming doesn't match pattern `{dj}_{version}.{ext}`

**Solution**: Manually rename files to follow convention:
```
julie_0.txt  # Version 0
julie_1.txt  # Version 1
julie_2.txt  # Version 2
```

## Advanced Usage

### Custom Filters

Edit `review_gui.py` to add custom filters:

```python
# Add new filter in sidebar section
st.session_state.filter_custom = st.selectbox(
    "Custom Filter",
    options=[...]
)

# Add filter logic in filter_items()
if st.session_state.filter_custom != "All":
    filtered = [i for i in filtered if custom_condition(i)]
```

### Keyboard Shortcuts

Streamlit doesn't support custom keyboard shortcuts by default, but you can use browser shortcuts:

- `Ctrl+R` / `Cmd+R`: Refresh page
- `Ctrl+F` / `Cmd+F`: Find on page
- `Tab`: Navigate between controls

### Bulk Operations

To approve/reject multiple items at once:

1. Export to CSV
2. Edit CSV with status changes
3. Write a script to read CSV and update review_status.json files

Example:
```python
import pandas as pd
import json
from pathlib import Path

df = pd.read_csv('bulk_updates.csv')

for _, row in df.iterrows():
    folder = Path(row['folder_path'])
    status_file = folder / 'review_status.json'
    
    status = {
        'status': row['new_status'],
        'reviewed_at': pd.Timestamp.now().isoformat(),
        'reviewer_notes': row['notes'],
        'script_issues': [],
        'audio_issues': []
    }
    
    status_file.write_text(json.dumps(status, indent=2))
```

## Integration Notes

### With Existing Pipeline

The Review GUI is read-only for generated content - it doesn't modify scripts/audio directly. It only:
- Reads from `data/generated/`
- Reads from `data/audit/`
- Writes `review_status.json` files
- Writes `regeneration_queue.json`

### With Audit System

- Audit status is read from `data/audit/{dj}/{passed|failed}/`
- Audit results are displayed but not modified
- Review status is independent of audit status
- Both can be used together for quality control

### Future Enhancements

Potential additions:
- Real-time regeneration (instead of queue)
- Multi-user review with reviewer tracking
- Advanced analytics dashboard
- Automated quality scoring
- Integration with training data pipeline
- Approval workflows and permissions

## Support

For issues or questions:

1. Check this documentation
2. Review `logs/regeneration_log.txt` for processing errors
3. Check Streamlit logs in terminal
4. Verify file permissions and paths
5. Ensure all services (Ollama, TTS) are running

## License

Part of the AI Radio Take 3 project.
