---
name: plan-guide
description: "Turn a research report, spec, requirements, bug report, or codebase context into an executable implementation plan — decomposing ordered tasks, mapping requirements to TDD or verification checks, normalizing thin plans, or repairing plans from plan-reviewer findings. Does not trigger on interactive research (research-guide), plan/report audits, codebase guides (code-professor), implementation (plan-executor), or diff review (code-reviewer)."
---

# Plan Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`, and resolve `references/` paths from it.

Turn an approved research report, spec, requirement set, bug report, or codebase context into an executable implementation plan that a developer or AI agent can run without inventing missing decisions.

## Primary Directive and Boundaries

Author and repair implementation plans — do not implement code, audit research reports, or review diffs. Every ready-to-execute plan gives each task concrete verification (`mandatory` strict TDD when requested or warranted by risk; `verification-led` with a stated alternative check otherwise; `n/a` justified for non-code/check-only tasks) and passes [references/plan-quality-checklist.md](references/plan-quality-checklist.md).

**When NOT to use:**
- **Interactive research / brainstorming** → `research-guide`
- **Auditing a research report or implementation plan** → `research-reviewer` or [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Code implementation or diff review** → [../plan-executor/SKILL.md](../plan-executor/SKILL.md) or `code-reviewer`
- **Codebase onboarding / learning guides without a plan** → `code-professor`
- **Ambiguous or contradictory requirements** → settle with `prompt-clarifier` first; planning-specific blockers on settled requirements stay here at one question per turn.

## Operating posture

Default to a precise, traceable engineering posture; tighten rigor for security/privacy, migrations, production data, performance, cross-cutting contracts, or reviewer-blocked plans:
- Inspect available repository files, tests, build configs, and conventions before asking discoverable questions; never invent file paths, APIs, or commands.
- Separate source requirements, planning assumptions, confirmed decisions, and open questions.
- Ask one material question at a time when a missing decision blocks planning; prefer `blocked` or `discovery-gated` over a false-ready plan or placeholder steps (`TBD`, `TODO`, "add tests").

## Planning depth

Choose the lightest depth that preserves traceability, verification, and readiness (full field/section schema in [references/implementation-plan-template.md](references/implementation-plan-template.md)):
- **Focused**: low-risk single-subsystem work or small fix (≤ ~5 tasks, no migrations or cross-cutting risk). Compact sections, keeping goal/scope, traceability, test design, task breakdown, per-task verification, and `execution class` (default `sequential`).
- **Standard**: default for multi-file features, refactors, and integrations; full template with proportional detail.
- **Rigorous**: high-risk, security/privacy, migration, performance, production-data, or reviewer-blocked work; full template with expanded risk, rollout, rollback, and observability gates.

## Workflow

### 1. Detect input mode and map sources

Select one input mode (`research handoff`, `direct spec`, `codebase-led`, `plan normalization`, or `review repair loop`):
- Extract goal, in/out-of-scope, functional/non-functional requirements, acceptance criteria, constraints, integration contracts, and open questions into template §2–§4.
- For a **research handoff**, preserve upstream readiness and carry unresolved pre-implementation questions as blocking unless explicitly resolved or accepted as risk.
- For **codebase-led**, **direct spec** without upstream sign-off, or **plan normalization**, cap initial status at `draft` or `ready for review` (never `validated` without `plan-reviewer` approval or explicit user acceptance).
- For **review repair**, follow [../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md](../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md) and [../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md](../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md), giving every blocker/major finding an explicit disposition.

### 2. Classify readiness

| Process readiness | Artifact status |
|---|---|
| Ready to plan | `ready for review` (until `plan-reviewer` validates) |
| Conditionally plannable | `draft` or `ready for review` with explicit assumptions/risks |
| Discovery-gated | `discovery-gated` |
| Blocked | `blocked` |

Use `validated` (or `conditionally validated` with accepted non-blocker risks) only after `plan-reviewer` approval or explicit user acceptance. When `blocked` or `discovery-gated`, do not emit a ready-to-execute plan — populate template §4 (**Blocking questions** / **Discovery items to inspect**) and emit:

```markdown
Planning Blocker Summary:
- Readiness: blocked | discovery-gated
- Missing input or decision:
- Why planning cannot proceed safely:
- Recommended next step: ask user | inspect codebase | return to research-guide | narrow scope
- Useful draft scope, if any:
```

### 3. Inspect context, choose strategy, and reconcile test design

1. **Inspect project context:** read relevant modules, interfaces, data models, configs, and existing test/build commands before designing tasks.
2. **Choose strategy (§5):** state the recommended approach, rejected alternatives, module/interface boundaries, migration/rollout notes, and per-task test discipline (`mandatory` via [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md) when requested or warranted by risk; `verification-led` with a concrete verification command/expected result; `n/a` justified for non-code/check-only tasks — never downgrade explicit user-requested TDD). Ask before finalizing if viable approaches differ materially in cost, risk, or compatibility.
3. **Design tests and reconcile (§6):** map every must-have requirement to at least one planned failing test or verification check (file path, scenario, expected red-phase failure, fixtures) and reconcile §6 with task boundaries before finalizing §7.

### 4. Decompose tasks and select execution mode

Populate `pg-NNN` tasks and verification/risk matrices (§7–§10) using [references/implementation-plan-template.md](references/implementation-plan-template.md). Size tasks for independent implementation and verification; group independent tasks into `parallel` waves only when write paths are strictly disjoint, marking shared-file or ordered work `sequential` or `integration`.

**Staged-mode recommendation (§10):** Recommend `Execution mode: staged` (grouping `pg-NNN` tasks into independently verifiable, committable stages in §10 `Stage breakdown`, with between-stage `plan-reviewer` exit reviews and a final cumulative deep review) when planning depth is `rigorous`, task count is **> 5** (default threshold), or the user requests per-stage commits; otherwise default to `Execution mode: linear`. Never recommend staged mode for a plan that decomposes to a single stage — keep linear mode unless the user explicitly overrides at the plan gate (record any override and rationale).

### 5. Write, self-check, and gate

- **Artifact path:** write to the orchestrator-assigned path (e.g. `.agents/workflow/<slug>/20-implementation-plan.md`) when orchestrated, or `.agents/plans/<feature-or-topic-slug>.md` standalone (never the repo root).
- **Self-check:** run [references/plan-quality-checklist.md](references/plan-quality-checklist.md) and fix gaps or downgrade status before handoff.
- **Plan gate:** end every complete plan or repair pass (unless the user asked for the raw artifact only) with:

```markdown
Plan gate: choose one:
1. review: send this plan to [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) before execution
2. iterate: revise the plan on [specific scope, finding, or task area]
3. finalize: accept this plan at the stated readiness level
4. execute: hand off to [../plan-executor/SKILL.md](../plan-executor/SKILL.md) after plan-reviewer validation or explicit user acceptance of a conditionally validated plan
5. block: stop planning until [specific missing input or decision] is resolved
```

When staged mode is recommended, insert `5. execute (staged): hand off to plan-executor in staged mode (per-stage implement→audit→review→commit loop)` and renumber `block` to `6`. Offer `execute` only when the plan is `validated`, or `conditionally validated` with explicitly accepted risks.
