"""extract_style_guides.py

1) Clean transcripts (remove timestamps)
2) Split into segments
3) Categorize segments into song_intro, song_outro, commentary, time, weather, other
4) Generate cleaned text files and categorized JSON files
5) Auto-generate initial STYLE_GUIDE markdown files using extracted examples

Run: python scripts/extract_style_guides.py
"""
import re
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'voice_references'
OUT = ROOT / 'data' / 'style_analysis'
DOCS = ROOT / 'docs' / 'script_improvement'
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

TRANSCRIPTS = {
    'julie': ASSETS / 'Julie' / 'Julie_Full_Voicelines_Script.txt',
    'mr_new_vegas': ASSETS / 'Mister_New_Vegas' / 'Mister_New_Vegas_Voice_Files_Script.txt'
}

INTRO_PATTERNS = re.compile(r"\b(here(?:'s| is| comes?)|coming up|up next|next up|coming up next|this next|coming up is|here come|now,? (?:this|coming))\b", re.I)
OUTRO_PATTERNS = re.compile(r"\b(hope you enjoyed|enjoyed that|that was|thanks|thank you|hope you all|hope you|you're listening to|that's the news|signing off|just kidding)\b", re.I)
TIME_PATTERNS = re.compile(r"\b(hour|time|minute|hourly|top of the hour|o'clock)\b", re.I)
WEATHER_PATTERNS = re.compile(r"\b(weather|rain|storm|sky|rad|radex|radiation|stormy|wind)\b", re.I)

STOPWORDS = set(["the","and","to","a","i","you","it","of","in","that","is","for","on","we","be","are","this","with","as","so","but","or","if","not","have","has","was","do","my","at","by","they","from","me","he","she","them","all","your","yourself","we're","you're"]) 


def clean_text(text):
    # Remove timestamp prefixes like 00:00:00 Speaker:
    text = re.sub(r"^\d{2}:\d{2}:\d{2}\s+Speaker:\s*", "", text, flags=re.M)
    return text.strip()


def split_segments(text):
    # Split on sentence boundaries keeping abbreviations simple
    # Split on (?<=[.!?])\s+(?=[A-Z0-9\'\"\(])
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9\"\'\(])', text)
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned


def categorize_segment(s):
    if INTRO_PATTERNS.search(s):
        return 'song_intro'
    if OUTRO_PATTERNS.search(s):
        return 'song_outro'
    if TIME_PATTERNS.search(s):
        return 'time'
    if WEATHER_PATTERNS.search(s):
        return 'weather'
    # Heuristic: lines that mention songs/artists like "Here is", "with", "singing", "by"
    if re.search(r"\b(by|with|singing|here is|here's|coming up)\b", s, re.I):
        return 'song_intro'
    # commentary catch-all
    if re.search(r"\b(I|we|friends|hey|oh|you)\b", s):
        return 'commentary'
    return 'other'


def top_vocabulary(segments, n=25):
    words = []
    for s in segments:
        toks = re.findall(r"\b[a-z']{3,}\b", s.lower())
        words.extend([w for w in toks if w not in STOPWORDS])
    c = Counter(words)
    return c.most_common(n)


def build_style_guide(name, intros, outros, vocab, starters, forbidden=None):
    title = f"# Style Guide: {name}\n\n"
    summary = "## Character Summary\nExtracted examples and rules from voice transcripts.\n\n"
    intros_md = "## Song Introduction Patterns\n\n"
    for i, it in enumerate(intros[:10], 1):
        intros_md += f"### Pattern {i}\n**Example:** \"{it}\"\n**When to use:** When introducing a song or artist.\n**Key elements:** conversational lead-in, artist/title mention.\n\n"
    outros_md = "## Song Outro Patterns\n\n"
    for i, ot in enumerate(outros[:6], 1):
        outros_md += f"### Pattern {i}\n**Example:** \"{ot}\"\n**When to use:** After a song finishes or to give a transition.\n**Key elements:** friendly wrap-up, occasional encouragement.\n\n"
    vocab_md = "## Vocabulary\n\n### Words/Phrases to USE\n| Word/Phrase | Example Usage | Notes |\n|-------------|---------------|-------|\n"
    for w, c in vocab[:20]:
        vocab_md += f"| {w} | "" | {c} occurrences |\n"
    avoid_md = "\n### Words/Phrases to AVOID\n| Word/Phrase | Why | Alternative |\n|-------------|-----|-------------|\n| modern slang | eras don't match | era-appropriate phrasing |\n"

    starters_md = "## Sentence Structures\n\n### Common Starters\n"
    for s in starters[:10]:
        starters_md += f"- \"{s}\"\n"

    doc = title + summary + intros_md + outros_md + vocab_md + avoid_md + starters_md + "\n## Differentiation Checklist\n- TBD (compare against other DJ)\n\n## Red Flags\n- Modern slang, profanity, or breaking era tone.\n"
    return doc


def process_transcript(key, path):
    raw = path.read_text(encoding='utf8')
    cleaned = clean_text(raw)
    segments = split_segments(cleaned)
    categorized = {}
    for s in segments:
        cat = categorize_segment(s)
        categorized.setdefault(cat, []).append(s)
    # write cleaned file
    (OUT / f"{key}_cleaned.txt").write_text('\n'.join(segments), encoding='utf8')
    (OUT / f"{key}_categorized.json").write_text(json.dumps(categorized, indent=2, ensure_ascii=False), encoding='utf8')

    # prepare style guide pieces
    intros = categorized.get('song_intro', [])
    outros = categorized.get('song_outro', [])
    vocab = top_vocabulary(segments, 50)
    starters = []
    for s in segments:
        # take first 6-8 words as starter candidate
        parts = s.split()
        if len(parts) >= 2:
            starters.append(' '.join(parts[:6]))
    # write style guide
    pretty_name = 'Julie' if key=='julie' else 'Mr. New Vegas'
    guide = build_style_guide(pretty_name, intros, outros, vocab, starters)
    (DOCS / f"STYLE_GUIDE_{key.upper()}.md").write_text(guide, encoding='utf8')

    return len(segments), {k: len(v) for k, v in categorized.items()}


if __name__ == '__main__':
    report = {}
    for k, p in TRANSCRIPTS.items():
        if not p.exists():
            print(f"Missing transcript for {k} at {p}")
            continue
        cnt, cat_counts = process_transcript(k, p)
        report[k] = {'segments': cnt, 'categories': cat_counts}
    print(json.dumps(report, indent=2))
