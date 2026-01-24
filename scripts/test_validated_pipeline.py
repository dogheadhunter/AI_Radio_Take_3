"""Test the new validated generation pipeline."""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_radio.generation.validated_pipeline import ValidatedGenerationPipeline, load_lyrics


def load_catalog_songs(catalog_path: Path, limit: int = 5):
    """Load songs from catalog."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    songs = data.get('songs', [])
    return [{"id": s['id'], "artist": s['artist'], "title": s['title']} for s in songs[:limit]]


def main():
    print("=" * 60)
    print("VALIDATED GENERATION PIPELINE TEST")
    print("=" * 60)
    
    # Load songs from catalog
    catalog_path = Path("data/catalog.json")
    if not catalog_path.exists():
        print("ERROR: data/catalog.json not found")
        return 1
    
    songs = load_catalog_songs(catalog_path, limit=3)
    print(f"\nLoaded {len(songs)} songs from catalog")
    
    # Check for lyrics
    lyrics_dir = Path("music_with_lyrics")
    for song in songs:
        lyrics = load_lyrics(song['title'], song['artist'], lyrics_dir)
        if lyrics:
            print(f"  ✓ Found lyrics for: {song['title']}")
        else:
            print(f"  - No lyrics for: {song['title']}")
    
    print("\n" + "=" * 60)
    print("GENERATING WITH VALIDATION")
    print("=" * 60)
    
    # Create validated pipeline
    pipeline = ValidatedGenerationPipeline(
        output_dir=Path("data/generated"),
        prompt_version="v2",
        max_retries=3,
        lyrics_dir=lyrics_dir,
    )
    
    djs = ["julie", "mr_new_vegas"]
    
    # Generate and validate
    results = pipeline.generate_batch(songs, djs)
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.success)
    failed = len(results) - passed
    
    print(f"\nTotal: {len(results)}")
    print(f"Passed: {passed} ({100*passed/len(results):.0f}%)")
    print(f"Failed: {failed}")
    
    # Show details
    print("\n--- PASSED SCRIPTS ---")
    for r in results:
        if r.success and r.script:
            print(f"\n[{r.script.dj}] {r.script.artist} - {r.script.title} (attempts: {r.attempts})")
            print(f"  Rule validation: {r.script.rule_validation.passed if r.script.rule_validation else 'N/A'}")
            print(f"  Character score: {r.script.character_validation.score:.1f}" if r.script.character_validation else "  Character: N/A")
            print(f"  Text: {r.script.text[:100]}...")
    
    print("\n--- FAILED SCRIPTS ---")
    for r in results:
        if not r.success:
            print(f"\n[FAILED] attempts: {r.attempts}")
            for err in r.errors[-3:]:  # Last 3 errors
                print(f"  - {err}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/audit") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        "timestamp": timestamp,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "scripts": [
            {
                "script_id": r.script.script_id,
                "dj": r.script.dj,
                "artist": r.script.artist,
                "title": r.script.title,
                "text": r.script.text,
                "attempts": r.attempts,
                "char_score": r.script.character_validation.score if r.script.character_validation else None,
            }
            for r in results if r.success and r.script
        ],
        "failures": [
            {"attempts": r.attempts, "errors": r.errors}
            for r in results if not r.success
        ]
    }
    
    output_path = output_dir / "validated_generation.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_path}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
