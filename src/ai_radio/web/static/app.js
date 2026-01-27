/**
 * Golden Age Of Radio Broadcast - Web Interface
 * Vintage radio with live metadata updates
 */

// DOM Elements
const tuneInBtn = document.getElementById('tuneInBtn');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('.status-text');
const nowPlaying = document.getElementById('nowPlaying');
const trackTitle = document.getElementById('trackTitle');
const trackArtist = document.getElementById('trackArtist');

// Audio element for playback
let audio = null;
let isPlaying = false;
let metadataInterval = null;

/**
 * Initialize the audio player with Media Session API support
 */
function initAudio() {
    if (audio) return audio;
    
    audio = new Audio();
    audio.preload = 'none';
    
    // Set up event listeners
    audio.addEventListener('play', onPlay);
    audio.addEventListener('pause', onPause);
    audio.addEventListener('error', onError);
    audio.addEventListener('ended', onEnded);
    
    // Enable background playback with Media Session API
    if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: 'Golden Age Of Radio Broadcast',
            artist: 'Live Broadcast',
            album: '1940s & 1950s Classics',
            artwork: [
                { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
                { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }
            ]
        });
        
        navigator.mediaSession.setActionHandler('play', () => {
            audio.play();
        });
        
        navigator.mediaSession.setActionHandler('pause', () => {
            audio.pause();
        });
    }
    
    return audio;
}

/**
 * Toggle playback - tune in or stop
 */
function togglePlayback() {
    const player = initAudio();
    
    if (isPlaying) {
        console.log('⏹️ CLIENT: User clicked Stop');
        // Stop playing - update state and UI immediately
        isPlaying = false;
        player.pause();
        player.src = '';
        
        // Update UI directly since events may not fire reliably
        updateStatus('offline', 'Ready to tune in');
        nowPlaying.style.display = 'none';
        tuneInBtn.querySelector('.btn-icon').textContent = '▶';
        tuneInBtn.querySelector('.btn-text').textContent = 'Tune In';
        tuneInBtn.setAttribute('aria-label', 'Tune in to AI Radio');
    } else {
        console.log('▶️ CLIENT: User clicked Tune In - requesting stream from server');
        // Set the stream URL
        player.src = '/stream';
        player.play().catch(err => {
            console.error('❌ CLIENT: Playback failed:', err);
            updateStatus('error', 'Playback failed. Please try again.');
        });
    }
}

/**
 * Event handlers
 */
function onPlay() {
    isPlaying = true;
    console.log('🎵 CLIENT: Audio started playing');
    updateStatus('online', 'BROADCASTING LIVE');
    nowPlaying.style.display = 'block';
    tuneInBtn.querySelector('.btn-icon').textContent = '⏸';
    tuneInBtn.querySelector('.btn-text').textContent = 'Stop';
    tuneInBtn.setAttribute('aria-label', 'Stop Golden Age Radio');
    
    // Start polling for metadata
    fetchMetadata();
    metadataInterval = setInterval(fetchMetadata, 5000);
}

function onPause() {
    isPlaying = false;
    console.log('⏸️ CLIENT: Audio paused');
    updateStatus('offline', 'OFF AIR');
    nowPlaying.style.display = 'none';
    tuneInBtn.querySelector('.btn-icon').textContent = '▶';
    tuneInBtn.querySelector('.btn-text').textContent = 'Tune In';
    tuneInBtn.setAttribute('aria-label', 'Tune in to Golden Age Radio');
    
    // Stop metadata polling
    if (metadataInterval) {
        clearInterval(metadataInterval);
        metadataInterval = null;
    }
}

function onError(e) {
    console.error('❌ CLIENT: Audio error:', e, {
        currentTime: audio ? audio.currentTime : 'N/A',
        networkState: audio ? audio.networkState : 'N/A',
        readyState: audio ? audio.readyState : 'N/A',
        error: audio ? audio.error : null
    });
    
    // Don't retry if we intentionally stopped
    if (!isPlaying) {
        console.log('ℹ️ CLIENT: Not retrying - intentionally stopped');
        return;
    }
    
    updateStatus('error', 'Connection error. Retrying...');
    
    // Auto-retry after 3 seconds if we were playing
    setTimeout(() => {
        if (audio && isPlaying) {
            console.log('🔄 CLIENT: Auto-retrying stream...');
            audio.src = '/stream?' + Date.now();
            audio.play();
        }
    }, 3000);
}

function onEnded() {
    console.log('🏁 CLIENT: Song ended, loading next from broadcast...', {
        currentTime: audio.currentTime,
        duration: audio.duration
    });
    if (isPlaying && audio) {
        // Just reload the stream - broadcast advances automatically
        audio.src = '/stream?' + Date.now(); // Cache buster
        audio.play().catch(err => {
            console.error('Auto-tune failed:', err);
            // Retry after a short delay
            setTimeout(() => {
                if (isPlaying) {
                    audio.src = '/stream?' + Date.now();
                    audio.play();
                }
            }, 3000);
        });
    }
}

/**
 * Fetch current track metadata from server
 */
async function fetchMetadata() {
    try {
        const response = await fetch('/api/now-playing');
        if (response.ok) {
            const data = await response.json();
            trackArtist.textContent = data.artist || 'Unknown Artist';
            trackTitle.textContent = data.title || 'Unknown Title';
            
            // Update Media Session API
            if ('mediaSession' in navigator) {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: data.title,
                    artist: data.artist,
                    album: 'Golden Age Of Radio Broadcast',
                    artwork: [
                        { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
                        { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }
                    ]
                });
            }
        }
    } catch (err) {
        console.error('Failed to fetch metadata:', err);
    }
}

/**}

/**
 * Update status indicator and text
 */
function updateStatus(state, text) {
    statusIndicator.className = `status-indicator ${state}`;
    statusText.textContent = text;
}

/**
 * Check server health
 */
async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        if (data.status === 'ok') {
            return true;
        }
    } catch (err) {
        console.error('Health check failed:', err);
    }
    return false;
}

/**
 * Initialize the app
 */
async function init() {
    // Check if server is available
    const healthy = await checkHealth();
    if (healthy) {
        console.log('AI Radio server is ready');
    } else {
        updateStatus('error', 'Server unavailable');
    }
    
    // Set up event listeners
    tuneInBtn.addEventListener('click', togglePlayback);
    
    // Register service worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').then(
            registration => {
                console.log('Service Worker registered:', registration);
            },
            err => {
                console.log('Service Worker registration failed:', err);
            }
        );
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
