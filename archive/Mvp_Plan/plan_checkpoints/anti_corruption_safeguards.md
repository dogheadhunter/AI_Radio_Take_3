# Anti-Corruption Safeguards

## Anti-Corruption Safeguards

### The Problem with LLM-Generated Code
LLMs can: 
- Generate code that looks correct but doesn't work
- Modify tests to make them pass instead of fixing code
- Lose context mid-conversation and generate inconsistent code
- Create subtle bugs that surface later
- Over-engineer simple solutions

### Safeguard System

#### 1. Test Immutability Rule
```
┌─────────────────────────────────────────────────────────────┐
│                    TEST IMMUTABILITY                         │
│                                                              │
│  Once a test is written and committed:                        │
│                                                              │
│  ✅ ALLOWED: Add new tests                                   │
│  ✅ ALLOWED: Add more assertions to existing tests           │
│  ❌ FORBIDDEN: Weaken assertions                             │
│  ❌ FORBIDDEN: Remove tests                                  │
│  ❌ FORBIDDEN: Change expected values to match wrong output  │
│                                                              │
│  Exception: Bug in test logic (requires human approval)      │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Human Validation Checkpoints
At every checkpoint, YOU (the human) must:
1. Run all tests yourself:  `pytest -v`
2. Manually verify ONE behavior works as expected
3. Review the git diff before committing
4. Confirm the output makes sense

#### 3. Regression Prevention
```
┌───────────────────────────────────��─────────────────────────┐
│                 REGRESSION PREVENTION                        │
│                                                              │
│  Before EVERY commit:                                        │
│                                                              │
│  1. Run: pytest --tb=short                                   │
│  2. ALL tests must pass (not just new ones)                  │
│  3. No warnings in test output                               │
│  4. Coverage must not decrease                               │
│                                                              │
│  If any test fails:                                           │
│  → DO NOT COMMIT                                             │
│  → Fix the code (not the test)                               │
│  → Re-run all tests                                          │
└─────────────────────────────────────────────────────────────┘
```

#### 4. Context Anchoring
Every coding session starts with: 
1. Read this roadmap document
2. Read the current phase's specification
3. Run all existing tests to confirm baseline
4. Review the last 3 commits to understand recent changes

#### 5. Validation Artifacts
Each checkpoint produces artifacts that prove success:
- Screenshot of passing tests
- Log file showing expected behavior
- Manual test result documentation
