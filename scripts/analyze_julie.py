"""Analyze Julie transcripts to produce detailed pattern extras for STYLE_GUIDE_JULIE.md
- filler word inventory with counts and contexts
- sentence starters top list
- vocabulary table with counts
- ensure forbidden list includes modern slang/profanity
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'data'/'style_analysis'/'julie_categorized.json'
OUT=ROOT/'docs'/'script_improvement'/'STYLE_GUIDE_JULIE.md'
if not IN.exists():
    print('Missing input:', IN); raise SystemExit(1)
c=json.load(open(IN,'r',encoding='utf8'))
segments=[s for v in c.values() for s in v]
# filler candidates
FILLERS = ['oh','well','you know','i mean','just','like','friends','hey','uh','hmm','ah','okay','actually','maybe']
filler_counts=Counter()
filler_contexts=defaultdict(list)
for s in segments:
    sl=s.lower()
    for f in FILLERS:
        if re.search(rf"\b{re.escape(f)}\b", sl):
            filler_counts[f]+=len(re.findall(rf"\b{re.escape(f)}\b", sl))
            if len(filler_contexts[f])<3:
                filler_contexts[f].append(s.strip())
# starters
starters=[ ' '.join(s.split()[:6]).strip() for s in segments if s.strip()]
starter_counts=Counter(starters)
# vocabulary
words=[]
for s in segments:
    toks=re.findall(r"\b[a-z']{3,}\b", s.lower())
    words.extend(toks)
stopset=set(['the','and','you','your','i','a','that','it','to','of','in','for','is','we','on','with','this','are','as','be','have','my','not','they','but','what','so'])
words_cleaned=[w for w in words if w not in stopset]
word_counts=Counter(words_cleaned).most_common(50)
# prepare outputs
filler_lines=[]
for f,count in filler_counts.most_common():
    contexts=' | '.join([c.replace('\n',' ') for c in filler_contexts[f]])
    filler_lines.append((f,count,contexts))
starter_top=[(s,c) for s,c in starter_counts.most_common(20)]
# read existing guide and update sections
template=OUT.read_text(encoding='utf8') if OUT.exists() else '# Style Guide: Julie\n\n'
# Insert Filler Words section
filler_md='''\n## Filler Words Inventory\n\nThe following fillers are commonly used by Julie (count = occurrences across segments):\n\n| Filler | Count | Example contexts |\n|--------|-------:|------------------|\n'''
for f,count,contexts in filler_lines:
    filler_md+=f'| {f} | {count} | {contexts} |\n'
# Insert Vocabulary table
vocab_md='''\n## Vocabulary (Top Words)\n\n| Word | Count |\n|------:|------:|\n'''
for w,c in word_counts[:30]:
    vocab_md+=f'| {w} | {c} |\n'
# Forbidden list
forbidden_md='''\n## Forbidden\n\n- Modern slang (e.g., "lit", "bruh", "OMG") — avoid to keep era-appropriate voice.\n- Profanity — Julie does not use explicit profanity in her lines.\n'''
# Starters
starters_md='''\n## Sentence Starters (Top)\n\n'''
for s,c in starter_top[:15]:
    starters_md+=f'- "{s}" ({c} occurrences)\n'
# Now replace or append these sections to guide
# We'll append to the end if not present, or replace existing headers
out=template
if '## Filler Words Inventory' in out:
    out=re.sub(r'## Filler Words Inventory[\s\S]*?(?=## Sentence Structures|$)', filler_md, out)
else:
    out+=filler_md
if '## Vocabulary (Top Words)' in out:
    out=re.sub(r'## Vocabulary \(Top Words\)[\s\S]*?(?=## Sentence Structures|$)', vocab_md, out)
else:
    out+=vocab_md
if '## Forbidden' in out:
    out=re.sub(r'## Forbidden[\s\S]*?(?=## Sentence Structures|$)', forbidden_md, out)
else:
    out+=forbidden_md
if '## Sentence Starters' in out:
    out=re.sub(r'## Sentence Starters[\s\S]*?(?=## Differentiation Checklist|$)', starters_md, out)
else:
    out+=starters_md
OUT.write_text(out,encoding='utf8')
print('Updated', OUT)
print('Top fillers:', filler_counts.most_common(10))
print('Top starters:', starter_top[:10])
print('Top vocab:', word_counts[:20])
