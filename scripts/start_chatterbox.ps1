# Start Chatterbox TTS Server (local, no Docker)
# Uses the cloned chatterbox repo and main project venv
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "=== Chatterbox TTS Server (Local) ===" -ForegroundColor Cyan

# Stop any existing process on port 3000
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    $existingPid = $port3000.OwningProcess | Select-Object -First 1
    Write-Host "Stopping existing process on port 3000 (PID: $existingPid)..." -ForegroundColor Yellow
    Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "Starting server on http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n"

# Run the Flask server using main project venv
& "$projectRoot\.venv\Scripts\python.exe" "$projectRoot\dev\chatterbox_server.py"
