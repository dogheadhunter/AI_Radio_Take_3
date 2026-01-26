# Mobile-Optimized Review GUI

This document describes the mobile-first UX/UI improvements made to the AI Radio Review GUI for optimal phone usage.

## Key Design Principles

### 1. Audio-First Layout
- **Audio is the primary content** - moved to the top of each review card
- Prominent audio player with large touch targets (54px+ height)
- Dual audio support (30sec/Full) uses tabs instead of side-by-side layout

### 2. Touch-Friendly Elements
- All buttons have minimum 48px touch targets
- Buttons include visual feedback on tap (scale animation)
- Larger text areas for comfortable editing
- Increased spacing between interactive elements

### 3. Single-Column Mobile Layout
- Side-by-side layouts automatically stack vertically on mobile
- Content sections are collapsible (expanders) to reduce scrolling
- Reference materials collapsed by default to prioritize the main content

### 4. Prominent Actions
- **APPROVE/REJECT buttons** are large and color-coded
- Quick save button appears immediately when changes are detected
- Regeneration buttons use full-width layout on mobile

### 5. Smart Navigation
- Pagination controls at **both top and bottom** of the page
- Page jump hidden in expander to reduce clutter
- Progress bar shows review completion at a glance
- Sidebar starts collapsed on mobile (swipe to reveal)

## Mobile UX Features

### Review Workflow on Phone

1. **Open sidebar** (swipe from left or tap hamburger)
2. **Set filters** to focus on specific content
3. **Collapse sidebar** to maximize review area
4. **Listen to audio** first (always visible at top)
5. **Read script** in expandable section
6. **Select issues** using tabbed interface (Script/Audio)
7. **Tap APPROVE or REJECT** with large buttons
8. **Navigate** using bottom pagination

### Status Indicators

Visual status pills with color coding:
- 🟢 **Approved** - Green background
- 🔴 **Rejected** - Red background  
- 🟡 **Pending** - Yellow background
- 🔵 **Passed** (audit) - Blue background
- 🟣 **Failed** (audit) - Pink background

### Unsaved Changes Warning

When editing a script on mobile:
- Yellow warning bar appears below text area
- Large "SAVE CHANGES" button (full width, primary style)
- Visual feedback on successful save

## CSS Breakpoints

| Breakpoint | Device | Layout |
|------------|--------|--------|
| < 768px | Phone | Single column, stacked layout |
| 768-1024px | Tablet | Adaptive 2-column where appropriate |
| > 1024px | Desktop | Full multi-column layout |

## Accessibility Features

- High contrast status badges
- Large tap targets (48px minimum)
- Clear visual hierarchy with headers
- Color + icon indicators (not color-alone)
- Touch-action optimizations for smooth scrolling

## Performance Considerations

- Audio loaded on-demand (base64 inline)
- Collapsible sections reduce initial render
- Pagination limits items per page (1-20)
- Session state preserves position across refreshes

## Testing on Mobile

### Method 1: Chrome DevTools
1. Open Review GUI in Chrome
2. Press F12 → Toggle Device Toolbar (Ctrl+Shift+M)
3. Select iPhone or Android preset

### Method 2: Tailscale Remote Access
See [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md) for accessing from your phone on the same network.

### Method 3: Streamlit Cloud
Deploy to Streamlit Cloud for public URL access from any device.

## Configuration Options

### Items Per Page
Mobile-optimized options: 1, 3, 5, 10, 20
- Recommend **3-5** for phone
- Recommend **10-20** for desktop

### Sidebar
- Starts collapsed on mobile
- Contains all filters and queue actions
- Swipe gesture to reveal

## Known Limitations

1. **Text editing** - On-screen keyboard takes screen space
2. **Long scripts** - May require scrolling within text area
3. **Audio download** - Some mobile browsers may have restrictions
4. **Multiselect** - Issue selection may require multiple taps

## Future Improvements

- [ ] Swipe gestures for next/previous item
- [ ] Pull-to-refresh functionality
- [ ] Offline mode with service worker
- [ ] Voice commands for approve/reject
- [ ] Haptic feedback on actions
