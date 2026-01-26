"""Utility functions for pipeline stages.

This module provides helper functions used across different pipeline stages,
including catalog loading, lyrics retrieval, and test utilities.
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import random
import re


def load_catalog_songs(catalog_path: Path, limit: Optional[int] = None, random_sample: bool = False) -> List[Dict]:
    """Load songs from catalog.json.
    
    Args:
        catalog_path: Path to catalog.json file
        limit: Optional limit on number of songs to load
        random_sample: If True with limit, randomly sample songs instead of taking first N
        
    Returns:
        List of song dictionaries with id, artist, and title fields
    """
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    songs = data.get('songs', [])
    
    # Convert to simpler format
    songs = [{"id": s['id'], "artist": s['artist'], "title": s['title']} for s in songs]
    
    # Apply random sampling if requested
    if random_sample and limit:
        songs = random.sample(songs, min(limit, len(songs)))
    elif limit:
        songs = songs[:limit]
    
    return songs


def get_lyrics_for_song(artist: str, title: str) -> Optional[str]:
    """Load lyrics from music_with_lyrics directory if available.
    
    Args:
        artist: Artist name
        title: Song title
        
    Returns:
        Lyrics text if found, None otherwise
    """
    lyrics_dir = Path("music_with_lyrics")
    if not lyrics_dir.exists():
        return None
    
    # Try various filename patterns
    patterns = [
        f"{title} by {artist}.txt",
        f"{artist} - {title}.txt",
        f"{title}.txt",
    ]
    
    for pattern in patterns:
        lyrics_path = lyrics_dir / pattern
        if lyrics_path.exists():
            try:
                return lyrics_path.read_text(encoding='utf-8')
            except Exception:
                pass
    
    return None


class FakeAuditorClient:
    """Simple fake auditor client for test mode.
    
    This provides a mock implementation of the auditor that can be used
    for testing without requiring the actual LLM auditor service.
    """
    
    def generate(self, prompt: str, *args, **kwargs) -> str:
        """Generate a fake audit result based on simple heuristics.
        
        Args:
            prompt: The audit prompt (script to audit)
            
        Returns:
            JSON string with audit result
        """
        # Extract script content from 'SCRIPT TO EVALUATE: "..."' format
        match = re.search(r'SCRIPT TO EVALUATE:\s*"([^"]*)"', prompt)
        if match:
            script = match.group(1).lower()
        else:
            # Fallback: extract from between '---' markers (legacy format)
            parts = prompt.split('---')
            script = parts[-1] if len(parts) > 1 else prompt
            script = script.lower()
        
        # Simple heuristics for pass/fail - be more lenient in test mode
        # Look for actual problematic content in the script
        if "awesome" in script or "😀" in script or "lol" in script or "omg" in script:
            return json.dumps({
                "criteria_scores": {
                    "character_voice": 4,
                    "era_appropriateness": 2,
                    "forbidden_elements": 1,
                    "natural_flow": 4,
                    "length": 6
                },
                "issues": ["Uses modern slang or emoji"],
                "notes": "Contains modern slang"
            })
        elif "borderline" in script:
            return json.dumps({
                "criteria_scores": {
                    "character_voice": 6,
                    "era_appropriateness": 6,
                    "forbidden_elements": 10,
                    "natural_flow": 6,
                    "length": 6
                },
                "issues": ["Slight character drift"],
                "notes": "Borderline but acceptable"
            })
        
        # Default: pass with good scores (for test mode)
        return json.dumps({
            "criteria_scores": {
                "character_voice": 8,
                "era_appropriateness": 8,
                "forbidden_elements": 10,
                "natural_flow": 8,
                "length": 8
            },
            "issues": [],
            "notes": "Good script"
        })
