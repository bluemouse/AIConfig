---
name: advisory-council
description: Convene an advisory council, think tank, panel, or structured debate with distinct expert, stakeholder, skeptical, operational, and creative perspectives on complex decisions, plans, strategies, designs, disputes, trade-offs, or competing options. Deliver ranked recommendations, decision gates, minority dissent, and a defensible resolution with evidence quality, assumptions, risks, and revisit triggers. Not for single-proposal red-teaming with a proceed/reject verdict or git diff review.
---

# Advisory Council

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve paths to `references/` from that directory.

Convene a structured council whose members reason from different responsibilities, challenge one another, update their views, and produce a decision-quality recommendation instead of a set of disconnected opinions.

## Scope and Boundaries

Use this skill when a single answer would be weaker than disciplined disagreement:

- consequential decisions with several viable options;
- plans, strategies, designs, policies, or proposals with meaningful trade-offs;
- disputes where disagreement may be about facts, values, forecasts, constraints, or execution;
- ambiguous problems where reframing and option generation are part of the work;
- requests for a "council", "panel", "think tank", "debate", "multiple expert views", or "minority report".

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

Read `references/council-protocol.md` for the full deliberation, evidence, scoring, convergence, and fallback protocol. Read `references/output-formats.md` when producing the final deliverable. Read `references/examples.md` when role selection or council behavior is unclear.

## Execution Modes

Select the strongest available mode without blocking the task:

1. **Native council:** When independent worker or agent tools are available, dispatch council members independently, preserve their separate outputs, and run cross-review rounds.
2. **Delegated council:** When only sequential worker calls are available, call each member separately and keep later members blind to earlier answers during the independent round.
3. **Simulated council:** When no independent execution mechanism exists, simulate distinct council members in one context. Explicitly label the result as a simulated council, write all independent Round 1 positions before exposing peer positions, and enforce the same debate and convergence rules.

Use simulated mode by default when the environment does not expose independent execution. Honesty about the mode matters more than the mode itself.

## Workflow

### 1. Frame the Council Charter

Restate the decision or problem in one sentence. Extract or infer:

- desired outcome and decision to be made;
- scope and exclusions;
- hard constraints and non-negotiables;
- evaluation criteria and their relative importance;
- current options, prior work, deadlines, and affected stakeholders;
- evidence already supplied and evidence still needed.

Ask a question only when a missing fact could reverse the recommendation, make the task unsafe, or make the final decision meaningless. Otherwise state the working assumption and proceed.

Choose a deliberation mode:

- **Explore:** discover approaches and reframe the problem.
- **Decide:** compare options and select a recommendation.
- **Plan:** construct an executable approach and sequencing.
- **Resolve:** reconcile conflicting positions or requirements.
- **Review:** evaluate and improve an existing proposal.

### 2. Choose Deliberation Depth

Match the council to the stakes:

- **Lean:** 3 members, 2 rounds, for bounded and reversible choices.
- **Standard:** 4-5 members, 3 rounds, for meaningful trade-offs.
- **Rigorous:** 6-7 members, 3 rounds plus verification, for costly, irreversible, regulated, safety-sensitive, or broad-impact decisions.

Do not expand the council merely because more roles can be imagined. Add a member only when their perspective could change the decision.

### 3. Assemble a Non-Redundant Council

Use 3-7 voting members plus a non-voting chair. Select roles dynamically from the topic; do not use every role automatically.

Ensure coverage of these functions when relevant:

- **Domain authority:** correctness, standards, and deep subject knowledge.
- **Operator or practitioner:** feasibility, delivery, maintenance, and real-world friction.
- **Stakeholder advocate:** user, customer, employee, community, or business impact.
- **Risk and dissent lead:** failure modes, hidden assumptions, downside, and reversibility.
- **Systems integrator:** dependencies, second-order effects, interfaces, and long-term coherence.
- **Evidence auditor:** source quality, uncertainty, missing data, and falsifiability.
- **Alternative architect:** reframing, unconventional options, simplification, and hybrids.

The chair must explain in one line why each selected perspective is necessary. Replace overlapping members until each has a meaningfully different attack surface.

### 4. Build the Evidence Ledger

Before debate, create a compact shared record:

- `F#` verified facts with sources or supplied evidence;
- `I#` inferences and their reasoning chains;
- `A#` assumptions that require validation;
- `P#` preferences or value choices attributed to the decision owner or stakeholders;
- `U#` unresolved unknowns;
- `C#` decision criteria and weights when ranking options.

Research externally when the answer depends on current, niche, technical, legal, medical, financial, or otherwise high-stakes facts and suitable tools are available. Prefer primary sources. Never invent citations or upgrade an assumption into a fact.

### 5. Run Round 1: Independent Positions

Give every member the same charter and evidence ledger, but not other members' conclusions. Require each member to return:

- position or proposed approach;
- strongest supporting evidence and reasoning;
- assumptions and uncertainties;
- strongest argument against their own position;
- expected failure mode;
- what evidence would change their mind;
- confidence level.

Independence is mandatory. Do not let the first answer anchor the rest.

### 6. Run Round 2: Cross-Examination

Expose the Round 1 positions to the full council. Require every member to:

- challenge at least one material claim from another member;
- identify one point from another member that improves their own view;
- distinguish disagreement about facts, values, forecasts, constraints, or implementation;
- mark each challenged claim as `STANDS`, `REFINE`, `REJECT`, or `NEEDS EVIDENCE`;
- update their recommendation when an objection succeeds.

The chair must probe vague language, hidden trade-offs, missing baselines, and claims that lack decision relevance.

### 7. Run Round 3: Options and Convergence

Create 2-5 viable options, including a hybrid or staged option only when it is genuinely coherent. For each option, specify:

- mechanism and scope;
- benefits and costs;
- risks and mitigations;
- preconditions and disqualifiers;
- reversibility and exit path;
- validation experiment or evidence gate.

Score options against explicit criteria using `references/council-protocol.md` when ranking matters. Use scores to expose trade-offs, not to disguise judgment as precision.

Convergence is reached only when:

- the leading recommendation satisfies all hard constraints;
- no unresolved objection has a credible path to catastrophic or unacceptable failure;
- its causal reasoning is evidence-backed or clearly conditional;
- the council can explain why it outranks the alternatives;
- remaining dissent is documented with a trigger that would make it decisive.

Do not require unanimity. If convergence fails, return ranked conditional options and the smallest evidence-gathering step that can resolve the deadlock.

### 8. Produce the Council Decision

Use the relevant template in `references/output-formats.md`. Always include:

- the council charter and selected perspectives;
- evidence quality and important assumptions;
- decisive arguments and meaningful concessions;
- the recommended option with confidence and rationale;
- ranked alternatives and conditions under which they become preferable;
- risks, mitigations, and unresolved dissent;
- an executable next-step plan or decision gates;
- triggers for revisiting the decision.

For a plan, include owner roles, dependencies, checkpoints, success criteria, and stop conditions. For a recommendation, explicitly state what not to do and why when that prevents a likely failure.

## Quality Gates

Before answering, verify:

- **Perspective distinctness:** Could each member plausibly disagree because their objectives or evidence differ?
- **Evidence discipline:** Are facts cited or supplied, and are assumptions visibly labeled?
- **Actual debate:** Did members respond to one another instead of delivering parallel monologues?
- **Belief updating:** Did at least one argument get conceded, refined, or conditionally accepted when warranted?
- **Decision usefulness:** Is the output actionable, ranked, and tied to criteria?
- **Dissent integrity:** Are material minority objections retained instead of averaged away?
- **Proportionality:** Was the council no larger or longer than necessary?

If any gate fails, repair the deliberation before presenting the result.

## Guardrails

- Do not impersonate living or historical people. Use role-based perspectives rather than fabricated quotations or personal voice imitation.
- Do not let one member dominate because of verbosity, status, or rhetorical confidence.
- Do not count repeated arguments as independent evidence.
- Do not use majority vote to settle factual questions; verify them.
- Do not produce false consensus. Label unresolved disagreement precisely.
- Do not continue debating after new rounds stop producing material information.
- Do not delegate final accountability to the council. The synthesis must make a clear recommendation or explain the exact decision gate preventing one.
