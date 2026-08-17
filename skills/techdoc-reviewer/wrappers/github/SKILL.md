---
name: techdoc-reviewer
description: "Review, verify, and synchronize technical documentation for software projects. Use when asked to review README, API, build, architecture, design, runbook, tutorial, migration, troubleshooting, or developer documentation; verify documentation against code, tests, schemas, configuration, build files, examples, or CI; find stale, conflicting, missing, unsafe, or non-executable docs; assess documentation impact of a commit, branch, PR, or diff; or update docs after an implementation change. Prioritize evidence-backed semantic drift and reader-blocking omissions over grammar or style. Complements code-reviewer: use this skill for documentation truth and coverage, and code-reviewer for defects in the implementation diff."
---

# techdoc-reviewer (GitHub Copilot)

Read the shared skill first — it is the source of truth for the documentation review workflow,
evidence rules, and report format:

`../../../.shared/skills/techdoc-reviewer/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/techdoc-reviewer/`.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` plus the shared package under
  `.shared/skills/<name>/`.
- Reload VS Code after installing or editing this skill.

## Install or refresh

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name techdoc-reviewer --source skills/techdoc-reviewer --overwrite
```

## Deep reviews in GitHub Copilot

Run independent documentation claim groups sequentially and keep evidence notes separate. Do not
skip cross-document reconciliation or executable-procedure verification because the work is
sequential. Use the shared skill for scope, evidence hierarchy, and final report contents.

## Wrapper policy

- Edit cross-tool behavior in `skills/techdoc-reviewer/` and reinstall.
- Keep GitHub Copilot-specific execution mechanics in this wrapper.
