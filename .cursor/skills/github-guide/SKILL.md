---
name: github-guide
description: "Use when delivering a pull request and its review on GitHub (github.com or GitHub Enterprise Server) from the command line with the `gh` CLI and `gh api` \u2014 opening a PR with `gh pr create`, posting a structured review with line-anchored inline comments, resolving review threads, detecting that the host is GitHub from the git remote, and scoping a classic or fine-grained token. Triggers on a github.com / GHES remote, `gh pr create`, `gh api .../pulls/.../reviews`, an inline review comment by path+line, resolving a review thread (resolveReviewThread), REQUEST_CHANGES / branch-protection merge gating, or GH_TOKEN / GH_ENTERPRISE_TOKEN scopes \u2014 even when the user doesn't say 'gh' but the repo is hosted on GitHub."
---

# github-guide wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/github-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/github-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/github-guide/`.
- Keep only Cursor-specific information in this wrapper.
