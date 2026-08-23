# Review Quality Checklist

Run this checklist before presenting a plan-reviewer report.

## Verdict and severity

- The verdict matches the highest-impact unresolved finding.
- `validated` has no blocker or major findings and no missing mandatory TDD, traceability, or verification gates.
- `conditionally validated` has no blockers, and every remaining major risk is explicit, narrow, and accepted or acceptably deferrable.
- `needs revision` is used when targeted repairs can make the plan executable.
- `blocked` is used when execution would be unsafe, impossible, or likely to build the wrong thing.

## Scope and depth

- Review depth is recorded as focused, standard, or rigorous.
- Focused review does not relax TDD, source traceability, blocker handling, task actionability, or verification.
- Rigorous review covers relevant domain, risk, rollout, rollback, migration, security/privacy, performance, observability, and execution-handoff concerns.
- Input mode and planning depth are reflected in the verdict rationale.

## Finding quality

- Every blocker and major finding has a concrete required fix and plan-guide action.
- Findings distinguish source-alignment defects from plan-format defects.
- Findings cite affected sections, task ids, source items, files, or verification items when available.
- No nit or style preference blocks execution.
- Prior finding ids are preserved on re-review; new ids are used only for new issues.

## Handoff quality

- The Guide handoff packet includes every required field from `guide-handoff-contract.md`.
- User decisions, codebase facts to inspect, upstream research/spec issues, and accepted execution risks are separated.
- Recommended repair mode minimizes churn and preserves stable task ids or validated sections where possible.
- Re-review requirement matches verdict and risk.

## Gate correctness

- Blocked and needs-revision reports do not offer accept or execute as executable-ready options.
- Conditionally validated reports state accepted risks before any execution handoff.
- Execute is offered only for validated plans or conditionally validated plans with explicitly accepted risks.
