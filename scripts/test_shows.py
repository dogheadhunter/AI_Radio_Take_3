"""Manual test script for radio shows (for demos/manual verification).

Run: .venv\Scripts\python scripts/test_shows.py

This script discovers shows under `data/shows`, lists them, selects the next episode for "The_Shadow" (if present), and simulates playback using the `ShowPlayer` with a simple `MockPlayback` implementation.
"""
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `src` package can be imported when running directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ai_radio.shows.show_manager import ShowManager, scan_shows, get_next_episode
from src.ai_radio.shows.show_player import ShowPlayer, play_show_block


def main():
    shows_path = Path("data/shows")
    print(f"Scanning for shows in: {shows_path.resolve()}")

    manager = ShowManager()
    shows = scan_shows(manager, shows_path)

    if not shows:
        print("No shows found. Create a show under data/shows/<ShowName>/ with episode files.")
        return

    print("Found shows:")
    for s in shows:
        print(f"- {s.name} ({len(s.episodes)} episodes) intro: {s.intro_path}")

    # Choose the first show for demo
    show = shows[0]
    print(f"\nDemo playing show: {show.name}")

    played = []

    class MockPlayback:
        def __init__(self):
            self.on_item_started = None

        def resume_music(self):
            print("[MockPlayback] resume_music called")

    mock = MockPlayback()
    mock.on_item_started = lambda item: print(f"[Playback] started item_type={item.item_type} path={item.path}")

    player = ShowPlayer(playback=mock)

    result = play_show_block(player, show)
    print(f"Show block finished. result.duration_seconds={result.duration_seconds}")


if __name__ == "__main__":
    main()
