---
name: techdoc-reviewer
description: 'Review, verify, and synchronize technical documentation for software
  projects. Use when asked to review README, API, build, architecture, design, runbook,
  tutorial, migration, troubleshooting, or developer documentation; verify documentation
  against code, tests, schemas, configuration, build files, examples, or CI; find
  stale, conflicting, missing, unsafe, or non-executable docs; assess documentation
  impact of a commit, branch, PR, or diff; or update docs after an implementation
  change. Prioritize evidence-backed semantic drift and reader-blocking omissions
  over grammar or style. Complements code-reviewer: use this skill for documentation
  truth and coverage, and code-reviewer for defects in the implementation diff.'
---

# techdoc-reviewer (Cursor)

Read the shared skill first — it is the source of truth for the documentation review workflow,
evidence rules, and report format:

`../../../.shared/skills/techdoc-reviewer/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/techdoc-reviewer/`.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` plus the shared package under
  `.shared/skills/<name>/`.
- Reload the Cursor window after installing or editing this skill.

## Install or refresh

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name techdoc-reviewer --source skills/techdoc-reviewer --overwrite
```

## Deep reviews in Cursor

For deep reviews involving distinct document domains or independently verifiable claim groups,
parallelize only the independent evidence passes with the Task tool. Give each pass its document
paths, purpose/audience, exact evidence targets, and the required output fields from the shared
report template. Keep the final conflict resolution, cross-document deduplication, severity
assignment, and synchronization decision in the parent review.

Do not use parallelism to split one tightly coupled workflow across agents; validate its complete
reader journey in one pass.

## Wrapper policy

- Edit cross-tool behavior in `skills/techdoc-reviewer/` and reinstall.
- Keep Cursor-specific execution mechanics in this wrapper.
