---
name: debugging-guide
description: "Use when diagnosing a software defect before fixing it — root-cause tracing with evidence before any production change, reproducing or shrinking failures, forming and testing hypotheses, choosing prevention-by-design tripwires, writing the regression test, and applying the minimal fix. Triggers on crashes, segfaults, access violations, use-after-free, 0xdddddddd fill patterns, regressions, flaky behavior, minimal repro, git bisect, precondition assertions, sanitizers, allocation tagging, dangling-pointer crashes, buffer-overwrite classes, and unclear integration failures — even when the user does not say debugging; skip it for a failure with an obvious, verified cause. Does not trigger on active merge/rebase integration (git-merge-guide), strict TDD coaching (test-driven-dev-guide), correctness audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), codebase learning (code-professor), profiling without a defect, or native GDB/LLDB steps while editing C++."
---

# Debugging Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Locate the true root cause of a software bug and apply the smallest correct fix. Treat
debugging as an evidence-driven investigation, not a guessing loop — not strict TDD
coaching, post-implementation correctness audit, diff review, or plan execution.

## When to Use

- Reproducing and tracing a crash, regression, flaky behavior, or non-obvious failure
- Gathering evidence and confirming cause before changing production code
- Writing or updating a regression test or durable reproducer for a specific defect
- Applying a focused production fix and verifying it with commands
- Producing a debugging report for reviewers or follow-up agents

## Iron rule

Do not propose or apply a production fix until you can state:

1. the observed symptom;
2. the earliest incorrect transition that caused it;
3. the evidence proving that transition is the root cause;
4. the test, command, or experiment that will fail before the fix and pass after it.

A symptom is not a root cause. A plausible explanation is not evidence. A manual check is
not enough when an automated test or durable reproducer can be created.

## Investigation contract

The workflow is the standard one you already know — freeze scope (inspect state before
editing; one-sentence bug definition; smallest affected surface), reproduce before
changing code (record exact commands, inputs, failing log slices, exit codes; for
intermittent failures capture frequency and at least one failing trace), read the failure
literally (first meaningful failure over cascade errors; known vs inferred), classify the
bug class, trace backward through data/state flow to the earliest incorrect transition,
and compare against the closest working example in the same codebase before inventing a
new approach. References carry the on-demand depth:

- Load `references/reproduction-and-bisection.md` when shrinking a slow repro or bisecting history.
- Load `references/determinism-and-replay.md` when the bug is intermittent and you need determinism, stress, logging, or record/replay.
- Load `references/bug-taxonomy.md` for bug classes and prevention-by-design tactics.
- Load `references/diagnostic-techniques.md` for tracing, differential comparison, bisecting, and bug-class-specific tactics.
- Load `references/instrumentation-and-checks.md` when adding assertions, sanitizers, or tripwires — instrument to surface the fault **earlier** or where it is cheaper to act on, not to restate what the crash already showed.

When reproduction exists and the defect is in **native C++**, apply the debugger
(GDB/LLDB) and sanitizer toolchain directly; debugger rules and sanitizer build flags
live in
[cpp-coding's build-and-verification.md](../cpp-coding/references/build-and-verification.md#native-debugging-with-gdblldb)
(via [cpp-coding](../cpp-coding/SKILL.md)).

## Hypothesis discipline

Test one hypothesis at a time, one variable per experiment. Before each experiment:

```text
Hypothesis: [specific root cause mechanism]
Evidence so far: [facts only]
Prediction: if true, [minimal observation] will show [specific result]
Experiment: [one command, diagnostic, breakpoint, assertion, or tiny probe]
Outcome: [confirmed/rejected + evidence]
```

- Prefer observation, instrumentation, and focused tests before production edits.
- If an experiment disproves the hypothesis, discard it and form a new one; do not stack speculative fixes.
- If three production fix attempts fail or each fix reveals a different shared-state/coupling problem, stop and reassess the design with the user before attempting another fix.

## Fix and verify

1. **Regression test first** — before the production fix, create the smallest failing test
   or reproducer that captures the root cause (unit test for a local bug, integration
   test for a boundary bug, end-to-end when only the full stack fails, or a deterministic
   reproducer script if no harness fits). Use
   [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md) when available.
   Do not write tests that encode the implementation detail you are about to change.
2. **Fix the earliest incorrect transition**, not the nearest symptom. Banned fixes:
   sleeps, hidden retries, silent fallbacks.
3. **Verify with evidence** — if verification cannot be run, state exactly why, what was
   not verified, and which command should be run next. Do not claim the bug is fixed
   without command-backed evidence.
4. **After the fix**, note the bug class and one structural prevention (what design or
   tripwire would have caught the whole class) for follow-up.

## Report

For non-trivial investigations, end with a compact report — load
`references/debugging-report.md` and follow the template: status; expected and actual
behavior; reproduction; root cause as the earliest incorrect transition; evidence and
rejected alternatives; changed files; tests/commands run with results; residual risk;
Next Step handoff. For a trivial fix with an obvious cause, a one-paragraph summary
covering root cause, fix, and verification suffices.

After the fix is verified, hand off deliberately: complex or shared-code fixes route to
[../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) for
requirement-level correctness proof, then to
[../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) for the fix diff; a small,
well-contained fix with a passing regression test needs only the code-reviewer pass.
Record the chosen next step in the report's Next Step field.

## Gotchas

Load `references/gotchas.md` for the full list. High-signal items:

- Access violations and segfaults usually mean an unmapped or dangling address — not permissions or threading.
- A freed-memory fill pattern (e.g. `0xdddddddd`) at a mapped address points to use-after-free, not a random overwrite.
- Treat "100% reproducible" as a working assumption; revise it if the bug later disappears.
- `git bisect` lies on flaky repros, mislabeled GOOD/BAD, or stale incremental builds — force clean rebuilds and bisect only deterministic repros.
- Instrumentation that only restates the crash adds no value — trip earlier or in a test.
- Refcounting or GC to keep objects alive converts a loud crash into a quiet leak and subtler state-divergence bugs.
- Reaching for "compiler bug" before ruling out your own undefined behavior is almost always wrong.

## Stop signs

Stop and return to investigation when you notice: proposing a fix before reproducing or
tracing the cause; changing multiple variables at once; adding a workaround to hide the
symptom; relying on a manual check when automated verification is possible; assuming the
error message is misleading without proving it; fixing code you do not understand; or
attempting a fourth speculative fix after three failed fixes.

When debugging was invoked from an active merge/rebase integration, return control to
[../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md) afterward.

## Progressive disclosure

- `references/bug-taxonomy.md` — classify bugs and choose prevention-by-design tactics
- `references/reproduction-and-bisection.md` — shrink repros and bisect regressions
- `references/instrumentation-and-checks.md` — assertions, sanitizers, and tripwire discipline
- `references/determinism-and-replay.md` — make intermittent bugs reproducible
- `references/diagnostic-techniques.md` — tracing, comparison, bisection, bug-class table
- `references/gotchas.md` — common misreadings and anti-patterns
- `references/debugging-report.md` — final report template
- [../cpp-coding/references/build-and-verification.md](../cpp-coding/references/build-and-verification.md) — C++ sanitizer builds, clang-tidy, coverage (via [cpp-coding](../cpp-coding/SKILL.md))
