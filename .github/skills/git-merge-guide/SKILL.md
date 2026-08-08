---
name: git-merge-guide
description: 'Guide complex local Git merges and rebases end-to-end: initiate operations,
  reconstruct intent from local history, resolve semantic conflicts, stage fixes without
  creating the final merge commit, continue rebases, review cleanly merged code for
  cross-branch integration bugs, run impact-based verification, and report results.
  Use when a local merge/rebase needs intent reconstruction, semantic resolution,
  combined-tree review, affected-test verification, or a merge report — even without
  saying git. Local evidence only; never fetch/push. Ask when intent is ambiguous;
  require permission before destructive ops. Does not trigger on push/fetch/pull,
  worktree lifecycle, simple single-file conflict triage (git-guide), cherry-pick/revert,
  final merge commits (git-guide), commit messages (commit-message-writer), diff review
  (code-reviewer), audits (implementation-auditor), plan execution (plan-executor),
  parallel dispatch (agent-runner), or debugging outside active integration (debugging-guide).'
---

# git-merge-guide wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/git-merge-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/git-merge-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/git-merge-guide/`.
- Keep only GitHub Copilot-specific information in this wrapper.
