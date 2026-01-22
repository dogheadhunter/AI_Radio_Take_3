# Context Management

## Context Management

### Preventing Context Rot

**For LLM-Assisted Development:**

#### 1. Session Start Protocol
Every coding session begins with:
```markdown
1. Read ROADMAP.md (this document)
2. Read current phase specification
3. Run:  pytest tests/ -v (establish baseline)
4. Review last 3 git commits
5. Read any flagged issues/TODOs
```

#### 2. Session End Protocol
Every coding session ends with: 
```markdown
1. Run: pytest tests/ -v (all must pass)
2. Commit all changes with clear messages
3. Update CHANGELOG.md if significant
4. Note any incomplete work in TODO
5. Push to GitHub
```

#### 3. Context Anchors
Key files that maintain context:
- `ROADMAP.md` — Overall plan (this document)
- `PROJECT_SPEC.md` — What we're building
- `CHANGELOG.md` — What's been done
- `data/catalog.json` — Current music state
- `logs/` — Recent activity

#### 4. Conversation Boundaries
When starting a new conversation with an LLM: 
```markdown
## Context for New Session

### Current Phase:  [X]
### Last Completed Checkpoint: [X. Y]
### Current Checkpoint: [X.Z]

### Recent Changes:
- [commit 1]
- [commit 2]
- [commit 3]

### Known Issues:
- [issue 1]

### Today's Goal:
[specific goal]
```

#### 5. Test-Driven Context
Tests serve as executable documentation:
- If unsure what code should do, read the tests
- Tests define the contract
- Tests don't lie (code might)
