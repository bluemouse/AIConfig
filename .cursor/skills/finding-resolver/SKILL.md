---
name: finding-resolver
description: Use when resolving, fixing, or addressing code review findings classified
  as local — applying targeted code fixes only to the specific findings, running verification,
  and producing a fix report for re-review. Also classifies findings as upstream and
  emits backward handoff packets when the root cause traces to an earlier phase. Triggers
  on prompts to fix review findings, resolve code review issues, address review comments,
  or apply review fixes — even when the user doesn't say 'finding resolver'. Does
  not trigger on code review itself (code-reviewer), plan execution (plan-executor),
  debugging a reproducible defect (debugging-guide), or git commit (git-commit).
---

# finding-resolver wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/finding-resolver/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/finding-resolver` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/finding-resolver/`.
- Keep only Cursor-specific information in this wrapper.
