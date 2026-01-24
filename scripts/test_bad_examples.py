"""Test auditor on bad examples to verify failure detection."""
from pathlib import Path
import json
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.ai_radio.generation.auditor import audit_script
from src.ai_radio.generation.llm_client import check_ollama_available

def main():
    if not check_ollama_available():
        print("❌ Ollama not available - cannot run real auditor test")
        return 1
    
    bad_dir = Path("data/generated_bad")
    bad_files = sorted(bad_dir.glob("*.json"))
    
    if not bad_files:
        print("❌ No bad examples found in data/generated_bad")
        return 1
    
    print(f"Testing auditor on {len(bad_files)} bad examples...\n")
    
    results = []
    for bad_file in bad_files:
        with open(bad_file, 'r', encoding='utf-8') as f:
            bad = json.load(f)
        
        # Handle both old and new formats
        script_text = bad.get('text') or bad.get('script_content', '')
        script_id = bad.get('script_id', bad_file.stem)
        dj = bad.get('dj', 'julie')
        
        print(f"Testing: {script_id}")
        print(f"  Text: {script_text[:60]}...")
        
        result = audit_script(
            client=None,  # Use default Ollama client
            script_content=script_text,
            script_id=script_id,
            dj=dj,
            content_type=bad.get('content_type', 'song_intro')
        )
        
        passed_str = "❌ PASSED (SHOULD FAIL)" if result.passed else "✅ FAILED (EXPECTED)"
        print(f"  Score: {result.score:.1f} - {passed_str}")
        print(f"  Issues: {result.issues}")
        print(f"  Notes: {result.notes}\n")
        
        results.append({
            "script_id": script_id,
            "expected_issues": bad.get('expected_issues', []),
            "actual_score": result.score,
            "actual_passed": result.passed,
            "actual_issues": result.issues,
            "criteria_scores": result.criteria_scores,
        })
    
    # Summary
    failed_count = sum(1 for r in results if not r['actual_passed'])
    print(f"\n{'='*70}")
    print(f"SUMMARY: {failed_count}/{len(results)} correctly failed")
    
    if failed_count == len(results):
        print("✅ ALL bad examples caught by auditor!")
    else:
        print(f"⚠️  {len(results) - failed_count} false negatives (bad scripts that passed)")
    
    # Save results
    output = Path("data/audit/bad_examples_audit.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output}")
    
    return 0 if failed_count == len(results) else 1


if __name__ == "__main__":
    exit(main())
