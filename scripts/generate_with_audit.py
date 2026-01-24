"""Generate scripts and run the auditor on them.

Usage examples:
  python scripts/generate_with_audit.py --intros --dj all --test --limit 10
"""
import argparse
from pathlib import Path
from datetime import datetime
import json
import logging
import re

logger = logging.getLogger(__name__)

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.auditor import audit_batch
import re


def load_catalog_songs(catalog_path: Path, limit: int = 10):
    """Load real songs from catalog.json."""
    import json
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    songs = data.get('songs', [])
    # Convert to simpler format
    return [{"id": s['id'], "artist": s['artist'], "title": s['title']} for s in songs[:limit]]


def sanitize_script(text: str) -> str:
    """Remove meta-commentary and sanitize TTS-breaking punctuation."""
    # Remove ALL parenthetical content (often meta-commentary)
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove dates/years
    text = re.sub(r'\b(19|20)\d{2}\b', '', text)  # Remove 4-digit years
    text = re.sub(r'\b\d{4}s\b', '', text)  # Remove decade references like "1940s"
    
    # Fix TTS-breaking punctuation
    text = text.replace('...', '…')  # Convert to single ellipsis character first
    text = re.sub(r'([?!]),', r'\1', text)  # Remove comma after ? or !
    text = re.sub(r'\s*-\s*', ' ', text)  # Remove dashes (often used for em-dash)
        # Fix common punctuation errors
    # Add comma before "and" in certain contexts
    text = re.sub(r'(\w+)\s+(and)\s+(?:we|I|it|that)', r'\1, \2 ', text)
    # Fix run-on questions (add ? before new sentence starting with capital)
    text = re.sub(r'(\w+)\s+([A-Z][a-z]+\s+(?:is|are|was|were|has|have))', r'\1? \2', text)
    # Fix missing periods before "Here's" or "Here are" 
    text = re.sub(r'(\w+)\s+(Here(?:\'s| is| are))', r'\1. \2', text)
        # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix ellipsis at sentence boundaries (…. or ….)
    text = re.sub(r'…\.', '.', text)  # Ellipsis + period → single period
    text = re.sub(r'\.{2,}', '.', text)  # Multiple periods → single period
    
    return text


def truncate_after_song_intro(text: str, artist: str, title: str) -> str:
    """Truncate any text that comes after the song introduction."""
    # First, validate artist name appears correctly (catch typos/truncations)
    # Look for partial matches that might indicate truncation
    artist_parts = artist.split()
    if len(artist_parts) > 1:
        # Check if only part of the name appears (e.g., "Louie Armst" instead of "Louis Armstrong")
        for part in artist_parts:
            if len(part) > 3:  # Only check meaningful parts
                # Look for truncated versions (e.g., "Armst" from "Armstrong")
                pattern = re.escape(part[:4])  # First 4 chars
                if re.search(r'\b' + pattern + r'[a-z]{0,2}\b', text, re.IGNORECASE):
                    # Found potentially truncated name - might be incomplete
                    # Try to verify full name is NOT present
                    if part.lower() not in text.lower():
                        # Truncation detected - reject this script
                        logger.warning(f"Detected truncated artist name in script: expected '{artist}', found partial match")
                        # Return empty to flag for rejection
                        return ""
    
    # Split by sentence boundaries more carefully (avoid splitting on abbreviations like Mr. Mrs. Dr.)
    # Simple approach: protect common abbreviations before splitting
    protected_text = text.replace('Mr.', 'Mr~')
    protected_text = protected_text.replace('Mrs.', 'Mrs~')
    protected_text = protected_text.replace('Ms.', 'Ms~')
    protected_text = protected_text.replace('Dr.', 'Dr~')
    
    sentences = re.split(r'([.!?])\s+', protected_text)
    result = []
    found_intro = False
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        sentence = sentences[i]
        punct = sentences[i+1] if i+1 < len(sentences) else '.'
        
        # Check if this sentence contains artist or title
        has_artist = artist.lower() in sentence.lower()
        has_title = title.lower() in sentence.lower()
        
        result.append(sentence + punct)
        
        # If we found both artist and title in this sentence, stop here
        if has_artist and has_title:
            found_intro = True
            break
        # Or if we found just one and we've already accumulated some text
        elif (has_artist or has_title) and len(result) > 1:
            found_intro = True
            break
    
    if found_intro:
        # Restore protected abbreviations
        final_text = ' '.join(result).strip()
        final_text = final_text.replace('Mr~', 'Mr.')
        final_text = final_text.replace('Mrs~', 'Mrs.')
        final_text = final_text.replace('Ms~', 'Ms.')
        final_text = final_text.replace('Dr~', 'Dr.')
        return final_text
    
    # Fallback: return original if no clear intro found (also restore protections)
    text = text.replace('Mr~', 'Mr.')
    text = text.replace('Mrs~', 'Mrs.')
    text = text.replace('Ms~', 'Ms.')
    text = text.replace('Dr~', 'Dr.')
    return text


class FakeAuditorClient:
    """Simple fake client that returns auditor-style JSON based on script content."""
    def generate(self, prompt: str, *args, **kwargs) -> str:
        # Extract script between '---' markers
        parts = prompt.split('---')
        script = parts[1] if len(parts) >= 2 else prompt
        p = script.lower()
        if "awesome" in p or "😀" in p or "emoji" in p:
            return json.dumps({
                "score": 3,
                "passed": False,
                "criteria_scores": {"character_voice": 4, "era_appropriateness": 2, "forbidden_elements": 1, "natural_flow": 4, "length": 6},
                "issues": ["Uses modern slang or emoji"],
                "notes": "Contains modern slang or emojis"
            })
        if "borderline" in p:
            return json.dumps({
                "score": 6,
                "passed": True,
                "criteria_scores": {"character_voice": 6, "era_appropriateness": 6, "forbidden_elements": 10, "natural_flow": 6, "length": 6},
                "issues": ["Slight character drift"],
                "notes": "Borderline but acceptable"
            })
        # default good
        return json.dumps({
            "score": 8,
            "passed": True,
            "criteria_scores": {"character_voice": 8, "era_appropriateness": 8, "forbidden_elements": 10, "natural_flow": 8, "length": 8},
            "issues": [],
            "notes": "Good"
        })


def generate_and_audit(intros: bool, dj: str, limit: int, test: bool, output_base: Path):
    pipeline = GenerationPipeline(output_dir=Path('data/generated'), prompt_version='v2')

    # Load real songs from catalog
    catalog_path = Path('data/catalog.json')
    if catalog_path.exists() and not test:
        songs = load_catalog_songs(catalog_path, limit)
    else:
        # Fallback for test mode
        songs = [{"id": f"test{i}", "artist": f"Test Artist {i}", "title": f"Test Song {i}"} for i in range(1, limit + 1)]
    
    selected_djs = [dj] if dj != 'all' else ['julie', 'mr_new_vegas']

    # Generate text scripts (text_only) for each DJ and song
    generated = []
    if test:
        # In test mode, generate deterministic placeholder scripts to avoid calling LLM
        for d in selected_djs:
            for s in songs:
                text = f"This is a test script for {d}. Introducing {s['title']} by {s['artist']}."
                generated.append({"script_id": f"{s['id']}_{d}", "script_content": text, "dj": d, "content_type": "song_intro"})
    else:
        for d in selected_djs:
            for s in songs:
                res = pipeline.generate_song_intro(song_id=s['id'], artist=s['artist'], title=s['title'], dj=d, text_only=True)
                if res.success and res.text:
                    # Sanitize script to remove meta-commentary and TTS-breaking punctuation
                    sanitized = sanitize_script(res.text)
                    # Truncate any text after song introduction (also validates artist name)
                    truncated = truncate_after_song_intro(sanitized, s['artist'], s['title'])
                    # Final cleanup: fix double periods that might have been created by truncation
                    truncated = re.sub(r'\.{2,}', '.', truncated) if truncated else ""
                    # Skip if validation failed (empty string returned)
                    if truncated:
                        generated.append({"script_id": f"{s['id']}_{d}", "script_content": truncated, "dj": d, "content_type": "song_intro"})
                    else:
                        logger.warning(f"Skipping script {s['id']}_{d} due to validation failure")
    # Prepare output dir
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = output_base / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Choose auditor client
    client = FakeAuditorClient() if test else None

    # Save generated scripts for traceability
    (out_dir / 'generated_scripts.json').write_text(
        json.dumps({"scripts": generated}, indent=2, ensure_ascii=False), 
        encoding='utf-8'
    )

    summary = audit_batch(generated, out_dir, client=client)

    # Write validation doc
    validation = {
        "timestamp": timestamp,
        "total_generated": len(generated),
        "audit_summary": summary,
    }
    (out_dir / 'AUDIT_SUMMARY.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')

    # Simple AUDITOR_VALIDATION.md placeholder
    md = f"# Auditor Validation\n\nGenerated: {len(generated)} scripts\n\nAudit summary:\n\n- total: {summary['total']}\n- passed: {summary['passed']}\n- failed: {summary['failed']}\n\nHuman validation: TBD\n"
    (out_dir / 'AUDITOR_VALIDATION.md').write_text(md, encoding='utf-8')

    print("Audit complete:", summary)
    print("Results saved to", out_dir)
    return out_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--intros', action='store_true', help='Generate song intros')
    parser.add_argument('--dj', default='all', choices=['all', 'julie', 'mr_new_vegas'])
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--test', action='store_true', help='Run in test mode with fake auditor')
    parser.add_argument('--output', default='data/audit')
    args = parser.parse_args()

    if not args.intros:
        parser.error('Currently only --intros is supported')

    out_dir = generate_and_audit(intros=True, dj=args.dj, limit=args.limit, test=args.test, output_base=Path(args.output))
    return 0


if __name__ == '__main__':
    main()
