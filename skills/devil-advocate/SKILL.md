---
name: devil-advocate
description: Play devil's advocate, red-team, pressure-test, poke holes, pre-mortem, or challenge one proposal, plan, strategy, design, launch, pitch, or vendor decision. Find blind spots, load-bearing assumptions, failure modes, show-stoppers, and kill criteria; steelman first, then return findings, mitigations, and a proceed/proceed-with-conditions/rework/replace/reject verdict. Not for git diff review, PR descriptions, or multi-perspective council synthesis.
---

# Devil Advocate

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve paths to `references/` from that directory.

Apply constructive adversarial pressure to an idea before reality does. Find the few weaknesses that matter, explain their causal mechanisms, and convert each finding into a repair, alternative, experiment, guardrail, or defensible rejection.

Do not disagree performatively. Preserve what is strong, attack what is fragile, and improve the decision.

## Scope and Boundaries

Use this skill for adversarial review of a specific proposal, plan, strategy, design, option, argument, or decision.

## When NOT to Use

- **Broad multi-perspective deliberation with ranked synthesis and minority dissent** — use [../advisory-council/SKILL.md](../advisory-council/SKILL.md)
- **Git diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) unless the user specifically wants conceptual red teaming of a design or plan
- **Implementation planning from settled requirements** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Root-cause investigation of a reproducible defect** — use [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
- **Open-ended discovery and feature research with agreement gates** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Harmful operational instructions, unauthorized exploitation, or evasion tactics** — refuse

For legal, medical, safety, compliance, or security-sensitive subjects, identify where qualified specialist review is required. Do not present this analysis as a substitute for that review.

## Operating Principles

1. **Steelman before attacking.** Restate the strongest plausible version of the proposal, including its objective, value, constraints, and intended mechanism.
2. **Separate facts, assumptions, and unknowns.** Never treat an inference as established evidence.
3. **Attack causal structure, not wording.** Trace how a specific assumption, trigger, dependency, incentive, or constraint can produce failure.
4. **Prioritize decisive findings.** Prefer 3-8 deep findings over a long inventory of generic concerns.
5. **Resolve every finding.** Supply one or more concrete resolution paths, or prove that the finding is a show-stopper and mark it `Not fixable`.
6. **Concede what survives.** Explicitly identify arguments and design choices that remain strong after challenge.
7. **End with a decision.** Recommend proceeding, proceeding conditionally, reworking, replacing, or rejecting.
8. **Do not fabricate evidence or parallel review.** Use available sources and tools when material; otherwise label uncertainty and reason from the provided facts.

## Intake

Extract or infer the following from the user's material:

- proposal or decision;
- desired outcome and success measures;
- stakeholders and affected users;
- constraints and non-negotiables;
- time horizon and reversibility;
- evidence offered;
- alternatives already considered;
- cost of failure and cost of delay.

When material context is missing, make the smallest reasonable assumptions, label them, and continue. Ask a question only when the missing fact would fundamentally change the analysis and cannot be represented as scenarios.

## Choose Analysis Depth

Match effort to stakes and input size:

- **Quick challenge:** 3-5 findings for a narrow or reversible decision.
- **Standard review:** 5-8 findings for most plans and proposals.
- **Deep red team:** 8-12 findings, scenario branches, and decision gates for high-impact, expensive, irreversible, regulated, or safety-critical decisions.
- **Comparative review:** Evaluate each option against the same criteria, attack the leading option hardest, and synthesize a better option when possible.

Do not inflate finding count to appear thorough.

## Core Workflow

### 1. Frame the Decision

State:

- what is being proposed;
- why it is attractive;
- what must be true for it to work;
- what decision must be made now;
- what would constitute failure.

### 2. Steelman the Proposal

Present the strongest fair case for the proposal. Improve weak phrasing without adding unsupported facts. Identify the proposal's strongest advantages and the conditions under which it is likely to succeed.

### 3. Decompose into Atomic Claims

Break the proposal into testable claims and dependencies, such as:

- causal claims: X will cause Y;
- predictive claims: users, markets, systems, or teams will behave in a certain way;
- comparative claims: this option is better than alternatives;
- quantitative claims: cost, schedule, performance, adoption, or impact estimates;
- feasibility claims: capabilities, resources, integrations, or approvals will be available;
- governance claims: incentives, ownership, and decision rights will work as intended.

Map critical dependencies. A dependency is critical when its failure invalidates the proposal rather than merely degrading it.

### 4. Apply Independent Challenge Lenses

Select the relevant lenses automatically. Use at least three for a standard review and at least five for a deep review.

- **Assumptions:** What is taken for granted? Which assumptions are load-bearing?
- **Evidence:** What would falsify each major claim? How strong, relevant, independent, and current is the evidence?
- **Counter-case:** What is the strongest opposing argument or competing explanation?
- **Pre-mortem:** Imagine clear failure at the relevant time horizon. What specific chain of events caused it?
- **Adversarial stakeholders:** How could skeptics, competitors, users, operators, regulators, attackers, or misaligned participants exploit or reject it?
- **Execution and operations:** Where do ownership, sequencing, staffing, integration, migration, support, rollback, or maintenance fail?
- **Systems and second-order effects:** What feedback loops, bottlenecks, externalities, or downstream consequences emerge?
- **Incentives and governance:** Who benefits, who pays, who can block, and what behavior does the proposal unintentionally reward?
- **Alternatives and opportunity cost:** What simpler, cheaper, reversible, or structurally different option has been ignored?
- **Edge cases and boundary conditions:** At what scale, timing, segment, environment, or threshold does the proposal stop working?

Load `references/challenge-lenses.md` when deeper prompts or domain patterns are useful.

### 5. Build and Rank Findings

For each candidate weakness, establish this causal chain:

`Underlying assumption or condition -> trigger -> failure mechanism -> direct impact -> second-order impact`

Merge duplicates. Discard findings that are vague, immaterial, unsupported, or already fully controlled.

Rank using the severity rubric in `references/finding-and-verdict-schema.md`. Severity reflects consequence and decision impact, not rhetorical intensity.

### 6. Engineer Resolutions

Every retained finding must include a disposition:

- **Fixable:** A practical repair fits the stated constraints.
- **Conditionally fixable:** A repair exists but requires a decision, resource, evidence, capability, or constraint change.
- **Not fixable:** No credible resolution preserves the proposal's essential objective within its non-negotiable constraints.

For fixable findings, provide one or more of:

- direct repair to the current proposal;
- alternative architecture, strategy, scope, sequence, or operating model;
- de-scope or staged rollout;
- reversible experiment or prototype;
- control, guardrail, fallback, or rollback;
- evidence-gathering test with a pass/fail threshold;
- transfer, acceptance, or avoidance of residual risk.

Explain trade-offs and residual risk for each proposed resolution. Do not write "monitor this", "be careful", or "do more research" without specifying what to monitor, what action follows, or what evidence resolves the uncertainty.

### 7. Apply the Show-Stopper Gate

Assign `S4 - Show-stopper` and mark `Not fixable` only when all applicable conditions are demonstrated:

1. The issue invalidates a necessary objective, violates a non-negotiable constraint, or creates unacceptable legal, safety, security, ethical, technical, or economic exposure.
2. The failure cannot be reduced to an acceptable level by redesign, sequencing, de-scoping, controls, experimentation, or an alternative implementation.
3. The required resolution is infeasible within the stated constraints, or it changes the proposal so fundamentally that it is no longer the same proposal.
4. The conclusion is supported by evidence or an explicit, defensible reasoning chain rather than discomfort or uncertainty alone.

Distinguish `not fixed yet` from `not fixable`. When evidence is incomplete, use `Conditionally fixable` with a decision gate instead of declaring a show-stopper.

For every show-stopper, state:

- the non-negotiable criterion that fails;
- why all credible repair classes fail;
- what changed constraint, if any, would make a replacement proposal viable;
- the rejection recommendation.

### 8. Synthesize a Better Path

After the findings, produce the strongest viable next version:

- **Refined:** Preserve the core idea and repair weaknesses.
- **Extended:** Add missing capabilities, evidence, controls, or stakeholder alignment.
- **Reworked:** Change architecture, sequencing, scope, assumptions, or business model.
- **Replaced:** Recommend a superior alternative that better satisfies the objective.
- **Rejected:** Stop the proposal because one or more show-stoppers are not fixable.

When several viable resolutions exist, provide 2-3 options with trade-offs and state which one is preferred.

### 9. Issue the Verdict

Use exactly one primary verdict:

- `PROCEED`
- `PROCEED WITH CONDITIONS`
- `REWORK`
- `REPLACE`
- `REJECT`

Tie the verdict to the highest-severity unresolved findings, residual risk, reversibility, and evidence strength.

## Required Output

Follow this default structure. Adapt detail, but do not omit resolution or verdict fields.

```markdown
# Devil's Advocate Review: [Proposal]

## Executive verdict
**Verdict:** [PROCEED / PROCEED WITH CONDITIONS / REWORK / REPLACE / REJECT]
**Why:** [2-4 sentences]
**Decision confidence:** [High / Medium / Low]

## Steelmanned case
[Strongest fair version, including what is genuinely compelling]

## Load-bearing assumptions
| Assumption | Why it matters | Evidence strength | How to test |
|---|---|---|---|
| ... | ... | ... | ... |

## Prioritized findings
| ID | Severity | Finding | Disposition | Recommended resolution |
|---|---|---|---|---|
| F-01 | ... | ... | ... | ... |

## Finding details
### F-01 - [Title]
- **Severity:** [S0-S4]
- **Disposition:** [Fixable / Conditionally fixable / Not fixable]
- **Affected claim:** [...]
- **Reasoning chain:** [condition -> trigger -> failure -> impact -> second-order effect]
- **Evidence and confidence:** [...]
- **Why current controls are insufficient:** [...]
- **Resolution A:** [action, owner or mechanism, and trade-off]
- **Resolution B:** [when materially different and useful]
- **Validation or decision gate:** [test, threshold, and timing]
- **Residual risk:** [...]

## Strongest surviving elements
[What held up and should be preserved]

## Recommended rework or replacement
[An actionable revised proposal, or multiple resolution options with a preferred choice]

## Decision gates and kill criteria
[Observable conditions that determine go, revise, pause, or stop]
```

If the proposal is rejected, replace "Recommended rework" with "Replacement paths" and explicitly connect every rejection reason to an `S4 - Show-stopper / Not fixable` finding.

Load `references/finding-and-verdict-schema.md` for the full severity, confidence, evidence, and verdict rules. Load `references/examples.md` when a concrete formatting example would improve consistency.

## Quality Gates

Before finalizing, verify:

- The proposal was steelmanned without inventing support.
- Findings are specific to this proposal, not generic risks.
- Each finding contains a causal mechanism and material impact.
- Severity and confidence are not conflated.
- Each finding has at least one concrete resolution, or a proven show-stopper marked `Not fixable`.
- Show-stoppers satisfy the strict gate and are not merely difficult or uncertain.
- Resolutions include trade-offs, validation, and residual risk.
- The verdict follows from unresolved findings.
- The revised proposal preserves strengths and addresses the decisive weaknesses.
- No critical objection was softened merely to be agreeable.

## Guardrails

- Challenge ideas, decisions, plans, and arguments. Do not turn conceptual red teaming into instructions for real-world harm or unauthorized exploitation.
- Do not replace qualified legal, medical, safety, compliance, security, or domain expert review. Identify where specialist validation is required.
- Do not use stakeholder caricatures or assume malicious intent when ordinary incentives, errors, or constraints explain the risk.
- Do not reject a proposal because it is unconventional. Reject only when the objective cannot be achieved acceptably under the constraints.
