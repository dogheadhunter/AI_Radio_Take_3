#!/usr/bin/env bash
# Save Docker images for offline use
set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CACHE_DIR="$SCRIPT_DIR/../dev/docker_cache"

mkdir -p "$CACHE_DIR"

echo "Saving Docker images to $CACHE_DIR for offline use..."

# List of images to cache (add more as needed)
IMAGES=(
  "python:3.10-slim"
)

for image in "${IMAGES[@]}"; do
  safe_name=$(echo "$image" | tr ':/' '_')
  tar_path="$CACHE_DIR/${safe_name}.tar"
  
  echo "Pulling $image..."
  docker pull "$image"
  
  echo "Saving $image to $tar_path..."
  docker save -o "$tar_path" "$image"
  
  echo "Saved $image successfully."
done

echo ""
echo "All images saved. To load them later, run: ./scripts/load_docker_images.sh"
