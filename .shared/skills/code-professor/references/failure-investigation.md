# Failure investigation guide

Use this document for a failure, regression, crash, hang, incorrect result, performance problem, resource leak, or flaky behavior.

This skill **documents failure for learning** — reproduction, evidence, ranked hypotheses, and optional candidate fixes as **proposals only**. When the user wants a **verified fix applied**, hand off to [../../debugging-guide/SKILL.md](../../debugging-guide/SKILL.md) — do not apply production patches in code-professor. See [skill-boundaries.md](skill-boundaries.md).

## Default structure

# Failure investigation: [symptom]

## 1. Symptom and scope

State the observed behavior, expected behavior, affected configuration, reproducibility, and known boundaries. Separate user-reported facts from verified observations.

## 2. Reproduction

Provide the smallest reliable reproduction found. Include prerequisites, exact commands, inputs, environment, and observed output.

## 3. Execution path under investigation

Trace the relevant path from trigger to failure. Cite each substantive step.

## 4. Evidence and narrowing

Present observations in the order that eliminates alternatives. Include tests, logs, debugger results, traces, diffs, or controlled experiments.

## 5. Root cause or ranked hypotheses

If established, explain the root cause, mechanism, and why it produces the symptom. If not established, provide ranked hypotheses with supporting and contradicting evidence plus the next discriminating test.

Every debugging conclusion requires permanent path:line support. Runtime-only evidence must also include the exact command or observation.

## 6. Candidate fix

When useful, describe:

- smallest plausible change
- files and interfaces affected
- invariants to preserve
- regression risk
- tests required
- confidence level

Do not call a proposal a confirmed fix until implementation and validation succeed in **debugging-guide**. Do not apply a fix in code-professor — hand off to [../../debugging-guide/SKILL.md](../../debugging-guide/SKILL.md).

## 7. Validation plan or result

List focused tests first, then broader checks. Report what was actually run, what passed or failed, and what could not be run.

## 8. Cleanup and remaining unknowns

Confirm temporary instrumentation was removed and repository state was restored. List unresolved questions and environmental limitations.
