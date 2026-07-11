---
name: cpp-performance-guide
description: "Comprehensive C++ performance optimization and investigation guidance. Use when profiling, benchmarking, reviewing, or improving C/C++ runtime performance, latency, throughput, memory use, allocations, cache locality, branch behavior, compiler optimization, vectorization, concurrency, lock contention, NUMA scaling, binary size, startup time, compile time, or regressions \u2014 even if the user says 'make it faster' without naming a profiler. Use for native desktop apps, services, libraries, game engines, rendering systems, finance/scientific workloads, Qt apps, mobile native stacks, and performance sign-off requiring reproducible measurements, tests, and a compact report."
---

# cpp-performance-guide wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/cpp-performance-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/cpp-performance-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/cpp-performance-guide/`.
- Keep only Claude Code-specific information in this wrapper.
