---
name: pull-request-guide
description: "Use when authoring a pull or merge request - writing the description, sizing and splitting the change, documenting how it was tested, surfacing tradeoffs, and getting it review-ready before assigning reviewers. Triggers on opening a PR/MR, PR descriptions or templates, large or atomic PRs, what to put in a PR, draft vs ready, stacked PRs, or self-review, even when the user doesn't say 'pull request'."
---

# pull-request-guide wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/pull-request-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/pull-request-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/pull-request-guide/`.
- Keep only Cursor-specific information in this wrapper.
