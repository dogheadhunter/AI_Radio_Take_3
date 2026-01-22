# Checkpoint 8.1: Pre-Flight Checklist

#### Checkpoint 8.1: Pre-Flight Checklist
**Verify everything is ready for 24-hour test.**

**Checklist:**
```markdown
## 24-Hour Test Pre-Flight Checklist

### Content Verification
- [ ] Catalog contains all songs
- [ ] All songs have at least one generated intro (Julie and Mr. New Vegas)
- [ ] Time announcements generated for all 48 slots (every 30 min × 2 DJs)
- [ ] Weather templates generated
- [ ] At least one radio show episode ready
- [ ] DJ handoff audio generated

### System Verification
- [ ] All tests pass:  `pytest tests/ -v`
- [ ] Station starts without errors:  `python -m ai_radio --dry-run`
- [ ] Ollama is not needed during playback (all content pre-generated)
- [ ] Chatterbox is not needed during playback (all content pre-generated)
- [ ] Log directory has write permissions
- [ ] Adequate disk space for 24 hours of logs

### Configuration Verification
- [ ] Music library path is correct
- [ ] Weather API key is configured (or weather disabled)
- [ ] Shows directory contains episode(s)

### Environmental Verification
- [ ] Computer will not sleep during test
- [ ] Screen saver won't interfere
- [ ] No scheduled restarts or updates
- [ ] Audio output is configured correctly
```

**Git Commit:** `docs:  add 24-hour test checklist`
