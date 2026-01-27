# AI Radio - Standalone Web GUI

A simple, dedicated web interface for tuning into the AI Radio 24/7 broadcast with a single button.

## Overview

The AI Radio Web GUI provides a standalone interface specifically designed for listening to the radio station. It features:

- **Simple tune-in button** - One-click access to start streaming
- **Background playback** - Audio continues when device is locked or app is in background (where supported)
- **Progressive Web App (PWA)** - Install on mobile devices for app-like experience
- **Accessibility** - Keyboard navigation, screen reader support, and high contrast mode
- **Responsive design** - Works on desktop, tablet, and mobile devices

## Quick Start

### 1. Start the Web Server

```bash
python scripts/run_radio_server.py
```

The server will start on `http://localhost:5000` by default.

### 2. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

### 3. Tune In

Click the **"Tune In"** button to start streaming the radio broadcast.

## Advanced Usage

### Custom Host and Port

```bash
# Run on a different port
python scripts/run_radio_server.py --port 8080

# Bind to all network interfaces
python scripts/run_radio_server.py --host 0.0.0.0 --port 5000

# Enable debug mode (auto-reload on code changes)
python scripts/run_radio_server.py --debug
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Host to bind the server to |
| `--port` | `5000` | Port number for the server |
| `--debug` | `False` | Enable debug mode with auto-reload |

## Features

### Background Playback

The web interface uses the **Media Session API** to enable background audio playback. This means:

- ✅ Audio continues when you lock your phone screen
- ✅ Audio continues when you switch to another app
- ✅ Media controls appear in notification tray (on supported devices)
- ⚠️ Browser tab closure behavior varies by browser

**Browser Support:**
- **Chrome/Edge**: Full support on Android, limited on desktop
- **Safari**: Full support on iOS 15+ and macOS
- **Firefox**: Limited support, may pause when tab is hidden

### Progressive Web App (PWA)

The interface can be installed as a standalone app on mobile devices:

1. Open the radio page in your mobile browser
2. Tap the "Add to Home Screen" option (location varies by browser)
3. Launch from your home screen like a native app

**Benefits of PWA installation:**
- App-like experience without app store download
- Faster loading with offline-capable UI
- Better background audio support

### Accessibility Features

The interface is designed with accessibility in mind:

- **Keyboard Navigation**: Tab through controls, Enter/Space to activate
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast Mode**: Automatic adjustments for users with visual needs
- **Reduced Motion**: Respects user's motion preferences
- **Focus Indicators**: Clear visual feedback for keyboard users

## Architecture

### File Structure

```
src/ai_radio/web/
├── __init__.py           # Web module initialization
├── server.py             # Flask server for streaming
└── static/               # Static web assets
    ├── index.html        # Main HTML page
    ├── app.js            # Client-side JavaScript
    ├── style.css         # Styles and responsive design
    ├── manifest.json     # PWA manifest
    └── sw.js             # Service worker for offline support
```

### Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: Vanilla JavaScript (no framework dependencies)
- **Audio**: HTML5 Audio API + Media Session API
- **PWA**: Service Workers + Web App Manifest
- **Styling**: CSS3 with CSS custom properties

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve main HTML page |
| `/health` | GET | Server health check |
| `/api/status` | GET | Current playback status |
| `/stream` | GET | Audio stream endpoint |
| `/manifest.json` | GET | PWA manifest |

## Browser Compatibility

### Desktop

| Browser | Version | Support | Notes |
|---------|---------|---------|-------|
| Chrome | 87+ | ✅ Full | Best experience |
| Firefox | 90+ | ⚠️ Partial | Background audio limited |
| Safari | 14+ | ✅ Full | macOS 11+ recommended |
| Edge | 87+ | ✅ Full | Chromium-based |

### Mobile

| Browser | Platform | Support | Notes |
|---------|----------|---------|-------|
| Chrome | Android 8+ | ✅ Full | Excellent background support |
| Safari | iOS 15+ | ✅ Full | Best on iOS 15.4+ |
| Firefox | Android | ⚠️ Partial | Limited background audio |
| Samsung Internet | Android | ✅ Full | Good support |

## Troubleshooting

### Audio Won't Play

1. **Check browser compatibility** - Ensure you're using a supported browser
2. **Check permissions** - Some browsers require user interaction before audio plays
3. **Check server** - Verify the Flask server is running
4. **Check network** - Ensure you can reach the server

### Background Playback Not Working

1. **Browser limitations** - Not all browsers support background audio equally
2. **Battery saver mode** - Some devices restrict background audio to save power
3. **Install as PWA** - Installing as a PWA often improves background support
4. **Update browser** - Ensure you're using the latest browser version

### Audio Stuttering or Buffering

1. **Check network connection** - Ensure stable internet connection
2. **Server performance** - Check if server has adequate resources
3. **Reduce quality** - Future versions may offer quality settings

## Development

### Running Tests

```bash
# Run web GUI tests
pytest tests/web/

# Run with playwright
pytest tests/web/test_radio_gui.py
```

### Local Development

```bash
# Start server in debug mode
python scripts/run_radio_server.py --debug

# Server will auto-reload on code changes
```

### Project Structure

The web GUI is intentionally standalone and separate from:
- The Streamlit review GUI (`review_gui.py`)
- The CLI station interface (`src/ai_radio/station/`)
- The generation pipeline (`src/ai_radio/stages/`)

This separation ensures the tune-in interface remains simple and focused.

## Platform Limitations

### iOS

- ✅ Background audio works well in Safari
- ✅ PWA installation supported
- ⚠️ Requires iOS 15.4+ for best experience
- ⚠️ Low Power Mode may pause playback

### Android

- ✅ Excellent background audio support in Chrome
- ✅ Media controls in notification shade
- ✅ Battery optimization may affect playback
- ✅ PWA works like native app

### Desktop

- ✅ Full playback support in all modern browsers
- ⚠️ Tab closure usually stops playback
- ⚠️ Background playback less consistent than mobile
- ✅ Good for active listening sessions

## Security Considerations

- Server binds to `0.0.0.0` by default for network access
- No authentication implemented (add if needed for production)
- HTTPS recommended for PWA features on public networks
- Service worker caches only static assets, not audio streams

## Future Enhancements

Potential improvements for future versions:

- [ ] HLS/DASH adaptive streaming for better quality
- [ ] Stream quality selection (low/medium/high)
- [ ] Volume control
- [ ] Now playing metadata display
- [ ] Schedule/program information
- [ ] Social sharing features
- [ ] Analytics/usage tracking
- [ ] Multi-DJ stream selection

## Support

For issues or questions:

1. Check this documentation
2. Review browser console for errors
3. Check Flask server logs
4. Open an issue on the repository

---

**Last Updated**: January 2026
**Version**: 1.0.0
