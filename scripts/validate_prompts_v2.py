"""Manual validation script for prompts_v2 using real Ollama integration."""
import json
from pathlib import Path
from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.llm_client import check_ollama_available
from src.ai_radio.generation.prompts import DJ

# Sample songs for testing
TEST_SONGS = [
    {"id": "test1", "artist": "Nat King Cole", "title": "Mona Lisa", "year": 1950},
    {"id": "test2", "artist": "Ella Fitzgerald", "title": "Dream a Little Dream of Me", "year": 1950},
    {"id": "test3", "artist": "Frank Sinatra", "title": "Fly Me to the Moon", "year": 1964},
    {"id": "test4", "artist": "Billie Holiday", "title": "God Bless the Child", "year": 1941},
    {"id": "test5", "artist": "Louis Armstrong", "title": "What a Wonderful World", "year": 1967},
    {"id": "test6", "artist": "Dean Martin", "title": "That's Amore", "year": 1953},
    {"id": "test7", "artist": "Tony Bennett", "title": "I Left My Heart in San Francisco", "year": 1962},
    {"id": "test8", "artist": "Bing Crosby", "title": "White Christmas", "year": 1942},
    {"id": "test9", "artist": "Judy Garland", "title": "Over the Rainbow", "year": 1939},
    {"id": "test10", "artist": "Doris Day", "title": "Que Sera, Sera", "year": 1956},
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
    
    # Create output directory
    output_dir = Path("data/manual_validation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline with v2 prompts
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
        try:
            result = pipeline_v2.generate_song_intro(
                song_id=song['id'],
                artist=song['artist'],
                title=song['title'],
                dj='julie',
                text_only=True  # Text only for validation
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
        try:
            result = pipeline_v2.generate_song_intro(
                song_id=song['id'],
                artist=song['artist'],
                title=song['title'],
                dj='mr_new_vegas',
                text_only=True
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
    
    # Save results
    results_file = output_dir / "prompt_v2_validation_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Create markdown report
    md_file = output_dir / "prompt_v2_validation_report.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Phase 2 Prompt V2 Validation Results\n\n")
        f.write(f"Generated on: {Path(__file__).parent.parent.name}\n\n")
        
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
