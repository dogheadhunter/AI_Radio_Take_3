"""Generate validated scripts for human review using new pipeline."""
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_radio.generation.validated_pipeline import ValidatedGenerationPipeline


def main():
    print("=" * 70)
    print("VALIDATED SCRIPT GENERATION")
    print("=" * 70)
    
    # Load catalog
    catalog_path = Path("data/catalog.json")
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Take first 10 songs
    songs = [
        {"id": s['id'], "artist": s['artist'], "title": s['title']}
        for s in catalog['songs'][:10]
    ]
    
    print(f"\nGenerating scripts for {len(songs)} songs × 2 DJs = {len(songs) * 2} scripts")
    print("Using multi-stage validation:")
    print("  1. Generation with lyrics context")
    print("  2. Rule-based validation (encoding, punctuation, structure)")
    print("  3. LLM character validation (voice, naturalness)")
    print("  4. Auto-regeneration if validation fails (max 3 attempts)")
    print()
    
    # Create pipeline
    pipeline = ValidatedGenerationPipeline(
        prompt_version='v2',
        max_retries=3,
    )
    
    # Generate
    djs = ['julie', 'mr_new_vegas']
    results = pipeline.generate_batch(songs, djs)
    
    # Summary
    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Passed: {len(passed)}/{len(results)} ({100*len(passed)/len(results):.0f}%)")
    print(f"Failed: {len(failed)}")
    
    # Show attempt distribution
    if passed:
        attempts_dist = {}
        for r in passed:
            attempts_dist[r.attempts] = attempts_dist.get(r.attempts, 0) + 1
        print("\nAttempts needed:")
        for attempts in sorted(attempts_dist.keys()):
            print(f"  {attempts} attempt(s): {attempts_dist[attempts]} scripts")
    
    # Save to review format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/manual_validation")
    output_dir.mkdir(exist_ok=True)
    
    # Save as CSV for review
    csv_path = output_dir / f"review_{timestamp}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'script_id', 'dj', 'artist', 'title', 
            'attempts', 'rule_passed', 'char_score',
            'script_text', 'human_passed', 'human_notes'
        ])
        
        for r in passed:
            script = r.script
            writer.writerow([
                script.script_id,
                script.dj,
                script.artist,
                script.title,
                r.attempts,
                'True',
                f"{script.character_validation.score:.1f}" if script.character_validation else '',
                script.text,
                '',  # human_passed
                '',  # human_notes
            ])
    
    # Save as JSON for backup
    json_path = output_dir / f"review_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total": len(results),
            "passed": len(passed),
            "failed": len(failed),
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
                for r in passed
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nReview files saved:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    
    # Convert CSV to Markdown for easier reading
    import subprocess
    try:
        subprocess.run([
            sys.executable, "-m", "scripts.csv_to_markdown",
            "--csv", str(csv_path),
            "--out", str(output_dir / f"review_{timestamp}.md")
        ], check=True)
        print(f"  MD:  {output_dir / f'review_{timestamp}.md'}")
    except:
        pass
    
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
