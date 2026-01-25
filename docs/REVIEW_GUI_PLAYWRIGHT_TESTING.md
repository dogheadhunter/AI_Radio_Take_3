# Review GUI Playwright MCP Testing Checklist

This document provides a comprehensive checklist for testing the AI Radio Review GUI using the Playwright MCP server. Use this for manual exploration and validation of the interface.

## Prerequisites

Before testing, ensure:

- [ ] Streamlit is installed: `pip install streamlit`
- [ ] Sample data exists: Run `python scripts/create_sample_data_for_review.py`
- [ ] Review GUI can start: `python run_review_gui.py`
- [ ] Playwright MCP is available in your environment

## Test Setup

### 1. Start the Review GUI

```bash
# From project root
python run_review_gui.py
```

The GUI should start at `http://localhost:8501`

### 2. Using Playwright MCP

The Playwright MCP server allows you to:
- Navigate to pages (`playwright-browser_navigate`)
- Take screenshots (`playwright-browser_take_screenshot`)
- Get page snapshots (`playwright-browser_snapshot`)
- Click elements (`playwright-browser_click`)
- Fill forms (`playwright-browser_fill_form`)
- Evaluate JavaScript (`playwright-browser_evaluate`)

## Testing Checklist

### A. Initial Load & Layout ✓

**Test: GUI Loads Successfully**

- [ ] Navigate to `http://localhost:8501`
- [ ] Verify page title shows "🎙️ AI Radio Review GUI"
- [ ] Verify subtitle: "Manual review and approval system for generated scripts and audio"
- [ ] Take screenshot and verify layout looks correct
- [ ] Check no console errors appear

**Playwright MCP Commands:**
```
1. playwright-browser_navigate(url="http://localhost:8501")
2. playwright-browser_snapshot()
3. playwright-browser_take_screenshot(filename="review_gui_initial_load.png")
```

**Expected Result:**
- Main heading visible
- Sidebar with filters visible
- Statistics dashboard visible
- No JavaScript errors

---

### B. Sidebar Filters ✓

**Test: All Filter Controls Present**

- [ ] Verify "Filters" heading in sidebar
- [ ] Check "Content Type" dropdown exists
- [ ] Check "DJ" dropdown exists
- [ ] Check "Audit Status" dropdown exists
- [ ] Check "Review Status" dropdown exists
- [ ] Check "Search Item ID" textbox exists
- [ ] Check "Items per page" selector exists

**Playwright MCP Commands:**
```
1. playwright-browser_snapshot()
2. Look for: "Content Type", "DJ", "Audit Status", "Review Status"
3. Take screenshot of sidebar
```

**Expected Result:**
- All 6 filter controls visible
- Default values selected (All, All, All, All, "", 10)

**Test: Content Type Filter Works**

- [ ] Click Content Type dropdown
- [ ] Verify options: All, intros, outros, time, weather
- [ ] Select "intros"
- [ ] Verify "Filtered Items" count updates
- [ ] Verify only intro items shown

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="Content Type dropdown")
2. playwright-browser_snapshot()
3. playwright-browser_click(element="intros option")
4. playwright-browser_snapshot()
```

**Expected Result:**
- Dropdown shows all content types
- Filtered count changes when selection made
- Only relevant items displayed

**Test: DJ Filter Works**

- [ ] Click DJ dropdown
- [ ] Verify options: All, julie, mr_new_vegas
- [ ] Select "julie"
- [ ] Verify filtered count updates
- [ ] Verify only Julie items shown

**Expected Result:**
- Both DJs available
- Filtering works correctly

**Test: Search Function Works**

- [ ] Type item name in search box (e.g., "Louis_Armstrong")
- [ ] Verify filtered items match search
- [ ] Clear search
- [ ] Verify all items return

**Playwright MCP Commands:**
```
1. playwright-browser_type(element="Search Item ID", text="Louis_Armstrong")
2. Wait 1 second
3. playwright-browser_snapshot()
```

**Expected Result:**
- Search filters items in real-time
- Only matching items displayed

---

### C. Statistics Dashboard ✓

**Test: Statistics Display Correctly**

- [ ] Verify "Total Items" shows count
- [ ] Verify "Filtered Items" shows count
- [ ] Verify "Approved" count displayed
- [ ] Verify "Rejected" count displayed
- [ ] Verify counts are numeric
- [ ] Verify counts update when filters change

**Playwright MCP Commands:**
```
1. playwright-browser_snapshot()
2. Look for metric values under each label
```

**Expected Result:**
- All 4 statistics visible with numeric values
- Total Items = sum of all items
- Filtered Items ≤ Total Items
- Approved + Rejected ≤ Total Items

---

### D. Actions Section ✓

**Test: Action Buttons Present**

- [ ] Verify "🔄 Refresh" button in sidebar
- [ ] Verify "Regen Queue" metric shows count
- [ ] If queue > 0, verify "🗑️ Clear Queue" button appears

**Playwright MCP Commands:**
```
1. playwright-browser_snapshot()
2. Look for "🔄 Refresh" button
3. Look for "Regen Queue" metric
```

**Expected Result:**
- Refresh button always visible
- Queue counter shows number (0 or more)
- Clear button only visible when queue > 0

**Test: Refresh Button Works**

- [ ] Click "🔄 Refresh" button
- [ ] Verify page reloads
- [ ] Verify data refreshes

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="🔄 Refresh button")
2. Wait 2 seconds
3. playwright-browser_snapshot()
```

**Expected Result:**
- Page refreshes without errors
- Latest data displayed

---

### E. Review Items Display ✓

**Test: Item Cards Show Correctly**

For each visible item:

- [ ] Verify item heading (artist-song name or time/weather ID)
- [ ] Verify metadata shows: Type, DJ, Audit status, Review status
- [ ] Verify status indicators (🟢 = passed/approved, 🔴 = failed/rejected, ⚪ = pending)
- [ ] Verify version selector dropdown
- [ ] Verify script text area visible
- [ ] Verify audio player present
- [ ] Verify "Review Decision" expandable section

**Playwright MCP Commands:**
```
1. playwright-browser_snapshot()
2. Look for item headings (h3 elements)
3. Take screenshot of first item
```

**Expected Result:**
- Items displayed in card format
- All metadata visible
- Clear visual indicators for status

**Test: Version Selector Works**

- [ ] Find item with version selector
- [ ] Click version dropdown
- [ ] Select different version (if multiple exist)
- [ ] Verify script content changes
- [ ] Verify audio player updates

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="Version dropdown")
2. playwright-browser_snapshot()
3. playwright-browser_click(element="version 1" or "version 0")
4. Wait 1 second
5. playwright-browser_snapshot()
```

**Expected Result:**
- Version selector shows all available versions
- Changing version updates displayed content

**Test: Version Comparison (if multiple versions)**

- [ ] Expand "📊 Compare Versions" section
- [ ] Select version to compare
- [ ] Verify comparison text appears
- [ ] Verify different versions shown side-by-side

**Expected Result:**
- Comparison section only visible for items with multiple versions
- Clear display of differences

---

### F. Review Decision Section ✓

**Test: Review Decision Section Expands**

- [ ] Find "✏️ Review Decision" section
- [ ] Click to expand (if collapsed)
- [ ] Verify section expands
- [ ] Verify all controls appear

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="✏️ Review Decision")
2. Wait 500ms
3. playwright-browser_snapshot()
```

**Expected Result:**
- Section expands when clicked
- All review controls visible

**Test: Script Issues Selector**

- [ ] Verify "Script Issues" multiselect
- [ ] Click to open options
- [ ] Verify appropriate issues for content type shown
  - For intros/outros: Character voice, era, forbidden elements, flow, length, lyrics, facts
  - For time: Character voice, flow, length, incorrect time
  - For weather: Character voice, weather data, flow, length, facts
- [ ] Select 2-3 issues
- [ ] Verify selections appear

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="Script Issues multiselect")
2. playwright-browser_snapshot()
3. playwright-browser_click(element="Character voice mismatch")
4. playwright-browser_snapshot()
```

**Expected Result:**
- Correct issue options for content type
- Multiple selections possible
- Selections tracked

**Test: Audio Issues Selector**

- [ ] Verify "Audio Issues" multiselect
- [ ] Click to open options
- [ ] Verify audio issues: garbled, wrong voice, mispronunciation, pacing, volume, artifacts, intonation
- [ ] Select 1-2 issues
- [ ] Verify selections appear

**Expected Result:**
- All audio issue options available
- Multiple selections work

**Test: Reviewer Notes**

- [ ] Verify "Reviewer Notes" text area
- [ ] Type test notes
- [ ] Verify text appears in field

**Playwright MCP Commands:**
```
1. playwright-browser_type(element="Reviewer Notes", text="Test review notes")
2. playwright-browser_snapshot()
```

**Expected Result:**
- Notes field accepts text input
- Text persists

---

### G. Review Actions ✓

**Test: Approve Button**

- [ ] Scroll to action buttons
- [ ] Click "✅ Approve" button
- [ ] Verify success message appears
- [ ] Verify review status updates to 🟢 (approved)
- [ ] Verify review decision collapses
- [ ] Refresh page
- [ ] Verify approval persists

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="✅ Approve button")
2. Wait 1 second
3. playwright-browser_snapshot()
4. playwright-browser_navigate(url="http://localhost:8501")
5. Wait for load
6. playwright-browser_snapshot()
```

**Expected Result:**
- Success message shows
- Status changes immediately
- Approval persists after refresh

**Test: Reject Button**

- [ ] Find pending item
- [ ] Select script/audio issues
- [ ] Add reviewer notes
- [ ] Click "❌ Reject" button
- [ ] Verify error message (red) appears
- [ ] Verify review status updates to 🔴 (rejected)
- [ ] Refresh page
- [ ] Verify rejection persists

**Expected Result:**
- Rejection saved successfully
- Status updates correctly
- Data persists

**Test: Regen Script Button**

- [ ] Find item with issues
- [ ] Add feedback in notes
- [ ] Click "🔄 Regen Script" button
- [ ] Verify "Added to regeneration queue" message
- [ ] Check sidebar "Regen Queue" count increases

**Playwright MCP Commands:**
```
1. playwright-browser_type(element="Reviewer Notes", text="Script needs improvement")
2. playwright-browser_click(element="🔄 Regen Script button")
3. Wait 1 second
4. playwright-browser_snapshot()
5. Check Regen Queue counter
```

**Expected Result:**
- Item added to queue
- Queue counter increments
- Success message shown

**Test: Regen Audio Button**

- [ ] Find item
- [ ] Add audio issue feedback
- [ ] Click "🔊 Regen Audio" button
- [ ] Verify added to queue
- [ ] Verify queue count increases

**Expected Result:**
- Audio-only regeneration queued
- Queue counter updates

**Test: Regen Both Button**

- [ ] Find item with multiple issues
- [ ] Add script and audio issues
- [ ] Click "🔄🔊 Regen Both" button
- [ ] Verify added to queue
- [ ] Verify queue count increases

**Expected Result:**
- Both script and audio queued
- Queue counter updates

---

### H. Pagination ✓

**Test: Pagination Controls**

- [ ] Verify "Page X of Y" indicator
- [ ] If total items > items per page:
  - [ ] Verify "Next ➡️" button enabled
  - [ ] Click Next
  - [ ] Verify page number increases
  - [ ] Verify different items shown
  - [ ] Verify "⬅️ Previous" button becomes enabled
  - [ ] Click Previous
  - [ ] Verify returns to first page

**Playwright MCP Commands:**
```
1. playwright-browser_snapshot()
2. playwright-browser_click(element="Next ➡️ button")
3. Wait 500ms
4. playwright-browser_snapshot()
5. playwright-browser_click(element="⬅️ Previous button")
6. Wait 500ms
7. playwright-browser_snapshot()
```

**Expected Result:**
- Pagination works correctly
- Buttons enable/disable appropriately
- Page indicator updates

**Test: Items Per Page**

- [ ] Click "Items per page" dropdown
- [ ] Select 5
- [ ] Verify only 5 items shown per page
- [ ] Verify pagination updates
- [ ] Select 20
- [ ] Verify 20 items shown

**Expected Result:**
- Items per page setting works
- Pagination recalculates correctly

---

### I. CSV Export ✓

**Test: CSV Export Button**

- [ ] Verify "📥 Export Reviews to CSV" button visible (when items exist)
- [ ] Click export button
- [ ] Verify download initiates
- [ ] Open downloaded CSV
- [ ] Verify columns: content_type, dj, item_id, latest_version, audit_status, review_status, reviewed_at, script_issues, audio_issues, reviewer_notes
- [ ] Verify data matches displayed items

**Playwright MCP Commands:**
```
1. playwright-browser_snapshot()
2. playwright-browser_click(element="📥 Export Reviews to CSV")
3. Wait for download
```

**Expected Result:**
- CSV downloads successfully
- Contains all review data
- Properly formatted

---

### J. Queue Management ✓

**Test: View Queue Status**

- [ ] After adding items to queue
- [ ] Verify "Regen Queue" counter shows correct count
- [ ] Verify "🗑️ Clear Queue" button appears

**Test: Clear Queue**

- [ ] With items in queue
- [ ] Click "🗑️ Clear Queue" button
- [ ] Verify confirmation or immediate clear
- [ ] Verify queue count returns to 0
- [ ] Verify clear button disappears

**Playwright MCP Commands:**
```
1. playwright-browser_click(element="🗑️ Clear Queue button")
2. Wait 1 second
3. playwright-browser_snapshot()
```

**Expected Result:**
- Queue clears successfully
- UI updates immediately

---

### K. Edge Cases & Error Handling ✓

**Test: No Items Scenario**

- [ ] Remove or rename data/generated directory
- [ ] Refresh GUI
- [ ] Verify "No items found" message
- [ ] Verify no errors displayed
- [ ] Verify filters still functional

**Expected Result:**
- Graceful handling of empty state
- Helpful message displayed

**Test: Corrupted Data**

- [ ] Create invalid review_status.json file
- [ ] Refresh GUI
- [ ] Verify graceful error handling
- [ ] Verify other items still load

**Expected Result:**
- Individual item errors don't crash GUI
- Error logged but interface continues

**Test: Filter Combination**

- [ ] Apply multiple filters simultaneously
  - Content Type = "intros"
  - DJ = "julie"
  - Audit Status = "Passed"
  - Review Status = "Pending"
- [ ] Verify filters work together (AND logic)
- [ ] Verify correct count shown

**Expected Result:**
- Multiple filters combine correctly
- Results match all criteria

---

### L. Responsive Design ✓

**Test: Desktop View (1920x1080)**

- [ ] Resize browser to 1920x1080
- [ ] Verify layout looks good
- [ ] Verify sidebar and main content balanced
- [ ] Take screenshot

**Playwright MCP Commands:**
```
1. playwright-browser_resize(width=1920, height=1080)
2. playwright-browser_take_screenshot(filename="desktop_view.png")
```

**Test: Tablet View (768x1024)**

- [ ] Resize browser to 768x1024
- [ ] Verify layout adapts
- [ ] Verify all controls accessible
- [ ] Take screenshot

**Playwright MCP Commands:**
```
1. playwright-browser_resize(width=768, height=1024)
2. playwright-browser_take_screenshot(filename="tablet_view.png")
```

**Expected Result:**
- Interface usable at different sizes
- No horizontal scrolling required

---

### M. Performance & Load Testing ✓

**Test: Load with Many Items**

- [ ] Generate 50+ sample items
- [ ] Reload GUI
- [ ] Verify loads in reasonable time (<5 seconds)
- [ ] Verify pagination works smoothly
- [ ] Verify filtering responsive

**Expected Result:**
- GUI handles larger datasets
- No performance degradation

**Test: Rapid Filter Changes**

- [ ] Quickly change filters multiple times
- [ ] Verify UI stays responsive
- [ ] Verify no crashes or errors

**Expected Result:**
- Smooth interaction
- No race conditions

---

## Test Results Summary Template

After completing tests, fill out:

```markdown
## Test Session: [Date/Time]

### Environment
- Browser: [Chrome/Firefox/Safari]
- OS: [Windows/Mac/Linux]
- Python: [version]
- Streamlit: [version]

### Results

| Test Category | Tests Passed | Tests Failed | Notes |
|---------------|--------------|--------------|-------|
| Initial Load | X/Y | | |
| Filters | X/Y | | |
| Statistics | X/Y | | |
| Review Items | X/Y | | |
| Review Actions | X/Y | | |
| Pagination | X/Y | | |
| CSV Export | X/Y | | |
| Queue Management | X/Y | | |
| Edge Cases | X/Y | | |
| Responsive | X/Y | | |

### Issues Found
1. [Description]
2. [Description]

### Screenshots
- [Link to screenshot 1]
- [Link to screenshot 2]
```

---

## Automation Tips

For automated testing with Playwright MCP:

1. **Create test script**:
   ```python
   # Use playwright-browser_navigate, snapshot, click, etc.
   ```

2. **Take screenshots at key points** for documentation

3. **Save page snapshots** for later analysis

4. **Test in multiple browsers**: Chrome, Firefox, Safari

5. **Run tests in both headless and headed modes**

---

## Troubleshooting

### Streamlit Won't Start
- Check port 8501 not in use: `lsof -i :8501`
- Try different port: `streamlit run review_gui.py --server.port=8502`

### Playwright Can't Connect
- Verify Streamlit running: `curl http://localhost:8501`
- Check firewall settings
- Ensure Playwright browsers installed: `playwright install`

### Tests Fail Intermittently
- Increase wait times for Streamlit to render
- Use `wait_for_selector` instead of fixed sleeps
- Check for race conditions in data loading

---

## Next Steps

After completing manual testing:

1. **Document findings** in test results template
2. **File issues** for any bugs found
3. **Update automated tests** based on findings
4. **Share screenshots** with team
5. **Sign off** on feature readiness

