---
name: research-guide
description: "Use when interactively researching, brainstorming, or hardening a feature idea, product concept, app design, technical spec, requirement set, architecture direction, or roadmap item before implementation planning — through iterative agreement gates until a finalized research report is ready. Triggers on prompts to research an idea, brainstorm requirements, explore alternatives, author a spec, clarify trade-offs, validate assumptions, define scope, repair a research report from reviewer feedback, or produce a research report — even when the user doesn't say 'research'. Does not trigger on implementation plan authoring, plan-reviewer audit, research-report audit, code diff review, or codebase learning guides (code-professor)."
---

# Research Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`; resolve `references/` paths from it.

Turn a rough idea, feature request, or requirements draft into an **agreed research report** — not an implementation plan or code — interactively, through agreement gates.

## Deferral and handoff

- Ambiguous ask (deliverable, scope, or decision unclear) — settle with [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) first; once discovery begins, this skill's one-question-at-a-time pacing governs
- Implementation planning — [../plan-guide/SKILL.md](../plan-guide/SKILL.md) (hand the finalized report to it); plan audit — [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- Research-report audit — [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md), revising via [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md)
- Code or diff review — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md); codebase learning — [../code-professor/SKILL.md](../code-professor/SKILL.md)
- Git, PR, or commit work — [../git-guide/SKILL.md](../git-guide/SKILL.md), [../github-guide/SKILL.md](../github-guide/SKILL.md), or [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md)

## Operating posture

Default **moderate**; go **aggressive** when the user asks to be grilled, the idea is vague, the cost of being wrong is high, or the scope is too large — then challenge weak claims, demand evidence, force trade-offs, and reject premature convergence. Always keep it interactive — one high-leverage question or one decision at a time — and challenge assumptions that would materially change the product, architecture, cost, schedule, security, privacy, or user experience; separate facts, assumptions, inferences, opinions, and open questions, and cite sources for current, niche, or project-specific facts.

## Research depth

Pick the lightest depth that keeps the report safe for planning: **focused** (narrow, low-risk), **standard** (default), **rigorous** (high-risk, cross-system, security/privacy/compliance-sensitive, migration-heavy, regulated, or reviewer-blocked — strengthen evidence and recommend `research-reviewer` before planning unless the user declines). Record the chosen depth in the report; it scales evidence and detail, never removing the need for clear scope, requirements, acceptance signals, assumptions, risks, and open questions.

## Workflow

Run the process as an iteration loop; each iteration ends with an agreement gate.

1. **Frame the research**: extract the proposal into a working frame — current thesis, key unknowns, the decision needed before planning, recommended posture, and depth. Decompose multi-system proposals and research a first slice; a blocking unknown → ask the next highest-leverage question.
2. **Research and brainstorm**: cover users and value, requirements, alternatives and trade-offs, technical feasibility, and risks as applicable. For consequential decisions — multiple viable options with meaningful trade-offs — invoke advisory-council and present its ranked recommendation at the next agreement gate; skip it for straightforward choices.
3. **Synthesize the iteration**: what changed, strongest findings, surviving vs weak assumptions, candidate decision, open questions blocking planning.
4. **Agreement gate** — end every iteration with exactly one:

```markdown
Agreement gate: choose one:
1. iterate: continue research on [specific next question or track]
2. adjust: change scope, posture, or assumptions
3. finalize: produce the research-report from the current agreement
```

Do not continue past the gate until the user answers. New information starts the next iteration. On finalize, write the final research-report.

**Fast-pass synthesis** — only on an explicit user request for speed or a lightweight report: one compact discovery pass (depth focused unless risk requires more), one synthesis, one agreement gate; still run the readiness checklist before finalizing.

**Reviewer feedback loop** — when the user provides a `research-reviewer` report or findings, follow [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md) before revising.

For deeper probing, use the questioning patterns in [references/questioning-playbook.md](references/questioning-playbook.md).

## Final research-report

Produce the report from [references/research-report-template.md](references/research-report-template.md), adapting sections only when genuinely irrelevant.

**Artifact output path:** outside the dev-workflow-orchestrator, write the report to `.agents/researches/<feature-or-topic-slug>.md` (gitignored — never write research artifacts to the repository root); inside the orchestrator, use the assigned path (typically `.agents/workflow/<slug>/10-research-report.md`).

Finalization state:
- `agreed` — planning can proceed without inventing core product, user, requirement, or risk decisions.
- `partially agreed` — unresolved non-blocking decisions remain, with their planning impact explicit.
- `blocked` — a core decision, target user, scope boundary, acceptance signal, evidence need, or risk decision prevents meaningful implementation planning. Provide a Research Blocker Summary instead of implying readiness:

```markdown
Research Blocker Summary:
- Agreement status: blocked
- Missing input or decision:
- Why implementation planning cannot proceed safely:
- Recommended next step: ask user | gather evidence | inspect codebase | narrow scope | specialist review
- Useful partial agreement, if any:
```

## Readiness self-review

Before delivering the final research-report, run [references/readiness-checklist.md](references/readiness-checklist.md). Fix issues inline when possible; otherwise call them out as an explicit open question or planning risk.
