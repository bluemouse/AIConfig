---
name: test-driven-dev-guide
description: "Use when guiding strict test-driven development through red-green-refactor cycles with real command evidence and minimal production changes. Triggers on TDD implementation, test-first bug fixes, red/green verification, and checking whether code was written test-first. Does not trigger on post-implementation correctness audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), codebase learning guides (code-professor), or framework-specific test wiring (cpp-coding, kotlin-coding)."
---

# Test Driven Dev Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Guide strict test-driven development: one vertical behavior slice at a time through
red-green-refactor, with real command evidence and minimal production changes.

## Primary Directive

Your job is to **coach strict TDD through red-green-refactor cycles**, not to execute
implementation plans, audit post-implementation correctness, review diffs, or configure
framework-specific test infrastructure.

## When to Use

- Implementing features, bug fixes, refactors, or behavior changes test-first
- Writing a failing regression test before fixing a bug
- Verifying red and green states with focused test commands
- Checking whether code was written test-first
- Guiding red-green-refactor with evidence in working notes

## When NOT to Use

- **Multi-unit plan execution** — use [../plan-executor/SKILL.md](../plan-executor/SKILL.md); apply TDD per plan task discipline (see Plan execution below)
- **Post-implementation correctness audit** — use
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
- **Structured diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Codebase learning or architecture guides** — use [../code-professor/SKILL.md](../code-professor/SKILL.md)
- **Behavior or acceptance criteria still undefined** — use
  [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) to settle what "done" means, then
  return here to write the first failing test
- **C++ GoogleTest/CMake test setup** — use [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md)
- **Kotlin/JVM test setup** — use [../kotlin-coding/SKILL.md](../kotlin-coding/SKILL.md)

### Plan execution

During [../plan-executor/SKILL.md](../plan-executor/SKILL.md) runs, follow the plan's
verification steps. Apply strict red-green-refactor per unit when the plan marks a task's
test discipline as `mandatory` (explicitly user-requested TDD or high-risk code work
from [../plan-guide/SKILL.md](../plan-guide/SKILL.md)) or when test discipline is omitted
on a code task. Tasks marked `verification-led` follow the plan's stated verification
strategy — this skill is not invoked for them unless the user asks for TDD anyway; the
strategy must still be concrete. Use `n/a` only for explicitly non-code or check-only
config/infra tasks. In this subordinate mode, keep the red-green evidence in the
execution notes and return control to the executor after each unit reaches green
instead of driving the whole plan.

## Core rule

Do not write production code for a behavior until a test for that behavior has been written, run, and observed failing for the expected reason. Work one vertical behavior slice at a time: red (one focused failing test), green (the smallest production change that passes it), refactor (only while tests stay green), repeat.

If code was already written before the test, do not adapt that code as the implementation. Treat it as exploratory work, discard or ignore it, then implement fresh from the failing test unless the user explicitly waives TDD.

Verify the red state proves the missing behavior, not a broken test: the failure message must match the missing behavior — not a compile error, fixture mistake, missing import, bad mock, or typo. If the new test passes immediately, it proves nothing; change it. If it errors, fix the setup and rerun until it fails correctly.

Record red evidence in working notes when the task is nontrivial:

```text
red: <command>
result: failed as expected because <specific missing behavior>
```

## Bugs and regressions

For a bug fix, first write a regression test that reproduces the observed failure. Verify it fails against the current code. Then fix the bug and verify the test passes. A bug is not fixed without a test that would have caught it.

For intermittent or platform-specific bugs, capture the smallest deterministic reproduction possible. If deterministic reproduction is impossible, document the limitation and add the closest automated guard plus manual verification notes.

## Mocks

Use mocks only to isolate true boundaries such as network, filesystem, clock, randomness, hardware, long-running services, or process execution. Never test that a mock exists — test the behavior of the system under test. Load `<SKILL_ROOT>/references/testing-anti-patterns.md` before adding mocks, test helpers, or production methods used only by tests.

## Completion checklist

Before claiming the change is complete, verify:

- Each changed behavior has at least one test.
- Each new test was observed failing for the expected reason before implementation.
- Focused tests pass.
- Relevant regression tests pass.
- Build or type-check passes when applicable.
- Output has no ignored failures, crashes, or unexplained warnings.
- Any skipped or unavailable tests are explicitly reported.

Report status using evidence, not confidence:

```text
verified:
- <command> => <result summary>
not verified:
- <scope> => <reason>
```

## Companion Skills

| Task | Path |
| --- | --- |
| Post-implementation correctness audit | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Structured diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| C++ GoogleTest/CMake testing | [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md) |
| Kotlin/JVM testing | [../kotlin-coding/SKILL.md](../kotlin-coding/SKILL.md) |
| Plan execution | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
