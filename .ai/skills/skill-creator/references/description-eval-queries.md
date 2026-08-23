# Description trigger eval queries

Use this guide when tuning a skill's `description` field for better discovery/triggering. Task evals (`evals/evals.json`) test skill *behavior*; this format tests whether the agent *invokes* the skill from the description alone.

For JSON schemas of task evals, grading, and benchmarks, see `schemas.md`.

---

## Format

Save as a JSON array (e.g. `trigger-eval-set.json`):

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Aim for ~20 queries: 8–10 should-trigger, 8–10 should-not-trigger. Focus on **near-misses** for negatives — not obviously unrelated prompts.

---

## Good vs bad queries

**Bad (too vague):**

- `"Format this data"`
- `"Extract text from PDF"`
- `"Create a chart"`

**Good (concrete, realistic):**

- `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

**Good should-not-trigger (near-miss):**

- Shares keywords with the skill but needs a different tool or a one-step answer the base model handles without the skill
- Adjacent domain where another skill or plain chat is more appropriate

**Bad should-not-trigger (too easy):**

- `"Write a fibonacci function"` as a negative test for a PDF skill — does not test discrimination

---

## Coverage for should-trigger queries

- Formal and casual phrasings of the same intent
- User never names the skill or file type but clearly needs it
- Uncommon use cases and cases where this skill should win over a adjacent skill

---

## Automated optimization (Claude Code / Cowork only)

When `run_loop.py` is available (see Claude Code wrapper), it splits the eval set ~60% train / 40% held-out test, runs each query multiple times, and proposes description revisions. Execution details are **not** shared here — see your tool wrapper.

Manual optimization (all tools): draft queries (Step 1), review with user via `assets/eval_review.html` (Step 2), revise description yourself, apply and sync wrappers (Step 4).
