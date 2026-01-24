"""Manual validation script for prompts_v2 using real Ollama integration."""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.llm_client import check_ollama_available
from src.ai_radio.generation.prompts import DJ

# Lyrics folder path
LYRICS_FOLDER = Path(__file__).parent.parent / "music_with_lyrics"

def extract_theme_from_lyrics(artist: str, title: str) -> str:
    """Extract opening lyrics from LRC format files to give LLM concrete song content.
    
    WHY: LLM needs actual song material to reduce semantic pressure. Without lyrics,
    it defaults to generic descriptions ('sultry vocals', 'crooning') from training data.
    With lyrics, it can make specific observations about the song's actual content.
    """
    # Try to find matching lyrics file
    pattern = f"{title} by {artist}.txt"
    lyrics_file = LYRICS_FOLDER / pattern
    
    if not lyrics_file.exists():
        # Try partial match
        for f in LYRICS_FOLDER.glob("*.txt"):
            if title.lower() in f.name.lower() and artist.split()[0].lower() in f.name.lower():
                lyrics_file = f
                break
    
    if not lyrics_file.exists():
        return ""
    
    try:
        with open(lyrics_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse LRC format: lines like "[00:15.69] Never know how much I love you"
        # Extract clean lyrics (strip timestamps) from opening verse
        import re
        lyric_lines = []
        
        for line in lines:
            # Match LRC timestamp pattern [MM:SS.xx] or [HH:MM:SS.xx]
            match = re.match(r'^\[[\d:\.]+\]\s*(.+)$', line)
            if match:
                lyric_text = match.group(1).strip()
                if lyric_text and not lyric_text.startswith('='):  # Skip separator lines
                    lyric_lines.append(lyric_text)
                    # Get first verse/chorus (4-6 lines usually enough for context)
                    if len(lyric_lines) >= 6:
                        break
        
        if lyric_lines:
            # Return opening lyrics as context - gives LLM concrete material to reference
            # Format: Simple description of what the song is about based on opening lines
            opening = " / ".join(lyric_lines[:3])  # First 3 lines for brevity
            return f"Opening lines: {opening}"
        return ""
    except Exception as e:
        return ""

# Sample songs for testing - use songs we have lyrics for
TEST_SONGS = [
    {"id": "test1", "artist": "Billie Holiday", "title": "All of Me", "year": 1941},
    {"id": "test2", "artist": "The Ink Spots", "title": "Address Unknown", "year": 1939},
    {"id": "test3", "artist": "Frank Sinatra", "title": "Blue Moon", "year": 1961},
    {"id": "test4", "artist": "Billie Holiday", "title": "God Bless the Child", "year": 1941},
    {"id": "test5", "artist": "Louis Armstrong", "title": "A Kiss to Build a Dream On", "year": 1951},
    {"id": "test6", "artist": "Dean Martin", "title": "Everybody Loves Somebody Sometimes", "year": 1964},
    {"id": "test7", "artist": "Peggy Lee", "title": "Fever", "year": 1958},
    {"id": "test8", "artist": "Bing Crosby", "title": "Dear Hearts And Gentle People", "year": 1949},
    {"id": "test9", "artist": "Fats Waller", "title": "Aint Misbehavin", "year": 1929},
    {"id": "test10", "artist": "Bob Wills", "title": "Bubbles In My Beer", "year": 1947},
]

def main():
    print("=" * 60)
    print("PHASE 2 MANUAL VALIDATION - PROMPTS V2")
    print("=" * 60)
    
    # Check Ollama
    if not check_ollama_available():
        print("\n❌ ERROR: Ollama is not available!")
        print("Please start Ollama before running this script:")
        print("  1. Run: ollama serve")
        print("  2. Ensure model is pulled: ollama pull llama2")
        return 1
    
    print("\n✅ Ollama is available")
    print("📝 Using fluffy/l3-8b-stheno-v3.2 model for script generation")
    
    # Create output directory
    output_dir = Path("data/manual_validation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline with v2 prompts (uses fluffy model by default from llm_client.py)
    pipeline_v2 = GenerationPipeline(output_dir=output_dir, prompt_version='v2')
    
    results = {
        "julie": [],
        "mr_new_vegas": []
    }
    
    # Generate Julie intros
    print("\n" + "=" * 60)
    print("GENERATING JULIE INTROS (v2 prompts)")
    print("=" * 60)
    for i, song in enumerate(TEST_SONGS, 1):
        print(f"\n[{i}/10] {song['artist']} - {song['title']}")
        # Extract lyrics context for this song
        lyrics_context = extract_theme_from_lyrics(song['artist'], song['title'])
        if lyrics_context:
            print(f"   📝 {lyrics_context[:60]}...")
        try:
            result = pipeline_v2.generate_song_intro(
                song_id=song['id'],
                artist=song['artist'],
                title=song['title'],
                dj='julie',
                text_only=True,  # Text only for validation
                lyrics_context=lyrics_context
            )
            if result.success:
                print(f"✅ Generated: {result.text[:80]}...")
                results["julie"].append({
                    "song": f"{song['artist']} - {song['title']}",
                    "text": result.text,
                    "score": "",
                    "notes": ""
                })
            else:
                print(f"❌ Failed: {result.error}")
                results["julie"].append({
                    "song": f"{song['artist']} - {song['title']}",
                    "text": f"FAILED: {result.error}",
                    "score": "0",
                    "notes": "Generation failed"
                })
        except Exception as e:
            print(f"❌ Exception: {e}")
            results["julie"].append({
                "song": f"{song['artist']} - {song['title']}",
                "text": f"ERROR: {e}",
                "score": "0",
                "notes": "Exception during generation"
            })
    
    # Generate Mr. New Vegas intros
    print("\n" + "=" * 60)
    print("GENERATING MR. NEW VEGAS INTROS (v2 prompts)")
    print("=" * 60)
    for i, song in enumerate(TEST_SONGS, 1):
        print(f"\n[{i}/10] {song['artist']} - {song['title']}")
        # Extract lyrics context for this song
        lyrics_context = extract_theme_from_lyrics(song['artist'], song['title'])
        if lyrics_context:
            print(f"   📝 {lyrics_context[:60]}...")
        try:
            result = pipeline_v2.generate_song_intro(
                song_id=song['id'],
                artist=song['artist'],
                title=song['title'],
                dj='mr_new_vegas',
                text_only=True,
                lyrics_context=lyrics_context
            )
            if result.success:
                print(f"✅ Generated: {result.text[:80]}...")
                results["mr_new_vegas"].append({
                    "song": f"{song['artist']} - {song['title']}",
                    "text": result.text,
                    "score": "",
                    "notes": ""
                })
            else:
                print(f"❌ Failed: {result.error}")
                results["mr_new_vegas"].append({
                    "song": f"{song['artist']} - {song['title']}",
                    "text": f"FAILED: {result.error}",
                    "score": "0",
                    "notes": "Generation failed"
                })
        except Exception as e:
            print(f"❌ Exception: {e}")
            results["mr_new_vegas"].append({
                "song": f"{song['artist']} - {song['title']}",
                "text": f"ERROR: {e}",
                "score": "0",
                "notes": "Exception during generation"
            })
    
    # Save results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"prompt_v2_validation_results_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Create markdown report with timestamp
    md_file = output_dir / f"prompt_v2_validation_report_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Phase 2 Prompt V2 Validation Results\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: fluffy/l3-8b-stheno-v3.2\n")
        f.write(f"Prompt Version: v2\n\n")
        
        f.write("## Julie Intros\n\n")
        f.write("| Song | Generated Text | Score (1-10) | Notes |\n")
        f.write("|------|----------------|--------------|-------|\n")
        for r in results["julie"]:
            text_preview = r['text'].replace('\n', ' ')[:100]
            f.write(f"| {r['song']} | {text_preview}... | {r['score']} | {r['notes']} |\n")
        f.write("\n**Average:** ___ / 10\n\n")
        
        f.write("## Mr. New Vegas Intros\n\n")
        f.write("| Song | Generated Text | Score (1-10) | Notes |\n")
        f.write("|------|----------------|--------------|-------|\n")
        for r in results["mr_new_vegas"]:
            text_preview = r['text'].replace('\n', ' ')[:100]
            f.write(f"| {r['song']} | {text_preview}... | {r['score']} | {r['notes']} |\n")
        f.write("\n**Average:** ___ / 10\n\n")
        
        f.write("## Differentiation Test\n\n")
        f.write("- Same song, both DJs: Can you tell them apart? ___\n")
        f.write("- Character bleed-through detected? ___\n\n")
        f.write("## Overall Pass: ___\n")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print(f"\n📄 Results saved to:")
    print(f"  - {results_file}")
    print(f"  - {md_file}")
    print("\n📝 Next steps:")
    print("  1. Review the generated intros in the markdown file")
    print("  2. Rate each intro 1-10 on character accuracy")
    print("  3. Fill in the score column and average")
    print("  4. Complete the differentiation test")
    print("  5. If average > 7, mark Phase 2.2 and 2.3 as complete")
    
    return 0

if __name__ == "__main__":
    exit(main())
