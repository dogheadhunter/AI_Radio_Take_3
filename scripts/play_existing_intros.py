"""Play existing generated intros and their corresponding songs.

Scans `data/generated/intros/julie` for intro WAVs, finds the corresponding song in
`data/catalog.json`, and plays intro then song using the PlaybackController.
"""
import json
import time
import re
from pathlib import Path
import sys

# Ensure repo root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai_radio.playback.player import PygameAudioPlayer
from src.ai_radio.playback.controller import PlaybackController, add_song_with_intro, start_playback

DATA = ROOT / "data"
INTROS_DIR = DATA / "generated" / "intros" / "julie"
CATALOG = DATA / "catalog.json"


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[\W_]+", " ", s)
    s = s.strip()
    return s


def find_song_for_folder(folder_name: str, catalog_songs: list):
    # folder_name like "Alberta_Hunter-The_Darktown_Strutters_Ball"
    if "-" in folder_name:
        artist_part, title_part = folder_name.split("-", 1)
    else:
        artist_part, title_part = folder_name, ""

    artist_norm = normalize(artist_part)
    title_norm = normalize(title_part)

    for song in catalog_songs:
        art = normalize(song.get("artist", ""))
        tit = normalize(song.get("title", ""))
        if artist_norm and artist_norm in art and title_norm and title_norm in tit:
            return ROOT / song["file_path"]
        # fallback: either artist matches or title matches
        if artist_norm and artist_norm in art and not title_norm:
            return ROOT / song["file_path"]
        if title_norm and title_norm in tit and not artist_norm:
            return ROOT / song["file_path"]
    return None


def main():
    if not INTROS_DIR.exists():
        print("No intros found at:", INTROS_DIR)
        return

    with open(CATALOG, "r", encoding="utf-8") as fh:
        catalog = json.load(fh)

    player = PygameAudioPlayer()
    if not player._pygame_available:
        print("pygame not available or failed to initialize. Aborting.")
        return

    controller = PlaybackController(player=player)

    controller.on_item_started = lambda item: print(f"STARTED -> {item.item_type}: {item.path.name}")
    controller.on_item_finished = lambda item: print(f"FINISHED -> {item.item_type}: {item.path.name}")

    added_any = False

    for folder in sorted(INTROS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        folder_name = folder.name
        # prefer WAV file in folder
        wavs = list(folder.glob("*.wav"))
        if not wavs:
            print(f"No WAV intros in {folder}")
            continue
        intro_wav = wavs[0]
        song_path = find_song_for_folder(folder_name, catalog.get("songs", []))
        if not song_path or not song_path.exists():
            print(f"Could not find song for intro {folder_name}")
            continue

        print(f"Queueing intro {intro_wav.name} then song {song_path.name}")
        add_song_with_intro(controller, song_path=song_path, intro_path=intro_wav, song_id=folder_name)
        added_any = True

    if not added_any:
        print("No matches found; nothing queued.")
        return

    start_playback(controller)

    # wait for queue to finish
    while controller.is_playing or controller.queue_length > 0:
        time.sleep(0.1)

    print("Done playing all intros and songs.")


if __name__ == "__main__":
    main()
