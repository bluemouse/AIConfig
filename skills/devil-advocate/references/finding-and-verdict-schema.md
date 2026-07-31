# Finding and Verdict Schema

Use this reference when assigning severity, evidence strength, confidence, fixability, or a final verdict.

## Severity Rubric

Severity expresses the decision consequence if the finding materializes.

| Level | Label | Definition | Typical decision effect |
|---|---|---|---|
| S0 | Observation | Useful note, clarification, or improvement with no material threat | Preserve or optionally improve |
| S1 | Minor | Local weakness with limited impact and an easy repair | Proceed; repair during execution |
| S2 | Material | Meaningful risk to cost, schedule, adoption, quality, operations, or credibility | Proceed only with an owned mitigation or test |
| S3 | Critical | High-impact weakness that can invalidate a major objective or cause unacceptable exposure, but has at least one credible repair path | Rework or impose hard preconditions before commitment |
| S4 | Show-stopper | Fatal conflict with a necessary objective or non-negotiable constraint and no credible repair that preserves the proposal | Reject the proposal; mark `Not fixable` |

Do not calculate severity mechanically. Consider impact, likelihood, detectability, reversibility, blast radius, time to harm, and whether the risk is concentrated in a critical dependency.

## Disposition Rubric

### Fixable

Use when a resolution is technically, economically, organizationally, and temporally feasible under existing constraints.

Required fields:

- repair mechanism;
- trade-off;
- validation step;
- residual risk.

### Conditionally Fixable

Use when a repair exists but depends on one or more explicit conditions:

- new evidence;
- additional budget, time, skills, authority, or access;
- a changed constraint;
- stakeholder agreement;
- a prototype or experiment meeting a threshold.

State the condition as a decision gate, not a vague recommendation.

### Not Fixable

Use only with `S4 - Show-stopper` after testing all reasonable repair classes:

1. repair the mechanism;
2. add controls or guardrails;
3. change sequence or rollout;
4. reduce scope;
5. substitute a component or stakeholder model;
6. run a reversible experiment;
7. accept or transfer residual risk;
8. change a negotiable constraint.

If one of these preserves the essential proposal and yields acceptable risk, the finding is not `Not fixable`.

## Evidence Strength

| Grade | Meaning |
|---|---|
| A | Direct, current, representative, independently verified, and reproducible evidence |
| B | Strong observational or operational evidence with limited uncertainty |
| C | Relevant but incomplete evidence, a small sample, analogy, or a single credible source |
| D | Anecdote, opinion, vendor claim, indirect analogy, or weakly representative data |
| F | No evidence offered or available |

Evidence strength is not the same as confidence. A strong deductive constraint can support high confidence without empirical data; a noisy dataset can provide evidence with low interpretive confidence.

## Confidence Rubric

- **High:** The causal mechanism is clear, major assumptions are verified, and plausible alternatives do not materially change the conclusion.
- **Medium:** The mechanism is credible but one or more material assumptions or estimates remain uncertain.
- **Low:** The finding is plausible but highly sensitive to missing facts, interpretation, or scenario selection.

Low confidence can still justify a decision gate when impact is severe and commitment is irreversible.

## Finding Completeness Test

A complete finding answers:

1. What exact claim or dependency is weak?
2. What condition triggers failure?
3. Through what mechanism does it fail?
4. What is the direct and second-order impact?
5. What evidence supports the finding, and how confident are we?
6. Why do existing controls not solve it?
7. What are the credible resolution paths?
8. What trade-offs and residual risks remain?
9. What test or threshold resolves the decision?
10. Is it fixable, conditionally fixable, or not fixable?

## Verdict Rules

### PROCEED

Use when no unresolved S3 or S4 findings remain, S2 risks have routine mitigations, and the proposal is sufficiently evidenced or reversible.

### PROCEED WITH CONDITIONS

Use when the core proposal is sound but one or more S2 or repaired S3 findings require explicit owners, thresholds, sequencing, or controls before or during execution.

### REWORK

Use when one or more S3 findings require material changes to scope, architecture, sequence, governance, economics, evidence, or operating model, while the core objective and much of the approach remain viable.

### REPLACE

Use when the objective is valid but a materially different alternative dominates the current proposal after risk, cost, reversibility, and opportunity cost are considered.

### REJECT

Use only when at least one S4 finding is marked `Not fixable`, or when several interacting S3 findings collectively create an effectively unrepairable proposal. When using interacting S3 findings, explain why no integrated rework can reduce the combined risk to an acceptable level and elevate the combination to an explicit S4 finding.
