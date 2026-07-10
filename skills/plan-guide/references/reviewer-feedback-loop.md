# Reviewer Feedback Loop

Use this protocol when the user provides a `plan-reviewer` report, review findings, or a Guide handoff packet.

## 1. Parse reviewer output

Extract:
- Verdict: validated, conditionally validated, needs revision, or blocked.
- Confidence: high, medium, or low.
- Execution recommendation: proceed, proceed with conditions, revise first, or do not execute.
- Active reviewer roles and domain assumptions.
- Findings with ids, severity, affected plan sections/tasks, issue, and required fix.
- Required revision plan.
- Guide handoff packet.
- Reviewer questions and re-review recommendation.

If the review lacks a handoff packet, synthesize one from verdict, findings, and required fixes.

## 2. Decide whether another plan iteration is required

| reviewer verdict | plan-guide response |
|---|---|
| Validated | No repair iteration is required. Offer finalization or optional polish. |
| Conditionally validated | Ask whether to accept conditions as execution risks or repair them before execution. |
| Needs revision | Require at least one targeted plan repair iteration before claiming readiness. |
| Blocked | Do not claim execution readiness. Resolve blocker findings or produce a blocked plan. |

Severity override:
- Any unresolved blocker prevents execution readiness.
- Any unresolved major finding prevents validated status unless explicitly accepted as an execution risk under a conditionally validated status.
- Minor/nit findings can be fixed opportunistically or carried if visible.

## 3. Triage each finding

Classify each material finding:

- **Revise plan**: existing context is enough to fix the plan.
- **Ask user**: a scope, product, risk, priority, or execution decision is required.
- **Inspect codebase**: repository/project facts must be checked before repair.
- **Research upstream**: source research/spec/requirements are insufficient; return to research-guide or source owner.
- **Narrow scope**: the plan is too broad or mixes independent systems.
- **Accept as execution risk**: allowed only for non-blocker findings and only if explicit.
- **Reject with rationale**: allowed only when the finding is out of scope, contradicted by source context, or based on a reviewer misunderstanding.
- **Still blocking**: cannot be resolved in the current context.

Do not silently reject reviewer findings.

## 4. Produce a repair summary before editing

```markdown
Plan-reviewer triage:
- Verdict received: [verdict, confidence]
- Repair iteration required: yes/no
- Highest-impact issue: [finding id and summary]
- Proposed repair track: [revise plan / ask user / inspect codebase / research upstream / narrow scope]
- Findings to resolve now: [ids]
- Findings to carry, reject, or leave blocked: [ids and rationale]
```

Then either revise the plan or ask the one next required question.

## 5. Update the implementation plan

When finalizing after reviewer feedback, include a **Reviewer feedback status** section with:
- Latest reviewer verdict and confidence.
- Findings resolved and where they were resolved.
- Findings accepted as execution risks.
- Findings rejected with rationale.
- Remaining blockers or major issues.
- Recommendation on whether another `plan-reviewer` pass is needed.

Prefer a clear blocked plan over a misleading ready plan.
