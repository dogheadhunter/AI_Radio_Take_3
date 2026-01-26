# AI Radio Backend API

This package provides a clean Python API for GUI and automation tools to interact with the AI Radio generation pipeline without CLI dependencies.

## Overview

The API is organized into four main modules:

- **`schemas.py`** - Shared data types (ContentType, DJ, SongInfo, etc.)
- **`content.py`** - Content discovery and listing (ContentAPI)
- **`generation.py`** - Trigger generation operations (GenerationAPI)
- **`audit.py`** - Script auditing and result management (AuditAPI)
- **`review.py`** - Human-in-the-loop approval workflow (ReviewAPI)

## Quick Start

```python
from src.ai_radio.api import ContentAPI, GenerationAPI, AuditAPI, ReviewAPI
from src.ai_radio.api import ContentType, DJ, SongInfo

# Initialize APIs
content_api = ContentAPI()
generation_api = GenerationAPI()
audit_api = AuditAPI()
review_api = ReviewAPI()

# List available content
scripts = content_api.list_scripts(dj=DJ.JULIE, content_type=ContentType.INTRO)
print(f"Found {len(scripts)} intro scripts for Julie")

# Generate new content
song = SongInfo(id="1", artist="Johnny Cash", title="Ring of Fire")
result = generation_api.generate_intro(song=song, dj=DJ.JULIE)
if result.success:
    print(f"Generated: {result.script_path}")

# Check audit results
audit_result = audit_api.get_audit_result(
    content_type=ContentType.INTRO,
    dj=DJ.JULIE,
    song=song,
)
if audit_result and not audit_result.passed:
    print(f"Audit failed: {audit_result.issues}")

# Review workflow
pending = review_api.list_pending_reviews()
for item in pending:
    print(f"Pending: {item.content.display_name}")
```

## Content API

The ContentAPI provides methods to discover and list generated content.

### Key Methods

```python
api = ContentAPI()

# Load song catalog
songs = api.load_catalog()

# List scripts by type and DJ
intros = api.list_scripts(content_type=ContentType.INTRO, dj=DJ.JULIE)
time_announcements = api.list_scripts(content_type=ContentType.TIME)

# Get specific script
script = api.get_script(
    content_type=ContentType.INTRO,
    dj=DJ.JULIE,
    song=SongInfo(id="1", artist="Artist", title="Song"),
)

# Get pipeline status
status = api.get_pipeline_status()
print(f"Scripts generated: {status.scripts_generated}")
print(f"Scripts passed audit: {status.scripts_passed}")

# Count content
counts = api.count_content()
```

## Generation API

The GenerationAPI triggers content generation.

### Key Methods

```python
api = GenerationAPI()

# Generate song intro
result = api.generate_intro(
    song=SongInfo(id="1", artist="Artist", title="Song"),
    dj=DJ.JULIE,
    text_only=True,
    overwrite=False,
)

# Generate with audit feedback (for regeneration)
result = api.generate_intro(
    song=song,
    dj=DJ.JULIE,
    audit_feedback="Character voice was too modern",
)

# Generate time announcement
result = api.generate_time_announcement(
    hour=14,
    minute=30,
    dj=DJ.JULIE,
)

# Generate weather announcement
result = api.generate_weather_announcement(
    hour=12,
    dj=DJ.MR_NEW_VEGAS,
    weather_summary="Clear skies, 75 degrees",
)

# Batch generation
results = api.generate_batch(
    songs=[song1, song2, song3],
    djs=[DJ.JULIE, DJ.MR_NEW_VEGAS],
    content_types=[ContentType.INTRO, ContentType.OUTRO],
)
```

## Audit API

The AuditAPI handles script quality evaluation.

### Key Methods

```python
api = AuditAPI(test_mode=False)  # Use test_mode=True for mock auditing

# Run audit on a script
result = api.audit_script(
    content_type=ContentType.INTRO,
    dj=DJ.JULIE,
    song=song,
    save_result=True,
)
print(f"Passed: {result.passed}, Score: {result.score}")

# List audit results
passed_audits = api.list_audit_results(passed=True)
failed_audits = api.list_audit_results(passed=False, dj=DJ.JULIE)

# Get specific audit result
result = api.get_audit_result(
    content_type=ContentType.INTRO,
    dj=DJ.JULIE,
    song=song,
)

# Get audit summary
summary = api.get_audit_summary()
print(f"Pass rate: {summary['pass_rate']:.1%}")

# Delete audit for re-auditing
api.delete_audit_result(content_type=ContentType.INTRO, dj=DJ.JULIE, song=song)
```

## Review API

The ReviewAPI manages the human-in-the-loop approval workflow.

### Key Methods

```python
api = ReviewAPI(test_mode=True)

# List pending reviews (failed audits awaiting approval)
pending = api.list_pending_reviews(dj=DJ.JULIE)

# Approve a script
api.approve(pending[0], notes="Sounds good!")

# Reject and queue for regeneration
api.reject(
    pending[1],
    reason="Wrong character voice",
    queue_regen=True,
)

# Get regeneration queue
regen_queue = api.get_regeneration_queue()

# Mark as regenerated (after actual regeneration)
api.mark_regenerated(regen_queue[0])

# Get review statistics
stats = api.get_review_stats()
print(f"Pending: {stats['pending']}, Approved: {stats['approved']}")
```

## Data Types

### Enums

```python
from src.ai_radio.api import ContentType, DJ, ReviewStatus

# Content types
ContentType.INTRO    # Song intro
ContentType.OUTRO    # Song outro
ContentType.TIME     # Time announcement
ContentType.WEATHER  # Weather announcement

# DJs
DJ.JULIE            # Julie personality
DJ.MR_NEW_VEGAS     # Mr. New Vegas personality

# Review statuses
ReviewStatus.PENDING       # Awaiting review
ReviewStatus.APPROVED      # Approved for use
ReviewStatus.REJECTED      # Rejected, not queued for regen
ReviewStatus.REGENERATING  # Queued for regeneration
```

### Dataclasses

```python
from src.ai_radio.api import SongInfo, ContentItem, GenerationResult, AuditResult, ReviewItem

# SongInfo - song metadata
song = SongInfo(id="1", artist="Johnny Cash", title="Ring of Fire")

# ContentItem - generated content
item.content_type   # ContentType enum
item.dj             # DJ enum
item.script_path    # Path to script file
item.audio_path     # Path to audio file (if exists)
item.script_text    # Script content (if loaded)
item.has_script     # True if script file exists
item.has_audio      # True if audio file exists
item.display_name   # Human-readable name

# GenerationResult - generation outcome
result.success      # True if generation succeeded
result.text         # Generated text
result.script_path  # Path to saved script
result.error        # Error message if failed

# AuditResult - audit outcome
result.passed       # True if passed audit
result.score        # Overall score (0-10)
result.criteria_scores  # Dict of individual scores
result.issues       # List of identified issues
result.notes        # Auditor notes

# ReviewItem - review queue item
item.content        # ContentItem being reviewed
item.audit_result   # Associated AuditResult
item.status         # ReviewStatus
item.needs_review   # True if pending
```

## Testing

The API layer is fully tested with mock support:

```bash
# Run API tests only
pytest tests/api/ -v

# Run with coverage
pytest tests/api/ --cov=src/ai_radio/api
```

### Test Mode

All APIs support `test_mode=True` for mock behavior:

```python
# Use fake auditor (no LLM calls)
audit_api = AuditAPI(test_mode=True)

# Use mock pipeline (no generation)
generation_api = GenerationAPI(test_mode=True)
```

## Integration with GUI

The API is designed to be the single point of integration for GUI tools:

```python
# Example: Streamlit GUI integration
import streamlit as st
from src.ai_radio.api import ContentAPI, ReviewAPI

content_api = ContentAPI()
review_api = ReviewAPI()

# Display pending reviews
pending = review_api.list_pending_reviews()
for item in pending:
    with st.expander(item.content.display_name):
        st.text(item.content.script_text)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve", key=f"approve_{item.content.display_name}"):
                review_api.approve(item)
        with col2:
            if st.button("Reject & Regen", key=f"reject_{item.content.display_name}"):
                review_api.reject(item, queue_regen=True)
```

## Design Principles

1. **No CLI dependencies** - APIs don't require CLI args or interactive input
2. **No UI dependencies** - APIs don't require Streamlit or any UI framework
3. **Structured results** - All operations return typed dataclasses
4. **Testable** - Full mock support for all external services
5. **Composable** - APIs can be used together or independently
