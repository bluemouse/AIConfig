# Research Report Template

Use this structure for the final report after the user chooses finalize. Keep it dense enough for implementation planning, but not padded.

```markdown
# Research Report: [Feature / Product / Idea Name]

## 1. Executive summary
[One short paragraph with the agreed direction, decision status, and most important trade-off.]

## 2. Agreement state
- Status: agreed | partially agreed | blocked
- Finalized on: [date if known]
- Decision owner: [user/team if known]
- Research posture used: moderate | aggressive
- Remaining decision needed before implementation planning: [none or list]

## 3. Problem statement
- Problem/opportunity:
- Target users/stakeholders:
- Current workaround or baseline:
- Why now:

## 4. Goals, non-goals, and success metrics
### Goals
- [goal]

### Non-goals
- [explicitly excluded scope]

### Success metrics
- [metric, target, measurement method if known]

## 5. Requirements
### Functional requirements
| id | requirement | priority | acceptance signal |
|----|-------------|----------|-------------------|
| fr-1 |  | must |  |

### Non-functional requirements
| id | requirement | priority | acceptance signal |
|----|-------------|----------|-------------------|
| nfr-1 |  | must |  |

## 6. Recommended direction
[State the recommended approach and why it best fits the goals and constraints.]

## 7. Alternatives considered
| option | summary | advantages | disadvantages | decision |
|--------|---------|------------|---------------|----------|
| option a |  |  |  | recommended/rejected/defer |

## 8. Evidence and assumption ledger
| item | type | confidence | source/evidence | planning impact |
|------|------|------------|-----------------|-----------------|
|  | sourced fact / project fact / user claim / assumption / inference | high/medium/low |  |  |

## 9. User experience and workflow implications
- Primary workflow:
- Edge workflows:
- Adoption/change-management considerations:
- Accessibility or localization considerations:

## 10. Technical implications
- Architecture impact:
- Data model or contract impact:
- Integrations/dependencies:
- Performance/scalability considerations:
- Security/privacy/compliance considerations:
- Observability/support needs:

## 11. Risks, edge cases, and mitigations
| risk or edge case | likelihood | impact | mitigation | owner/phase |
|-------------------|------------|--------|------------|-------------|
|  |  |  |  |  |

## 12. Open questions
| question | why it matters | proposed owner | required before implementation? |
|----------|----------------|----------------|---------------------------------|
|  |  |  | yes/no |

## 13. Implementation-planning handoff
- Recommended implementation slice:
- Suggested milestones:
- Dependencies to resolve first:
- Testing focus:
- Rollout or migration notes:
- Definition of ready for implementation planning:
```

Rules:
- Keep unresolved uncertainty visible instead of hiding it.
- Convert vague desires into testable requirements where possible.
- Mark optional ideas as future work rather than bloating the first implementation slice.
- Do not include implementation tasks unless they are needed to clarify planning inputs.
