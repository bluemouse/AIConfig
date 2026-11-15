# Review Quality Checklist

Run this checklist before presenting a research-reviewer report.

## Verdict and severity

- The verdict matches the highest-impact unresolved finding.
- `ready` has no blocker or major findings and no missing mandatory planning-readiness inputs.
- `conditionally ready` has no blockers, and every remaining major risk is explicit, narrow, and accepted or acceptably deferrable.
- `needs revision` is used when targeted repairs can make the report ready for implementation planning.
- `blocked` is used when planning would be unsafe, misleading, impossible, or likely to build the wrong thing.

## Scope and depth

- Review depth is recorded as focused, standard, or rigorous.
- Focused review does not relax source alignment, evidence separation, blocker handling, acceptance signals, or implementation-handoff checks.
- Rigorous review covers relevant domain, risk, rollout, migration, security/privacy, compliance, performance, observability, support, and planning-handoff concerns.
- Research depth, agreement state, and domain assumptions are reflected in the verdict rationale.

## Finding quality

- Every blocker and major finding has a concrete required fix and research-guide action.
- Findings distinguish source/evidence defects from report-structure defects.
- Findings cite affected sections, requirement ids, evidence items, risk rows, source items, files, or open questions when available.
- No nit or style preference blocks planning.
- Prior finding ids are preserved on re-review; new ids are used only for new issues.

## Handoff quality

- The research handoff packet includes every required field from `research-guide-handoff-contract.md` when the verdict requires one.
- User decisions, codebase facts to inspect, evidence to gather, assumptions to validate, and accepted planning risks are separated.
- Recommended repair track minimizes churn and preserves stable ids or validated sections where possible.
- Re-review requirement matches verdict and risk.

## Gate correctness

- Blocked and needs-revision reports do not offer accept as planning-ready.
- Conditionally ready reports state accepted risks before any planning handoff.
- Handoff to `plan-guide` is recommended only for ready reports, or conditionally ready reports with explicitly accepted planning risks.
