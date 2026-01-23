# Phase 2 Overview

## Phase 2: Content Generation Pipeline

### Overview
| Attribute | Value |
|-----------|-------|
| **Goal** | LLM and TTS integration for generating DJ content |
| **Duration** | 3-4 sessions |
| **Complexity** | High |
| **Dependencies** | Phase 0 complete, Phase 1 helpful but not required |

### Important Note on Testing
LLM and TTS are external services.  Tests must: 
- Use mocking for unit tests
- Have separate integration tests that call real services
- Never depend on specific LLM output (it's non-deterministic)
