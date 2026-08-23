# Challenge Lenses

Use these prompts selectively. Do not mechanically answer every question.

## 1. Assumption and Socratic Lens

Identify load-bearing assumptions by asking:

- What must be true for the proposal to create value?
- Which assumption is treated as a fact without evidence?
- Which stakeholder behavior is assumed rather than designed for?
- Which constraint is assumed fixed but may be negotiable?
- Which hidden dependency has no owner?
- What would a domain expert challenge first?
- What belief, if false, collapses the rest of the proposal?

Convert major assumptions into observable tests.

## 2. Evidence and Falsification Lens

For each major claim:

- What evidence is cited?
- Is it representative of the intended environment, scale, users, and time horizon?
- What result would disprove the claim?
- Is the claim measurable and time-bounded?
- Are there competing explanations for the evidence?
- Is the evidence independent, or produced by a party with incentives?
- Does the proposal confuse correlation, selection effects, or survivorship with causation?

Flag unfalsifiable claims as decision-quality defects. Repair them by defining measurable success and failure thresholds.

## 3. Strongest Counter-Case Lens

Construct the best opposing position:

- What would a smart, informed skeptic argue?
- Which alternative explains the same facts with fewer assumptions?
- What trade-off is the proposal understating?
- What is the strongest reason to preserve the status quo?
- What option achieves the objective with less complexity or irreversibility?
- What would make the leading alternative win?

Do not use weak objections. Attack the most defensible version of the proposal.

## 4. Pre-Mortem Lens

Set a concrete future scene: the proposal clearly failed.

Build failure narratives that include:

- a specific trigger;
- a threshold, scale, date, or boundary condition;
- first-, second-, and third-order effects;
- detection point;
- why detection came too late;
- the assumption that proved false;
- an early warning signal.

Ask what would guarantee failure, then check whether those conditions already exist.

## 5. Adversarial Stakeholder Lens

Adopt independent perspectives relevant to the proposal, for example:

- end user or customer;
- operator or support team;
- executive sponsor or finance owner;
- regulator, auditor, legal reviewer, or procurement;
- competitor or substitute provider;
- supplier, partner, or platform owner;
- misaligned internal team;
- attacker or abuse actor, within safe conceptual boundaries;
- new employee or inexperienced implementer.

For each perspective, identify incentives, objections, exploit paths, refusal conditions, and likely workarounds.

## 6. Execution and Operational Lens

Probe:

- Who owns each critical dependency and decision?
- Where are critical paths or all-or-nothing transitions?
- What happens during migration, rollback, degraded mode, or partial adoption?
- What operational burden appears after launch?
- Which capabilities must be learned rather than bought?
- Which estimates assume best-case coordination?
- What is the bus factor?
- How will incidents, exceptions, and support be handled?
- What becomes difficult to change after commitment?

Prefer staged, reversible transitions when uncertainty is high.

## 7. Systems and Second-Order Lens

Trace:

- feedback loops that amplify success or failure;
- local optimization that degrades the larger system;
- bottlenecks moved rather than removed;
- externalities shifted to another team or stakeholder;
- new dependencies and coupling;
- behavior induced by metrics, automation, or incentives;
- long-term maintenance, lock-in, and path dependence;
- effects at 10x scale or under stress.

Ask what workaround users will invent and how that workaround changes future requirements.

## 8. Incentive and Governance Lens

Check:

- Who receives benefits and who bears costs?
- Who can block or silently undermine the proposal?
- Are decision rights aligned with accountability?
- Does the metric invite gaming or Goodhart's law?
- Is success dependent on voluntary behavior against incentives?
- What happens when the sponsor, budget, or leadership changes?
- Are exceptions likely to become the normal path?

Repair with ownership, authority, incentives, escalation, and auditability, not appeals to cooperation.

## 9. Alternatives and Opportunity-Cost Lens

Generate structurally different options, not cosmetic variants:

- do nothing or delay;
- narrower scope;
- manual process before automation;
- buy, partner, reuse, or standardize;
- centralized versus decentralized;
- reversible pilot versus full commitment;
- policy/process change versus technology build;
- eliminate the need rather than satisfy it.

Compare total cost, time to evidence, reversibility, operational burden, option value, and strategic fit.

## 10. Edge-Case and Boundary Lens

Vary:

- scale: smallest, typical, peak, and 10x;
- time: launch, steady state, turnover, and end-of-life;
- actors: novice, expert, hostile, constrained, and accessibility needs;
- data: missing, stale, malformed, biased, duplicated, or sensitive;
- environment: offline, degraded, cross-region, low-resource, or regulated;
- adoption: partial, forced, resisted, or used differently than intended.

An edge case becomes a prioritized finding only when plausible and material.

## Suggested Lens Combinations

| Proposal type | Primary lenses | Secondary lenses |
|---|---|---|
| Product or feature | Assumptions, evidence, stakeholder, alternatives | incentives, edge cases |
| Architecture or migration | Pre-mortem, execution, systems, edge cases | evidence, alternatives |
| Business strategy | Counter-case, evidence, incentives, alternatives | pre-mortem, systems |
| Policy or process | Stakeholder, incentives, execution, evidence | systems, edge cases |
| Security or safety design | Adversarial stakeholder, pre-mortem, systems | evidence, operations |
| Data-driven recommendation | Evidence, assumptions, counter-case | systems, alternatives |
| Vendor or tool selection | Alternatives, evidence, operations, incentives | pre-mortem, lock-in |
| High-stakes irreversible decision | All relevant lenses; emphasize falsification, pre-mortem, alternatives, and decision gates | independent specialist review |
