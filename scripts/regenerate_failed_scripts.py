"""Regenerate only the failed scripts from human validation."""
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_radio.generation.validated_pipeline import ValidatedGenerationPipeline


def main():
    print("=" * 70)
    print("REGENERATING FAILED SCRIPTS")
    print("=" * 70)
    
    # Failed scripts from human validation
    failed_scripts = [
        {
            "id": "2",
            "artist": "Louis Armstrong",
            "title": "A Kiss to Build a Dream On",
            "dj": "julie",
            "reason": "Too flowery/poetic - needs grounded conversational tone"
        },
        {
            "id": "5",
            "artist": "Fats Waller",
            "title": "Ain't Misbehavin'",
            "dj": "mr_new_vegas",
            "reason": "Too aggressive/preachy - needs smooth lounge host tone"
        }
    ]
    
    print(f"\nRegenerating {len(failed_scripts)} failed scripts")
    print("Updated validator with refined red flags:")
    print("  - Julie: Detecting flowery/poetic language")
    print("  - Mr. NV: Detecting aggressive/preachy/critic language")
    print()
    
    # Create pipeline with refined validators
    pipeline = ValidatedGenerationPipeline(
        prompt_version='v2',
        max_retries=3,
    )
    
    # Regenerate each failed script
    results = []
    for script_info in failed_scripts:
        print(f"\nRegenerating {script_info['id']}_{script_info['dj']}:")
        print(f"  Artist: {script_info['artist']}")
        print(f"  Title: {script_info['title']}")
        print(f"  Issue: {script_info['reason']}")
        
        result = pipeline.generate_song_intro(
            song_id=script_info['id'],
            artist=script_info['artist'],
            title=script_info['title'],
            dj=script_info['dj'],
        )
        
        results.append((script_info, result))
        
        if result.success:
            print(f"  ✓ Passed after {result.attempts} attempt(s)")
            print(f"  Character score: {result.script.character_validation.score:.1f}")
            print(f"  Text: {result.script.text[:100]}...")
        else:
            print(f"  ✗ Still failed after {result.attempts} attempts")
            if result.errors:
                print(f"  Errors: {result.errors[-1]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("REGENERATION RESULTS")
    print("=" * 70)
    
    passed = [r for _, r in results if r.success]
    failed = [r for _, r in results if not r.success]
    
    print(f"Passed: {len(passed)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")
    
    if passed:
        print("\nAttempts needed:")
        attempts_dist = {}
        for r in passed:
            attempts_dist[r.attempts] = attempts_dist.get(r.attempts, 0) + 1
        for attempts in sorted(attempts_dist.keys()):
            print(f"  {attempts} attempt(s): {attempts_dist[attempts]} scripts")
    
    # Save regenerated scripts to new review file
    if passed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("data/manual_validation")
        csv_path = output_dir / f"regenerated_{timestamp}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'script_id', 'dj', 'artist', 'title', 
                'attempts', 'rule_passed', 'char_score',
                'script_text', 'original_issue', 'human_passed', 'human_notes'
            ])
            
            for script_info, r in results:
                if r.success:
                    script = r.script
                    writer.writerow([
                        script.script_id,
                        script.dj,
                        script.artist,
                        script.title,
                        r.attempts,
                        'True',
                        f"{script.character_validation.score:.1f}",
                        script.text,
                        script_info['reason'],
                        '',  # human_passed
                        '',  # human_notes
                    ])
        
        print(f"\nRegenerated scripts saved to: {csv_path}")
    
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
