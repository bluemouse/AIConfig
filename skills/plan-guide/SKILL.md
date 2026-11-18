---
name: plan-guide
description: "Use when turning a research report, spec, requirements, bug report, or technical context into an executable implementation plan — decomposing work into ordered tasks, mapping requirements to implementation, designing TDD-first tests, defining verification and acceptance checks, exploring the codebase to plan from a rough ask, normalizing a thin or external plan into TDD-first tasks, writing a focused bug-fix plan, or revising a plan from plan-reviewer findings before execution. Triggers on prompts to write an implementation plan, create a task breakdown, map requirements to tasks, plan tests or verification for a feature, explore the codebase and turn a feature ask into a plan, expand a thin plan with TDD specs, create a focused plan for a small fix, normalize an external markdown plan, or repair a plan from reviewer feedback — even when the user doesn't say plan. Does not trigger on interactive research, report audit, learning guides (code-professor), implementation, or diff review."
---

# Plan Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to turn an approved research-report, spec, requirement set, bug report, or technical context into an implementation plan that a developer, engineer, or AI agent can execute without inventing missing decisions.

## Primary Directive

Your job is to **author and repair implementation plans**, not to implement code, audit research reports, or review code diffs. Every ready-to-execute plan gives each task concrete verification: strict test-driven development (TDD) with failing tests written before production changes when the requirement, the plan, or the task's risk profile calls for it, and a stated alternative verification strategy otherwise. Do not claim a plan is ready when source context, requirements, decisions, planned tests, or verification criteria are missing.

## When to Use

- Turning a research report, spec, or requirements into an executable implementation plan
- Decomposing work into ordered tasks with traceability and verification
- Repairing a plan from plan-reviewer Guide handoff findings
- Mapping acceptance criteria to tasks and validation commands

## When NOT to Use

- **Interactive research or brainstorming** — use research-guide
- **Auditing a research report** — use research-reviewer
- **Auditing an implementation plan before execution** — use plan-reviewer
- **Code implementation** — use plan-executor
- **Code or diff review** — use code-reviewer
- **Codebase learning or documentation without a plan** — use code-professor

**Boundary vs code-professor:** this skill outputs an **implementation plan** with tasks and TDD specs; code-professor outputs **learning guides**. Narrow codebase inspection here supports task breakdown; full orientation or module teaching belongs in code-professor.

## Companion Skills

- Preferred upstream input from research-guide; optional report audit via research-reviewer; quality loop with [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md); downstream execution via plan-executor; TDD discipline via test-driven-dev-guide; diff review during execution via code-reviewer.
- When the source spec or request is **ambiguous** rather than merely incomplete — conflicting requirements, undefined terms, or several plausible readings — settle it with prompt-clarifier before planning. Planning blockers on otherwise-settled requirements stay here, at this skill's one-question-at-a-time pacing.
- When discovery-gated and the user needs codebase literacy before planning: code-professor (orientation or module guide — then return here for the plan).

## Operating posture

Default to a careful, engineering-focused posture: precise, concrete, and traceable.

Use a stricter posture when the work is high risk, cross-cutting, security/privacy-sensitive, migration-heavy, performance-sensitive, user-visible, or when plan-reviewer returned blocked or needs revision.

Always:
- Ground the plan in the provided research-report, spec, requirements, bug report, codebase context, and reviewer findings.
- Separate source requirements, planning assumptions, implementation decisions, and open questions.
- Inspect available codebase or project context before asking the user for facts that can be discovered.
- Ask one material question at a time when a missing decision blocks a correct plan.
- Prefer a blocked planning report over a false-ready plan.
- Make every must-have requirement traceable to at least one task, at least one planned failing test or verification check (verification check for check-only requirements), and one verification step.
- Plan verification concretely: for every code-producing task, specify the failing test(s) to write before any production change when its discipline is `mandatory`, or the stated alternative verification when it is `verification-led`.
- Make every task independently understandable by a fresh implementer.
- Include exact file paths, interfaces, commands, and expected outcomes when the repository or execution context is available.
- If exact codebase details are unavailable, mark the plan as draft or discovery-gated rather than pretending paths or commands are known.
- Never use placeholders such as TBD, TODO, later, add tests, handle edge cases, or similar vague instructions in a ready-to-execute plan.

## Planning depth

Choose the lightest depth that preserves traceability, verification, and readiness:

- **Focused**: low-risk work in one subsystem or a small bug fix — roughly five or fewer tasks, no migration, production-data, security/privacy cross-cutting, or multi-system integration concerns. Keep the plan compact, but still include concrete verification for every task (red-phase tests where the task's discipline is `mandatory`), and blocker handling. Still required: goal and scope, source traceability, test design, task breakdown, verification per task, and execution class (default `sequential` when work is not parallelizable); lengthy architecture alternatives, risk/rollout matrix detail, and domain specialists may be shortened or omitted.
- **Standard**: default for most feature, refactor, integration, or multi-file work. Use the full template with proportional detail.
- **Rigorous**: high-risk, cross-cutting, security/privacy-sensitive, migration-heavy, performance-sensitive, user-visible, production-data, or reviewer-blocked work. Preserve all template sections and strengthen risk, rollout, rollback, observability, and domain-specialist coverage.

Depth changes section detail, not the quality bar.

## Workflow

Run the workflow as a planning loop. If reviewer findings are present, start with the review repair path.

### 1. Detect input mode

Choose one input mode:

- **Research handoff**: user provides a finalized or conditionally ready research-guide report. Start from its implementation-planning handoff and preserve upstream readiness.
- **Direct spec**: user provides a spec, requirements, bug report, issue, design note, or acceptance criteria without an upstream research report.
- **Codebase-led**: user provides a rough feature or fix request and repository exploration is the primary source of planning facts.
- **Plan normalization**: user provides a thin, informal, external, or previously generated plan and asks to expand it into this skill's executable format.
- **Review repair loop**: user provides a plan-reviewer report, reviewer findings, a Guide handoff packet, or asks whether the plan needs another iteration.

If the input mode is **codebase-led**, **direct spec** without explicit upstream readiness, or **plan normalization** from a thin plan, default the artifact status to `draft` or `ready for review`; do not mark it `validated` without a plan-reviewer result or explicit user acceptance. If plan-reviewer feedback is present, follow [../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md](../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md) before rewriting the plan.

### 2. Intake and source mapping

Extract the source of truth:
- Input mode and upstream artifact type: research-report, spec, requirements, bug report, issue, code context, prior plan, external plan, or reviewer report.
- Goal, intended outcome, scope, non-goals, and first useful slice.
- Functional and non-functional requirements, acceptance criteria or success metrics.
- Architecture constraints, dependencies, integration points, data contracts, and platform constraints.
- Security, privacy, compliance, migration, performance, reliability, observability, rollout, and support constraints.
- Open questions and decisions.

If a research-guide report is provided, preserve its agreement state and implementation-planning readiness; map its handoff (recommended implementation slice, suggested milestones, dependencies to resolve first, testing focus, rollout or migration notes, definition of ready) into plan sections; carry open questions marked required before implementation as blocking questions unless the user explicitly resolves or accepts them as execution risks; and if the report is not ready, conditionally ready, or blocked, reflect that status in the plan readiness without upgrading it absent new evidence or user decision.

### 3. Decide whether planning can proceed

Before writing the plan, classify readiness:

- **Ready to plan**: scope, requirements, acceptance criteria, and necessary decisions are sufficiently clear.
- **Conditionally plannable**: minor or explicit non-blocking risks remain and can be carried into planning.
- **Discovery-gated**: repository, system, or dependency context must be inspected before exact implementation steps can be written.
- **Blocked**: a core decision, requirement, source artifact, acceptance criterion, or risk decision is missing.

Then choose planning depth per **Planning depth** above and record it in §1 Planning status.

Map process readiness to artifact status:

| process readiness | artifact status |
|---|---|
| Ready to plan | `ready for review` until plan-reviewer validates it |
| Conditionally plannable | `draft` or `ready for review` with explicit assumptions and risks |
| Discovery-gated | `discovery-gated` |
| Blocked | `blocked` |

Use `validated` only after plan-reviewer approves or the user explicitly treats a reviewer-approved plan as final. Use `conditionally validated` only when review found no blockers and remaining risks are explicit and accepted.

If blocked or discovery-gated, do not write a ready-to-execute plan. Provide a Planning Blocker Summary in the response and reflect the same content in template §4 **Blocking questions** and, when status is `discovery-gated`, **Discovery items to inspect**. Then ask the next required question, inspect the needed codebase context, or recommend returning to research-guide:

```markdown
Planning Blocker Summary:
- Readiness: blocked | discovery-gated
- Missing input or decision:
- Why planning cannot proceed safely:
- Recommended next step: ask user | inspect codebase | return to research-guide | narrow scope
- Useful draft scope, if any:
```

### 4. Explore available project context

When the task targets an existing codebase and tools/files are available, inspect before planning: relevant directories, files, tests, configuration, build scripts, dependency manifests, and coding patterns; existing interfaces, naming conventions, data models, feature flags, rollout mechanisms, and observability patterns; and test commands and verification workflows. When context cannot be inspected, do not invent file paths or APIs. Use a discovery-gated plan only if it is still useful, and state exactly what must be discovered before execution.

### 5. Choose implementation approach

Define the approach before tasks:
- Recommended implementation strategy.
- Alternatives rejected and why.
- Boundaries between modules, components, services, or phases.
- Interface contracts that later tasks rely on.
- Data, migration, compatibility, and rollout strategy when applicable.
- Test discipline: strict red-green-refactor via [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md) when the user explicitly requests TDD or the task's risk profile calls for it; `verification-led` for other code tasks with a stated alternative verification strategy (fixture-gated check, schema conformance, build+run evidence); `n/a` only when a task has no production code to test — for example pure documentation, or config/infra changes verified by command/check-based validation (lint, parse, plan dry-run, schema validate) — and state why. Explicit user-requested TDD is never downgraded.

If multiple approaches are viable and the choice materially affects cost, risk, UX, architecture, or compatibility, present the decision and ask before finalizing the plan.

### 6. Design tests and verification iteratively

Design tests and verification from the requirements, interfaces, and the planned decomposition, iterating with steps 5–7 until **every must-have requirement has at least one planned failing test or verification check** (check-only requirements by verification check), task boundaries support independent red-green cycles, and verification coverage is complete. For each planned test, specify when known: test id, type, requirement ids covered, test file path and name, arrange/act/assert intent with the expected failure message before implementation exists, fixtures/mocks/test data needed, and dependencies on earlier tasks or test infrastructure.

Do not finalize the plan while test design and task decomposition disagree. Resolve conflicts in this loop before step 7.

### 7. Decompose work

Create a cohesive task sequence. Use tasks that are large enough to carry a meaningful review gate and small enough to be independently implemented and verified. Populate each task with the full field set defined in [references/implementation-plan-template.md](references/implementation-plan-template.md) — task id, source requirements, dependencies, exact file paths, execution class and file ownership, interfaces, red-phase tests, implementation steps, test discipline (`mandatory` default | `n/a` justified), verification command, acceptance criteria, and risks/stop conditions.

Avoid fixed-length plans. Use as many tasks as required, but split the plan when independent subsystems should be planned separately.

When tasks can run independently, define execution waves for plan-executor. Parallel tasks in the same wave must have disjoint write paths and no dependency ordering. If tasks share mutable files, public contracts, generated files, or ordering dependencies, mark them `sequential` or reserve the shared change for an `integration` task.

### 7a. Staged-mode recommendation

After decomposing work into tasks (§7), decide the execution mode. Staged mode groups the `pg-NNN` tasks into ordered, self-contained stages (§10 `Stage breakdown`) — each stage independently verifiable and committable, with plan-reviewer stage-exit review between stages and a final deep code review on the cumulative diff.

Recommend `Execution mode: staged` when planning depth is `rigorous`, the plan has **more than 5** `pg-NNN` tasks (tunable threshold — 5 is the default boundary), or the user requests it (e.g., per-stage commits). Otherwise default to `Execution mode: linear`. Never recommend staged mode for a plan that decomposes to a single stage — that degenerates to linear mode plus a stage-exit review with nothing left to check. The user may still override at the plan gate to force staged semantics. Record any override (in either direction) and the rationale in the plan.

When staged mode is recommended, extend the plan gate (§11): insert `execute (staged)` as option 5 and renumber `block` to option 6:

```markdown
5. execute (staged): hand off to plan-executor in staged mode (per-stage implement→audit→review→commit loop)
6. block: stop planning until [specific missing input or decision] is resolved
```

### 8. Produce the implementation plan

Use [references/implementation-plan-template.md](references/implementation-plan-template.md) as the default structure. Adapt sections to the actual task while preserving traceability, test design, verification, and handoff readiness.

#### Artifact output path

When invoked **outside the dev-workflow-orchestrator** (i.e., no orchestrator assigned an input/output artifact path), write the implementation plan to `.agents/plans/<feature-or-topic-slug>.md`. The `.agents/plans/` directory is gitignored. Do not write planning artifacts to the repository root — it pollutes the working tree and risks accidental commits.

When invoked **inside the orchestrator**, the orchestrator assigns the output path (typically `.agents/workflow/<slug>/20-implementation-plan.md`); use that path instead.

Include planning readiness and review status, source traceability, architecture and execution strategy, test design (red-phase specs for `mandatory` tasks, verification specs for `verification-led`), task breakdown, requirement-to-task and verification matrices, risk/rollout/rollback/observability notes, and an execution handoff with execution waves, parallelizable work, file ownership, stop conditions, and verification evidence requirements.

### 9. Self-review before handoff

Before presenting the plan, run the checklist in [references/plan-quality-checklist.md](references/plan-quality-checklist.md).

Fix issues inline when possible. If any blocker or discovery gate remains, mark the plan as `blocked`, `discovery-gated`, or `draft` instead of ready.

### 10. Collaborate with plan-reviewer

This skill and plan-reviewer form a quality loop: this skill produces an implementation plan, plan-reviewer audits it against the source context and returns a review-report with a Guide handoff packet, and this skill consumes the report — repairing the plan, asking needed questions, narrowing scope, or blocking execution — until the plan is validated or explicitly blocked. When a plan-reviewer report is provided, follow [../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md](../dev-workflow-orchestrator/references/reviewer-core/producer-feedback-loop.md) and [../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md](../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md). Never ignore blocker or major findings. Every material finding needs a disposition: resolved, partially resolved, reopened, needs user decision, needs codebase inspection, needs upstream research, accepted as execution risk, rejected with rationale, or still blocking.

### 11. End with a plan gate

After each complete plan or repair iteration, end with one gate unless the user explicitly requested only the final artifact:

```markdown
Plan gate: choose one:
1. review: send this plan to [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) before execution
2. iterate: revise the plan on [specific scope, finding, or task area]
3. finalize: accept this plan at the stated readiness level
4. execute: hand off to [../plan-executor/SKILL.md](../plan-executor/SKILL.md) after plan-reviewer validation or explicit user acceptance of a conditionally validated plan
5. block: stop planning until [specific missing input or decision] is resolved
```

Offer `execute` only when the plan is `validated`, or `conditionally validated` with explicitly accepted risks. Do not offer `execute` for blocked, discovery-gated, or draft plans. If the plan is not validated by [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md), recommend review before execution. If the user insists on execution with unresolved findings, preserve the risks and stop conditions in the handoff.
