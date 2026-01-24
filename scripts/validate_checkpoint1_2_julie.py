from pathlib import Path
import re
p=Path('docs/script_improvement/STYLE_GUIDE_JULIE.md')
if not p.exists():
    print('Missing style guide'); raise SystemExit(2)
s=p.read_text(encoding='utf8')
# intros: count occurrences of 'Pattern' examples in Intro section
intros = re.findall(r"## Song Introduction Patterns[\s\S]*?## Song Outro Patterns", s)
intro_examples = re.findall(r"\*\*Example:\*\* \"(.*?)\"", intros[0], re.S) if intros else []
# outros
outros_section = re.findall(r"## Song Outro Patterns[\s\S]*?## Vocabulary", s)
outro_examples = re.findall(r"\*\*Example:\*\* \"(.*?)\"", outros_section[0], re.S) if outros_section else []
# filler inventory
has_filler = '## Filler Words Inventory' in s
# starters
m = re.search(r"## Sentence Starters(?:.*)\n([\s\S]*?)(?=\n## |\Z)", s)
if m:
    starter_block = m.group(1)
    starters = re.findall(r"- \"(.*?)\"", starter_block)
else:
    starters = []
# vocabulary list count
vocab_table = re.findall(r"## Vocabulary \(Top Words\)[\s\S]*?## Forbidden", s)
vocab_words = re.findall(r"\|\s*([a-zA-Z' ]+)\s*\|\s*(\d+)\s*\|", vocab_table[0]) if vocab_table else []
forbidden = 'modern slang' in s.lower() and 'profanity' in s.lower()
print('intro_examples:', len(intro_examples))
print('outro_examples:', len(outro_examples))
print('has_filler:', has_filler)
print('starters_count:', len(starters))
print('vocab_count:', len(vocab_words))
print('forbidden_present:', forbidden)
ok=True
if len(intro_examples) < 10:
    print('FAIL: fewer than 10 intro examples')
    ok=False
if len(outro_examples) < 5:
    print('FAIL: fewer than 5 outro examples')
    ok=False
if not has_filler:
    print('FAIL: filler inventory missing')
    ok=False
if len(starters) < 10:
    print('FAIL: fewer than 10 sentence starters')
    ok=False
if len(vocab_words) < 20:
    print('FAIL: fewer than 20 vocab words')
    ok=False
if not forbidden:
    print('FAIL: forbidden list incomplete')
    ok=False
if ok:
    print('\nCHECKPOINT 1.2 (Julie) PASSED')
    raise SystemExit(0)
else:
    print('\nCHECKPOINT 1.2 (Julie) FAILED')
    raise SystemExit(2)
