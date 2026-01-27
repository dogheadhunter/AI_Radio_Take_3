/**
 * AI Radio - Web Interface
 * Simple tune-in interface with background playback support
 */

// DOM Elements
const tuneInBtn = document.getElementById('tuneInBtn');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('.status-text');
const nowPlaying = document.getElementById('nowPlaying');
const trackTitle = document.getElementById('trackTitle');

// Audio element for playback
let audio = null;
let isPlaying = false;

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
            title: 'AI Radio - 24/7 Golden Age Hits',
            artist: 'AI Radio',
            album: 'Live Broadcast',
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
        player.pause();
        player.src = '';
    } else {
        // Set the stream URL
        player.src = '/stream';
        player.play().catch(err => {
            console.error('Playback failed:', err);
            updateStatus('error', 'Playback failed. Please try again.');
        });
    }
}

/**
 * Event handlers
 */
function onPlay() {
    isPlaying = true;
    updateStatus('online', 'Broadcasting live');
    nowPlaying.style.display = 'block';
    tuneInBtn.querySelector('.btn-icon').textContent = '⏸';
    tuneInBtn.querySelector('.btn-text').textContent = 'Stop';
    tuneInBtn.setAttribute('aria-label', 'Stop AI Radio');
}

function onPause() {
    isPlaying = false;
    updateStatus('offline', 'Ready to tune in');
    nowPlaying.style.display = 'none';
    tuneInBtn.querySelector('.btn-icon').textContent = '▶';
    tuneInBtn.querySelector('.btn-text').textContent = 'Tune In';
    tuneInBtn.setAttribute('aria-label', 'Tune in to AI Radio');
}

function onError(e) {
    console.error('Audio error:', e);
    updateStatus('error', 'Connection error. Retrying...');
    
    // Auto-retry after 3 seconds if we were playing
    if (isPlaying) {
        setTimeout(() => {
            if (audio && isPlaying) {
                audio.play();
            }
        }, 3000);
    }
}

function onEnded() {
    // Stream ended unexpectedly, try to reconnect
    console.log('Stream ended, reconnecting...');
    if (isPlaying) {
        audio.play();
    }
}

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
