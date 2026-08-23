# Sources

## Repository reference draft (tutorial-writer)

- **Path:** `references/skills/tutorial-writer/SKILL.md` and bundled
  `references/tutorial-patterns.md`
- **Last reviewed:** 2026-08-15
- **Used for:**
  - Example-first workflow, writing rules, default output shape, and quality gate
  - `references/tutorial-patterns.md` → guide skeletons, visual selector, example rules,
    professional-use checklist, and anti-patterns
- **Aspects extracted:**
  - Progressive running-example ladder → `SKILL.md`, `references/tutorial-patterns.md`
  - Observable-result teaching loop → `SKILL.md`
  - Purposeful diagram guidance → `SKILL.md`, visual selector in reference
  - Source-fidelity and no-fabrication rules → `SKILL.md`, example quality rules

## Peer skill patterns (repository)

- **Path:** `skills/minutes-writer/SKILL.md`, `skills/code-professor/SKILL.md`,
  `skills/prompt-clarifier/SKILL.md`
- **Last reviewed:** 2026-08-15
- **Used for:**
  - Primary directive and draft-only boundary → `SKILL.md`
  - When NOT to Use cross-links and companion skills table → `SKILL.md`
  - Reference routing and quick completion checklist → `SKILL.md`
- **Aspects extracted:**
  - `<SKILL_ROOT>` resolution pattern → `SKILL.md`
  - Sibling-skill deferrals for research, codebase learning, and clarification →
    `SKILL.md`

## Eval queries (repository)

- **Path:** `skills/tutorial-writer/eval-queries.json`
- **Last reviewed:** 2026-08-15
- **Used for:**
  - Description trigger testing via `run_eval.py`
- **Aspects extracted:**
  - Positive triggers: tutorial, quickstart, walkthrough, user guide, how-to, lesson,
    rewrite, review
  - Negative boundaries: API reference lookup, implementation/debugging, release notes,
    research, codebase onboarding, isolated diagram requests
