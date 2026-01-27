#!/usr/bin/env liquidsoap

# Golden Age Of Radio Broadcast - Liquidsoap Configuration
# Professional broadcast with metadata and smooth transitions

# Performance tuning
settings.log.level.set(4)
settings.frame.duration.set(0.04)
settings.decoder.priorities.ffmpeg.set(10)

# Load the playlist
playlist_path = "C:/Users/doghe/AI_Radio_Take_3/liquidsoap/playlist.m3u"

# Create a rotating playlist (loops forever)
radio = playlist(
  mode="randomize",
  reload_mode="watch",
  playlist_path
)

# Smooth transitions between songs (3 second crossfade)
radio = crossfade(
  duration=3.0,
  fade_in=2.0,
  fade_out=2.0,
  radio
)

# Make it infallible (never stops)
radio = mksafe(radio)

# Output to HTTP as WAV
output.harbor(
  %wav(stereo=true, samplerate=44100),
  port=8000,
  mount="/stream",
  radio
)

# Store current track in server variables (accessible via HTTP)
current_artist = ref("")
current_title = ref("")

def update_metadata(m) =
  artist = m["artist"] ?? "Unknown Artist"
  title = m["title"] ?? "Unknown Title"
  current_artist := artist
  current_title := title
  log("Now playing: #{artist} - #{title}")
end

# Apply metadata tracking to our radio source
radio.on_metadata(synchronous=false, update_metadata)

# HTTP endpoint for metadata using harbor's built-in handler  
def json_metadata_handler(_) =
  artist = current_artist()
  title = current_title()
  
  # Build proper JSON manually since json.stringify creates arrays
  json_str = '{"artist":"' ^ artist ^ '","title":"' ^ title ^ '","status":"live"}'
  
  http.response(
    content_type="application/json",
    data=json_str
  )
end

harbor.http.register.simple(
  port=8000,
  method="GET",
  "/metadata",
  json_metadata_handler
)

log("Golden Age Of Radio Broadcast started on http://localhost:8000/stream")
log("Metadata available at http://localhost:8000/metadata")
