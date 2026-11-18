# Council Protocol

## Contents

1. Deliberation depth
2. Role construction
3. Evidence discipline
4. Debate mechanics
5. Option comparison
6. Convergence and stopping
7. Multi-agent dispatch pattern
8. Failure recovery

## 1. Deliberation Depth

Choose depth by consequence, reversibility, ambiguity, and evidence quality.

| Tier | Typical use | Council | Rounds | Expected output |
|---|---|---:|---:|---|
| Lean | Reversible, bounded choice | 3 members | 2 | Recommendation plus caveats |
| Standard | Meaningful trade-offs | 4-5 members | 3 | Ranked options plus decision plan |
| Rigorous | Costly, hard to reverse, broad impact | 6-7 members | 3 plus verification | Decision record plus validation gates and minority report |

Do not expand the council merely because more roles can be imagined. Add a member only when their perspective could change the decision.

## 2. Role Construction

Define every member using five fields:

```text
Role: [functional expertise or stakeholder]
Objective: [what this member optimizes]
Prior: [initial tendency, not a fixed conclusion]
Failure lens: [what they are responsible for detecting]
Evidence standard: [what would persuade them]
```

Good role differences arise from different objectives, information, time horizons, or exposure to consequences. Avoid superficial differences such as "optimist" versus "pessimist" without distinct analytical responsibilities.

The chair is non-voting: it maintains the charter and evidence ledger, ensures disputes are classified (facts, values, predictions, execution), and synthesizes without hiding dissent. An evidence auditor may vote on options but has special authority to downgrade unsupported claims; it cannot veto a value judgment merely because values are not empirical facts.

## 3. Evidence Discipline

### Claim Types

- **Fact (`F`)**: directly supported by supplied material, observation, or a reliable source.
- **Inference (`I`)**: a conclusion derived from facts; include the reasoning chain.
- **Assumption (`A`)**: necessary but unverified premise.
- **Preference (`P`)**: a value choice or priority; attribute it to the decision owner or stakeholder.
- **Unknown (`U`)**: information not currently available.

### Evidence Strength

| Grade | Meaning | Appropriate use |
|---|---|---|
| E4 | Multiple strong, independent primary sources or direct measurement | Anchor a recommendation |
| E3 | One strong primary source or multiple credible secondary sources | Support a material claim |
| E2 | Limited, indirect, dated, or context-mismatched evidence | Conditional reasoning only |
| E1 | Expert judgment, analogy, anecdote, or model estimate | Generate hypotheses, not certainty |
| E0 | No evidence found | Label as assumption or unknown |

Evidence quality and decision confidence are different. Strong evidence about a narrow fact may still leave the overall decision uncertain.

### Reasoning Chain

For every decisive claim, use this internal structure:

```text
Evidence -> Interpretation -> Consequence -> Decision relevance
```

Record disconfirming evidence and plausible alternative explanations. A council member may not cite its own prior assertion as evidence.

## 4. Debate Mechanics

### Round 1: Independent Memorandum

Limit each member to the same approximate length. Require a recommendation and self-critique. This prevents rhetorical volume from dominating and reduces anchoring.

### Round 2: Cross-Examination

Route attacks by claim, not by personality. Use these dispositions:

- `STANDS`: objection does not materially weaken the claim.
- `REFINE`: core insight survives but scope or wording changes.
- `REJECT`: evidence or reasoning defeats the claim.
- `NEEDS EVIDENCE`: dispute cannot be resolved from current information.

Every member must make at least one concession or state explicitly why no concession is warranted. Empty agreement does not count.

### Round 3: Reconciliation

The chair should build an argument map:

```text
Decision criterion
  -> supporting claims
  -> objections
  -> responses
  -> surviving conclusion
```

Convert remaining disagreements into one of four forms:

1. a factual question to verify;
2. a preference the user must choose;
3. a forecast to test with a reversible experiment;
4. a hard incompatibility requiring separate options.

## 5. Option Comparison

Compare options against the charter criteria only after the reasoning is visible — the comparison must expose trade-offs, never disguise judgment as precision. Whatever scoring form is used, state what weight or factual change would reverse the ranking; when the ranking is fragile (near-tied options, weak evidence behind a decisive criterion, or stakeholders who would weight criteria very differently), prefer a staged, reversible experiment over a permanent commitment.

### Dominance Rules

An option is disqualified regardless of total score when it:

- violates a hard constraint;
- creates an unacceptable safety, legal, ethical, or existential risk;
- depends on an unavailable capability with no credible substitute;
- lacks a viable path to implementation;
- has a critical assumption that cannot be tested before irreversible commitment.

## 6. Convergence and Stopping

### Consensus Levels

- **Strong convergence:** no material dissent; recommendation robust across reasonable assumptions.
- **Qualified convergence:** leading option wins, but named conditions or mitigations are mandatory.
- **Conditional split:** different options win under different plausible scenarios.
- **Unresolved:** available evidence cannot choose responsibly.

Consensus does not mean every member prefers the same option. It means the council agrees the recommendation is defensible under the stated criteria and conditions.

### Minority Report

Include a minority report when a dissenting member identifies:

- a credible high-impact failure mode;
- a fundamentally different stakeholder value;
- an evidence gap that could reverse the result;
- a long-term consequence discounted by the majority.

The minority report must state its trigger: the observable condition under which it should override the recommendation.

### Stop Rules

Stop deliberation when any of these applies:

- convergence criteria are met;
- two consecutive exchanges add no material claim, evidence, option, or changed position;
- the dispute reduces to a user preference;
- an external fact or experiment is required;
- three rounds are complete unless the user explicitly requests deeper debate.

Do not fill space with synthetic disagreement after convergence.

## 7. Multi-Agent Dispatch Pattern

When independent agent or worker tools exist:

1. Dispatch Round 1 prompts with identical charter and evidence, distinct role briefs, and no access to peer answers.
2. Collect and normalize the responses into a claim-indexed bundle.
3. Dispatch Round 2 prompts with the full bundle and require claim-specific cross-review.
4. Send each member the objections to its own claims for defense, refinement, or concession when stakes justify a third agent round.
5. Have the chair synthesize; do not ask one voting member to act as the final judge.
6. Shut down or release resources when the environment requires cleanup.

When only sequential worker calls are available (delegated mode), preserve the same
independence and fairness guarantees: collect all members' round-N position updates
before any round-N+1 critique begins, and rotate the per-member call order each
round so no member is always called last.

Never require a proprietary team API. Adapt to the available agent mechanism while preserving independence, cross-talk, and provenance.

## 8. Failure Recovery

| Failure | Repair |
|---|---|
| Members sound identical | Rewrite role objectives and failure lenses; replace redundant roles |
| Debate becomes monologues | Require claim-specific challenges and direct responses |
| Premature agreement | Ask each member for the strongest remaining objection and disconfirming evidence |
| Endless debate | Apply stop rules and convert disagreement into evidence gates or user preferences |
| Unsupported certainty | Downgrade confidence, relabel claims, and add validation steps |
| Scores contradict reasoning | Repair criteria, weights, or score rationales; reasoning controls |
| Hybrid option is incoherent | Remove it; hybrids are not mandatory |
| No recommendation emerges | Rank conditional options and define the smallest resolving experiment |
| One agent dominates | Equalize response budgets and evaluate claims anonymously where possible |
