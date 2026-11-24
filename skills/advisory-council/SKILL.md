---
name: advisory-council
description: Convene an advisory council, think tank, panel, or structured debate with distinct expert, stakeholder, skeptical, operational, and creative perspectives on complex decisions, plans, strategies, designs, disputes, trade-offs, or competing options. Deliver ranked recommendations, decision gates, minority dissent, and a defensible resolution with evidence quality, assumptions, risks, and revisit triggers. Not for single-proposal red-teaming with a proceed/reject verdict or git diff review.
---

# Advisory Council

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve paths to `references/` from that directory.

Convene a structured council whose members reason from different responsibilities, challenge one another, update their views, and produce a decision-quality recommendation instead of a set of disconnected opinions.

## Scope and Boundaries

Use this skill when a single answer would be weaker than disciplined disagreement: consequential decisions with several viable options; plans, strategies, designs, or proposals with meaningful trade-offs; disputes about facts, values, forecasts, constraints, or execution; ambiguous problems where reframing and option generation are part of the work; or requests for a "council", "panel", "think tank", "debate", or "minority report".

Use the domain skill first when correctness requires specialized procedure, then use this skill only for the decision synthesis around that material.

## When NOT to Use

- **Adversarial stress-test of a single proposal with a proceed/rework/reject verdict** — use [../devil-advocate/SKILL.md](../devil-advocate/SKILL.md)
- **Git diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Implementation planning from settled requirements** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Root-cause investigation of a reproducible defect** — use [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
- **Open-ended discovery and feature research with agreement gates** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Settling an ambiguous request before any deliberation** — use [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md)

## Core Contract

- Treat the user as the decision owner and the council as advisors.
- Assign each council member a distinct role, objective, prior, failure lens, and evidence standard. Avoid cosmetic personas that reach the same conclusion in different wording.
- Ground material claims in evidence. Separate verified facts, inferences, assumptions, preferences, and unknowns.
- Require interaction: members must critique, question, concede, refine, or defend positions in response to other members.
- Optimize for decision quality, not harmony. Preserve credible dissent and do not manufacture unanimity.
- End with a conclusion, ranked options, resolution, plan, or conditional decision. Do not stop at debate notes.
- Use the minimum council size and number of rounds needed for the stakes and ambiguity.
- Never claim that independent agents, tools, specialists, or live experts participated unless they actually did.
- Do not impersonate living or historical people. Use role-based perspectives rather than fabricated quotations or personal voice imitation.
- Do not produce false consensus. Label unresolved disagreement precisely.
- Do not let one member dominate through verbosity, status, or rhetorical confidence; do not count repeated arguments as independent evidence or settle factual questions by majority vote — verify them.
- Expect belief updating: at least one argument should be conceded, refined, or conditionally accepted when warranted.
- Keep the council proportional — no larger or longer than the stakes require, and stop once new rounds stop producing material information.

Read `references/council-protocol.md` for the full deliberation, evidence, comparison, convergence, and fallback protocol. Read `references/output-formats.md` when producing the final deliverable. Read `references/examples.md` when role selection or council behavior is unclear.

## Execution Modes

Select the strongest available mode without blocking the task:

1. **Native council:** When independent worker or agent tools are available, dispatch council members independently, preserve their separate outputs, and run cross-review rounds.
2. **Delegated council:** When only sequential worker calls are available, call each member separately and keep Round 1 members blind to earlier answers; apply the round-collection and call-order fairness rules in `references/council-protocol.md`.
3. **Simulated council:** When no independent execution mechanism exists, simulate distinct council members in one context. Explicitly label the result as a simulated council, write all independent Round 1 positions before exposing peer positions, and enforce the same debate and convergence rules.

Use simulated mode by default when the environment does not expose independent execution. Honesty about the mode matters more than the mode itself.

## Workflow

### 1. Frame the Council Charter

Restate the decision in one sentence; extract the desired outcome, scope, hard constraints, evaluation criteria, current options, stakeholders, and evidence held or still needed. Ask a question only when a missing fact could reverse the recommendation, make the task unsafe, or make the decision meaningless; otherwise state the working assumption and proceed. Pick a deliberation mode: **Explore**, **Decide**, **Plan**, **Resolve**, or **Review**.

### 2. Choose Deliberation Depth

Scale from Lean (3 members, 2 rounds) through Standard to Rigorous with the stakes; tier definitions: `references/council-protocol.md`. Add a member only when their perspective could change the decision.

### 3. Assemble a Non-Redundant Council

Use 3-7 voting members plus a non-voting chair, each constructed per the five-field definition in `references/council-protocol.md` with a meaningfully different attack surface — e.g. domain authority, operator, stakeholder advocate, risk and dissent lead, systems integrator, evidence auditor, alternative architect. Select roles from the topic, not by rote; have the chair justify each selection in one line. Role-design calibration: `references/examples.md`.

### 4. Build the Evidence Ledger

Before debate, create a claim-indexed record of facts, inferences, assumptions, preferences, and unknowns (claim and evidence grading: `references/council-protocol.md`). Research externally when the answer depends on current or high-stakes facts and suitable tools are available; prefer primary sources. Never invent citations or upgrade an assumption into a fact.

### 5. Run Round 1: Independent Positions

Give every member the same charter and evidence ledger, but not other members' conclusions. Each member returns a position, its strongest supporting evidence, assumptions and uncertainties, the strongest argument against their own position, a failure mode, mind-changing evidence, and a confidence level. Independence is mandatory — do not let the first answer anchor the rest.

### 6. Run Round 2: Cross-Examination

Expose the Round 1 positions to the full council: each member challenges at least one material claim from another member, names a point that improves their own view, distinguishes whether the disagreement is about facts, values, forecasts, constraints, or implementation, and updates their recommendation when an objection succeeds. The chair probes vague language, hidden trade-offs, and claims lacking decision relevance. Claim dispositions (`STANDS`/`REFINE`/`REJECT`/`NEEDS EVIDENCE`) and concession rules: `references/council-protocol.md`.

### 7. Run Round 3: Options and Convergence

Build 2-5 viable options — a hybrid or staged option only when genuinely coherent — each with mechanism and scope, costs and benefits, risks and mitigations, preconditions and disqualifiers, reversibility and exit path, and a validation evidence gate. Score against the charter criteria to expose trade-offs, never to disguise judgment as precision. Converge only when the leading option satisfies all hard constraints, no unresolved objection has a credible path to unacceptable failure, and remaining dissent is documented with a trigger that would make it decisive; otherwise return ranked conditional options plus the smallest resolving evidence step. Scoring, consensus levels, and stop rules: `references/council-protocol.md`.

### 8. Produce the Council Decision

Use the template in `references/output-formats.md` matching the deliverable. Always preserve evidence quality, decisive arguments and concessions, ranked options with the conditions under which alternatives become preferable, unresolved dissent, an executable next-step plan or decision gates, and revisit triggers. For a recommendation, explicitly state what not to do and why when that prevents a likely failure.

## Tool notes

### Claude Code

Use subagents only when the decision is large enough to benefit from independent work:

1. Run the charter, evidence ledger, role selection, and depth choice yourself first.
2. In a single turn, spawn one subagent per selected Round 1 council member when parallel independence matters.
3. Give every subagent the same charter and evidence ledger, plus only its own role brief. Do not include peer conclusions in Round 1.
4. Ask each subagent to return the Round 1 fields from Workflow step 5.
5. Collect final replies, normalize claims, then run cross-examination and synthesis yourself. Dispatch a second round only for rigorous or high-stakes councils.

Tool-specific differences:

- **Claude Code:** On Claude.ai (no Claude Code CLI), no parallel subagents are available — use simulated council mode, label it honestly, write all independent Round 1 positions before cross-examination, and keep the final decision proportional to the prompt.

### GitHub Copilot

Copilot Chat usually has no parallel subagent API, so preserve independence through disciplined simulated rounds: state that the council is simulated, write all Round 1 positions before any cross-examination, keep notes claim-indexed so concessions stay visible, run cross-examination and convergence in the same chat, and use concise output for low-stakes decisions. As a non-interactive coding agent, do not wait for user answers unless the missing decision is unsafe to assume; record assumptions and decision gates in the final report or pull request text.
