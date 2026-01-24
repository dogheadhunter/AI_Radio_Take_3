import json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IN_DIR=ROOT/'data'/'style_analysis'
OUT_DIR=ROOT/'docs'/'script_improvement'
OUT_DIR.mkdir(parents=True, exist_ok=True)
for name in ['julie','mr_new_vegas']:
    c=json.load(open(IN_DIR/f'{name}_categorized.json','r',encoding='utf8'))
    all_segments=[s for v in c.values() for s in v]
    random.seed(42)
    samples=random.sample(all_segments, min(10,len(all_segments)))
    out=OUT_DIR/f'{name}_validation_samples.md'
    with open(out,'w',encoding='utf8') as f:
        f.write(f'# Validation samples for {name}\n\n')
        for i,s in enumerate(samples,1):
            f.write(f'## Sample {i}\n{s}\n\n')
    print('Wrote',out)
