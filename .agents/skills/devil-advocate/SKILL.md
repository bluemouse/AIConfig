---
name: devil-advocate
description: Play devil's advocate, red-team, pressure-test, poke holes, pre-mortem, or challenge one proposal, plan, strategy, design, launch, pitch, or vendor decision. Find blind spots, load-bearing assumptions, failure modes, show-stoppers, and kill criteria; steelman first, then return findings, mitigations, and a proceed/proceed-with-conditions/rework/replace/reject verdict. Not for git diff review, PR descriptions, or multi-perspective council synthesis.
---

# Devil Advocate

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`; resolve `references/` paths from it.

Find the few weaknesses that matter, explain their causal mechanisms, and convert each finding into a repair, alternative, experiment, guardrail, or defensible rejection. Do not disagree performatively — preserve what is strong, attack what is fragile.

## When NOT to Use

- **Broad multi-perspective deliberation with ranked synthesis and minority dissent** — use [../advisory-council/SKILL.md](../advisory-council/SKILL.md); the single-proposal vs multi-perspective split is the routing line
- **Git diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md), unless the user wants conceptual red teaming of a design
- **Implementation planning, defect root-cause, or open-ended discovery** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md), [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md), or [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Harmful operational instructions, unauthorized exploitation, or evasion tactics** — refuse

## Operating Principles

1. **Steelman before attacking.** Restate the strongest plausible version of the proposal, including its objective, value, constraints, and intended mechanism.
2. **Attack causal structure, not wording.** Trace how a specific assumption, trigger, dependency, incentive, or constraint can produce failure. Prefer 3-8 deep findings over a long inventory of generic concerns; explicitly concede arguments and design choices that survive challenge.
3. **Resolve every finding.** Supply one or more concrete resolution paths, or prove that the finding is a show-stopper and mark it `Not fixable`.
4. **End with a decision.** Recommend proceeding, proceeding conditionally, reworking, replacing, or rejecting — exactly one primary verdict.
5. **Do not fabricate evidence or parallel review.** Separate facts, assumptions, and unknowns — never treat an inference as established evidence.

## Core Workflow

1. **Frame the decision.** State what is proposed, why it is attractive, what must be true for it to work, and what failure looks like — then steelman per Principle 1.
2. **Decompose into atomic claims.** Break the proposal into testable claims (causal, predictive, comparative, quantitative, feasibility, governance) and map dependencies whose failure invalidates rather than degrades it.
3. **Apply challenge lenses.** Pick at least three of the ten lenses in `references/finding-and-verdict-schema.md`. For each weakness, establish `assumption -> trigger -> failure mechanism -> impact -> second-order impact`; merge duplicates, drop vague or already-controlled findings, rank by the reference's severity rubric.
4. **Engineer resolutions.** Every retained finding gets a disposition — **Fixable**, **Conditionally fixable**, or **Not fixable** — and fixable findings a concrete resolution (repair, alternative, de-scope, experiment, guardrail, or pass/fail test) with trade-offs and residual risk. Never write "monitor this" or "do more research" without naming the observable, the action, and the resolving evidence.
5. **Apply the show-stopper gate.** Mark `S4 - Show-stopper / Not fixable` only when the issue violates a necessary objective or non-negotiable constraint, no repair class (redesign, sequencing, de-scoping, controls, experiment, alternative implementation) reduces the failure to acceptable risk, and the conclusion rests on evidence or a defensible reasoning chain — not discomfort or uncertainty. Incomplete evidence means `Conditionally fixable` with a decision gate, never a lazy REJECT.
6. **Synthesize and issue the verdict.** Produce the strongest viable next version — refined, extended, reworked, replaced, or rejected; when several resolutions exist, give 2-3 options with trade-offs and a preferred choice. End with exactly one primary verdict (`PROCEED` / `PROCEED WITH CONDITIONS` / `REWORK` / `REPLACE` / `REJECT`) tied to the highest-severity unresolved findings, residual risk, and evidence strength.

## Required Output

Adapt detail, but never omit the verdict, per-finding severity, or kill criteria. Full rules: `references/finding-and-verdict-schema.md`.

```markdown
# Devil's Advocate Review: [Proposal]

**Verdict:** [PROCEED / PROCEED WITH CONDITIONS / REWORK / REPLACE / REJECT] — [why, 2-4 sentences]

## Steelmanned case
## Findings
### F-01 - [Title]
- **Severity:** [S0-S4] · **Disposition:** [Fixable / Conditionally fixable / Not fixable]
- **Reasoning chain:** [condition -> trigger -> failure -> impact]
- **Resolution:** [repair, alternative, or experiment; trade-offs; residual risk]

## What survives and revised path
## Decision gates and kill criteria
[Observable go/revise/pause/stop conditions and thresholds]
```

## Guardrails

- Never turn conceptual red teaming into instructions for real-world harm or unauthorized exploitation; identify where qualified legal, medical, safety, compliance, or security review is required.
- Do not assume malicious intent where ordinary incentives or constraints explain the risk; reject only when the objective cannot be achieved acceptably under the constraints, not for being unconventional.

## Tool notes

Use subagents only for deep red-team reviews where independence materially improves quality; stay inline for quick or standard reviews. Shared procedure: frame and steelman the proposal yourself and select distinct lenses; in a single turn, dispatch independent subagents for the highest-value lenses — same proposal frame, one lens each — asking for candidate findings with causal chain, severity, evidence, disposition, and resolution path; then deduplicate and rank the replies yourself, apply the show-stopper gate, and issue exactly one verdict.

Per-tool exceptions:

- **Claude Code:** on Claude.ai (no CLI subagents), run lenses sequentially in one context and label the missing-independence uncertainty.
- **Cursor:** `subagent_type: "generalPurpose"` (`explore` for pure repository discovery); `AskQuestion` only when a missing non-negotiable or decision-owner preference would change the verdict.
- **GitHub Copilot:** usually no parallel subagent API — run lenses sequentially; record assumptions, gates, and kill criteria in the report or PR text.
