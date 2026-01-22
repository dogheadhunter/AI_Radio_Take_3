# Refactoring Guidelines

## Refactoring Guidelines

### When to Refactor

| Signal | Action |
|--------|--------|
| Same code in 3+ places | Extract to shared function |
| Function > 50 lines | Break into smaller functions |
| File > 300 lines | Split into modules |
| Test is hard to write | Simplify the code |
| You can't explain what code does | Rewrite for clarity |

### How to Refactor Safely

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFE REFACTORING                          │
│                                                              │
│  1. All tests pass BEFORE refactoring                        │
│  2. Make ONE change at a time                                │
│  3. Run tests after EACH change                              │
│  4. If tests fail, UNDO the change                           │
│  5. Commit after each successful change                      │
│  6. Never refactor and add features simultaneously           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Refactoring Commit Pattern
```
refactor(component): description of change

- What was changed
- Why it was changed
- No behavior changes

All tests pass. 
```
