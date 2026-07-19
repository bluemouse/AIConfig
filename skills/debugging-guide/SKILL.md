---
name: debugging-guide
description: "Use when diagnosing a software defect before fixing it — reproducing or shrinking failures, tracing root cause with evidence, ranking hypotheses, choosing prevention-by-design tripwires, writing regression tests, applying a minimal fix, and verifying with commands. Triggers on crashes, segfaults, access violations, use-after-free, 0xdddddddd fill patterns, failing tests, build failures, regressions, flaky behavior, minimal repro, git bisect, precondition assertions, sanitizers, allocation tagging and zero-on-shutdown leak checks, dangling-pointer crashes, buffer-overwrite classes, and integration failures — even when the user does not say debugging. Does not trigger on strict TDD coaching (test-driven-dev-guide), correctness audits (implementation-auditor), diff review (code-reviewer), plan execution (plan-executor), codebase learning (code-professor), profiling without a defect, ownership API design (cpp-memory-guide), or native GDB/LLDB steps while editing C++ (cpp-coding)."
---

# Debugging Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Locate the true root cause of a software bug and apply the smallest correct fix. Treat
debugging as an evidence-driven investigation, not a guessing loop.

## Primary Directive

Your job is to **diagnose the root cause with evidence and apply a minimal verified fix**,
not to coach strict TDD, audit post-implementation correctness, review diffs, or execute
implementation plans.

## When to Use

- Reproducing and tracing a crash, failing test, build failure, regression, or flaky behavior
- Gathering evidence, forming hypotheses, and confirming cause before changing production code
- Writing or updating a regression test or durable reproducer for a specific defect
- Applying a focused production fix and verifying it with commands
- Producing a debugging report for reviewers or follow-up agents

## When NOT to Use

- **Strict TDD coaching during active implementation** — use
  [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md)
- **Post-implementation correctness audit** — use
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
- **Structured diff or commit review** — use
  [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Plan execution without a debugging focus** — use
  [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- **Open-ended codebase learning or architecture documentation** — use
  [../code-professor/SKILL.md](../code-professor/SKILL.md) when the goal is a teaching
  guide, not a verified fix
- **Performance optimization or profiling without a defect** — use language or domain skills
- **Ownership/lifetime API design (not chasing a specific bug)** — use
  [../cpp-memory-guide/SKILL.md](../cpp-memory-guide/SKILL.md) for C++ memory design

## Iron rule

Do not propose or apply a production fix until you can state:

1. the observed symptom;
2. the earliest incorrect transition that caused it;
3. the evidence proving that transition is the root cause;
4. the test, command, or experiment that will fail before the fix and pass after it.

A symptom is not a root cause. A plausible explanation is not evidence. A manual check is
not enough when an automated test or durable reproducer can be created.

## Workflow

### 1. Freeze the scope

- Inspect the current state before editing: branch, dirty files, recent commits, failing command, config, environment, and user-provided reproduction steps.
- Do not switch branches, discard changes, reformat unrelated files, or mix cleanup with debugging unless the user explicitly asks.
- Define the bug in one sentence: expected behavior, actual behavior, and impact.
- Identify the smallest affected surface: function, module, boundary, platform, build variant, dependency, data shape, feature flag, or external service.

### 2. Reproduce before changing code

- Run the failing command, test, build, scenario, or minimal manual reproduction before editing.
- Record exact commands, inputs, relevant logs, stack traces, assertions, screenshots, timestamps, exit codes, dependency versions, and platform details.
- For intermittent failures, repeat enough times to estimate frequency and capture at least one failing trace. Record seed, order, clock, thread, device, network, and cache state when relevant.
- If the failure cannot be reproduced, add diagnostics or request missing reproduction data. Do not guess a fix.
- Load `references/reproduction-and-bisection.md` when shrinking a slow repro or bisecting history.
- Load `references/determinism-and-replay.md` when the bug is intermittent and you need determinism, stress, logging, or record/replay.

### 3. Read the failure literally

- Read the complete error message, stack trace, assertion text, and surrounding logs before opening broad code areas.
- Prefer the first meaningful failure in time over later cascade errors.
- Follow line numbers, file paths, invariant names, error codes, request ids, object ids, and thread/process ids exactly.
- Separate what is known from what is inferred. Mark assumptions until evidence proves them.
- Load `references/scientific-debugging.md` when ranking hypotheses from crash or error evidence.

### 4. Classify the bug

- Name the bug class before tracing deeply: logic/edge case, unexpected initial condition, state mutation, memory safety, concurrency, build/config, platform, integration/schema, flakiness, or design flaw.
- Ask what design or tripwire would have prevented every bug in that class, not only this instance.
- After the fix, note the class and one structural prevention for follow-up.
- Load `references/bug-taxonomy.md` for class-specific prevention tactics.

### 5. Trace backward to the earliest incorrect transition

Start at the observable failure and walk backward through data, control, state, configuration, ownership, timing, or build flow.

For each hop, answer:

- What input entered here?
- What output or state left here?
- What invariant should hold here?
- Where was that invariant first violated?
- Which caller, dependency, config, generated file, cache, thread, or platform condition allowed it?

For multi-component systems, instrument boundaries first: UI to app, app to service, service to database, parser to model, producer to consumer, build step to packaging, host to plugin, or client to server. Log what enters and exits each boundary once, then remove temporary diagnostics before finishing unless they are intentionally useful permanent observability.

Load `references/diagnostic-techniques.md` for tracing, differential comparison, bisecting, and bug-class-specific tactics.
Load `references/instrumentation-and-checks.md` when adding assertions, sanitizers, or tripwires — instrument to surface the fault **earlier** or where it is cheaper to act on, not to restate what the crash already showed.

When reproduction exists and the defect is in **native C++**, load GDB/LLDB, sanitizer,
and core-dump steps from
[../cpp-coding/references/native-debugging.md](../cpp-coding/references/native-debugging.md)
(via [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md)).

### 6. Compare against working patterns

- Find the closest working example in the same codebase before inventing a new approach.
- Compare broken and working paths: inputs, flags, lifetime, thread, platform, config, data shape, generated artifacts, dependency versions, and recent diffs.
- List differences before judging which difference matters.
- Read reference implementations completely when the bug is caused by an incomplete pattern, adapter, protocol, API contract, or framework lifecycle.

### 7. Form and test one hypothesis at a time

Use this exact thought structure before each experiment:

```text
Hypothesis: [specific root cause mechanism]
Evidence so far: [facts only]
Prediction: if true, [minimal observation] will show [specific result]
Experiment: [one command, diagnostic, breakpoint, assertion, or tiny probe]
Outcome: [confirmed/rejected + evidence]
```

Rules:

- Test one variable at a time.
- Prefer observation, instrumentation, and focused tests before production edits.
- If an experiment disproves the hypothesis, discard it and form a new one; do not stack speculative fixes.
- If three production fix attempts fail or each fix reveals a different shared-state/coupling problem, stop and reassess the design with the user before attempting another fix.

### 8. Create a failing test or durable reproducer

Before the production fix, create the smallest regression test or reproducer that captures the root cause.

Prefer, in order:

1. a focused unit test when the bug is local;
2. an integration or component test when the boundary is the bug;
3. a system/end-to-end test when behavior only fails in the full stack;
4. a deterministic reproducer script or command if the codebase lacks a suitable test harness.

Use [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md) when available. The test or reproducer must fail against the buggy behavior and pass only after the fix. Do not write tests that simply encode the implementation detail you are about to change.

### 9. Apply the minimal root-cause fix

- Fix the earliest incorrect transition, not the nearest symptom.
- Make the smallest production change that satisfies the failing test and preserves existing valid behavior.
- Keep names, architecture, style, error handling, ownership, and threading conventions consistent with nearby code.
- Add validation or defensive handling only at boundaries where invalid state can enter.
- Avoid broad catches, sleeps, global state, hidden retries, silent fallbacks, duplicated logic, or unrelated refactors.
- If cleanup is necessary to make the fix safe, state why it is required for the fix.

### 10. Verify with evidence

Run verification in increasing scope:

1. the new failing test or reproducer;
2. the smallest existing related test set;
3. broader package/module tests affected by the change;
4. build, typecheck, lint, sanitizer, race detector, static analyzer, platform-specific test, or performance check when relevant.

If verification cannot be run, state exactly why, what was not verified, and which command should be run next. Do not claim the bug is fixed without command-backed evidence.

Use [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) when available for an independent correctness and evidence review.

### 11. Produce the debugging report

End every debugging task with a compact report. Load `references/debugging-report.md` and follow the template.

The report must include:

- status;
- expected and actual behavior;
- reproduction command or steps;
- root cause as the earliest incorrect transition;
- evidence and rejected alternatives;
- changed files and fix summary;
- tests/commands run with results;
- residual risk and follow-up.

After the fix is verified, hand off deliberately: for complex or shared-code fixes, route to [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) for requirement-level correctness proof, then to [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) for the fix diff before delivery. For a small, well-contained fix with a passing regression test, a direct [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) pass is enough. Record the chosen next step in the report's Next Step field.

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

Stop and return to investigation when you notice any of these:

- proposing a fix before reproducing or tracing the cause;
- changing multiple variables at once;
- adding a workaround to hide the symptom;
- relying only on a manual check when automated verification is possible;
- assuming the error message is misleading without proving it;
- skipping a working-example comparison;
- fixing code you do not understand;
- attempting a fourth speculative fix after three failed fixes.

## Completion checklist

Before finishing, ensure:

- root cause is specific and evidence-backed;
- regression test or durable reproducer exists when feasible;
- fix is minimal and localized;
- unrelated changes are absent or explicitly justified;
- exact verification commands and outcomes are reported;
- temporary diagnostics are removed or intentionally retained as useful observability.

## Progressive disclosure

Load these references on demand:

- `references/bug-taxonomy.md` — classify bugs and choose prevention-by-design tactics
- `references/scientific-debugging.md` — hypothesis ranking and confirm-before-fix discipline
- `references/reproduction-and-bisection.md` — shrink repros and bisect regressions
- `references/instrumentation-and-checks.md` — assertions, sanitizers, and tripwire discipline
- `references/determinism-and-replay.md` — make intermittent bugs reproducible
- `references/diagnostic-techniques.md` — tracing, comparison, bisection, bug-class table
- `references/gotchas.md` — common misreadings and anti-patterns
- `references/debugging-report.md` — final report template
- [../cpp-coding/references/native-debugging.md](../cpp-coding/references/native-debugging.md) — C++ GDB/LLDB, sanitizers, core dumps (after repro exists; via [cpp-coding](../cpp-coding/SKILL.md))
