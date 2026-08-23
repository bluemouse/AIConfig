# Sources

## Repository bootstrap (minutes-writer)

- **Path:** `skills/minutes-writer/SKILL.md` and bundled `references/`
- **Last reviewed:** 2026-07-09
- **Used for:**
  - Full skill workflow, content rules, and output expectations
  - `references/minutes-template.md` → default structure and style examples
  - `references/source-fidelity-checklist.md` → pre-return verification
  - `references/failure-and-guardrails.md` → errors, guardrails, confidentiality
  - `references/worked-example.md` → fidelity patterns with sample source and output
- **Aspects extracted:**
  - Source hierarchy and transcript-first evidence rules → `SKILL.md`
  - Decision vs discussion vs action-item separation → `SKILL.md`, checklist, worked example
  - `not specified` convention for missing metadata → template, worked example, checklist

## Peer skill patterns (repository)

- **Path:** `skills/commit-message-writer/SKILL.md`, `skills/pull-request-guide/SKILL.md`
- **Last reviewed:** 2026-07-09
- **Used for:**
  - Primary directive and draft-only boundary → `SKILL.md`, `references/failure-and-guardrails.md`
  - When NOT to Use cross-links → `SKILL.md`
  - Phased workflow with reference routing and completion checklist → `SKILL.md`
- **Aspects extracted:**
  - `<SKILL_ROOT>` resolution pattern → `SKILL.md`
  - Reference routing table and quick completion checklist → `SKILL.md`
  - Sibling skill cross-links (`../pull-request-guide`, `../commit-message-writer`) → `SKILL.md`

## Eval queries (repository)

- **Path:** `skills/minutes-writer/eval-queries.json`
- **Last reviewed:** 2026-07-09
- **Used for:**
  - Description trigger testing via `run_eval.py`
- **Aspects extracted:**
  - Positive triggers: minutes, MoM, recap, summary, write up, format, revise, validate
  - Negative boundaries: Jira tickets, Confluence publish, PR description, commit messages
