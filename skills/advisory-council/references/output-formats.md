# Output Formats

Use the lightest format that still supports the decision. Adapt headings to the user's requested deliverable, but preserve evidence, rationale, dissent, and next actions.

## Standard Council Decision

```markdown
# Advisory Council: [Decision or topic]

## Decision
**Recommendation:** [option]
**Confidence:** [High / Medium / Low]
**Consensus:** [Strong convergence / Qualified convergence / Conditional split / Unresolved]

[Two to four sentences explaining why this is the best available choice.]

## Charter
- **Question:** ...
- **Outcome sought:** ...
- **Hard constraints:** ...
- **Working assumptions:** ...

## Council
| Perspective | Responsibility | Why included |
|---|---|---|
| ... | ... | ... |

## Evidence state
- **Strong evidence:** ...
- **Weak or indirect evidence:** ...
- **Decision-critical unknowns:** ...

## What changed during debate
- [Initial claim] -> [objection] -> [concession or refinement]
- ...

## Ranked options
| Rank | Option | Why it ranks here | Conditions / disqualifiers |
|---:|---|---|---|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |

## Recommendation rationale
[Evidence -> interpretation -> consequence -> decision relevance.]

## Risks and safeguards
| Risk | Likelihood / impact | Mitigation | Trigger or owner |
|---|---|---|---|
| ... | ... | ... | ... |

## Minority report
[Material dissent and the condition under which it should override the recommendation. Write "None material" only when justified.]

## Action plan
1. [Immediate action with owner/role and success criterion]
2. ...

## Revisit triggers
- [Observable event, failed assumption, threshold, or date that should reopen the decision]
```

## Ranked Option Matrix

Use for explicit comparisons.

```markdown
## Decision criteria
| Criterion | Weight | Why it matters | Evidence quality |
|---|---:|---|---|
| ... | ...% | ... | E0-E4 |

## Option scores
| Option | C1 | C2 | C3 | Weighted result | Robustness |
|---|---:|---:|---:|---:|---|
| ... | 0-5 | 0-5 | 0-5 | ... | Stable / Fragile |

### Score rationale
- **[Option] / [Criterion]:** [one-line evidence-based rationale]

### Sensitivity
[State which weight, fact, or constraint change reverses the ranking.]
```

## Council-Produced Plan

```markdown
# Agreed Plan: [Objective]

## Chosen approach
[Approach, rationale, and rejected alternatives.]

## Non-negotiable constraints
- ...

## Workstreams
| Phase / workstream | Owner role | Dependencies | Deliverable | Success criterion | Stop condition |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Decision gates
1. **Gate:** ...
   - Evidence required: ...
   - Proceed when: ...
   - Pivot or stop when: ...

## Risk controls
- ...

## Verification
- [How to establish that the plan worked]

## Reconsideration triggers
- ...
```

## Unresolved Council

Use when a responsible recommendation is impossible from current evidence.

```markdown
# Council Result: Decision Pending Evidence

## What the council agrees on
- ...

## Why the decision remains unresolved
[Name the exact factual uncertainty, value conflict, or hard incompatibility.]

## Conditional ranking
1. If [condition], choose [option] because ...
2. If [condition], choose [option] because ...

## Resolving step
**Smallest useful test:** ...
**Evidence to collect:** ...
**Decision threshold:** ...
**Cost and reversibility:** ...

## Interim safe action
[What can proceed without prejudging the final decision.]
```

## Concise Response

For a lean council, compress the output to:

1. recommendation and confidence;
2. three selected perspectives;
3. decisive evidence and trade-off;
4. ranked alternative;
5. main dissent or unknown;
6. next action and revisit trigger.
