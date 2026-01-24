# Audit Criteria

This document defines the criteria used by the script auditor to evaluate DJ scripts.

## Criteria and Weights

- **Character Voice** (30%) — Does the script sound like the intended DJ (Julie or Mr. New Vegas)?
- **Era Appropriateness** (25%) — Avoids anachronisms and modern slang when inappropriate for the era.
- **Forbidden Elements** (20%) — No emojis, profanity, or disallowed content.
- **Natural Flow** (15%) — The script reads naturally and conversationally.
- **Length Appropriate** (10%) — Suitable length for the content type.

## Scoring Scale

- 10: Perfect
- 8-9: Strong
- 6-7: Acceptable (PASS)
- 4-5: Weak (FAIL)
- 1-3: Major issues (FAIL)

## Pass Threshold

- Score >= 6 is considered a pass.

## Output Format

The auditor must respond with JSON in this format:

```json
{
  "score": <number 1-10>,
  "passed": <true|false>,
  "criteria_scores": {
    "character_voice": <1-10>,
    "era_appropriateness": <1-10>,
    "forbidden_elements": <1-10>,
    "natural_flow": <1-10>,
    "length": <1-10>
  },
  "issues": [<list of issues>],
  "notes": "<brief notes>"
}
```

## Examples

- Pass example: score 7, all criteria >= 6, no issues.
- Fail example: score 3, multiple issues listed with clear notes.
