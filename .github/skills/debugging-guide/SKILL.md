---
name: debugging-guide
description: "Use when diagnosing a software defect before fixing it \u2014 reproducing or shrinking failures, tracing root cause with evidence, ranking hypotheses, choosing prevention-by-design tripwires, writing regression tests, applying a minimal fix, and verifying with commands. Triggers on crashes, segfaults, access violations, use-after-free, 0xdddddddd fill patterns, failing tests, build failures, regressions, flaky behavior, minimal repro, git bisect, precondition assertions, sanitizers, allocation tagging and zero-on-shutdown leak checks, dangling-pointer crashes, buffer-overwrite classes, and integration failures \u2014 even when the user does not say debugging. Does not trigger on strict TDD coaching (test-driven-dev-guide), post-implementation audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), performance profiling without a defect, greenfield ownership API design (cpp-memory-guide), or native-only GDB/LLDB recipe steps while already editing C++ (cpp-coding native-debugging)."
---

# debugging-guide wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/debugging-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/debugging-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/debugging-guide/`.
- Keep only GitHub Copilot-specific information in this wrapper.
