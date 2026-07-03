# JSON Schemas

This document defines JSON schemas used when tracking manual skill evaluations in GitHub Copilot.

---

## evals.json

Optional test cases for a skill. Store at `evals/evals.json` within the skill directory.

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

**Fields:**

- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute in Copilot agent mode
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable statements for manual review

---

## feedback.json

Capture user review notes after running test prompts in Copilot.

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

Freeform notes per iteration. Example structure:

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
