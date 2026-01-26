"""
Launcher script for the AI Radio Review GUI.

Runs the Streamlit app with appropriate configuration.
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit review GUI."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    # Path to the review GUI
    gui_script = project_root / "review_gui.py"
    
    if not gui_script.exists():
        print(f"Error: Could not find review_gui.py at {gui_script}")
        sys.exit(1)
    
    # Launch Streamlit
    print("Starting AI Radio Review GUI...")
    print(f"Project root: {project_root}")
    print(f"GUI script: {gui_script}")
    print("\nPress Ctrl+C to stop the server.\n")
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(gui_script),
            "--server.port=8501",
            "--server.address=0.0.0.0",  # Allow network access (e.g., via Tailscale)
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ], cwd=str(project_root), check=True)
    except KeyboardInterrupt:
        print("\nShutting down Review GUI...")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
