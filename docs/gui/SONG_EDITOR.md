# Song Editor Feature Documentation

## Overview

The Song Editor is a new page in the Review GUI that provides a song-centric view for reviewing and editing all content related to a specific song. This feature allows you to:

- View all intros and outros for a specific song
- See the complete song lyrics
- Manually edit scripts
- Mark scripts as manually rewritten
- Regenerate audio for edited scripts

## Accessing the Song Editor

1. Launch the Review GUI: `python run_review_gui.py`
2. In the sidebar, select **"Song Editor"** from the Page radio buttons
3. The Song Editor page will load with a song selector

## Features

### Song Selection

- **Song Dropdown**: Select from 132+ available songs
- Songs are displayed as "Artist - Title"
- Sorted alphabetically by artist and title

### Song Information Display

- **Song Title**: Displayed prominently at the top
- **Artist Name**: Shows the song's artist
- **Song ID**: The internal identifier used in the file system
- **Lyrics Viewer**: Expandable section showing the complete song lyrics (read-only)

### Content Sections

#### Intros Section
Shows all generated intros for the selected song, organized by DJ (Julie, Mr. New Vegas):

- Version selector for each DJ's intros
- Status indicators (Audit status, Review status)
- Manual rewrite indicator if script has been manually edited

#### Outros Section
Shows all generated outros for the selected song, organized by DJ:

- Version selector for each DJ's outros
- Status indicators (Audit status, Review status)
- Manual rewrite indicator if script has been manually edited

### Script Editing

For each intro/outro item:

1. **View Current Script**: The script is displayed in an editable text area
2. **Edit Script**: Modify the script text directly in the text area
3. **Save Changes**: Click the "💾 Save Changes" button (appears when script is modified)
4. **Manual Rewrite Marking**: When saved, the script is automatically marked as "manually rewritten"
   - A green success message appears: "✏️ Manually rewritten (version X) - This version will be used for audio generation"
   - The system tracks which version was manually edited
   - This marking persists in the `review_status.json` file

### Audio Playback

- Audio player for each version
- Plays .wav files directly in the browser
- Located side-by-side with the script editor

### Audio Regeneration

After manually editing a script:

1. Click the "🔊 Regenerate Audio" button
2. The item is added to the regeneration queue with the note: "Manual script edit - regenerate audio with updated script"
3. Process the queue later using `python scripts/process_regen_queue.py`
4. The new audio will be generated using your manually edited script

## Workflow Example

### Typical Workflow for Manual Script Editing

1. **Select a Song**:
   - Choose "Louis Armstrong - A Kiss to Build a Dream On" from the dropdown

2. **Review Lyrics**:
   - Expand the "📜 Song Lyrics" section
   - Read through the lyrics to understand the song's theme and content

3. **Find the Intro to Edit**:
   - Scroll to the "🎤 Intros" section
   - Locate "Julie - Intro" (or "Mr New Vegas - Intro")

4. **Review Current Version**:
   - Select the desired version from the version dropdown
   - Listen to the current audio
   - Read the current script

5. **Edit the Script**:
   - Click in the script text area
   - Make your edits (e.g., incorporate more lyrics, improve pacing, fix character voice)
   - The "💾 Save Changes" button will appear

6. **Save Your Edits**:
   - Click "💾 Save Changes"
   - Success message confirms the save and manual rewrite marking

7. **Regenerate Audio**:
   - Click "🔊 Regenerate Audio"
   - Confirmation shows it's been added to the queue

8. **Process Regeneration** (later):
   - Run `python scripts/process_regen_queue.py`
   - New audio file will be generated with your edited script

## Technical Details

### Data Storage

**Manual Rewrite Tracking**:
When you manually edit a script, the following is saved to `review_status.json`:

```json
{
  "manually_rewritten": true,
  "rewritten_version": 0,
  "rewritten_at": "2026-01-25T19:30:00",
  "status": "pending",
  "reviewer_notes": "",
  "script_issues": [],
  "audio_issues": []
}
```

**Key Fields**:
- `manually_rewritten`: Boolean flag indicating manual editing
- `rewritten_version`: Which version number was manually edited
- `rewritten_at`: ISO timestamp of when the edit was made

### Regeneration Queue

When you regenerate audio for a manually edited script, a queue entry is created:

```json
{
  "content_type": "intros",
  "dj": "julie",
  "item_id": "Louis_Armstrong-A_Kiss_to_Build_a_Dream_On",
  "folder_path": "/path/to/folder",
  "regenerate_type": "audio",
  "feedback": "Manual script edit - regenerate audio with updated script",
  "added_at": "2026-01-25T19:30:00"
}
```

The queue processor will:
1. Read the manually edited script
2. Generate new audio using TTS
3. Save as the next version number
4. Preserve the manual rewrite marking

### File Naming Conventions

The Song Editor correctly handles different naming conventions:

**Intros/Time/Weather**:
- `julie_0.txt`, `julie_0.wav`
- `julie_1.txt`, `julie_1.wav`
- etc.

**Outros**:
- `mr_new_vegas_outro.txt`, `mr_new_vegas_outro.wav` (version 0)
- `mr_new_vegas_outro_1.txt`, `mr_new_vegas_outro_1.wav` (version 1)
- etc.

## Integration with Review List

The Song Editor and Review List pages are independent but share data:

- **Review Status**: Changes made in one page are reflected in the other
- **Regeneration Queue**: Queue items from both pages are combined
- **Manual Rewrite Marking**: Visible in both views

To switch between pages:
- Use the **Page** radio buttons in the sidebar
- Select "Review List" for the original review interface
- Select "Song Editor" for the song-centric editing interface

## Benefits of Song Editor

1. **Contextual Editing**: See lyrics while editing scripts
2. **Complete View**: All intros/outros for a song in one place
3. **Easy Comparison**: Switch between versions quickly
4. **Manual Control**: Full control over script content
5. **Audio Generation**: Regenerate audio with your improved scripts
6. **Version Tracking**: System tracks which scripts are manually edited

## Tips

- **Use Lyrics**: Reference the lyrics when writing scripts to incorporate meaningful quotes
- **Character Voice**: Match the DJ's character (Julie's warmth vs Mr. New Vegas's smoothness)
- **Save Often**: Click save after making changes to avoid losing work
- **Test Audio**: Always listen to the current audio before editing
- **Batch Editing**: Edit multiple songs before processing the regeneration queue
- **Version Management**: Keep earlier versions by editing later version numbers

## Keyboard Shortcuts

- **Tab**: In the script editor, inserts a tab (use Shift+Tab to outdent)
- **Ctrl/Cmd + A**: Select all text in the editor
- **Ctrl/Cmd + Z**: Undo changes (before saving)

## Troubleshooting

**"No songs found in music_with_lyrics directory"**
- Ensure the `music_with_lyrics` directory exists
- Verify it contains `.txt` files in the format "Title by Artist.txt"

**"No intros generated for this song yet"**
- This song hasn't been processed by the generation pipeline yet
- Generate content first using the main pipeline

**Script won't save**
- Check file permissions on the `data/generated` directory
- Ensure the folder exists for that song/DJ combination

**Audio doesn't play**
- Ensure the `.wav` file exists
- Check browser audio support
- Try a different browser

**Manual rewrite marking doesn't appear**
- Refresh the page after saving
- Check the `review_status.json` file directly

## Future Enhancements

Potential improvements for the Song Editor:

- [ ] Side-by-side script comparison (original vs. edited)
- [ ] Script templates based on song characteristics
- [ ] AI-assisted script suggestions
- [ ] Bulk editing across multiple songs
- [ ] Export/import edited scripts
- [ ] Collaborative editing with version history
- [ ] Real-time audio preview without regeneration
