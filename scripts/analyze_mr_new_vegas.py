"""Analyze Mr. New Vegas transcript for patterns required by Checkpoint 1.3
- Extract intro/outro examples
- Identify romantic phrasing examples
- Compile 1950s-ish vocabulary list (top words)
- Note pacing markers (pauses, interjections)
- Identify signature phrases
- Update STYLE_GUIDE_MR_NEW_VEGAS.md
"""
import json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'data'/'style_analysis'/'mr_new_vegas_categorized.json'
OUT=ROOT/'docs'/'script_improvement'/'STYLE_GUIDE_MR_NEW_VEGAS.md'
if not IN.exists():
    print('Missing',IN); raise SystemExit(1)
cat=json.load(open(IN,'r',encoding='utf8'))
segments=[s for v in cat.values() for s in v]
# intros and outros
intros=cat.get('song_intro',[])[:50]
outros=cat.get('song_outro',[])[:50]
# romantic phrasing: lines containing love/kiss/darling/you are beautiful/you deserve
rom_keys=["love","kiss","darling","special someone","i love you","you are wonderful","beautiful","you're listening to me"]
romantic=[]
for s in segments:
    ls=s.lower()
    for k in rom_keys:
        if k in ls:
            romantic.append(s); break
# signature phrases (exact repeats)
sig_counts=Counter([s.strip() for s in segments])
signature=[(t,c) for t,c in sig_counts.most_common() if c>1][:20]
# 1950s vocabulary: top words
words=[]
for s in segments:
    toks=re.findall(r"\b[a-z']{3,}\b", s.lower())
    words.extend(toks)
stop=set(['the','and','you','your','i','a','that','it','to','of','in','for','is','we','on','with','this','are','as','be','have','my','not','they','but','what','so'])
wc=Counter([w for w in words if w not in stop])
top_words=wc.most_common(50)
# pacing markers: look for short interjections, ellipses, exclamations
pauses=[s for s in segments if '...' in s or '--' in s or re.search(r"\b(uh|huh|oh|ah|hmm)\b", s.lower())]
exclaims=[s for s in segments if '!' in s]
# Update guide
template=OUT.read_text(encoding='utf8') if OUT.exists() else '# Style Guide: Mr. New Vegas\n\n'
rom_md='''\n## Romantic / Intimate Phrasing\n\nExamples where Mr. New Vegas addresses the listener directly in a romantic/intimate tone:\n\n'''
for s in romantic[:20]:
    rom_md+=f'- "{s}"\n'
sig_md='''\n## Signature Phrases\n\nRecurring lines or catchphrases used by Mr. New Vegas:\n\n'''
for t,c in signature[:20]:
    sig_md+=f'- "{t}" ({c} occurrences)\n'
words_md='''\n## 1950s Vocabulary (Top Words)\n\n| Word | Count |\n|------:|------:|\n'''
for w,c in top_words[:30]:
    words_md+=f'| {w} | {c} |\n'
pace_md='''\n## Pacing & Markers\n\n- Pauses/Interjections examples (short lines, "uh", "hmm", etc.):\n'''
for s in pauses[:8]:
    pace_md+=f'  - "{s}"\n'
pace_md+='\n- Exclamations and emphatic lines:\n'
for s in exclaims[:8]:
    pace_md+=f'  - "{s}"\n'
forbidden_md='''\n## Forbidden\n\n- Modern slang and profanity should be avoided when writing for Mr. New Vegas.\n- Avoid harsh, aggressive language that breaks his suave persona.\n'''
# Merge into document
out=template
for sec,md in [('## Romantic / Intimate Phrasing',rom_md),('## Signature Phrases',sig_md),('## 1950s Vocabulary (Top Words)',words_md),('## Pacing & Markers',pace_md),('## Forbidden',forbidden_md)]:
    if sec in out:
        out=re.sub(rf"{re.escape(sec)}[\s\S]*?(?=\n## |\Z)", md, out)
    else:
        out+=md
OUT.write_text(out,encoding='utf8')
print('Updated',OUT)
print('Intros:',len(intros),'Outros:',len(outros),'Romantic examples:',len(romantic),'Signature count:',len(signature))
print('Top words:',top_words[:20])
