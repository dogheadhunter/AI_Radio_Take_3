"""Generate scripts and run the auditor on them.

Usage examples:
  python scripts/generate_with_audit.py --intros --dj all --test --limit 10
"""
import argparse
from pathlib import Path
from datetime import datetime
import json

from src.ai_radio.generation.pipeline import GenerationPipeline
from src.ai_radio.generation.auditor import audit_batch


TEST_SONGS = [
    {"id": f"test{i}", "artist": f"Artist {i}", "title": f"Song {i}"} for i in range(1, 11)
]


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

    songs = TEST_SONGS[:limit]
    selected_djs = [dj] if dj != 'all' else ['julie', 'mr_new_vegas']

    # Generate text scripts (text_only) for each DJ and song
    generated = []
    for d in selected_djs:
        for s in songs:
            res = pipeline.generate_song_intro(song_id=s['id'], artist=s['artist'], title=s['title'], dj=d, text_only=True)
            if res.success and res.text:
                generated.append({"script_id": f"{s['id']}_{d}", "script_content": res.text, "dj": d, "content_type": "song_intro"})

    # Prepare output dir
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = output_base / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Choose auditor client
    client = FakeAuditorClient() if test else None

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
