---
name: debugging-guide
description: "Use when diagnosing a software defect before fixing it \u2014 reproducing or shrinking failures, tracing root cause with evidence, ranking hypotheses, choosing prevention-by-design tripwires, writing regression tests, applying a minimal fix, and verifying with commands. Triggers on crashes, segfaults, access violations, use-after-free, 0xdddddddd fill patterns, failing tests, build failures, regressions, flaky behavior, minimal repro, git bisect, precondition assertions, sanitizers, allocation tagging and zero-on-shutdown leak checks, dangling-pointer crashes, buffer-overwrite classes, and integration failures \u2014 even when the user does not say debugging. Does not trigger on strict TDD coaching (test-driven-dev-guide), correctness audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), codebase learning (code-professor), profiling without a defect, ownership API design (cpp-memory-guide), or native GDB/LLDB steps while editing C++ (cpp-coding)."
---

# debugging-guide wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/debugging-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/debugging-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/debugging-guide/`.
- Keep only Cursor-specific information in this wrapper.
