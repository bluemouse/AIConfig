---
name: commit-message-writer
description: "Draft git commit messages in Conventional Commits format from staged changes, the working tree, a single commit, or a commit range \u2014 compact one-liner plus verbose subject and body. Use when the user asks for a commit message, conventional commit, draft commit msg, write commit message for staged/unstaged changes, message for last commit or commit range, or /commit-message-style requests \u2014 even if they do not say \"conventional commits\". Does not run git commit unless the user explicitly asks afterward."
---

# commit-message-writer wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/commit-message-writer/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/commit-message-writer` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/commit-message-writer/`.
- Keep only GitHub Copilot-specific information in this wrapper.
