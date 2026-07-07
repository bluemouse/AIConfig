---
name: git-guide
description: "Use when running git operations or resolving repo-state issues. Triggers on merge conflicts, rebases, worktrees, feature-worktree create / merge / abandon / cleanup, branch cleanup, push/rebase before a PR, staging and committing (when the user supplies or already has a message), or history rewrites \u2014 even when the user doesn't say 'git'. For drafting Conventional Commit messages from diffs, use commit-message-writer."
---

# git-guide wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/git-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/git-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/git-guide/`.
- Keep only Claude Code-specific information in this wrapper.
