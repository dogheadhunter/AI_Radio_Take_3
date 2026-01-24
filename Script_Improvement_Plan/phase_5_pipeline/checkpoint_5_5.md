# Checkpoint 5.5: CLI and Options

## Status
**NOT STARTED** ⬜

## Goal
Create comprehensive command-line interface for all pipeline operations.

## Tasks

### 1. Implement Content Type Selection
- [ ] `--intros` flag
- [ ] `--outros` flag
- [ ] `--time` flag
- [ ] `--weather` flag
- [ ] `--all-content` flag

### 2. Implement DJ Selection
- [ ] `--dj julie` option
- [ ] `--dj mr_new_vegas` option
- [ ] `--dj all` option

### 3. Implement Mode Selection
- [ ] `--test` mode (limit 10, specific songs)
- [ ] `--limit N` option
- [ ] `--random` option
- [ ] `--same-set` option (reproducible test runs)

### 4. Implement Stage Control
- [ ] `--stage generate|audit|audio|all` option
- [ ] `--skip-audio` flag
- [ ] `--resume` flag

### 5. Implement Output Options
- [ ] `--dry-run` flag
- [ ] `--verbose` flag
- [ ] Help text
- [ ] Usage examples

## CLI Options

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
--test            Test mode (limit 10, specific songs)
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

## Success Criteria

| Criterion | Status |
|-----------|--------|
| All options implemented | ⬜ |
| `--test` and `--same-set` work for iteration | ⬜ |
| `--resume` correctly skips completed work | ⬜ |
| Help text is clear and complete | ⬜ |

## Next Steps
Proceed to Phase 5 Gate validation to confirm all criteria met.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-24 | Checkpoint created from Phase 5 specification |
