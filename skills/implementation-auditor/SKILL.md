---
name: implementation-auditor
description: "Use when auditing an implementation for requirement coverage and fresh test/build evidence after code changes, bug fixes, or plan execution — producing a compact evidence-weighted audit report. Triggers on correctness audits, requirement mapping, test-gap analysis, and completion checks before claiming done. Does not trigger on active local merge/rebase integration verification (git-merge-guide), diff review (code-reviewer), plan authoring (plan-guide), pre-execution plan audit (plan-reviewer), plan execution (plan-executor), codebase learning guides (code-professor), or strict TDD coaching (test-driven-dev-guide)."
---

# Implementation Auditor

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

## Scope and boundaries

Audit an implementation against a plan, bug, or requirement set: combine analytical review with fresh command evidence and produce a compact audit report — not an implementation report or a structured diff review. Use this skill after code changes, bug fixes, or [../plan-executor/SKILL.md](../plan-executor/SKILL.md) runs, and before claiming completion or merge readiness.

Do not claim correctness from inspection alone, and do not claim tests pass unless the relevant command was run in the current session and its output was read. Default to read-only auditing: do not modify implementation files unless the user explicitly asks for fixes. Temporary local commands, builds, generated test artifacts, and logs are allowed when needed; clean them up when practical and report leftovers.

This skill proves whether requirements are met (requirement coverage, correctness, test-to-behavior mapping). It does not judge diff quality, design, readability, or maintainability. Neighboring skills own: active merge/rebase integration verification — [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md) (use this skill only afterward, when requirement or acceptance-criteria coverage still needs separate proof); structured diff or commit review — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) (audit first, then review the diff); plan execution — [../plan-executor/SKILL.md](../plan-executor/SKILL.md); pre-execution plan audit — [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md); plan authoring or repair — [../plan-guide/SKILL.md](../plan-guide/SKILL.md); strict TDD coaching during implementation — [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md); codebase learning or architecture guides — [../code-professor/SKILL.md](../code-professor/SKILL.md).

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

### Artifact output path

When invoked **outside the dev-workflow-orchestrator** (i.e., no orchestrator assigned an input/output artifact path), write the audit report to `.agents/plans/<feature-or-topic-slug>-audit.md`. The `.agents/plans/` directory is gitignored. Do not write audit artifacts to the repository root — it pollutes the working tree and risks accidental commits.

When invoked **inside the orchestrator**, the orchestrator assigns the output path (typically `.agents/workflow/<slug>/31-implementation-audit.md`); use that path instead.

## Verdict routing

End every audit by routing on the verdict — see [references/audit-report-template.md](references/audit-report-template.md) "Next-action routing by verdict" for the full mapping: `pass`/`pass with risks` → code-reviewer for diff review, then delivery; `fail` → plan-executor or debugging-guide, then re-audit; `blocked` → resolve what could not run, then re-audit — never report pass when blocked.

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

- **blocker:** missing test for core requirement or known bug reproduction.
- **major:** missing platform, integration, failure-path, or concurrency coverage.
- **minor:** missing low-risk edge case or documentation of manual verification.

## Platform and stack selection

Load `<SKILL_ROOT>/references/test-command-matrix.md` to choose commands by platform or tech stack. Prefer repository-specific commands from docs or CI over generic commands. When multiple stacks exist, run commands for the affected stack and any integration boundary touched by the change.

## Report requirements

The final report must be clear enough for a debugging agent, implementor, or reviewer to act on without rerunning the whole audit. Include exact commands, outcomes, key log snippets or summaries, and file-level observations. Be concise but precise.

Use `<SKILL_ROOT>/references/audit-report-template.md` for the final format.
