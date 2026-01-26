# Documentation Index

This directory contains all project documentation. Documents are categorized by current status.

## 📌 Essential Documents (Start Here)

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | **System architecture overview** - modular pipeline design |
| [LLM_CONTEXT.md](LLM_CONTEXT.md) | **LLM-optimized context** - for AI assistants and context windows |

## 🧪 Testing Documentation

| Document | Description |
|----------|-------------|
| [../tests/TESTING_MODES.md](../tests/TESTING_MODES.md) | Testing modes (mock vs integration) |
| [TESTING_QUICK_REF.md](TESTING_QUICK_REF.md) | Quick reference for testing commands |
| [MOCK_TESTING_SETUP.md](MOCK_TESTING_SETUP.md) | Mock testing implementation details |

## 🔧 Setup & Configuration

| Document | Description |
|----------|-------------|
| [setup_services.md](setup_services.md) | Ollama and TTS service setup |
| [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md) | Remote access configuration |

## 🎛️ Optional: Review GUI (Streamlit)

> **Note**: The Review GUI is an **optional** Streamlit interface for manual content review. 
> It is not required for core pipeline operation.

| Document | Description |
|----------|-------------|
| [gui/REVIEW_GUI.md](gui/REVIEW_GUI.md) | Review GUI documentation |
| [gui/REVIEW_GUI_TESTING.md](gui/REVIEW_GUI_TESTING.md) | GUI testing guide |
| [gui/REVIEW_GUI_PLAYWRIGHT_TESTING.md](gui/REVIEW_GUI_PLAYWRIGHT_TESTING.md) | Playwright E2E tests |
| [gui/SONG_EDITOR.md](gui/SONG_EDITOR.md) | Song editor component |
| [MOBILE_REVIEW_UI.md](MOBILE_REVIEW_UI.md) | Mobile-optimized UI notes |

## 📊 Script Improvement (Reference)

> **Note**: These documents describe the script generation and quality validation process.
> Most relevant content is now in [ARCHITECTURE.md](ARCHITECTURE.md).

| Document | Description |
|----------|-------------|
| [script_improvement/PIPELINE_ARCHITECTURE.md](script_improvement/PIPELINE_ARCHITECTURE.md) | Legacy pipeline architecture |
| [script_improvement/PIPELINE_QUICK_REF.md](script_improvement/PIPELINE_QUICK_REF.md) | Quick reference for pipeline |
| [script_improvement/PROMPT_ARCHITECTURE.md](script_improvement/PROMPT_ARCHITECTURE.md) | Prompt engineering design |
| [script_improvement/STYLE_GUIDE_JULIE.md](script_improvement/STYLE_GUIDE_JULIE.md) | Julie DJ personality guide |
| [script_improvement/STYLE_GUIDE_MR_NEW_VEGAS.md](script_improvement/STYLE_GUIDE_MR_NEW_VEGAS.md) | Mr. New Vegas personality guide |
| [script_improvement/AUDIT_CRITERIA.md](script_improvement/AUDIT_CRITERIA.md) | Script audit criteria |
| [script_improvement/AUDITOR_VALIDATION.md](script_improvement/AUDITOR_VALIDATION.md) | Auditor validation process |
| [script_improvement/AUDIT_HUMAN_REVIEW.md](script_improvement/AUDIT_HUMAN_REVIEW.md) | Human review process |

## 🗄️ Archived Documentation

See [`../archive/`](../archive/) for historical documentation including:
- `Script_Improvement_Plan/` - Phase 1-6 improvement plan (completed)
- `Mvp_Plan/` - Original MVP planning documents

## Quick Navigation

**For Developers:**
1. Start with [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
2. See [../README.md](../README.md) for setup and CLI usage
3. Check [../tests/TESTING_MODES.md](../tests/TESTING_MODES.md) for testing

**For LLM Assistants:**
1. Load [LLM_CONTEXT.md](LLM_CONTEXT.md) at session start
2. Reference [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture

**For Content Review:**
1. See [REVIEW_GUI.md](REVIEW_GUI.md) for the optional Streamlit interface
