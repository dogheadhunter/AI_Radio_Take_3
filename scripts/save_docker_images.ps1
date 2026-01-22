# Save Docker images for offline use
# Usage: .\scripts\save_docker_images.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$cacheDir = Join-Path (Split-Path -Parent $here) "dev\docker_cache"

if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir | Out-Null
}

Write-Host "Saving Docker images to $cacheDir for offline use..."

# List of images to cache (add more as needed)
$images = @(
    "python:3.10-slim"
)

foreach ($image in $images) {
    $safeName = $image -replace '[:/]', '_'
    $tarPath = Join-Path $cacheDir "$safeName.tar"
    
    Write-Host "Pulling $image..."
    docker pull $image
    
    Write-Host "Saving $image to $tarPath..."
    docker save -o $tarPath $image
    
    Write-Host "Saved $image successfully."
}

Write-Host "`nAll images saved. To load them later, run: .\scripts\load_docker_images.ps1"
