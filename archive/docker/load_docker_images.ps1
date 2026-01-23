# Load Docker images from cache for offline use
# Usage: .\scripts\load_docker_images.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$cacheDir = Join-Path (Split-Path -Parent $here) "dev\docker_cache"

if (-not (Test-Path $cacheDir)) {
    Write-Error "No cache directory found at $cacheDir. Run save_docker_images.ps1 first."
    Exit 1
}

Write-Host "Loading Docker images from $cacheDir..."

$tarFiles = Get-ChildItem -Path $cacheDir -Filter "*.tar"
foreach ($tarFile in $tarFiles) {
    Write-Host "Loading $($tarFile.Name)..."
    docker load -i $tarFile.FullName
}

Write-Host "`nAll images loaded successfully."
