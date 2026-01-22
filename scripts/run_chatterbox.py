#!/usr/bin/env python3
"""
Run the Chatterbox TTS server on port 3000.
This wraps Chatterbox in a Flask API compatible with AI_Radio TTSClient.
"""
import subprocess
import sys
from pathlib import Path

# Ensure we're in the AI_Radio_Take_3 directory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == '__main__':
    server_path = project_root / "dev" / "chatterbox_server.py"
    chatterbox_root = Path(r"C:\Users\doghe\chatterbox")
    
    print(f"Starting Chatterbox TTS server from {server_path}...")
    print("Server will run on http://localhost:3000")
    print("Press Ctrl+C to stop")
    print()
    
    # Use Chatterbox's venv Python (which has all the TTS dependencies)
    venv_python = chatterbox_root / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print(f"ERROR: Chatterbox venv not found at {venv_python}")
        print("Please run: cd C:\\Users\\doghe\\chatterbox && python -m venv .venv && .venv\\Scripts\\pip install -e .")
        sys.exit(1)
    
    try:
        subprocess.run([str(venv_python), str(server_path)], check=True)
    except KeyboardInterrupt:
        print("\nShutting down Chatterbox server...")
