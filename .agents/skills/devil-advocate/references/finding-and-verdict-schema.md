# Finding, Verdict, and Challenge-Lens Reference

Use this reference for the challenge-lens prompts and the severity, evidence, confidence, fixability, and verdict rules.

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

- **Fixable:** a repair is technically, economically, organizationally, and temporally feasible under existing constraints. State the repair, its trade-off, a validation step, and the residual risk.
- **Conditionally fixable:** a repair exists but depends on an explicit condition — new evidence, budget, time, skills, authority, a changed constraint, stakeholder agreement, or a prototype meeting a threshold. State the condition as a decision gate, not a vague recommendation.
- **Not fixable:** use only with `S4 - Show-stopper`, after testing all reasonable repair classes: repair the mechanism; add controls or guardrails; change sequence or rollout; reduce scope; substitute a component or stakeholder model; run a reversible experiment; accept or transfer residual risk; change a negotiable constraint. If one of these preserves the essential proposal at acceptable risk, the finding is not `Not fixable`.

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

- **High:** the causal mechanism is clear, major assumptions are verified, and plausible alternatives do not materially change the conclusion.
- **Medium:** the mechanism is credible but one or more material assumptions or estimates remain uncertain.
- **Low:** the finding is plausible but highly sensitive to missing facts, interpretation, or scenario selection.

Low confidence can still justify a decision gate when impact is severe and commitment is irreversible.

## Verdict Rules

- **PROCEED:** no unresolved S3 or S4 findings remain, S2 risks have routine mitigations, and the proposal is sufficiently evidenced or reversible.
- **PROCEED WITH CONDITIONS:** the core proposal is sound but one or more S2 or repaired S3 findings require explicit owners, thresholds, sequencing, or controls before or during execution.
- **REWORK:** one or more S3 findings require material changes to scope, architecture, sequence, governance, economics, evidence, or operating model, while the core objective and much of the approach remain viable.
- **REPLACE:** the objective is valid but a materially different alternative dominates the current proposal after risk, cost, reversibility, and opportunity cost are considered.
- **REJECT:** only when at least one S4 finding is marked `Not fixable`, or when several interacting S3 findings collectively create an effectively unrepairable proposal — in that case, explain why no integrated rework reduces the combined risk to an acceptable level and elevate the combination to an explicit S4 finding.

## Challenge Lenses

Use these prompts selectively. Do not mechanically answer every question.

1. **Assumptions and Socratic:** What must be true for the proposal to create value? Which assumption is treated as fact without evidence? Which hidden dependency has no owner? What belief, if false, collapses the rest of the proposal? Convert major assumptions into observable tests.
2. **Evidence and falsification:** For each major claim, is the cited evidence representative of the intended environment, scale, and time horizon? What result would disprove it? Is the evidence independent or produced by a party with incentives? Does it confuse correlation or survivorship with causation? Flag unfalsifiable claims as decision-quality defects; repair them with measurable success and failure thresholds.
3. **Strongest counter-case:** What would a smart, informed skeptic argue? Which alternative explains the same facts with fewer assumptions? What trade-off is understated? Attack the most defensible version, not weak objections.
4. **Pre-mortem:** Set a concrete future scene where the proposal clearly failed. Build failure narratives with a specific trigger, a threshold or boundary condition, first- through third-order effects, the detection point, why detection came too late, the assumption that proved false, and an early warning signal. Ask what would guarantee failure, then check whether those conditions already exist.
5. **Adversarial stakeholders:** Adopt perspectives relevant to the proposal — user or customer, operator, sponsor, regulator, competitor, supplier or platform owner, misaligned internal team, attacker (within safe conceptual boundaries), novice. For each, identify incentives, objections, exploit paths, refusal conditions, and likely workarounds.
6. **Execution and operations:** Who owns each critical dependency? Where are all-or-nothing transitions? What happens during migration, rollback, degraded mode, or partial adoption? Which estimates assume best-case coordination? What becomes difficult to change after commitment? Prefer staged, reversible transitions when uncertainty is high.
7. **Systems and second-order effects:** Trace feedback loops that amplify success or failure, local optimization that degrades the larger system, bottlenecks moved rather than removed, externalities shifted to others, behavior induced by metrics or incentives, lock-in and path dependence, and effects at 10x scale or under stress. Ask what workaround users will invent and how it changes future requirements.
8. **Incentives and governance:** Who receives benefits and who bears costs? Who can block or silently undermine? Are decision rights aligned with accountability? Does the metric invite gaming? Is success dependent on voluntary behavior against incentives? What happens when the sponsor or budget changes? Repair with ownership, authority, incentives, escalation, and auditability — not appeals to cooperation.
9. **Alternatives and opportunity cost:** Generate structurally different options, not cosmetic variants: do nothing or delay, narrower scope, manual before automated, buy/partner/reuse/standardize, reversible pilot versus full commitment, eliminate the need rather than satisfy it. Compare total cost, time to evidence, reversibility, operational burden, and strategic fit.
10. **Edge cases and boundaries:** Vary scale (smallest, typical, peak, 10x), time (launch, steady state, end-of-life), actors (novice, expert, hostile, constrained), data (missing, stale, biased, sensitive), environment (degraded, cross-region, regulated), and adoption (partial, forced, resisted, misused). An edge case becomes a finding only when plausible and material.
