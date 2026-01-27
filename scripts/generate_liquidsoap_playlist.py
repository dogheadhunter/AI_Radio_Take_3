#!/usr/bin/env python3
"""Generate Liquidsoap playlist from catalog.json"""

import json
import sys
from pathlib import Path

def generate_playlist():
    """Generate .m3u playlist for Liquidsoap from catalog.json"""
    
    # Load catalog
    catalog_path = Path(__file__).parent.parent / "data" / "catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Get all songs
    songs = catalog.get('songs', [])
    if not songs:
        print("ERROR: No songs found in catalog", file=sys.stderr)
        return 1
    
    # Generate M3U Extended format playlist
    output_path = Path(__file__).parent.parent / "liquidsoap" / "playlist.m3u"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for song in songs:
            # Get file path (absolute for Liquidsoap)
            file_path = Path(song['file_path']).resolve()
            
            # M3U Extended format: #EXTINF:duration,Artist - Title
            artist = song.get('artist', 'Unknown Artist')
            title = song.get('title', 'Unknown Title')
            duration = int(song.get('duration_seconds', 0))
            
            f.write(f"#EXTINF:{duration},{artist} - {title}\n")
            f.write(f"{file_path}\n")
    
    print(f"✅ Generated playlist: {output_path}")
    print(f"   Total songs: {len(songs)}")
    return 0

if __name__ == "__main__":
    sys.exit(generate_playlist())
