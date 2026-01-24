from src.ai_radio.generation import llm_client
from src.ai_radio.generation.auditor import audit_batch, load_audit_results
from pathlib import Path
import shutil
import json

def _generate(client, prompt):
    parts = prompt.split('---')
    script_text = parts[1] if len(parts) >= 2 else prompt
    p = script_text.lower()
    if "awesome" in p or "emoji" in p or "😀" in p or "👍" in p:
        return json.dumps({
            "score": 3,
            "passed": False,
            "criteria_scores": {"character_voice": 4, "era_appropriateness": 2, "forbidden_elements": 1, "natural_flow": 4, "length": 6},
            "issues": ["Uses modern slang or emoji"],
            "notes": "Contains modern slang or emojis"
        })
    if "sounds like generic dj" in p or "not julie" in p:
        return json.dumps({
            "score": 3,
            "passed": False,
            "criteria_scores": {"character_voice": 2, "era_appropriateness": 6, "forbidden_elements": 10, "natural_flow": 5, "length": 6},
            "issues": ["Not in character"],
            "notes": "Sounds like generic DJ rather than the target character"
        })
    if "borderline" in p:
        return json.dumps({
            "score": 6,
            "passed": True,
            "criteria_scores": {"character_voice": 6, "era_appropriateness": 6, "forbidden_elements": 10, "natural_flow": 6, "length": 6},
            "issues": ["Slight character drift"],
            "notes": "Borderline but acceptable"
        })
    return json.dumps({
        "score": 8,
        "passed": True,
        "criteria_scores": {"character_voice": 8, "era_appropriateness": 8, "forbidden_elements": 10, "natural_flow": 8, "length": 8},
        "issues": [],
        "notes": "Good overall"
    })

# Install mock
llm_client.generate_text = _generate

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
print('FILES:', list(out.rglob('*.json')))
for r in load_audit_results(out):
    print(r.script_id, r.passed, r.score, r.content_type)
