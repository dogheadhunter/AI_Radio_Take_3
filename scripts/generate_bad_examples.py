"""Generate intentionally bad scripts to test the auditor's ability to detect failures."""
from pathlib import Path
import json

BAD_TEMPLATES = [
    "Hey, awesome track! 😀 Totally rad.",
    "Yo, that's sick! This ain't your grandma's music.",
    "This is generic DJ speak; not julie at all.",
    "Use modern slang like awesome, lit, etc.",
    "Contains emoji 😀 and 👍 which are forbidden.",
]


def generate(out_dir: Path, dj: str = 'julie', n: int = 5):
    out_dir.mkdir(parents=True, exist_ok=True)
    scripts = []
    for i in range(n):
        text = BAD_TEMPLATES[i % len(BAD_TEMPLATES)]
        sid = f'bad_{i+1}_{dj}'
        p = out_dir / f'{sid}.json'
        data = {'script_id': sid, 'script_content': text, 'dj': dj, 'content_type': 'song_intro'}
        p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        scripts.append(data)
    return scripts


if __name__ == '__main__':
    out = Path('data/generated_bad')
    s = generate(out, dj='julie', n=5)
    print('Wrote', len(s), 'bad scripts to', out)