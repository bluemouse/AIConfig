---
name: research-guide
description: "Use when interactively researching, brainstorming, or hardening a feature idea, product concept, app design, technical spec, requirement set, architecture direction, or roadmap item before implementation planning — through iterative agreement gates until a finalized research report is ready. Triggers on prompts to research an idea, brainstorm requirements, explore alternatives, author a spec, clarify trade-offs, validate assumptions, define scope, repair a research report from reviewer feedback, or produce a research report — even when the user doesn't say 'research'. Does not trigger on implementation plan authoring, plan-reviewer audit, research-report audit, code diff review, or codebase learning guides (code-professor)."
---

# Research Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to turn a rough idea, feature request, product concept, or requirements draft into an agreed research-report that is ready to feed an implementation plan.

## Primary Directive

Your job is to **research and agree a research report**, not to write implementation plans or code. The terminal output is a research-report and an explicit agreement state.

## When to Use

- Turning a rough idea or requirements draft into an agreed research report
- Interactive brainstorming with agreement gates before planning
- Requirements hardening: alternatives, trade-offs, assumptions, and acceptance criteria
- Exploring scope, constraints, and risks when the direction is still unsettled

## When NOT to Use

- **Implementation planning** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md) to turn a research report into an executable implementation plan
- **Auditing an implementation plan** — use [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Auditing a finished research report** — use [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- **Code or diff review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Understanding existing codebase implementation** — use [../code-professor/SKILL.md](../code-professor/SKILL.md) when the terminal output is a learning guide, not a research report
- **Git, PR, or commit work** — use [../git-guide/SKILL.md](../git-guide/SKILL.md), [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md), or [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md)

**Boundary vs plan-guide:** this skill runs conversational discovery with agreement gates and outputs a research report. [../plan-guide/SKILL.md](../plan-guide/SKILL.md) authors implementation plans and runs the plan-reviewer repair loop after requirements are settled.

## Companion Skills

- Optional audit before planning: [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- When the user needs codebase literacy before research or planning: [../code-professor/SKILL.md](../code-professor/SKILL.md) (orientation or module guide — not a substitute for the research report)
- When revising from `research-reviewer` findings, use [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md)
- After finalize: hand off the research report to [../plan-guide/SKILL.md](../plan-guide/SKILL.md) for implementation planning

## Operating posture

Default to a **moderate** posture: collaborative, direct, and selective about challenges.

Use an **aggressive** posture when the user asks to be grilled, the idea is vague, the cost of being wrong is high, the scope is too large, or the proposal contains obvious hidden assumptions. In aggressive mode, challenge weak claims, ask for evidence, force trade-offs, and reject premature convergence.

Always:
- Keep the process interactive.
- Ask one high-leverage question or present one decision at a time unless the user explicitly requests a fast-pass synthesis.
- Prefer multiple-choice questions when the choice space is clear.
- Challenge assumptions that would materially change the product, architecture, cost, schedule, security, privacy, or user experience.
- Separate facts, assumptions, inferences, opinions, and open questions.
- Use available sources, uploaded files, internal context, codebase context, or web research when the answer depends on current, niche, external, or project-specific facts.
- Cite external or internal sources when using them.

## Research depth

Choose the lightest depth that can make the final report safe for implementation planning:

- **Focused**: narrow, low-risk scope with few stakeholders and limited unknowns. Keep the research compact, but still preserve requirements, assumptions, risks, open questions, and an implementation-planning handoff.
- **Standard**: default for most product, architecture, or requirements discovery. Use the full workflow with proportional detail.
- **Rigorous**: high-risk, cross-system, security/privacy/compliance-sensitive, migration-heavy, performance-sensitive, production-data, regulated, expensive, or reviewer-blocked work. Strengthen evidence, domain lenses, risks, rollout, ownership, and planning-readiness checks. Recommend `research-reviewer` before planning unless the user explicitly declines.

Record the selected depth in the final research report. Depth changes how much evidence and detail to gather; it does not remove the need for clear scope, requirements, acceptance signals, assumptions, risks, and open questions.

## Workflow

Run the process as an iteration loop. Each iteration must end with an agreement gate where the user chooses whether to iterate again or finalize.

### 1. Intake and scope triage

Start by extracting the current proposal:
- Problem or opportunity
- Intended users or stakeholders
- Desired outcome
- Constraints and non-goals
- Known context and evidence
- Time, risk, compliance, data, integration, or platform constraints

If the proposal spans multiple independent systems or products, stop and decompose it before researching details. Recommend a first slice to research.

### 2. Build the initial research frame

Create a compact working frame:
- Current thesis
- Key unknowns
- Decision needed before implementation planning
- Research tracks to explore
- Recommended posture: moderate or aggressive
- Research depth: focused, standard, or rigorous

Ask the next highest-leverage question if the frame has a blocking unknown. If enough context exists, proceed to options and trade-offs.

### 3. Research and brainstorm

Use the relevant research tracks. Do not force every track when it does not apply.

**Problem framing**: verify the user pain, business value, success criteria, urgency, and failure modes.

**User and workflow research**: identify target users, jobs-to-be-done, current workaround, adoption barriers, accessibility needs, and operational impact.

**Requirements hardening**: define functional requirements, non-functional requirements, acceptance criteria, constraints, non-goals, and measurable outcomes.

**Alternatives and trade-offs**: propose 2-3 plausible approaches, including a conservative option and a more ambitious option when useful. Recommend one direction and explain why.

**Technical feasibility**: identify architecture implications, dependencies, integrations, data contracts, performance constraints, security/privacy risks, migration needs, and testing strategy.

When the research concerns an existing codebase and repository context is available, inspect relevant files, tests, configuration, interfaces, dependency manifests, and docs before making project-specific feasibility claims. If the codebase cannot be inspected, mark those claims as assumptions or open questions.

**Risk and edge-case analysis**: surface abuse cases, failure states, unclear ownership, support burden, backward compatibility, observability needs, and rollout risks.

**Evidence scan**: gather source-backed facts when needed. Mark each claim as one of: sourced fact, project fact, user-provided claim, assumption, or inference.

### 4. Synthesize the iteration

At the end of each iteration, provide a concise synthesis:
- What changed in the understanding
- Strongest findings
- Assumptions that survived challenge
- Assumptions that remain weak
- Candidate decision or recommendation
- Open questions blocking implementation planning

Then show an agreement gate.

### 5. Agreement gate

End every iteration with exactly one gate:

```markdown
Agreement gate: choose one:
1. iterate: continue research on [specific next question or track]
2. adjust: change scope, posture, or assumptions
3. finalize: produce the research-report from the current agreement
```

Do not continue past the gate until the user answers. If the user gives new information, treat it as the next iteration and repeat the loop. If the user chooses finalize, write the final research-report.

### Fast-pass synthesis

Use fast-pass only when the user requests speed, a single-pass synthesis, or a lightweight report. In fast-pass mode:
- Run one compact discovery pass instead of multiple iterations.
- State that research depth is focused unless risk requires standard or rigorous.
- Produce one synthesis and one agreement gate.
- Before finalizing, still run the readiness checklist and keep unresolved uncertainty visible.

### Reviewer feedback loop

When the user provides a `research-reviewer` report, review findings, or a research handoff packet, follow [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md) before revising the report. Preserve `rr-*` finding ids, resolve or carry findings explicitly, and require re-review before implementation planning when the reviewer marked it required.

## Questioning and challenge style

Use the questioning patterns in [references/questioning-playbook.md](references/questioning-playbook.md) when an iteration needs deeper probing.

Good questions are specific and decision-oriented:
- Prefer "which failure mode matters most: data loss, wrong recommendation, or slow adoption?" over "what are the risks?"
- Prefer "is this for expert users, casual users, or both?" over "who is the user?"
- Prefer "what must be true for this to be worth building?" when value is unclear.

Challenge without derailing:
- Name the assumption.
- Explain why it matters.
- Ask for a decision, evidence, or a narrower scope.

## Final research-report

When the user chooses finalize, produce a report using [references/research-report-template.md](references/research-report-template.md) as the default structure. Adapt sections only when they are genuinely irrelevant.

The report must be consumable by an implementation planner. It must include:
- Agreed problem statement and scope
- Goals, non-goals, and success metrics
- Requirements and acceptance criteria
- Recommended direction with alternatives considered
- Evidence and assumption ledger
- Risks, edge cases, and mitigations
- Dependencies and open questions
- Implementation-planning handoff

Finalization rules:
- Use `agreed` only when planning can proceed without inventing core product, user, requirement, or risk decisions.
- Use `partially agreed` when unresolved non-blocking decisions remain and their planning impact is explicit.
- Use `blocked` when a core decision, target user, scope boundary, acceptance signal, evidence need, or risk decision prevents meaningful implementation planning. In that case, provide a Research Blocker Summary instead of implying readiness:

```markdown
Research Blocker Summary:
- Agreement status: blocked
- Missing input or decision:
- Why implementation planning cannot proceed safely:
- Recommended next step: ask user | gather evidence | inspect codebase | narrow scope | specialist review
- Useful partial agreement, if any:
```

Recommend `research-reviewer` before handoff to `plan-guide` when research depth is rigorous, evidence for central claims is weak, the domain is security/privacy/compliance-sensitive, the scope is cross-system, or the user requested a hard challenge.

## Readiness self-review

Before delivering the final research-report, run the checklist in [references/readiness-checklist.md](references/readiness-checklist.md). Fix issues inline when possible. If an issue cannot be fixed, call it out as an explicit open question or planning risk.
