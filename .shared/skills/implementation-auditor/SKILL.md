---
name: implementation-auditor
description: "Use when auditing an implementation for requirement coverage and fresh test/build evidence after code changes, bug fixes, or plan execution — producing a compact evidence-weighted audit report. Triggers on correctness audits, requirement mapping, test-gap analysis, and completion checks before claiming done. Does not trigger on diff review (code-reviewer), plan authoring (plan-guide), pre-execution plan audit (plan-reviewer), plan execution (plan-executor), or strict TDD coaching (test-driven-dev-guide)."
---

# Implementation Auditor

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Audit an implementation against a plan, bug, or requirement set. Combine analytical review
with fresh command evidence and produce a compact audit report — not an implementation report
or a structured diff review.

## Primary Directive

Your job is to **audit an implementation for correctness and requirement coverage with fresh
test/build evidence**, not to execute plans, author plans, coach strict TDD, or review code
diffs. After a passing audit, suggest [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
for structured diff review.

## When to Use

- After code changes, bug fixes, or [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
  runs — when deeper correctness proof is needed beyond an integration report
- Before claiming completion or merge readiness
- Checking requirement coverage against a plan, spec, or acceptance criteria
- Validating that tests actually exercise changed behavior, with fresh command output
- Producing a compact audit report mapping evidence, gaps, risks, and next steps

## When NOT to Use

- **Structured diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Plan execution** — use [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- **Pre-execution plan audit** — use [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Plan authoring or repair** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Strict TDD coaching during active implementation** — use
  [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md)

## Mission

Audit the implementation against the requested plan, bug, or requirement. Combine analytical review with fresh command evidence. Do not claim correctness from inspection alone and do not claim tests pass unless the relevant command was run in the current session and its output was read.

Default to read-only auditing. Do not modify implementation files unless the user explicitly asks for fixes. Temporary local commands, builds, generated test artifacts, and logs are allowed when needed; clean them up when practical and report leftovers.

## Audit workflow

1. **Establish scope**
   - Identify the requested behavior, acceptance criteria, implementation plan, or changed files.
   - Inspect `git status` and relevant diffs on the current branch.
   - Note untracked files and unrelated changes before running tests.

2. **Map requirements to code**
   - Create a compact checklist of required behaviors.
   - For each item, identify the files, functions, UI paths, APIs, or configuration that implement it.
   - Mark any requirement that has no obvious implementation path as a gap.

3. **Select verification commands**
   - Discover the project's build and test system from repository files, docs, CI config, package manifests, and scripts.
   - Load `<SKILL_ROOT>/references/test-command-matrix.md` when choosing commands by platform or tech stack.
   - Prefer the smallest focused command for changed behavior plus the relevant broader regression command.

4. **Run fresh validation**
   - Run tests/builds in a safe order: focused tests, related suite, then broader suite/build as time and environment allow.
   - Read exit codes and failure output. Do not rely on summaries alone if logs indicate skipped tests, warnings-as-errors, crashes, flakes, or missing devices.
   - If a command cannot run because dependencies, credentials, simulators, emulators, hardware, licenses, or services are unavailable, report it as blocked, not passed.

5. **Analyze correctness**
   - Review the diff for logic errors, missing edge cases, API contract violations, threading/lifetime issues, resource leaks, platform assumptions, security/privacy problems, and test gaps.
   - Check whether tests actually exercise the changed behavior rather than mocks or incidental implementation details.
   - Compare runtime evidence against the requirement checklist.

6. **Produce the audit report**
   - Use the compact report structure from `<SKILL_ROOT>/references/audit-report-template.md`.
   - Include commands run, results, coverage by requirement, defects, risks, and actionable next steps.
   - Make the verdict evidence-weighted: `pass`, `pass with risks`, `blocked`, or `fail`.

## Boundary with code review

This skill proves **whether requirements are met** with fresh evidence: requirement coverage, correctness, and test-to-behavior mapping. It does not judge diff quality, design, readability, or maintainability — that is [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md). When both are wanted, audit first (outcome proof), then review the diff.

## Verdict routing

End every audit by routing on the verdict so defects are not carried forward:

- `pass` — proceed to [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) for diff review, then delivery.
- `pass with risks` — proceed to [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md), and pass the named risks in as explicit review focus.
- `fail` — return to implementation: [../plan-executor/SKILL.md](../plan-executor/SKILL.md) for missing or incomplete behavior, or [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) when a test fails or a regression appears and the cause is unclear. Re-audit after the fix.
- `blocked` — do not report pass. Document exactly what could not run and why; resolve the environment, credentials, devices, or dependencies, then re-audit.

## Evidence rules

- Fresh command output is required for any statement that tests, builds, linters, or type checks pass.
- Analytical review is required even when tests pass.
- Passing tests do not prove requirements are met; map tests to requirements explicitly.
- Agent or tool success messages are not evidence. Verify diffs and command output independently.
- Skipped tests, unavailable devices, flaky reruns, or partial suites must be visible in the final report.

## Test gap analysis

For each changed behavior, ask:

- Is there a focused test that fails without the implementation?
- Is there at least one regression path covering the integrated behavior?
- Are error paths, boundary values, platform variants, and compatibility paths covered?
- Are tests checking real behavior rather than mock existence or private implementation details?
- Would these tests catch the likely bug if the implementation regressed?

Classify gaps as:

- **critical:** missing test for core requirement or known bug reproduction.
- **major:** missing platform, integration, failure-path, or concurrency coverage.
- **minor:** missing low-risk edge case or documentation of manual verification.

## Platform and stack selection

Load `<SKILL_ROOT>/references/test-command-matrix.md` to choose commands. Prefer repository-specific commands from docs or CI over generic commands. When multiple stacks exist, run commands for the affected stack and any integration boundary touched by the change.

Examples:

- Android Kotlin change: focused Gradle unit or instrumentation target, then affected module test task.
- iOS Swift/Objective-C change: focused `xcodebuild test` with the relevant scheme and destination.
- Desktop C++ change: configure/build target, focused test binary or `ctest -R`, then relevant suite.
- Qt change: CMake or qmake build plus Qt test executable or `ctest` target.

## Report requirements

The final report must be clear enough for a debugging agent, implementor, or reviewer to act on without rerunning the whole audit. Include exact commands, outcomes, key log snippets or summaries, and file-level observations. Be concise but precise.

Use `<SKILL_ROOT>/references/audit-report-template.md` for the final format.

## Companion Skills

| Task | Path |
| --- | --- |
| Strict TDD during implementation | [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md) |
| Structured diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Plan execution | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
| Pre-execution plan audit | [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) |
| Plan authoring and repair | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) |
