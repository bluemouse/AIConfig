---
name: code-review-plus
description: Review git diffs and commits — staged changes, unstaged changes, the full working tree, the last commit, a specific commit, or a commit range — and return a structured, findings-first report with proposed fixes. Use whenever the user asks to review code, review a diff, review staged/unstaged/working-tree changes, review a commit or commit range, do a code review, or asks for a security/performance/design/test review of recent changes — even if they don't say "code review" explicitly (e.g. "check this diff", "look over my changes", "any issues in this commit", "is this ready to merge", "review my branch against main"). Supports six selectable review scopes (design, correctness, maintainability, security, performance, tests), three effort levels (basic, standard, deep), and an interactive mode that asks up front what to review, in what scope, and how deep before starting — say "review interactively" or "guided review" to trigger it.
---

# code-review-plus (GitHub Copilot)

Read the shared skill first — it is the source of truth for review workflow, scopes, effort
tiers, and output format:

`../../../.shared/skills/code-review-plus/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/code-review-plus/`. Resolve paths to
`references/`, `scripts/`, and `assets/` from that directory.

This wrapper adds **GitHub Copilot / VS Code-native** execution. Copilot Chat does not
expose parallel subagents — adapt the deep-effort loop accordingly.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Reload VS Code** after installing or editing skills so Copilot rediscovers them

## Install or refresh code-review-plus

From repo root (or ask the user to run in a terminal):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name code-review-plus --source skills/code-review-plus --overwrite
```

If bootstrap source exists at `skills/code-review-plus/`, use that path for `--source`
only.

## Deep effort in Copilot: sequential scope passes

At `deep` effort, follow the shared **Deep Effort: Parallel Scope Passes** intent, but
run scope passes **sequentially** in one session — Copilot has no subagent API:

1. Run Scope & Intent Alignment first (inline).
2. For each selected scope, read `<SKILL_ROOT>/references/scope-checklists.md` for that
   section (and matching Conditional Extensions), apply the *how to look* heuristic, and
   keep notes separate per scope.
3. After all scopes, run cross-scope dedup, verify pass, and gap sweep yourself per the
   shared skill.

Do not skip the verify or gap-sweep stages just because passes were sequential — they are
what separate `deep` from `standard`.

## PR review comments

This skill produces an in-chat report only. If the user asks to post findings as PR
review comments, say this skill does not support that — suggest they copy findings into
the PR manually.

## Wrapper policy

- Edit cross-tool review behavior in `../../../.shared/skills/code-review-plus/`
- Edit Copilot-specific mechanics here
- Do not duplicate the full shared skill body in this file
