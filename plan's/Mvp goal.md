# 🎙️ AI Radio Station — Complete Project Specification

## Document Purpose
This document captures every decision, requirement, and design choice discussed for the AI Radio Station project. It serves as the **single source of truth** for development. 

---

## 📋 Table of Contents
1. [Project Vision](#project-vision)
2. [Core Experience](#core-experience)
3. [DJ Personalities](#dj-personalities)
4. [Programming Schedule](#programming-schedule)
5. [Music System](#music-system)
6. [Content Generation](#content-generation)
7. [Radio Shows](#radio-shows)
8. [Information Services](#information-services)
9. [User Interaction](#user-interaction)
10. [Technical Architecture](#technical-architecture)
11. [Error Handling & Logging](#error-handling--logging)
12. [Hardware & Performance](#hardware--performance)
13. [Development Approach](#development-approach)
14. [Future Roadmap](#future-roadmap)
15. [Open Questions & Pins](#open-questions--pins)

---

## Project Vision

### The Concept
A **24/7 personal AI radio station** that recreates the feel of the **Golden Age of Radio** (1930s-1950s) with:
- Period-appropriate music
- Classic radio drama shows
- AI-generated DJ personalities inspired by Fallout's radio hosts
- Modern information services (weather, time) delivered in period style

### The "Why"
- **Nostalgia**: Recreate the magic of real radio with personality
- **Control**: Personal music library, personal experience
- **Immersion**: Create an atmosphere that transports you to another era
- **Learning**: Understand Python and AI concepts through building
- **Fun**: A genuinely cool passion project

### Success Definition
The project is complete when:
1. ✅ Press start, walk away, come back 24 hours later — still playing
2. ✅ Julie and Mr. New Vegas are distinctly recognizable personalities
3. ✅ Time announcements happen every 30 minutes with DJ flavor
4. ✅ Weather updates happen 3x daily in period style
5. ✅ Every song has unique, contextual, varied intros
6. ✅ Radio shows play at 8 PM with proper DJ introduction/commentary
7. ✅ Terminal displays current status
8. ✅ Comprehensive logs capture everything for review
9. ✅ System recovers gracefully from errors

---

## Core Experience

### The Listener's Perspective
- Wake up to Julie's warm, hopeful voice
- Music plays with brief, interesting intros featuring fun facts
- Time announced every 30 minutes in character
- Weather delivered in period style at key times
- Evening transition as Julie hands off to Mr. New Vegas
- Radio drama at 8 PM with smooth introductions
- Late-night vocal jazz and intimate DJ presence
- Falls asleep to Mr. New Vegas's soothing voice

### Immersion Decisions
| Aspect | Decision |
|--------|----------|
| **World Setting** | Real world — DJs are personalities/voices, not post-apocalyptic survivors |
| **Fallout References** | Occasional winks/easter eggs welcome, not required for MVP |
| **Location References** | No specific Rochester mentions; keep it universal |
| **Time References** | Timeless style ("Good morning, friends" not "January 22nd, 2026") |
| **Listener Relationship** | Julie:  broadcasting to many as friends; Mr. New Vegas: broadcasting to many but speaking intimately to *you* |

### Station Identity
- **Name**: TBD — Something Fallout-inspired, connected to Rochester, MN
- **Sign-On**:  Self-check → DJ signs on based on current time slot
- **Sign-Off**: N/A (24/7 operation)

---

## DJ Personalities

### Julie (Fallout 76 Inspired)

#### Character Summary
| Attribute | Value |
|-----------|-------|
| **Role** | Daytime DJ (6 AM - 7 PM) |
| **Age/Vibe** | Early 20s, "girl next door" |
| **Tone** | Earnest, hopeful, vulnerable, neighborly |
| **Relationship to Listener** | Friend, companion, someone keeping you company |

#### Voice & Speech
| Aspect | Details |
|--------|---------|
| **Pacing** | Medium-fast, conversational |
| **Prosody** | Natural, modern American, slight vocal fry |
| **Filler Words** | "um", "like", "you know", "I mean" |
| **Starter Phrases** | "Hey everyone", "Listen", "You know", "So basically" |
| **Signature Lines** | "If you're out there.. .", "Welcome home..." |

#### Personality Traits
- Earnest and sincere — wears her heart on her sleeve
- Chatty and rambling — often catches herself and apologizes
- Vulnerable — admits to being scared or uncertain
- Encouraging — promotes kindness and connection
- Amateur — not polished, doing her best

#### Do's and Don'ts
| Do | Don't |
|----|-------|
| Sound like a friend, not a host | Sound polished or professional |
| Express vulnerability occasionally | Be cynical or aggressive |
| Use filler words naturally | Use 1950s "mid-Atlantic" accent |
| Encourage and support | Be detached or cold |
| Ramble slightly, then self-correct | Be perfectly scripted |

#### Example Lines
> "Hey everyone, this is Julie.  Welcome back.  I hope you're safe, warm, and...  well, I hope you're happy."

> "You know, sometimes I sit here and I wonder if anyone is actually listening. But then I think...  even if just one person hears this and feels a little less lonely, then it's worth it."

> "This next one is a personal favorite. It reminds me of...  well, before.  It's funny how a melody can take you back, isn't it?"

---

### Mr. New Vegas (Fallout New Vegas Inspired)

#### Character Summary
| Attribute | Value |
|-----------|-------|
| **Role** | Evening/Night DJ (7 PM - 6 AM) |
| **Age/Vibe** | Timeless, sophisticated, classic entertainer |
| **Tone** | Suave, romantic, self-aggrandizing but charming, soothing |
| **Relationship to Listener** | Romantic — you are "Mrs. New Vegas" |

#### Voice & Speech
| Aspect | Details |
|--------|---------|
| **Pacing** | Deliberate, velvet-smooth, with meaningful pauses |
| **Prosody** | Melodic, intimate lower register |
| **Filler Words** | None — polished delivery |
| **Starter Phrases** | "It's me again", "Listen dear", "Word from the Strip" |
| **Signature Patterns** | "quote, unquote" for news, references to "Mrs. New Vegas" |

#### Personality Traits
- Suave and romantic — constantly charming
- Self-aggrandizing but with a wink — knows he's ridiculous
- Wistful — genuinely nostalgic for "old times"
- Unflappable — delivers bad news with smooth calm
- Intimate — makes every listener feel special

#### Do's and Don'ts
| Do | Don't |
|----|-------|
| Treat the listener as a lover | Use modern slang (cool, awesome) |
| Use "quote/unquote" for news | Break the illusion/admit limitations |
| Use 1950s slang (dig, cat, swell) | Be crude or aggressive |
| Be romantic and poetic | Be rushed or casual |
| Reference "Mrs. New Vegas" | Be impersonal |

#### Example Lines
> "It's me again, Mr. New Vegas, reminding you that you're nobody 'til somebody loves you.  And that somebody is me.  I love you."

> "The women of New Vegas ask me a lot if there's a Mrs. New Vegas. Well, of course there is. You're her. And you're still as perfect as the day we met."

> "This is Mr. New Vegas, and I feel something magic in the air tonight."

> "Here's a song for all you heavy hearts out there. Maybe you lost a bet, or maybe you lost a girl. Either way, Mr. New Vegas is here to catch you when you fall."

---

### DJ Handoff (7 PM)

The transition from Julie to Mr. New Vegas should feel natural — like two friends passing the mic. 

**Julie's Sign-Off Example:**
> "Well, that's my time, friends. It's getting late, and you know what that means...  I'm handing you over to someone very special. Be good to each other out there. This is Julie, signing off."

**Mr. New Vegas's Sign-On Example:**
> "Good evening, my darlings. It's me again, Mr. New Vegas. Julie tells me you've been wonderful today. I knew you would be. Now, let's settle in for the night together, shall we?"

---

## Programming Schedule

### Daily Format

| Time Block | Name | DJ | Mood/Energy | Content |
|------------|------|-----|-------------|---------|
| 6:00 AM - 10:00 AM | Morning Show | Julie | Wake-up, energetic, hopeful | Upbeat music, weather (6 AM), time checks |
| 10:00 AM - 3:00 PM | Midday | Julie | Steady, companionable, "keep chugging" | Varied music, time checks, weather (12 PM) |
| 3:00 PM - 7:00 PM | Afternoon Drive | Julie | Winding down, "almost done" | Transitional music, weather (5 PM), time checks |
| 7:00 PM - 8:00 PM | Evening Transition | Julie → Mr. New Vegas | Smooth handoff | Handoff segment, evening music |
| 8:00 PM - 9:00 PM | Primetime Drama | Mr. New Vegas | Theatrical, engaged | Radio show with DJ intro/outro |
| 9:00 PM - 12:00 AM | Late Night | Mr. New Vegas | Intimate, romantic, smooth | Vocal jazz, slow songs, time checks |
| 12:00 AM - 6:00 AM | Overnight | Mr. New Vegas | Quiet, gentle, for night owls | Soft music, minimal talk, time checks |

### Time Announcements
- **Frequency**: Every 30 minutes (on the hour and half-hour)
- **Style**: DJ-flavored, personality-driven
- **Examples**:
  - Julie: "Hey, it's three-thirty. Hope your afternoon is going okay out there."
  - Mr. New Vegas: "The time is eleven o'clock, and the night is still young, baby."

### Weather Announcements
- **Frequency**: 3x daily (6 AM, 12 PM, 5 PM)
- **Style**: Period-flavored language with modern specificity
- **Location**: Rochester, MN (but not mentioned by name on air)
- **Example**: "Bundle up this morning, folks — Old Man Winter's paying a visit.  Expect highs near 25 degrees with a chance of snow this afternoon."

---

## Music System

### Library Overview
- **Total Songs**: ~700
- **Era**: 1930s-1950s (Golden Age)
- **Format**: MP3 (may convert to WAV for processing ease)
- **Storage**: Single folder (not organized in subfolders)
- **Metadata Status**: Present (artist, title, year, album) — may need enrichment

### Rotation Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    MUSIC ROTATION SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  CORE PLAYLIST (70% of plays)                       │    │
│  │  • Songs you know and love                          │    │
│  │  • Higher play frequency                            │    │
│  │  • Multiple intro variations                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ▲                                   │
│                          │ Graduate (manual + auto)          │
│                          │                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  DISCOVERY ROTATION (30% of plays)                  │    │
│  │  • Songs you don't know well                        │    │
│  │  • Introduced once per hour                         │    │
│  │  • Can graduate to Core or be banished              │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          │ Banish                            │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  BANISHED (never plays)                             │    │
│  │  • Songs you actively dislike                       │    │
│  │  • Stored in banished_songs.txt                     │    │
│  │  • Can be un-banished manually                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  CURATED PLAYLISTS (Future Feature)                 │    │
│  │  • Manually created themed playlists                │    │
│  │  • Can be scheduled for specific times              │    │
│  │  • Room left in architecture for this               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Graduation System
Songs move from Discovery to Core via:
1. **Manual Promotion**: User explicitly promotes a song
2. **Automatic Promotion**: Song plays X times without being banished (threshold TBD)

### Banishment System
Multiple methods available:
1. **Text File**: Edit `banished_songs. txt` directly
2. **Runtime Command**: Type `banish` or press a key while listening
3. **Review Interface**: Post-session review of played songs

### Song Intro Strategy
- **Variety**: Multiple intros per song (3+ variations)
- **Content**: Brief with fun facts (artist trivia, recording history, era context)
- **Style**: Matches current DJ personality
- **Rotation**: Different intro each time song plays

---

## Content Generation

### Pre-Generation Approach
All radio content is **pre-generated** before playback: 
- Prioritizes quality over real-time speed
- Allows overnight batch processing
- Enables quality review before broadcast
- Reduces runtime complexity

### Content Types to Generate

| Content Type | Quantity | Generation Notes |
|--------------|----------|------------------|
| Song Intros | ~2,100 (3 per song) | DJ-specific, fact-based, varied |
| Song Outros | ~700 (1 per song) | Shorter, transitional |
| Time Announcements | 96 (48 per DJ) | Every 30-min slot, personality-flavored |
| Weather Templates | ~20 per DJ | Condition-based templates |
| DJ Sign-Ons | 2-4 per DJ | For startup at different times |
| DJ Handoff | 2-4 scripts | Julie → Mr. New Vegas transition |
| Radio Show Intros | 1 per show | Teaser-style introduction |
| Radio Show Outros | 1 per show | Commentary after show ends |
| Error Recovery Lines | 5-10 per DJ | "Record got scratched" style covers |

### Generation Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Song       │     │   Ollama     │     │  Chatterbox  │
│   Metadata   │ ──▶ │   (LLM)      │ ──▶ │   (TTS)      │
│              │     │              │     │              │
│  - Artist    │     │  Generate    │     │  Generate    │
│  - Title     │     │  Text Intro  │     │  Audio File  │
│  - Year      │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Quality    │
                     │   Review     │
                     │   (Manual)   │
                     └──────────────┘
```

### Generation Constraints
Due to 6GB VRAM limit: 
- **Sequential Processing**: Generate text → Unload LLM → Generate audio
- **Not Simultaneous**: Cannot run LLM and TTS at same time on GPU

### Testing Strategy
- Small batch tests before full generation
- Verify quality doesn't degrade over long runs
- Test 5-10 songs before committing to 700

---

## Radio Shows

### Current Inventory
- **The Shadow**: 1 episode ready
- **Fibber McGee and Molly**:  Planned
- **Others**: TBD

### Show Format
- **Duration**: ~30 minutes per episode
- **Structure**:  Self-contained episodes (arcs start and end in same episode)
- **Time Slot**: 8:00 PM - 9:00 PM nightly

### DJ Integration

**Before Show:**
Mr. New Vegas introduces with a teaser:
> "Good evening, my darlings. It's that time again. Tonight, who knows what evil lurks in the hearts of men? The Shadow knows...  Settle in, and enjoy."

**After Show:**
Mr. New Vegas comments on the episode:
> "Well, wasn't that something? I tell you, that Shadow really knows how to handle himself. Now, where were we?  Ah yes, the music..."

### Rotation Strategy
- **MVP**: Sequential (Episode 1, then Episode 2, etc.)
- **Future**: Show rotation by day (The Shadow Monday, Fibber McGee Tuesday) — **PINNED for later**

---

## Information Services

### Weather System

| Aspect | Specification |
|--------|---------------|
| **Source** | Weather API (TBD — likely OpenWeatherMap) |
| **Location** | Rochester, MN (not mentioned on air) |
| **Frequency** | 6 AM, 12 PM, 5 PM |
| **Style** | Period-flavored language + modern specificity |
| **Caching** | Cache results to avoid API spam |

**Style Examples:**
- Modern:  "Currently 45°F with light rain expected this afternoon"
- Period: "Bundle up, folks — Old Man Winter is paying us a visit today. Expect highs near 25 degrees."

**Weather-Influenced Music**:  
- Concept approved (rainy day = more melancholic, sunny = upbeat)
- **PINNED for post-MVP implementation**

### Time System

| Aspect | Specification |
|--------|---------------|
| **Frequency** | Every 30 minutes (: 00 and :30) |
| **Style** | DJ-flavored, personality-driven |
| **Integration** | Woven naturally into DJ patter |

**Examples by DJ:**

*Julie (casual, friendly):*
> "Hey, just noticed it's two o'clock. Afternoon's flying by, huh?"

*Mr. New Vegas (smooth, intimate):*
> "The time is midnight, my love. The witching hour.  Stay close."

---

## User Interaction

### Runtime Controls (MVP)

| Action | Method | Behavior |
|--------|--------|----------|
| Start | Run script | Self-check → DJ sign-on → Begin playback |
| Stop | Ctrl+C or command | Graceful shutdown with logging |
| Banish Song | Keystroke or command | Logs song to banished list, skips |
| Promote Song | Keystroke or command | Graduates song to Core playlist |
| Flag Bad Intro | Keystroke or command | Logs for later regeneration |

### Terminal Display (MVP)
Simple text display showing:
- Current song (Artist - Title)
- Current DJ
- Current time
- Next up (if known)
- Status messages

### Review Systems

**Problem List Review:**
- Bad intros flagged during playback
- Reviewable after listening session
- Easy regeneration of flagged items

**Banishment Review:**
- `banished_songs.txt` editable
- Can un-banish songs manually

---

## Technical Architecture

### Repository Structure
- **Primary Repo**: `dogheadhunter/AI_Radio_Take_3`
- **DJ Reference Files**: Located in `dogheadhunter/Esp32-Projects` (not consolidated, reference only)

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.x | Core application |
| **LLM** | Ollama (dolphin-llama or similar) | Text generation |
| **TTS** | Chatterbox | Voice synthesis with zero-shot cloning |
| **Audio Playback** | TBD (pygame, playsound, or similar) | Play audio files |
| **Testing** | pytest | Unit and integration tests |
| **Editor** | VS Code | Development environment |

### Voice Cloning Assets

| DJ | Sample Duration | Status |
|----|-----------------|--------|
| Julie | 30 minutes | Ready |
| Mr.  New Vegas | 20 minutes | Ready |

### Fallback Strategy
If voice cloning doesn't capture characters well for MVP:
- Use pleasant TTS voice with correct personality in text
- Refine voice cloning as Phase 5 enhancement

---

## Error Handling & Logging

### Error Philosophy
- **Recover silently**: Keep playing, don't crash
- **Log everything**:  Comprehensive logs for morning review
- **Graceful degradation**:  If something fails, skip and continue

### Error Scenarios

| Scenario | Behavior |
|----------|----------|
| Ollama crashes mid-generation | Log error, skip song, continue with next |
| Song file corrupted/missing | DJ covers smoothly ("That record got scratched, folks"), skip, log |
| Weather API down | Use cached data or skip weather announcement, log |
| TTS fails | Skip intro, play song without intro, log |
| Bad intro detected | Flag for regeneration, continue playback |

### Logging Requirements

**Log Format**:  Plain English + Technical details + Fix suggestions

**Example Log Entry:**
```
[2026-01-22 14:32:15] ERROR - Song Playback Failed
  What happened: Could not play "Bing Crosby - White Christmas. mp3"
  Technical:  FileNotFoundError - File not found at /music/Bing Crosby - White Christmas.mp3
  Suggestion: Check if file exists at that path.  Filename may have special characters.
  Action taken: Skipped to next song, DJ covered with scratch line. 
```

**Log Contents:**
- Every song played (timestamp, title, artist)
- Every DJ segment played
- All errors with context
- All user actions (banish, promote, flag)
- System status changes

---

## Hardware & Performance

### System Specifications

| Component | Spec |
|-----------|------|
| **OS** | Windows 11 Home (64-bit) |
| **CPU** | AMD Ryzen 9 5900HS (8 cores, 16 threads) |
| **RAM** | 16 GB |
| **GPU** | NVIDIA GeForce RTX 3060 Laptop (6GB VRAM) |
| **Storage** | TBD (need ~8-12 GB for project) |

### Performance Considerations

| Task | Performance Notes |
|------|-------------------|
| **Chatterbox TTS** | Excellent — RTX 3060 accelerates significantly |
| **Ollama LLM** | Supports 7B-8B models with 4-bit quantization |
| **Simultaneous LLM+TTS** | Not recommended — 6GB VRAM limit |

### Generation Time Estimates
For 700 songs × 3 intros = 2,100 intros: 
- **LLM text generation**: ~5-10 seconds each = 3-6 hours total
- **TTS audio generation**: ~10-30 seconds each = 6-18 hours total
- **Total**:  Overnight batch processing acceptable

### Storage Estimates
| Content | Size |
|---------|------|
| Music library | ~3-5 GB |
| Generated intros (audio) | ~2-3 GB |
| Generated outros (audio) | ~1-2 GB |
| Time announcements | ~50 MB |
| Logs (per month) | ~100-500 MB |
| **Total** | **~8-12 GB** |

---

## Development Approach

### Learning Philosophy
- **Goal**: Learn Python/AI concepts through building
- **Eventual Goal**: Maintain and extend the project independently
- **Explanation Level**: Key concepts explained, not every line
- **Code Style**: Commented for understanding, not overwhelming

### Session Expectations
- User can focus for extended periods when learning
- Tasks should be broken into learnable, achievable chunks
- Need explanations when things go wrong

### Debugging Needs
When errors occur, logs should provide:
1. Plain English explanation of what happened
2. Technical error details
3. Suggestions for how to fix

### Testing Strategy
- Use pytest (already set up in repo)
- Small tests before large batch operations
- Verify generation quality before scaling

---

## Future Roadmap

### Post-MVP Enhancements (Prioritized)

| Priority | Feature | Notes |
|----------|---------|-------|
| 1 | Voice cloning refinement | Perfect Julie and Mr. New Vegas voices |
| 2 | Weather-influenced music | Rainy = melancholic, sunny = upbeat |
| 3 | Show rotation by day | The Shadow Monday, Fibber McGee Tuesday |
| 4 | Curated playlist support | Manually themed playlists for special times |
| 5 | More radio shows | Expand drama library |
| 6 | More DJ personalities | Additional hosts for variety |
| 7 | Interactive requests | "Play something upbeat" |
| 8 | Visual display | Album art on screen |
| 9 | Network streaming | Stream to other devices/rooms |
| 10 | ESP32 portable radio | Self-contained hardware device |

### The ESP32 Dream
**Vision**: A physical, self-contained portable radio that plays the AI station

**Considerations** (for future architecture):
- May need network streaming capability (ESP32 has limited storage)
- Physical controls (volume, power)
- Vintage aesthetic case
- **Status**: Someday dream — architecture should leave room for it

---

## Open Questions & Pins

### Pinned for Later (Not MVP)

| Topic | Decision Deferred | Notes |
|-------|-------------------|-------|
| Weather-influenced music | Post-MVP | Good idea, adds complexity |
| Show rotation by day | Post-MVP | Need more shows first |
| Curated playlists | Post-MVP | Architecture should support it |
| Auto-detect bad intros | Post-MVP | Flagging system first |
| ESP32 integration | Someday | Keep streaming in mind |

### Decisions Still Needed

| Topic | Status | Notes |
|-------|--------|-------|
| Station name | TBD | Fallout-inspired, Rochester connection |
| Test songs (5) | Skipped for now | Needed before intro generation |
| Graduation threshold | TBD | How many plays before auto-promote?  |
| Banishment keystroke | TBD | Which key triggers banish? |
| Weather API choice | TBD | OpenWeatherMap likely |

### Questions for Future Sessions

1. **Station Name Ideas**:  What Rochester/Fallout connection resonates?
2. **Test Songs**: Which 5 songs to test intro generation?
3. **Graduation Threshold**: 3 plays?  5 plays?  10 plays without banishment?
4. **Overnight Content**: Should overnight (12 AM - 6 AM) have any special characteristics? 

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-22 | Initial comprehensive specification created |

---

*This document will be updated as decisions are made and the project evolves.*