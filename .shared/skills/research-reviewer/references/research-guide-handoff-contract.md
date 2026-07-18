# Research Guide Handoff Contract

The research-guide handoff packet is the structured bridge from `research-reviewer` back to `research-guide` when the report is not yet ready for planning.

Produce it for `needs revision` and `blocked` verdicts, and for `conditionally ready` when the conditions are not already accepted.

## Required fields

```markdown
## Research handoff packet
- Target skill: research-guide
- Review verdict: ready | conditionally ready | needs revision | blocked
- Confidence: high | medium | low
- Planning recommendation: proceed | proceed with accepted risks | revise first | do not plan yet
- Iteration required: yes | no
- Highest-priority repair track: clarify scope | validate assumption | gather evidence | resolve open question | reconcile contradiction | narrow direction | expand alternatives | none
- Recommended research-guide repair mode: full rewrite | targeted section repair | blocker-only repair | research iteration | narrow scope | none
- Sections or ids to preserve unchanged:
  - [section, requirement id, evidence item, risk id, or open-question id]
- Findings requiring research-guide action:
  - [finding id]: [severity] [summary]
    - required action: revise report | ask user | inspect codebase | gather evidence | validate assumption | resolve open question | reconcile contradiction | narrow scope | expand alternatives | accept as planning risk | re-review
    - affected section: [scope/goals/requirements/evidence/risks/etc.]
    - expected revision: [concrete change]
- User decisions needed:
  - [decision]
- Assumptions to validate:
  - [assumption and how to validate]
- Open questions blocking readiness:
  - [question]
- Findings that may be accepted as planning risks:
  - [finding id and risk]
- Findings rejected or out of scope:
  - [finding id and rationale]
- Re-review required before planning: yes | no | recommended
```

## Semantics

- `Iteration required` must be yes for `blocked` and `needs revision` verdicts.
- `Iteration required` must be yes for `conditionally ready` unless all conditions are already explicitly accepted.
- `Planning recommendation` must be `do not plan yet` when core scope, target users, recommendation, acceptance criteria, or a blocking open question is missing.
- `Planning recommendation` must be `revise first` when unresolved major findings would force the planner to invent missing decisions.
- `Highest-priority repair track` names the single next best move, not every option.
- `Recommended research-guide repair mode` should minimize churn while making planning readiness honest.
- `Sections or ids to preserve unchanged` protects stable requirement ids, evidence ledger rows, risk rows, open-question ids, and sections that already passed review.
- Separate user decisions from assumptions to validate and from open questions.
- Make expected revisions concrete enough for `research-guide` to apply without re-reading the full review.
- Re-review is required before planning after a `blocked` verdict, and after `needs revision` unless the fixes were trivial and self-evident.
