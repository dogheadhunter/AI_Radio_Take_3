"""
Lyrics file parser for AI Radio.

Parses lyrics files and matches them to songs in the catalog.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict
import re
from collections import Counter


@dataclass
class LyricsData:
    """Parsed lyrics data."""
    title: str
    artist: str
    lyrics: str
    is_instrumental: bool
    provider: Optional[str] = None
    file_path: Optional[Path] = None


_METADATA_RE = re.compile(r"^(?P<key>[^:]+):\s*(?P<value>.*)$")

_STOPWORDS = {
    "the", "and", "a", "to", "of", "in", "it", "is", "that", "you", "i", "my", "me",
    "oh", "on", "for", "with", "this", "not", "be", "we", "are", "as", "your", "s",
}


def parse_lyrics_file(file_path: Path) -> Optional[LyricsData]:
    """
    Parse a lyrics file into structured data.

    Returns None if file cannot be parsed.
    """
    if not file_path.exists():
        return None

    text = file_path.read_text(encoding="utf-8")
    # Split metadata from lyrics by long dashed line or blank line
    parts = re.split(r"\n-{3,}\n", text, maxsplit=1)
    metadata_block = parts[0]
    lyrics_block = parts[1] if len(parts) > 1 else ""

    metadata = {}
    for line in metadata_block.splitlines():
        m = _METADATA_RE.match(line.strip())
        if m:
            key = m.group("key").strip().lower()
            value = m.group("value").strip()
            metadata[key] = value

    title = metadata.get("title")
    artist = metadata.get("artist")
    provider = metadata.get("provider")
    instrumental_flag = metadata.get("instrumental")
    is_instrumental = False
    if instrumental_flag is not None:
        is_instrumental = instrumental_flag.lower() in ("true", "1", "yes")

    # If TITLE or ARTIST missing, try to infer from filename 'Title by Artist.txt'
    if not title or not artist:
        name = file_path.stem
        # Try pattern 'Title by Artist'
        if " by " in name:
            parts2 = name.split(" by ")
            if not title:
                title = parts2[0].strip()
            if not artist:
                artist = parts2[1].strip()

    # Strip leading/trailing whitespace from lyrics
    lyrics = lyrics_block.strip()

    # If instrumental, ensure lyrics empty
    if is_instrumental:
        lyrics = ""

    if not title or not artist:
        return None

    return LyricsData(
        title=title,
        artist=artist,
        lyrics=lyrics,
        is_instrumental=is_instrumental,
        provider=provider,
        file_path=file_path,
    )


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 1]


def extract_lyrics_context(lyrics: LyricsData, max_length: int = 200) -> str:
    """
    Extract a brief context summary from lyrics.

    This is what gets passed to the prompt - not the full lyrics,
    but a summary of themes, mood, or notable lines.
    """
    if lyrics.is_instrumental:
        return "An instrumental piece."

    # Build theme from most common words
    tokens = _tokenize(lyrics.lyrics)
    if not tokens:
        return "No clear lyrics available."

    counts = Counter(tokens)
    common = [w for w, _ in counts.most_common(5)]
    theme = ", ".join(common[:3])

    # Determine mood heuristically
    mood_keywords = {
        "melancholic": ["sad", "cry", "lonely", "tears", "blue", "gone", "goodbye"],
        "romantic": ["love", "lover", "darling", "kiss", "heart", "baby"],
        "playful": ["laugh", "fun", "joke", "smile", "dance"],
        "nostalgic": ["remember", "used", "back", "when"],
        "angry": ["hate", "leave", "die", "mad"],
    }
    mood = None
    for m, kw_list in mood_keywords.items():
        if any(k in tokens for k in kw_list):
            mood = m
            break
    if not mood:
        mood = "nostalgic"

    # Notable element: pick a short memorable line (first non-empty non-bracketed line)
    line_candidates = [l.strip() for l in lyrics.lyrics.splitlines() if l.strip() and not l.strip().startswith("[")]
    notable = None
    if line_candidates:
        notable = line_candidates[0]
        if len(notable) > 80:
            notable = notable[:77].rstrip() + "..."

    parts = [f"This song is about {theme}.", f"The mood is {mood}."]
    if notable:
        parts.append(f"Notable line: '{notable}'")

    result = " ".join(parts).strip()
    if len(result) > max_length:
        return result[: max_length - 3].rstrip() + "..."
    return result


def match_lyrics_to_catalog(
    lyrics_dir: Path,
    catalog: 'SongCatalog',
) -> Dict[str, LyricsData]:
    """
    Match lyrics files to songs in the catalog.

    Returns dict mapping song_id -> LyricsData
    """
    # Normalize catalog into a list of dicts with 'id', 'title', 'artist'
    songs = []
    if isinstance(catalog, dict) and "songs" in catalog:
        songs = catalog["songs"]
    elif isinstance(catalog, list):
        songs = catalog
    else:
        # Try to treat as object with attribute 'songs'
        try:
            songs = getattr(catalog, "songs")
        except Exception:
            songs = []

    def norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower()) if s else ""

    by_title_artist = {}
    by_title = {}
    by_artist = {}

    for s in songs:
        sid = str(s.get("id"))
        t = norm(s.get("title"))
        a = norm(s.get("artist"))
        key = f"{t}::{a}"
        by_title_artist[key] = sid
        if t and t not in by_title:
            by_title[t] = sid
        if a and a not in by_artist:
            by_artist[a] = sid

    matched: Dict[str, LyricsData] = {}

    for p in lyrics_dir.glob("*.txt"):
        ld = parse_lyrics_file(p)
        if not ld:
            continue
        t = norm(ld.title)
        a = norm(ld.artist)
        key = f"{t}::{a}"
        sid = None
        if key in by_title_artist:
            sid = by_title_artist[key]
        elif t in by_title:
            sid = by_title[t]
        elif a in by_artist:
            sid = by_artist[a]
        if sid:
            matched[sid] = ld

    return matched
