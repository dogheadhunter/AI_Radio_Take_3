# Start development services (mock TTS). Requires Docker.
Set-StrictMode -Version Latest
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location "$here/..\dev"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker not installed or not in PATH"
    Exit 1
}
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "docker-compose not found; attempting 'docker compose'"
}
docker-compose -f docker-compose.yml up -d
Write-Host "Services started. mock-tts listening on http://localhost:3000"
Pop-Location