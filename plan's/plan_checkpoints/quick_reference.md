# Quick Reference

## Quick Reference

### Command Cheat Sheet
```bash
# Run all tests
pytest tests/ -v

# Run specific phase tests
pytest tests/library/ -v
pytest tests/generation/ -v
pytest tests/playback/ -v

# Run integration tests
pytest tests/integration/ -v -m integration

# Run with coverage
pytest tests/ --cov=src/ai_radio --cov-report=html

# Scan music library
python scripts/scan_library. py /path/to/music

# Generate content (test)
python scripts/generate_content.py --intros --dj julie --limit 5

# Run station (dry run)
python -m ai_radio --dry-run

# Run station
python -m ai_radio
```

### Git Tag Summary
| Tag | Milestone |
|-----|-----------|
| `v0.1.0-foundation` | Phase 0 complete |
| `v0.2.0-library` | Phase 1 complete |
| `v0.3.0-generation` | Phase 2 complete |
| `v0.4.0-playback` | Phase 3 complete |
| `v0.5.0-dj` | Phase 4 complete |
| `v0.6.0-shows` | Phase 5 complete |
| `v0.7.0-services` | Phase 6 complete |
| `v0.8.0-integration` | Phase 7 complete |
| `v1.0.0-mvp` | MVP complete!  🎉 |

*This roadmap is your guide.  Follow it step by step, validate each checkpoint, and you will have a working AI Radio Station.*
