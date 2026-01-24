from pathlib import Path
import re, json, sys
p=Path('data/style_analysis')
ok=True
for name in ['julie','mr_new_vegas']:
    cleaned=p/(name+'_cleaned.txt')
    cat=p/(name+'_categorized.json')
    if not cleaned.exists() or not cat.exists():
        print(f'MISSING: {name} files')
        ok=False
        continue
    txt=cleaned.read_text(encoding='utf8')
    has_ts = bool(re.search(r"\d{2}:\d{2}:\d{2}", txt))
    seg_count = sum(1 for _ in txt.splitlines() if _.strip())
    c=json.load(open(cat,'r',encoding='utf8'))
    cats=list(c.keys())
    cat_counts={k:len(v) for k,v in c.items()}
    total_categorized=sum(cat_counts.values())
    print(f"{name}: has_timestamp={has_ts}, lines={seg_count}, categories={cats}, cat_counts={cat_counts}, total_categorized={total_categorized}")
    # Success criteria for checkpoint 1.1
    if has_ts:
        print('FAIL: timestamps remain')
        ok=False
    if not set(['song_intro','song_outro','commentary','time','weather','other']).issubset(set(cats)):
        print('FAIL: missing categories')
        ok=False
    if total_categorized < 20:
        print('FAIL: fewer than 20 categorized segments')
        ok=False
if ok:
    print('\nCHECKPOINT 1.1 PASSED')
    sys.exit(0)
else:
    print('\nCHECKPOINT 1.1 FAILED')
    sys.exit(2)
