# Guide Handoff Contract

The Guide handoff packet is the structured bridge from `plan-reviewer` back to `plan-guide`.

## Required fields

```markdown
## Guide handoff packet
- Target skill: plan-guide
- Review verdict: validated | conditionally validated | needs revision | blocked
- Confidence: high | medium | low
- Execution recommendation: proceed | proceed with accepted risks | revise first | do not execute
- Iteration required: yes | no
- Input mode observed: research handoff | direct spec | codebase-led | plan normalization | review repair loop | unknown
- Planning depth observed: focused | standard | rigorous | unknown
- Review depth used: focused | standard | rigorous
- Highest-priority repair track: revise plan | ask user | inspect codebase | research upstream | narrow scope | split plan | accept risks | none
- Recommended plan-guide repair mode: full rewrite | targeted section repair | blocker-only repair | split plan | none
- Sections or task ids to preserve unchanged:
  - [section or task id]
- Findings requiring plan-guide action:
  - [finding id]: [severity] [summary]
    - required action: [action]
    - affected plan area: [section/task]
    - expected repair: [concrete change]
- User decisions needed:
  - [decision]
- Codebase/project facts to inspect:
  - [fact]
- Upstream research/spec issues:
  - [issue]
- Findings that may be accepted as execution risks:
  - [finding id and risk]
- Findings rejected or out of scope:
  - [finding id and rationale]
- Re-review required before execution: yes | no | recommended
```

## Semantics

- `Iteration required` must be yes for blocked and needs revision verdicts.
- `Iteration required` must be yes for conditionally validated verdicts unless all conditions are already explicitly accepted.
- `Execution recommendation` must be do not execute when unresolved blockers exist.
- `Execution recommendation` must be revise first when unresolved major findings prevent reliable execution.
- `Highest-priority repair track` should identify the next best move, not list every possible move.
- `Recommended plan-guide repair mode` should minimize churn: prefer targeted section repair when the plan structure is sound and full rewrite only when the plan is broadly unsafe, inconsistent, or untraceable.
- `Sections or task ids to preserve unchanged` should protect stable ids and validated sections during re-review loops.
- Separate user decisions from codebase facts and upstream research gaps.
- Make expected repairs concrete enough for `plan-guide` to apply without reinterpreting the full review.
