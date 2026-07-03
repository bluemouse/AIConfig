# JSON Schemas

Optional schemas for tracking manual skill evaluations in Cursor.

---

## evals.json

Store at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

---

## feedback.json

Capture review notes after running test prompts in Cursor.

```json
{
  "reviews": [
    {
      "eval_id": 1,
      "prompt": "The user's task prompt",
      "feedback": "Missing axis labels on the chart",
      "passed": false
    },
    {
      "eval_id": 2,
      "prompt": "Another task prompt",
      "feedback": "",
      "passed": true
    }
  ],
  "status": "complete"
}
```

Empty `feedback` with `passed: true` means the result looked good.

---

## iteration-notes.md

Freeform notes per iteration:

```markdown
# Iteration 2

## Changes made
- Clarified step 3 in SKILL.md
- Added validate_output.py to scripts/

## Test results
- Eval 1: pass
- Eval 2: fail — forgot to run validation script

## Next steps
- Add explicit instruction to run validate_output.py before finishing
```
