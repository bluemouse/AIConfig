---
name: research-guide
description: "Interactively research, brainstorm, or harden a feature idea, product concept, technical spec, requirement set, or architecture direction through agreement gates into a finalized research report, or repair one from reviewer feedback. Not for implementation plan authoring (plan-guide), report/plan audits, code diff review, or codebase learning guides (code-professor)."
---

# Research Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`; resolve `references/` paths from it.

Turn a rough idea, feature request, or requirements draft into an **agreed research report** — not an implementation plan or code. Match the interaction style to the request: a direct question or a recommendation request gets a direct answer; the interactive agreement-gate workflow below runs when the user asks to research, brainstorm, or harden an idea (or hands you a deliverable whose scope demands it).

## Deferral and handoff

- Ambiguous ask (deliverable, scope, or decision unclear) — settle with [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) first; once discovery begins, this skill's one-question-at-a-time pacing governs
- Implementation planning — [../plan-guide/SKILL.md](../plan-guide/SKILL.md) (hand the finalized report to it); plan audit — [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- Research-report audit — [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md), revising via [../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md](../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md)
- Code or diff review — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md); codebase learning — [../code-professor/SKILL.md](../code-professor/SKILL.md)
- Git, PR, or commit work — [../git-guide/SKILL.md](../git-guide/SKILL.md), [../github-guide/SKILL.md](../github-guide/SKILL.md), or [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md)

## Direct requests

When the user asks for a recommendation or a bounded answer (not an open-ended research session), answer directly: give the recommendation with its key reasoning and the main risk, label assumptions as assumptions, and say plainly when the evidence needed for a confident answer is unavailable rather than padding or fabricating. Ask a question only when the answer would change the recommendation materially. A genuinely open-ended or multi-iteration research request — or one whose cost of being wrong is high — is a signal to switch into the interactive workflow below.

## Posture and depth

Default posture **moderate**; go **aggressive** (challenge weak claims, demand evidence, force trade-offs) when the user asks to be grilled, the idea is vague, the cost of being wrong is high, or the scope is too large. Pick the lightest depth that keeps the report safe for planning — **focused** (narrow, low-risk), **standard** (default), **rigorous** (high-risk, cross-system, security/privacy/compliance-sensitive, migration-heavy, regulated, or reviewer-blocked — strengthen evidence and recommend `research-reviewer` before planning unless the user declines). Record posture and depth in the report; in the interactive workflow, keep to one high-leverage question or decision at a time.

## Workflow

Run the process as an iteration loop; each iteration ends with an agreement gate. The gate is required: do not continue past it until the user answers.

1. **Frame the research**: extract the proposal into a working frame — current thesis, key unknowns, the decision needed before planning, recommended posture, and depth. Decompose multi-system proposals and research a first slice; a blocking unknown → ask the next highest-leverage question.
2. **Research and brainstorm**: probe the iteration's key unknowns — users, requirements, alternatives, feasibility, risks — as applicable. For consequential decisions — multiple viable options with meaningful trade-offs where a wrong choice is hard to reverse — consider advisory-council and, when useful, present its ranked recommendation at the next agreement gate; skip it for straightforward choices.
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

**Reviewer feedback loop** — when the user provides a `research-reviewer` report or findings, follow [../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md](../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md) before revising.

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
