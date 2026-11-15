# Validation Rubric

Use this rubric to assign severity, verdict, confidence, and planning readiness.

## Severity levels

| severity | meaning | planning impact | examples |
|---|---|---|---|
| Blocker | The report cannot safely or meaningfully feed implementation planning. | Planning should not proceed. | Missing problem or target user; recommendation contradicts requirements; core decision unresolved; high-risk compliance/security claim unsupported; acceptance criteria absent for critical behavior. |
| Major | The report can be understood, but planning would require risky invention or significant clarification. | Revise before serious planning, or carry as explicit planning risk only if accepted. | Weak evidence for a central claim; unclear priority; missing integration dependency; alternative rejected without a valid reason; major risk lacks mitigation. |
| Minor | The report is mostly usable, but clarity, completeness, or traceability should improve. | Can often be fixed during planning. | Requirement wording is vague but intent is clear; metric lacks target; non-blocking open question lacks owner. |
| Question | A reviewer needs clarification before assigning severity or recommending a fix. | May become major or blocker depending on answer. | Ambiguous stakeholder; unclear domain constraint; missing source for a claim that may be important. |
| Nit | Editorial or formatting issue with no planning impact. | Does not affect readiness. | Section name inconsistency, duplicated phrasing, minor formatting. |

## Verdict rules

| verdict | required conditions |
|---|---|
| Ready | No blocker or major findings. Minor/nit findings do not prevent implementation planning. |
| Conditionally ready | No blocker findings. Major findings are explicit, narrow, and can be accepted as early planning risks. |
| Needs revision | One or more major findings prevent reliable implementation planning, but targeted fixes can make the report ready. |
| Blocked | One or more blocker findings make planning unsafe, misleading, or impossible. |

Do not assign Ready when any of these are missing or contradictory:
- Problem statement
- Target users or stakeholders
- Scope and non-goals
- Recommended direction or decision status
- Must-have requirements
- Acceptance criteria or testable acceptance signals for core behavior
- Evidence/assumption separation for central claims
- Blocking open questions clearly labeled
- Implementation-planning handoff

## Confidence levels

| confidence | use when |
|---|---|
| High | The report is complete enough to judge, and findings are grounded in explicit report content or cited sources. |
| Medium | The report is mostly reviewable, but some domain or source context is missing. |
| Low | The review depends on inferred context, missing sections, or unverified domain assumptions. |

## Audit categories

### Completeness

Check whether the report includes enough information for planning:
- Problem/opportunity
- Users/stakeholders
- Goals and non-goals
- Success metrics
- Functional and non-functional requirements
- Acceptance criteria or acceptance signals
- Alternatives considered
- Evidence and assumption ledger
- Risks, edge cases, and mitigations
- Dependencies and open questions
- Implementation-planning handoff

### Consistency

Check for contradictions:
- Goals conflict with non-goals.
- Requirements exceed stated scope.
- Recommendation ignores constraints.
- Alternatives are rejected for reasons that also apply to the recommendation.
- Open questions contradict the agreement state.
- Success metrics cannot measure the stated outcome.

### Evidence quality

Check whether:
- External or internal facts are cited when sources are used.
- User claims are labeled as user claims.
- Assumptions have confidence and planning impact.
- Inferences are not presented as facts.
- Current or domain-specific claims are marked for verification when unsourced.

### Requirements quality

Check whether requirements are:
- Atomic enough to plan.
- Testable enough to validate.
- Prioritized as must/should/could or equivalent.
- Traceable to goals or risks.
- Not mixed with implementation tasks.
- Accompanied by acceptance signals.

### Risk quality

Check whether risks include:
- Failure mode or edge case.
- Likelihood and impact.
- Mitigation or owner/phase.
- Security, privacy, data, operational, migration, performance, and adoption concerns where relevant.

### Handoff readiness

Check whether an implementation planner can identify:
- First implementation slice.
- Dependencies to resolve first.
- Testing focus.
- Rollout, migration, or rollback concerns.
- Blocking vs non-blocking open questions.

## Finding format

Every material finding should include:
- id: rr-001, rr-002, etc.
- severity
- affected section
- issue
- why it matters
- required fix
- recommended research-guide action: revise report, ask user, inspect codebase, gather evidence, validate assumption, resolve open question, reconcile contradiction, narrow scope, expand alternatives, accept as planning risk, or re-review
- owner suggestion when useful
