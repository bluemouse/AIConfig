---
name: techdoc-reviewer
description: "Review, verify, and synchronize technical documentation for software projects. Use when asked to review README, API, build, architecture, design, runbook, tutorial, migration, troubleshooting, or developer documentation; verify documentation against code, tests, schemas, configuration, build files, examples, or CI; find stale, conflicting, missing, unsafe, or non-executable docs; assess documentation impact of a commit, branch, PR, or diff; or update docs after an implementation change. Prioritize evidence-backed semantic drift and reader-blocking omissions over grammar or style. Complements code-reviewer: use this skill for documentation truth and coverage, and code-reviewer for defects in the implementation diff."
---

# techdoc-reviewer (Claude Code)

Read the shared skill first — it is the source of truth for the documentation review workflow,
evidence rules, and report format:

`../../../.shared/skills/techdoc-reviewer/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/techdoc-reviewer/`.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` plus the shared package under
  `.shared/skills/<name>/`.
- Restart or reload the Claude Code session after installing or editing this skill.

## Install or refresh

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name techdoc-reviewer --source skills/techdoc-reviewer --overwrite
```

## Deep reviews in Claude Code

For deep reviews involving separate document domains or independent claim groups, use subagents
only for independent evidence passes. Include each pass's documentation paths, audience/purpose,
evidence targets, and required finding fields from the shared report template. Reconcile
conflicts, duplicate findings, severity, and the decision to synchronize documentation yourself.

Keep a complete multi-step procedure in one review pass rather than splitting its sequence across
subagents.

## Wrapper policy

- Edit cross-tool behavior in `skills/techdoc-reviewer/` and reinstall.
- Keep Claude Code-specific execution mechanics in this wrapper.
