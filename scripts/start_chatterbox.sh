#!/usr/bin/env bash
# Start Chatterbox TTS from the local repository at /c/Users/doghe/chatterbox
# Stops any mock TTS on port 3000 first
set -e

CHATTERBOX_PATH="/c/Users/doghe/chatterbox"

if [ ! -d "$CHATTERBOX_PATH" ]; then
  echo "Chatterbox not found at $CHATTERBOX_PATH"
  exit 1
fi

echo "Stopping any processes using port 3000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

echo "Starting Chatterbox from $CHATTERBOX_PATH..."
cd "$CHATTERBOX_PATH"

# Check if node_modules exists; if not, run npm install
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies (npm install)..."
  npm install
fi

echo "Starting Chatterbox server (npm run dev)..."
echo "Chatterbox will run in this terminal. Press Ctrl+C to stop."
npm run dev
