"""Generate comparative Differentiation sections and insert into both style guides"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
jul=ROOT/'docs'/'script_improvement'/'STYLE_GUIDE_JULIE.md'
mr=ROOT/'docs'/'script_improvement'/'STYLE_GUIDE_MR_NEW_VEGAS.md'
diff_jul="""
## Differentiation Checklist

- **Tone:** Julie is warm, folksy, and empathetic; Mr. New Vegas is suave, polished, and flirtatious. ✅
- **Pacing:** Julie is conversational and reflective with gentle pauses; Mr. New Vegas is brisk, showman-like, and often promotional. ✅
- **Formality:** Julie is informal and neighborly (uses "friends", personal anecdotes); Mr. New Vegas uses formal salutations ("ladies and gentlemen") and promotional language. ✅
- **Listener Relationship:** Julie speaks as a neighbor and friend; Mr. New Vegas performs *to* the listener with flirtatious charm. ✅
- **Vocabulary Era:** Julie uses Appalachian/local references and nostalgic phrases; Mr. New Vegas uses post-war/New Vegas/casino/news vocabulary. ✅
- **Signature Elements:** Julie references home, family, dancing, and small comforts; Mr. New Vegas uses catchphrases, sponsor mentions, and newsy segues. ✅

### Red Flags (script is wrong for this DJ)
- Julie: uses sponsor-like promos, heavy self-promotion, or overtly flirtatious lines like "I'm your Mr. New Vegas". ⚠️
- Mr. New Vegas: uses rural Appalachian references, overly informal "friends"/personal vulnerability without showmanship. ⚠️

### Quick Check
- If it says "ladies and gentlemen" or mentions casinos → probably Mr. New Vegas.
- If it uses "friends" and talks about home/coalmines/Nuka Cola → probably Julie.
"""

diff_mr=diff_jul

for p,content in [(jul,diff_jul),(mr,diff_mr)]:
    text=p.read_text(encoding='utf8')
    if '## Differentiation Checklist' in text:
        import re
        text=re.sub(r'## Differentiation Checklist[\s\S]*?(?=## Red Flags|\Z)', content, text)
    else:
        text+="\n"+content
    p.write_text(text,encoding='utf8')
print('Inserted differentiation sections')
