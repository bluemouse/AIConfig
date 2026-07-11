---
name: test-driven-dev-guide
description: "Use when guiding strict test-driven development through red-green-refactor cycles with real command evidence and minimal production changes. Triggers on TDD implementation, test-first bug fixes, red/green verification, and checking whether code was written test-first. Does not trigger on post-implementation correctness audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), or framework-specific test wiring (cpp-testing, kotlin-testing, python-coding)."
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

- **Multi-unit plan execution** — use [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
  unless the user explicitly requests strict TDD (see Plan execution below)
- **Post-implementation correctness audit** — use
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
- **Structured diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **C++ GoogleTest/CMake test setup** — use [../cpp-testing/SKILL.md](../cpp-testing/SKILL.md)
- **Kotlin/JVM test setup** — use [../kotlin-testing/SKILL.md](../kotlin-testing/SKILL.md)

### Plan execution

During [../plan-executor/SKILL.md](../plan-executor/SKILL.md) runs, follow the plan's
verification steps. Apply strict red-green-refactor per unit when the plan marks a task's
test discipline as `mandatory`, or when the user requires TDD; otherwise defer full TDD
coaching to explicit user request. In this subordinate mode, keep the red-green evidence in
the execution notes and return control to the executor after each unit reaches green
instead of driving the whole plan.

## Core rule

Do not write production code for a behavior until a test for that behavior has been written, run, and observed failing for the expected reason.

Follow one vertical behavior slice at a time:

1. **Red:** write one focused test for the next observable behavior.
2. **Verify red:** run the smallest relevant test command and confirm the test fails because the behavior is missing, not because of syntax, setup, or an incorrect assertion.
3. **Green:** write the smallest production change that makes that test pass.
4. **Verify green:** rerun the focused test, then run the relevant regression scope.
5. **Refactor:** clean only after green; keep tests passing after every meaningful refactor.
6. **Repeat:** choose the next behavior or edge case.

If code was already written before the test, do not adapt that code as the implementation. Treat it as exploratory work, discard or ignore it, then implement fresh from the failing test unless the user explicitly waives TDD.

## Choose the next test

Prefer tests that express externally visible behavior. Start with the smallest end-to-end tracer bullet that proves the path works, then add edge cases, errors, and boundaries.

A good TDD test:

- Describes the behavior in its name.
- Has one reason to fail.
- Uses the public or intended API.
- Exercises real code when practical.
- Avoids asserting implementation details.
- Avoids mocks unless a real external dependency is slow, nondeterministic, dangerous, or unavailable.

Do not write all tests first and then all implementation. That is not TDD; it creates speculative tests before the design has been shaped by the first vertical slice.

## Verify red correctly

After writing the test, run only the focused test or smallest target that includes it.

Acceptable red state:

- The new test fails.
- The failure message matches the missing behavior.
- The failure is not caused by compile errors, fixture mistakes, missing imports, bad mocks, or typos.

If the test passes immediately, change the test because it does not prove the new behavior. If it errors, fix the test setup and rerun until it fails correctly.

Record the red evidence in working notes when the task is nontrivial:

```text
red: <command>
result: failed as expected because <specific missing behavior>
```

## Implement green minimally

Write only the production code required to pass the current failing test. During green:

- Do not add untested options, branches, abstractions, logging, configuration, or cleanup.
- Do not refactor unrelated code.
- Do not broaden behavior beyond the current test.
- Prefer a simple local implementation over a premature framework.

It is acceptable for green code to be temporarily plain, duplicated, or narrowly shaped. Improve it only during refactor with tests still passing.

## Refactor safely

Refactor only after the focused test and relevant regression scope pass. During refactor:

- Preserve behavior.
- Keep changes small.
- Rerun focused tests after each meaningful change.
- Run the broader suite before completion.
- Stop and revert the refactor if tests fail and the cause is unclear.

Do not add new behavior while refactoring. Add a new failing test first.

## Bugs and regressions

For a bug fix, first write a regression test that reproduces the observed failure. Verify it fails against the current code. Then fix the bug and verify the test passes. A bug is not fixed without a test that would have caught it.

For intermittent or platform-specific bugs, capture the smallest deterministic reproduction possible. If deterministic reproduction is impossible, document the limitation and add the closest automated guard plus manual verification notes.

## Mocking rules

Use mocks only to isolate true boundaries such as network, filesystem, clock, randomness, hardware, long-running services, or process execution. Before mocking, identify what side effects the real dependency provides and whether the test depends on them.

Never test that a mock exists. Test the behavior of the system under test. Load `<SKILL_ROOT>/references/testing-anti-patterns.md` when adding mocks, test helpers, or production methods used only by tests.

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

## Related references

- Load `<SKILL_ROOT>/references/testing-anti-patterns.md` before adding or changing mocks, fixtures, test utilities, or test-only cleanup.

## Companion Skills

| Task | Path |
| --- | --- |
| Post-implementation correctness audit | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Structured diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| C++ GoogleTest/CMake testing | [../cpp-testing/SKILL.md](../cpp-testing/SKILL.md) |
| Kotlin/JVM testing | [../kotlin-testing/SKILL.md](../kotlin-testing/SKILL.md) |
| Plan execution | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
