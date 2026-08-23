# Reviewer Feedback Loop

Use this protocol when the user provides a `research-reviewer` report, review findings, or a research handoff packet. Field semantics match [../../research-reviewer/references/research-guide-handoff-contract.md](../../research-reviewer/references/research-guide-handoff-contract.md). When updating a report after prior findings, preserve finding identity so a later re-review can judge what changed.

## 1. Parse reviewer output

Extract from the review report and handoff packet:

- Verdict: ready, conditionally ready, needs revision, or blocked.
- Confidence: high, medium, or low.
- Planning recommendation: proceed, proceed with accepted risks, revise first, or do not plan yet.
- Iteration required: yes or no.
- Highest-priority repair track: clarify scope, validate assumption, gather evidence, resolve open question, reconcile contradiction, narrow direction, expand alternatives, or none.
- Recommended research-guide repair mode: full rewrite, targeted section repair, blocker-only repair, research iteration, narrow scope, or none.
- Sections or ids to preserve unchanged.
- Findings with ids, severity, affected report sections, issue, required fix, and research-guide action.
- User decisions needed, assumptions to validate, open questions blocking readiness, and accepted planning risks.
- Findings rejected or out of scope.
- Re-review required before planning: yes, no, or recommended.
- Active reviewer roles, domain assumptions, and required revision plan when provided.

If the review lacks a handoff packet, synthesize one from verdict, findings, and required fixes using the field list in the handoff contract.

Treat `proceed with accepted risks` as explicit planning risks recorded in the research report, not informal conditions.

## 2. Decide whether another research iteration is required

| reviewer verdict | research-guide response |
|---|---|
| Ready | No repair iteration is required. Offer finalization, optional polish, or handoff to plan-guide. |
| Conditionally ready | Ask whether to accept remaining risks as planning risks or repair them before planning. |
| Needs revision | Require at least one targeted research/report repair iteration before claiming planning readiness. |
| Blocked | Do not claim planning readiness. Resolve blocker findings or produce a blocked research report. |

Severity override:
- Any unresolved blocker prevents planning readiness.
- Any unresolved major finding prevents `agreed` status unless explicitly accepted as a planning risk under `partially agreed` or `conditionally ready`.
- Minor/nit findings can be fixed opportunistically or carried if visible.

Honor `Iteration required` and `Re-review required before planning` from the handoff packet. After a blocked verdict, require re-review before implementation planning. After needs revision, re-review unless every finding was trivial and self-evidently fixed.

## 3. Choose repair mode and preserve stable structure

Use `Recommended research-guide repair mode` and `Sections or ids to preserve unchanged` to minimize churn:

| repair mode | use when |
|---|---|
| Blocker-only repair | Only blocker findings remain and other report sections are sound. |
| Targeted section repair | Default when findings map to specific report sections or ledger entries. |
| Research iteration | New evidence, user decisions, codebase inspection, or domain clarification is needed. |
| Narrow scope | The report mixes independent products, systems, or user workflows. |
| Full rewrite | The report is broadly inconsistent, untraceable, or unsafe for planning. |
| None | Ready or no edits needed. |

- Preserve listed requirement ids, evidence ledger items, risk ids, open-question ids, and validated sections unless a finding requires changing them.
- Keep original `rr-*` finding ids for unresolved or partially resolved issues; create new ids only for genuinely new issues.
- Mark findings resolved, partially resolved, reopened, accepted as planning risk, rejected with rationale, or still blocking.

## 4. Triage each finding

Classify each material finding:

- **Revise report**: existing context is enough to fix the research report.
- **Ask user**: a scope, product, risk, priority, or decision is required.
- **Inspect codebase**: repository/project facts must be checked before repair.
- **Gather evidence**: external, internal, current, or domain facts must be sourced.
- **Validate assumption**: an important claim must be confirmed, disproven, or downgraded.
- **Resolve open question**: a blocking question must be answered or explicitly carried as a planning risk.
- **Reconcile contradiction**: report sections disagree and must be made consistent.
- **Narrow scope**: the research scope is too broad or mixes independent systems.
- **Expand alternatives**: decision quality is weak because credible options were omitted.
- **Accept as planning risk**: allowed only for non-blocker findings and only if explicit.
- **Reject with rationale**: allowed only when the finding is out of scope, contradicted by source context, or based on a reviewer misunderstanding.
- **Still blocking**: cannot be resolved in the current context.

Do not silently reject or drop prior blocker or major findings.

## 5. Produce a repair summary before editing

```markdown
Research-reviewer triage:
- Verdict received: [verdict, confidence]
- Planning recommendation: [proceed | proceed with accepted risks | revise first | do not plan yet]
- Repair iteration required: yes/no
- Repair mode: [full rewrite | targeted section repair | blocker-only repair | research iteration | narrow scope | none]
- Sections or ids to preserve unchanged: [list]
- Highest-impact issue: [finding id and summary]
- Proposed repair track: [revise report | ask user | inspect codebase | gather evidence | validate assumption | resolve open question | reconcile contradiction | narrow scope | expand alternatives]
- Findings to resolve now: [ids]
- Findings to carry, reject, or leave blocked: [ids and rationale]
- Re-review required before planning: [yes | no | recommended]
```

Then either revise the report or ask the one next required question.

## 6. Update the research report

When finalizing after reviewer feedback, include a **Reviewer feedback status** section with:

- Latest reviewer verdict and confidence.
- Findings resolved, partially resolved, and reopened, with original finding ids preserved.
- Findings accepted as planning risks.
- Findings rejected with rationale.
- Remaining blockers or major issues.
- Recommendation on whether another `research-reviewer` pass is needed.

Prefer a clearly blocked research report over a misleading ready-for-planning report.
