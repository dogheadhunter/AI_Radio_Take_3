# Review GUI Test Checklist

This document provides a comprehensive checklist for manual and automated testing of the AI Radio Review GUI introduced in PR #11.

## Purpose

The Copilot agent couldn't run Streamlit during development due to firewall restrictions, so the GUI needs thorough manual testing. This checklist covers all acceptance criteria and critical functionality.

---

## Running the Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Create sample data (optional):**
   ```bash
   python scripts/create_sample_data_for_review.py
   ```

### Manual Testing

1. **Start the Review GUI:**
   ```bash
   python run_review_gui.py
   ```
   GUI should be accessible at `http://localhost:8501`

2. **Follow the checklist items below** one by one

### Automated Testing with Playwright

1. **Ensure GUI is running** on `http://localhost:8501`

2. **Run Playwright E2E tests:**
   ```bash
   pytest tests/e2e/test_review_gui.py -v
   ```

3. **Run with visible browser (headed mode):**
   ```bash
   pytest tests/e2e/test_review_gui.py -v --headed
   ```

### With Playwright MCP Server

If using Copilot with Playwright MCP:
1. Ensure GUI is running on `http://localhost:8501`
2. Use MCP to navigate and interact with the page
3. Follow the checklist items one by one
4. Take screenshots for documentation

---

## Test Checklist

### 1. Core Functionality

#### GUI Launch
- [ ] GUI launches without errors (`python run_review_gui.py`)
- [ ] Page loads at `http://localhost:8501`
- [ ] Title displays: "🎙️ AI Radio Review GUI"
- [ ] Subtitle displays: "Manual review and approval system for generated scripts and audio"
- [ ] No console errors in browser developer tools
- [ ] No Python errors in terminal

#### Review Tab - Content Display
- [ ] Review tab displays list of generated content
- [ ] Items show correct metadata (Type, DJ, Audit Status, Review Status)
- [ ] Status indicators display correctly:
  - 🟢 for passed/approved
  - 🔴 for failed/rejected
  - ⚪ for pending
- [ ] Item headings show correct format (artist-song or time/weather ID)

#### Audio Player
- [ ] Audio player is visible for each content item
- [ ] Audio player plays generated audio files
- [ ] Audio controls work (play, pause, seek)
- [ ] Audio loads without errors
- [ ] Multiple audio players can play independently

#### Script Editor
- [ ] Script text displays correctly in editor
- [ ] Text area is editable
- [ ] Script content matches the selected version
- [ ] Text wrapping works properly
- [ ] Font is readable

#### Filters
- [ ] **Content Type filter** works:
  - [ ] Dropdown shows: All, intros, outros, time, weather
  - [ ] Selecting "intros" shows only intro items
  - [ ] Selecting "outros" shows only outro items
  - [ ] Selecting "time" shows only time announcements
  - [ ] Selecting "weather" shows only weather reports
  - [ ] Selecting "All" shows all items
- [ ] **DJ filter** works:
  - [ ] Dropdown shows: All, julie, mr_new_vegas
  - [ ] Selecting "julie" shows only Julie's content
  - [ ] Selecting "mr_new_vegas" shows only Mr. New Vegas content
  - [ ] Selecting "All" shows both DJs
- [ ] **Audit Status filter** works:
  - [ ] Options: All, Passed, Failed
  - [ ] Filtering updates item list correctly
- [ ] **Review Status filter** works:
  - [ ] Options: All, Pending, Approved, Rejected
  - [ ] Filtering updates item list correctly
- [ ] **Multiple filters** work together (AND logic)
- [ ] **Statistics update** when filters change

#### Pagination
- [ ] Pagination controls are visible
- [ ] "Page X of Y" indicator shows correct values
- [ ] "Next ➡️" button works
- [ ] "⬅️ Previous" button works
- [ ] Buttons enable/disable appropriately
- [ ] Items per page selector works (5, 10, 20, 50)
- [ ] Changing items per page updates display correctly

#### Search
- [ ] Search by item ID/song name works
- [ ] Search field is visible
- [ ] Typing filters items in real-time
- [ ] Clearing search shows all items again
- [ ] Search is case-insensitive
- [ ] Partial matches work

---

### 2. Regeneration (Critical - Must Use API) ⚠️

**IMPORTANT**: All regeneration must go through the API layer, NOT direct pipeline calls.

#### Regenerate Script Button
- [ ] "🔄 Regenerate Script" button is visible
- [ ] Clicking button triggers generation via API
- [ ] **Check logs for "Regenerating via API"** (not direct pipeline)
- [ ] Regeneration goes through full pipeline:
  - [ ] Fetches lyrics from catalog
  - [ ] Validates script content
  - [ ] Runs audit process
- [ ] After regeneration, new version appears in version selector
- [ ] Success message is displayed
- [ ] Item is added to regeneration queue

#### Regenerate Audio Button
- [ ] "🔊 Regenerate Audio" button is visible
- [ ] Clicking button generates new audio from current script
- [ ] Audio regeneration preserves script content
- [ ] New audio file is created
- [ ] Audio player updates to new file
- [ ] Success message is displayed

#### Regenerate Both Button
- [ ] "🔄🔊 Regenerate Both" button is visible
- [ ] Clicking button regenerates both script and audio
- [ ] Script regeneration happens first
- [ ] Audio generation follows script regeneration
- [ ] Both files are updated
- [ ] Success message is displayed

#### API Integration Verification (Critical)
- [ ] **No direct imports** of `GenerationPipeline` or `ValidatedGenerationPipeline` in `review_gui.py`
- [ ] All generation calls go through `gui_backend.regenerate_content()`
- [ ] Logs show **"Regenerating via API"** not direct pipeline calls
- [ ] Check `review_gui.py` imports:
  ```python
  # Should see:
  from src.ai_radio.gui import backend as gui_backend
  
  # Should NOT see:
  # from src.ai_radio.generation.pipeline import GenerationPipeline
  # from src.ai_radio.generation.pipeline import ValidatedGenerationPipeline
  ```

---

### 3. Manual Editing & Version History

#### Edit Script Text
- [ ] Can edit script text in the text area
- [ ] Text area accepts keyboard input
- [ ] Can select, cut, copy, paste text
- [ ] Changes are visible immediately

#### Save Edited Script
- [ ] "Save Edit" or "Regenerate Audio from Edit" button is visible
- [ ] Clicking save creates a NEW version file
- [ ] New version follows naming pattern:
  - If `julie_0.txt` existed, creates `julie_1.txt`
  - If `julie_1.txt` existed, creates `julie_2.txt`
- [ ] Old versions are preserved (not overwritten)
- [ ] File permissions are correct
- [ ] Timestamp is updated

#### Version Selector
- [ ] Version selector dropdown is visible
- [ ] Dropdown shows all available versions
- [ ] Can switch between versions
- [ ] Switching versions updates displayed script
- [ ] Switching versions updates audio player (if audio exists)
- [ ] Current version is highlighted/selected

#### Regenerate Audio from Edit
- [ ] "Regenerate Audio from Edit" button works
- [ ] Creates audio file from manually edited text
- [ ] Uses current script text (not regenerated)
- [ ] Audio matches edited script content
- [ ] New audio version is created

---

### 4. Side-by-Side Diff

#### Diff Comparison Section
- [ ] Diff comparison section is visible
- [ ] Section can be expanded/collapsed
- [ ] Heading is clear (e.g., "📊 Compare Versions")

#### Version Comparison Selector
- [ ] Can select a previous version to compare against
- [ ] Dropdown shows available versions
- [ ] Current version is excluded from comparison list

#### Diff Display - Additions
- [ ] Additions shown in **green highlighting**
- [ ] Added text is clearly visible
- [ ] Color contrast is sufficient
- [ ] Added lines/words are marked

#### Diff Display - Deletions
- [ ] Deletions shown in **red highlighting**
- [ ] Deleted text is clearly visible
- [ ] Color contrast is sufficient
- [ ] Deleted lines/words are marked

#### Diff Modes
- [ ] **Inline diff mode** works (for mobile):
  - [ ] Shows changes in single column
  - [ ] Additions and deletions inline
  - [ ] Readable on narrow screens
- [ ] **Table/side-by-side diff mode** works (for desktop):
  - [ ] Shows old version on left
  - [ ] Shows new version on right
  - [ ] Aligned by lines
  - [ ] Clear visual separation

---

### 5. Catalog Browser

#### Catalog Tab
- [ ] Catalog tab is accessible
- [ ] Tab switches from Review to Catalog view
- [ ] Catalog tab shows list of songs
- [ ] Song list loads without errors

#### Search & Filter
- [ ] Search by artist name works
- [ ] Search by song title works
- [ ] Search is case-insensitive
- [ ] Partial matches work
- [ ] Clearing search shows all songs

#### Generation Status Display
- [ ] Each song shows generation status
- [ ] **Intro status** shows correctly:
  - ✅ if intro generated
  - ❌ if intro not generated
- [ ] **Outro status** shows correctly:
  - ✅ if outro generated
  - ❌ if outro not generated
- [ ] Status updates when content is generated

#### Lyrics Display
- [ ] Lyrics display for each song
- [ ] Lyrics are readable
- [ ] Lyrics section can expand/collapse
- [ ] Lyrics formatting is preserved

#### Jump to Review
- [ ] "Jump to Review" button is visible for generated content
- [ ] Clicking button navigates to Review tab
- [ ] Correct item is shown/selected in Review tab
- [ ] Navigation is smooth

#### Side-by-Side Comparison
- [ ] Lyrics and script comparison section works
- [ ] Lyrics shown on one side
- [ ] Generated script shown on other side
- [ ] Can compare intro script with lyrics
- [ ] Can compare outro script with lyrics
- [ ] Helps verify accuracy

---

### 6. Mobile Experience (via Tailscale)

#### Mobile Browser Loading
- [ ] GUI loads on mobile browser
- [ ] No layout breaking
- [ ] All sections accessible

#### Touch Targets
- [ ] Buttons are large enough (minimum 48px)
- [ ] Touch targets don't overlap
- [ ] Easy to tap buttons without mistakes
- [ ] Dropdowns work with touch

#### Audio Player on Mobile
- [ ] Audio player is usable on mobile
- [ ] Play/pause button works
- [ ] Seek bar works with touch
- [ ] Volume controls work (if visible)

#### Script Editing on Mobile
- [ ] Text area is usable on mobile
- [ ] Can edit text with mobile keyboard
- [ ] Selection works
- [ ] No layout shifting when keyboard appears

#### Navigation on Mobile
- [ ] Tabs work on mobile
- [ ] Sidebar accessible (may be collapsible)
- [ ] Scrolling works smoothly
- [ ] Pagination works

#### Collapsible Sections
- [ ] Expandable sections work on mobile
- [ ] Tapping expands/collapses correctly
- [ ] No double-tap delays
- [ ] Smooth animations

---

### 7. Statistics & Actions

#### Statistics Dashboard
- [ ] "Total Items" shows correct count
- [ ] "Filtered Items" shows correct count
- [ ] "Approved" count is accurate
- [ ] "Rejected" count is accurate
- [ ] Statistics update when filters change
- [ ] Statistics update after review actions

#### Refresh Button
- [ ] "🔄 Refresh" button is visible
- [ ] Clicking refreshes data from disk
- [ ] No errors on refresh
- [ ] Current filters are preserved (or reset)

#### Regeneration Queue
- [ ] "Regen Queue" counter shows count
- [ ] Count increases when items added to queue
- [ ] Count decreases when queue is processed
- [ ] "🗑️ Clear Queue" button appears when queue > 0
- [ ] Clicking clear queue empties the queue
- [ ] Queue file is updated correctly

---

### 8. Review Decision Workflow

#### Review Decision Section
- [ ] "✏️ Review Decision" section is visible
- [ ] Section can expand/collapse
- [ ] All controls appear when expanded

#### Script Issues Selector
- [ ] "Script Issues" multiselect is visible
- [ ] Can select multiple issues
- [ ] Issues appropriate for content type:
  - **Intros/Outros**: Character voice, era, forbidden elements, flow, length, lyrics, facts
  - **Time**: Character voice, flow, length, incorrect time
  - **Weather**: Character voice, weather data, flow, length, facts

#### Audio Issues Selector
- [ ] "Audio Issues" multiselect is visible
- [ ] Can select multiple issues
- [ ] Issues available: garbled, wrong voice, mispronunciation, pacing, volume, artifacts, intonation

#### Reviewer Notes
- [ ] "Reviewer Notes" text area is visible
- [ ] Can type notes
- [ ] Notes are saved with review
- [ ] Notes are preserved on page refresh

#### Approve Action
- [ ] "✅ Approve" button is visible
- [ ] Clicking approves the item
- [ ] Success message appears (green)
- [ ] Review status updates to 🟢 Approved
- [ ] Status persists after page refresh
- [ ] Timestamp is recorded

#### Reject Action
- [ ] "❌ Reject" button is visible
- [ ] Can select issues before rejecting
- [ ] Clicking rejects the item
- [ ] Error/info message appears (red)
- [ ] Review status updates to 🔴 Rejected
- [ ] Issues and notes are saved
- [ ] Status persists after page refresh

---

### 9. CSV Export

#### Export Button
- [ ] "📥 Export Reviews to CSV" button is visible
- [ ] Button only appears when items exist
- [ ] Clicking triggers download

#### CSV File Content
- [ ] CSV file downloads successfully
- [ ] File has correct headers:
  - content_type
  - dj
  - item_id
  - latest_version
  - audit_status
  - review_status
  - reviewed_at
  - script_issues
  - audio_issues
  - reviewer_notes
- [ ] Data matches displayed items
- [ ] All filtered items included in export
- [ ] CSV is well-formed (no broken lines)
- [ ] Can open in Excel/Google Sheets

---

### 10. Error Handling & Edge Cases

#### No Content
- [ ] If no generated content exists, shows helpful message
- [ ] No errors displayed
- [ ] Filters still work (show empty results)

#### Missing Files
- [ ] If script file missing, graceful error message
- [ ] If audio file missing, graceful error message
- [ ] Other items still display correctly

#### Corrupted Data
- [ ] If review_status.json corrupted, recovers gracefully
- [ ] If audit JSON corrupted, shows appropriate error
- [ ] Application doesn't crash

#### Network/Service Errors
- [ ] If Ollama unavailable during regen, shows error message
- [ ] If TTS service down, shows error message
- [ ] User can continue using other features

---

### 11. Performance

#### Load Time
- [ ] GUI loads in < 5 seconds with typical data (~100 items)
- [ ] GUI loads in < 10 seconds with large data (~500 items)
- [ ] No timeout errors

#### Filter Responsiveness
- [ ] Filters update instantly (< 500ms)
- [ ] No lag when changing filters
- [ ] No freeze when applying multiple filters

#### Pagination Performance
- [ ] Page changes are fast (< 300ms)
- [ ] No delay when clicking next/previous
- [ ] Large page sizes (50+ items) still performant

---

## Test Results Template

After completing tests, document results:

```markdown
## Test Session: [Date/Time]

### Environment
- OS: [Windows/Mac/Linux]
- Browser: [Chrome/Firefox/Safari] [Version]
- Python: [version]
- Streamlit: [version]

### Test Results

| Category | Passed | Failed | Notes |
|----------|--------|--------|-------|
| Core Functionality | X/Y | | |
| Regeneration (API) | X/Y | | |
| Manual Editing & Versions | X/Y | | |
| Side-by-Side Diff | X/Y | | |
| Catalog Browser | X/Y | | |
| Mobile Experience | X/Y | | |
| Statistics & Actions | X/Y | | |
| Review Decision | X/Y | | |
| CSV Export | X/Y | | |
| Error Handling | X/Y | | |
| Performance | X/Y | | |

### Critical Issues Found
1. [Issue description]
2. [Issue description]

### Minor Issues Found
1. [Issue description]
2. [Issue description]

### Screenshots
- [Link or path to screenshot 1]
- [Link or path to screenshot 2]

### Overall Assessment
[ ] Ready for production
[ ] Minor fixes needed
[ ] Major fixes needed

### Sign-off
Tested by: [Name]
Date: [Date]
```

---

## Playwright MCP Testing

For automated exploration with Playwright MCP:

### Navigation
```
playwright-browser_navigate(url="http://localhost:8501")
playwright-browser_snapshot()
```

### Take Screenshots
```
playwright-browser_take_screenshot(filename="review_gui_main.png")
playwright-browser_take_screenshot(filename="catalog_tab.png")
```

### Interact with Elements
```
playwright-browser_click(element="Content Type dropdown", ref="...")
playwright-browser_type(element="Search box", text="Louis Armstrong", ref="...")
```

### Check for Errors
```
playwright-browser_console_messages()
```

---

## Acceptance Criteria from Issue #10

This checklist covers all acceptance criteria:

- ✅ GUI launches without errors
- ✅ Review tab displays content list
- ✅ Audio player works
- ✅ Script editing works
- ✅ Filters work (all types)
- ✅ Pagination works
- ✅ Search works
- ✅ Regeneration uses API (critical)
- ✅ Version history works
- ✅ Diff comparison works
- ✅ Catalog browser works
- ✅ Mobile experience tested
- ✅ API integration verified

---

## Next Steps

1. Complete manual testing following this checklist
2. Run automated Playwright tests
3. Document all findings
4. File issues for any bugs
5. Get sign-off from stakeholders
6. Deploy to production

---

## Troubleshooting

### Streamlit won't start
```bash
# Check if port is in use
lsof -i :8501
# Kill process if needed
kill -9 [PID]
# Try different port
streamlit run review_gui.py --server.port=8502
```

### Playwright tests fail
```bash
# Reinstall browsers
playwright install --force
# Check Streamlit is running
curl http://localhost:8501
```

### Import errors
```bash
# Ensure in project root
cd /path/to/AI_Radio_Take_3
# Reinstall dependencies
pip install -r requirements.txt
```
