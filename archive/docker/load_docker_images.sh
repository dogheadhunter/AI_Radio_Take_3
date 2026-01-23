#!/usr/bin/env bash
# Load Docker images from cache for offline use
set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CACHE_DIR="$SCRIPT_DIR/../dev/docker_cache"

if [ ! -d "$CACHE_DIR" ]; then
  echo "No cache directory found at $CACHE_DIR. Run save_docker_images.sh first."
  exit 1
fi

echo "Loading Docker images from $CACHE_DIR..."

for tar_file in "$CACHE_DIR"/*.tar; do
  if [ -f "$tar_file" ]; then
    echo "Loading $(basename "$tar_file")..."
    docker load -i "$tar_file"
  fi
done

echo ""
echo "All images loaded successfully."
