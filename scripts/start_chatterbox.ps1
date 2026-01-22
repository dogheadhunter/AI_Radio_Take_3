# Start Chatterbox TTS from the local repository at C:\Users\doghe\chatterbox
# Stops any mock TTS on port 3000 first
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$chatterboxPath = "C:\Users\doghe\chatterbox"

if (-not (Test-Path $chatterboxPath)) {
    Write-Error "Chatterbox not found at $chatterboxPath"
    Exit 1
}

Write-Host "Stopping any processes using port 3000..."
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    $pid = $port3000.OwningProcess
    Write-Host "Killing process $pid on port 3000..."
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

Write-Host "Starting Chatterbox from $chatterboxPath..."
Push-Location $chatterboxPath

# Check if node_modules exists; if not, run npm install
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies (npm install)..."
    npm install
}

Write-Host "Starting Chatterbox server (npm run dev)..."
Write-Host "Chatterbox will run in this terminal. Press Ctrl+C to stop."
npm run dev

Pop-Location
