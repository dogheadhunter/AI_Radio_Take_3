#!/usr/bin/env bash
# Start development services (mock TTS). Requires Docker and docker-compose.
set -e
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$DIR/dev"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not installed or not in PATH"
  exit 1
fi
if ! command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose not found; try 'docker compose' or install docker-compose"
  exit 1
fi

docker-compose -f docker-compose.yml up -d

echo "Services started. mock-tts listening on http://localhost:3000"