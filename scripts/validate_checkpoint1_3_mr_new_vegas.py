from pathlib import Path
import re
p=Path('docs/script_improvement/STYLE_GUIDE_MR_NEW_VEGAS.md')
if not p.exists():
    print('Missing guide'); raise SystemExit(2)
s=p.read_text(encoding='utf8')
# intros
m_intros=re.search(r"## Song Introduction Patterns[\s\S]*?## Song Outro Patterns", s)
intros = re.findall(r"\*\*Example:\*\* \"(.*?)\"", m_intros.group(0), re.S) if m_intros else []
# outros
m_outros=re.search(r"## Song Outro Patterns[\s\S]*?## Vocabulary", s)
outros = re.findall(r"\*\*Example:\*\* \"(.*?)\"", m_outros.group(0), re.S) if m_outros else []
# romantic
rom = re.search(r"## Romantic / Intimate Phrasing[\s\S]*?(?=\n## |\Z)", s)
rom_examples = re.findall(r"- \"(.*?)\"", rom.group(0)) if rom else []
# 1950s vocab table
vocab = re.search(r"## 1950s Vocabulary \(Top Words\)[\s\S]*?(?=\n## |\Z)", s)
vocab_words = re.findall(r"\|\s*([a-zA-Z' ]+)\s*\|\s*(\d+)\s*\|", vocab.group(0)) if vocab else []
# signature phrases
sig = re.search(r"## Signature Phrases[\s\S]*?(?=\n## |\Z)", s)
sigs = re.findall(r"- \"(.*?)\"(?: \((\d+) occurrences\))?", sig.group(0)) if sig else []
# forbidden
forbidden_present = 'modern slang' in s.lower() and 'profanity' in s.lower()
print('intros:',len(intros),'outros:',len(outros),'romantic:',len(rom_examples),'vocab:',len(vocab_words),'sigs:',len(sigs),'forbidden:',forbidden_present)
ok=True
if len(intros) < 10:
    print('FAIL: fewer than 10 intro examples')
    ok=False
if len(outros) < 5:
    print('FAIL: fewer than 5 outro examples')
    ok=False
if len(rom_examples) < 10:
    print('FAIL: fewer than 10 romantic examples')
    ok=False
if len(vocab_words) < 15:
    print('FAIL: fewer than 15 1950s vocab words')
    ok=False
if len(sigs) < 3:
    print('WARN: fewer than 3 signature phrases documented')
# final
if ok:
    print('\nCHECKPOINT 1.3 (Mr. New Vegas) PASSED')
    raise SystemExit(0)
else:
    print('\nCHECKPOINT 1.3 (Mr. New Vegas) FAILED')
    raise SystemExit(2)
