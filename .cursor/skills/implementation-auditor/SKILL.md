---
name: implementation-auditor
description: "Use when auditing an implementation for requirement coverage and fresh test/build evidence after code changes, bug fixes, or plan execution \u2014 producing a compact evidence-weighted audit report. Triggers on correctness audits, requirement mapping, test-gap analysis, and completion checks before claiming done. Does not trigger on diff review (code-reviewer), plan authoring (plan-guide), pre-execution plan audit (plan-reviewer), plan execution (plan-executor), or strict TDD coaching (test-driven-dev-guide)."
---

# implementation-auditor wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/implementation-auditor/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/implementation-auditor` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/implementation-auditor/`.
- Keep only Cursor-specific information in this wrapper.
