from src.ai_radio.generation.auditor import audit_batch, load_audit_results
from pathlib import Path
import shutil
scripts=[
    {"script_id":"good_julie","script_content":"Hey there, you know, this is Julie. Lovely tune ahead.","dj":"julie"},
    {"script_id":"bad_julie_slang","script_content":"Hey, awesome track! 😀","dj":"julie"},
    {"script_id":"bad_mrnv","script_content":"Yo, that was awesome, totally rad.","dj":"mr_new_vegas"},
    {"script_id":"borderline_julie","script_content":"This is a borderline script with slight drift.","dj":"julie"},
    {"script_id":"good_mrnv","script_content":"A smooth evening, the lights shimmer over the lounge.","dj":"mr_new_vegas"},
]
out=Path('tmp_audit_check')
shutil.rmtree(out, ignore_errors=True)
summary=audit_batch(scripts, out, client=None)
print('SUMMARY:', summary)
for r in load_audit_results(out):
    print(r.script_id, r.passed, r.score, r.content_type)
