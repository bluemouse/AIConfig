---
name: test-driven-dev-guide
description: "Use when guiding strict test-driven development through red-green-refactor cycles with real command evidence and minimal production changes. Triggers on TDD implementation, test-first bug fixes, red/green verification, and checking whether code was written test-first. Does not trigger on post-implementation correctness audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), codebase learning guides (code-professor), or framework-specific test wiring (cpp-testing, kotlin-testing, python-coding)."
---

# test-driven-dev-guide wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/test-driven-dev-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/test-driven-dev-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/test-driven-dev-guide/`.
- Keep only Claude Code-specific information in this wrapper.
