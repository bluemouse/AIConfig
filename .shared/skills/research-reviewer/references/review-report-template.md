# Review Report Template

Use this structure for the final review-report. Adapt only when sections are irrelevant.

```markdown
# Research Review Report: [Research Report / Feature / Idea Name]

## 1. Verdict
- Verdict: ready | conditionally ready | needs revision | blocked
- Confidence: high | medium | low
- Audit posture: balanced | aggressive
- Active reviewer roles/lenses: [list]
- Domain assumptions: [domain and confidence, or none]
- Planning recommendation: [proceed / proceed with conditions / revise first / do not plan yet]

## 2. Source report summary
- Report decision or recommendation:
- Agreement state claimed by the report:
- Scope reviewed:
- Sections or inputs missing from the review:

## 3. Top findings
| id | severity | affected section | issue | required fix |
|----|----------|------------------|-------|--------------|
| rr-001 | blocker/major/minor/question/nit |  |  |  |

## 4. Cross-lens audit
### Completeness
[Pass/fail/partial plus concise findings.]

### Consistency
[Contradictions, tension, or alignment findings.]

### Evidence and assumptions
[Unsupported claims, weak assumptions, source gaps, confidence issues.]

### Requirements and acceptance criteria
[Testability, priority, traceability, missing acceptance signals.]

### Alternatives and decision quality
[Whether the recommendation follows from goals, constraints, evidence, and trade-offs.]

### Risks and edge cases
[Missing or weak risks, mitigations, owners, rollout concerns.]

### Technical and implementation readiness
[Dependencies, architecture impact, data/contracts, testing, rollout, observability, support.]

### Domain-specialist review
[Domain-specific findings, or state why no domain lens was needed.]

## 5. Traceability matrix
| planning input | present? | quality | notes |
|----------------|----------|---------|-------|
| problem statement | yes/no/partial | strong/adequate/weak/missing |  |
| target users/stakeholders | yes/no/partial | strong/adequate/weak/missing |  |
| goals and non-goals | yes/no/partial | strong/adequate/weak/missing |  |
| success metrics | yes/no/partial | strong/adequate/weak/missing |  |
| requirements | yes/no/partial | strong/adequate/weak/missing |  |
| acceptance criteria | yes/no/partial | strong/adequate/weak/missing |  |
| alternatives considered | yes/no/partial | strong/adequate/weak/missing |  |
| evidence/assumptions | yes/no/partial | strong/adequate/weak/missing |  |
| risks/mitigations | yes/no/partial | strong/adequate/weak/missing |  |
| open questions | yes/no/partial | strong/adequate/weak/missing |  |
| implementation handoff | yes/no/partial | strong/adequate/weak/missing |  |

## 6. Required revision plan
### Must fix before implementation planning
1. [Required fix]

### Should fix before or during early planning
1. [Recommended fix]

### Optional cleanup
1. [Minor improvement]

## 7. Final readiness assessment
[One concise paragraph explaining whether the report can be consumed for implementation planning and under what conditions.]

Review gate: choose one:
1. revise: update the source research report using the required fixes
2. re-review: run another pass after edits or with a stricter posture
3. specialize: review again with a specific domain specialist lens
4. accept: treat the report as ready at the stated verdict level
```

Rules:
- Keep the verdict visible at the top.
- Use severity consistently with `validation-rubric.md`.
- Focus on planning impact rather than style preference.
- Do not include a long rewrite of the original report unless requested.
- If the report is strong, still list residual assumptions and minor risks.
