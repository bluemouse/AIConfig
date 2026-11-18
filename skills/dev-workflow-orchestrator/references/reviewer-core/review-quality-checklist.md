# Review Quality Checklist (shared by plan-reviewer and research-reviewer)

Run this checklist before presenting a review report. Per-skill parameters:

| parameter | plan-reviewer | research-reviewer |
|---|---|---|
| Accept verdict | `validated` | `ready` |
| Conditional verdict | `conditionally validated` | `conditionally ready` |
| Downstream step | execution | implementation planning |
| Handoff contract | `guide-handoff-contract.md` (plan-reviewer) | `research-guide-handoff-contract.md` (research-reviewer) |

## Verdict and severity

- The verdict matches the highest-impact unresolved finding.
- The accept verdict has no blocker or major findings and no missing mandatory inputs (for plans: TDD where the task's discipline is `mandatory`, traceability, per-task verification; for reports: planning-readiness inputs).
- The conditional verdict has no blockers, and every remaining major risk is explicit, narrow, and accepted or acceptably deferrable.
- `needs revision` is used when targeted repairs can make the artifact ready for its downstream step.
- `blocked` is used when the downstream step would be unsafe, impossible, misleading, or likely to build the wrong thing.

## Scope and depth

- Review depth is recorded as focused, standard, or rigorous.
- Focused review does not relax the skill's core checks (plan: verification, source traceability, blocker handling, task actionability, mandatory-TDD tasks; report: source alignment, evidence separation, blocker handling, acceptance signals, handoff checks).
- Rigorous review covers relevant domain, risk, rollout, rollback, migration, security/privacy, (report: compliance,) performance, observability, and handoff concerns.
- The producing skill's observed input mode and depth are reflected in the verdict rationale.

## Finding quality

- Every blocker and major finding has a concrete required fix and producing-skill action.
- Findings distinguish source/evidence defects from artifact-structure defects.
- Findings cite affected sections, ids, source items, files, or verification items when available.
- No nit or style preference blocks the downstream step.
- Prior finding ids are preserved on re-review; new ids are used only for new issues.

## Handoff quality

- The handoff packet includes every required field from the skill's handoff contract.
- User decisions, codebase facts to inspect, upstream issues, and accepted risks are separated.
- Recommended repair mode minimizes churn and preserves stable ids or validated sections where possible.
- Re-review requirement matches verdict and risk.

## Gate correctness

- Blocked and needs-revision reports do not offer accept as downstream-ready.
- Conditional reports state accepted risks before any handoff.
- Handoff to the downstream step is offered only for accepted reports, or conditional reports with explicitly accepted risks.
