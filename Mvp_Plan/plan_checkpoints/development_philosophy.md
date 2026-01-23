# Development Philosophy

## Development Philosophy

### Core Principles

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT CYCLE                         │
│                                                              │
│    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐ │
│    │ PLAN │ ─▶ │ CODE │ ─▶ │ TEST │ ─▶ │DEBUG │ ─▶ │COMMIT│ │
│    └──────┘    └──────┘    └──────┘    └──────┘    └──────┘ │
│        ▲                                    │                │
│        └────────────────────────────────────┘                │
│                    ITERATE                                   │
└─────────────────────────────────────────────────────────────┘
```

### The Rules

1. **No code without a test plan**:  Every function has tests defined BEFORE implementation
2. **No commit without passing tests**: All tests must pass before GitHub push
3. **No phase advancement without gate validation**: Success criteria are non-negotiable
4. **Small, atomic commits**: Each commit does ONE thing
5. **Human validates, LLM implements**: You run tests and confirm behavior
6. **Tests are sacred**: Tests are NEVER modified to pass — code is modified to pass tests

### Complexity Management

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each file does ONE thing |
| **Shallow Modules** | No function longer than 50 lines |
| **Explicit over Implicit** | No magic, everything is obvious |
| **Fail Fast** | Errors surface immediately |
| **Log Everything** | Every action is traceable |
