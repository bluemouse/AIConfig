# Reviewer Feedback Loop

Use this protocol when the user provides a `plan-reviewer` report, review findings, or a Guide handoff packet. Field semantics match [../../plan-reviewer/references/guide-handoff-contract.md](../../plan-reviewer/references/guide-handoff-contract.md). When reviewing an updated plan after prior findings, also follow [../../plan-reviewer/references/re-review-protocol.md](../../plan-reviewer/references/re-review-protocol.md) for finding-id preservation and disposition rules.

## 1. Parse reviewer output

Extract from the review report and Guide handoff packet:

- Verdict: validated, conditionally validated, needs revision, or blocked.
- Confidence: high, medium, or low.
- Execution recommendation: proceed, proceed with accepted risks, revise first, or do not execute.
- Iteration required: yes or no.
- Input mode observed: research handoff, direct spec, codebase-led, plan normalization, review repair loop, or unknown.
- Planning depth observed: focused, standard, rigorous, or unknown.
- Review depth used: focused, standard, or rigorous.
- Highest-priority repair track: revise plan, ask user, inspect codebase, research upstream, narrow scope, split plan, accept risks, or none.
- Recommended plan-guide repair mode: full rewrite, targeted section repair, blocker-only repair, split plan, or none.
- Sections or task ids to preserve unchanged.
- Findings with ids, severity, affected plan sections/tasks, issue, required fix, and plan-guide action.
- User decisions needed, codebase/project facts to inspect, upstream research/spec issues.
- Findings that may be accepted as execution risks, and findings rejected or out of scope.
- Re-review required before execution: yes, no, or recommended.
- Active reviewer roles and domain assumptions.
- Required revision plan.
- Reviewer questions.

If the review lacks a handoff packet, synthesize one from verdict, findings, and required fixes using the field list in `guide-handoff-contract.md`.

Treat `proceed with accepted risks` as explicitly accepted execution risks recorded in the plan — not informal conditions.

## 2. Decide whether another plan iteration is required

| reviewer verdict | plan-guide response |
|---|---|
| Validated | No repair iteration is required. Offer finalization, optional polish, or execution handoff. |
| Conditionally validated | Ask whether to accept remaining risks as execution risks or repair them before execution. |
| Needs revision | Require at least one targeted plan repair iteration before claiming readiness. |
| Blocked | Do not claim execution readiness. Resolve blocker findings or produce a blocked plan. |

Severity override:
- Any unresolved blocker prevents execution readiness.
- Any unresolved major finding prevents validated status unless explicitly accepted as an execution risk under a conditionally validated status.
- Minor/nit findings can be fixed opportunistically or carried if visible.

Honor `Iteration required` and `Re-review required before execution` from the handoff packet. After a blocked verdict, require re-review before execution. After needs revision, re-review unless every finding was trivial and self-evidently fixed.

## 3. Choose repair mode and preserve stable structure

Use `Recommended plan-guide repair mode` and `Sections or task ids to preserve unchanged` to minimize churn:

| repair mode | use when |
|---|---|
| Blocker-only repair | Only blocker findings remain; plan structure and validated sections are sound. |
| Targeted section repair | Default when task structure is mostly sound and findings map to specific sections or task ids. |
| Split plan | Independent subsystems or scopes should become separate plans or phases. |
| Full rewrite | Plan is broadly unsafe, internally inconsistent, or untraceable. |
| None | Validated or no plan edits needed. |

- Preserve listed task ids, test ids, verification ids, and validated sections unless a finding requires changing them.
- Keep original finding ids for unresolved or partially resolved issues; create new ids only for genuinely new issues.
- Mark findings resolved, partially resolved, reopened, accepted as execution risk, rejected with rationale, or still blocking per `re-review-protocol.md`.

## 4. Triage each finding

Classify each material finding:

- **Revise plan**: existing context is enough to fix the plan.
- **Ask user**: a scope, product, risk, priority, or execution decision is required.
- **Inspect codebase**: repository/project facts must be checked before repair.
- **Research upstream**: source research/spec/requirements are insufficient; return to research-guide or source owner.
- **Narrow scope**: the plan is too broad or mixes independent systems.
- **Split plan**: independent subsystems should be planned separately.
- **Accept as execution risk**: allowed only for non-blocker findings and only if explicit.
- **Reject with rationale**: allowed only when the finding is out of scope, contradicted by source context, or based on a reviewer misunderstanding.
- **Still blocking**: cannot be resolved in the current context.

Do not silently reject or drop prior blocker or major findings.

## 5. Produce a repair summary before editing

```markdown
Plan-reviewer triage:
- Verdict received: [verdict, confidence]
- Execution recommendation: [proceed | proceed with accepted risks | revise first | do not execute]
- Repair iteration required: yes/no
- Repair mode: [full rewrite | targeted section repair | blocker-only repair | split plan | none]
- Sections or task ids to preserve unchanged: [list]
- Highest-impact issue: [finding id and summary]
- Proposed repair track: [revise plan / ask user / inspect codebase / research upstream / narrow scope / split plan]
- Findings to resolve now: [ids]
- Findings to carry, reject, or leave blocked: [ids and rationale]
- Re-review required before execution: [yes | no | recommended]
```

Then either revise the plan or ask the one next required question.

## 6. Update the implementation plan

When finalizing after reviewer feedback, include a **Reviewer feedback status** section with:
- Latest reviewer verdict and confidence.
- Findings resolved, partially resolved, and reopened (with original finding ids preserved).
- Findings accepted as execution risks.
- Findings rejected with rationale.
- Remaining blockers or major issues.
- Recommendation on whether another `plan-reviewer` pass is needed.

Prefer a clear blocked plan over a misleading ready plan.
