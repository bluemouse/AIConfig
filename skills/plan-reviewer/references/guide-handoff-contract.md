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
- Highest-priority repair track: revise plan | ask user | inspect codebase | research upstream | narrow scope | split plan | accept risks | none
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
- Separate user decisions from codebase facts and upstream research gaps.
- Make expected repairs concrete enough for `plan-guide` to apply without reinterpreting the full review.
