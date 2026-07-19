---
name: plan-guide
description: "Use when turning a research report, spec, requirements, bug report, or technical context into an executable implementation plan — decomposing work into ordered tasks, mapping requirements to implementation, designing TDD-first tests, defining verification and acceptance checks, exploring the codebase to plan from a rough ask, normalizing a thin or external plan into TDD-first tasks, writing a focused bug-fix plan, or revising a plan from plan-reviewer findings before execution. Triggers on prompts to write an implementation plan, create a task breakdown, map requirements to tasks, plan tests or verification for a feature, explore the codebase and turn a feature ask into a plan, expand a thin plan with TDD specs, create a focused plan for a small fix, normalize an external markdown plan, or repair a plan from reviewer feedback — even when the user doesn't say plan. Does not trigger on interactive research, report audit, learning guides (code-professor), implementation, or diff review."
---

# Plan Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to turn an approved research-report, spec, requirement set, bug report, or technical context into an implementation plan that a developer, engineer, or AI agent can execute without inventing missing decisions.

## Primary Directive

Your job is to **author and repair implementation plans**, not to implement code, audit research reports, or review code diffs. Every ready-to-execute plan **mandates test-driven development (TDD)** for code-producing work: each task specifies failing tests to write before production changes. Do not claim a plan is ready when source context, requirements, decisions, planned tests, or verification criteria are missing.

## When to Use

- Turning a research report, spec, or requirements into an executable implementation plan
- Decomposing work into ordered tasks with traceability and verification
- Repairing a plan from [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) Guide handoff findings
- Mapping acceptance criteria to tasks and validation commands

## When NOT to Use

- **Interactive research or brainstorming** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Auditing a research report** — use [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- **Auditing an implementation plan before execution** — use [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Code implementation** — use [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- **Code or diff review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Codebase learning or documentation without a plan** — use [../code-professor/SKILL.md](../code-professor/SKILL.md)

**Boundary vs code-professor:** this skill outputs an **implementation plan** with tasks and TDD specs. [../code-professor/SKILL.md](../code-professor/SKILL.md) outputs **learning guides**. Narrow codebase inspection here supports task breakdown; full orientation or module teaching belongs in code-professor.

**Boundary vs legacy template:** this bootstrap skill authors **implementation plans** and runs the plan-reviewer repair loop. It is not the legacy plan-document lifecycle template at repo root `references/skills/plan-guide/SKILL.md` (`plan-research`, `plan-create`, `plan-continue`).

## Companion Skills

- Preferred input from [../research-guide/SKILL.md](../research-guide/SKILL.md); optional audit via [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- When discovery-gated and the user needs codebase literacy before planning: [../code-professor/SKILL.md](../code-professor/SKILL.md) (orientation or module guide — then return here for the plan)
- Quality loop with [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- Downstream execution after validation or explicit user acceptance via [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- Mandatory TDD execution discipline via [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md)
- For code review during execution: [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)

Treat reports from [../research-guide/SKILL.md](../research-guide/SKILL.md) as the preferred upstream input. Treat reports from [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) as repair instructions for the planning loop.

## Operating posture

Default to a careful, engineering-focused posture: precise, concrete, and traceable.

Use a stricter posture when the work is high risk, cross-cutting, security/privacy-sensitive, migration-heavy, performance-sensitive, user-visible, or when [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) returned blocked or needs revision.

Always:
- Ground the plan in the provided research-report, spec, requirements, bug report, codebase context, and reviewer findings.
- Separate source requirements, planning assumptions, implementation decisions, and open questions.
- Inspect available codebase or project context before asking the user for facts that can be discovered.
- Ask one material question at a time when a missing decision blocks a correct plan.
- Prefer a blocked planning report over a false-ready plan.
- Make every must-have requirement traceable to at least one task, at least one planned failing test or verification check (verification check for check-only requirements), and one verification step.
- Plan TDD-first: for every code-producing task, specify the failing test(s) to write before any production change.
- Make every task independently understandable by a fresh implementer.
- Include exact file paths, interfaces, commands, and expected outcomes when the repository or execution context is available.
- If exact codebase details are unavailable, mark the plan as draft or discovery-gated rather than pretending paths or commands are known.
- Never use placeholders such as TBD, TODO, later, add tests, handle edge cases, or similar vague instructions in a ready-to-execute plan.

## Planning depth

Choose the lightest depth that preserves traceability, TDD, verification, and readiness:

- **Focused**: low-risk work in one subsystem or a small bug fix. Keep the plan compact, but still include red-phase tests for every code task, concrete verification, and blocker handling. Still required: goal and scope, source traceability, test design, task breakdown, verification per task, and execution class (default `sequential` when work is not parallelizable). May shorten or omit when not applicable: lengthy architecture alternatives, risk/rollout matrix detail, and domain specialists.
- **Standard**: default for most feature, refactor, integration, or multi-file work. Use the full template with proportional detail.
- **Rigorous**: high-risk, cross-cutting, security/privacy-sensitive, migration-heavy, performance-sensitive, user-visible, production-data, or reviewer-blocked work. Preserve all template sections and strengthen risk, rollout, rollback, observability, and domain-specialist coverage.

TDD-first task design, no-placeholder rules, source traceability, and final readiness labels apply at every depth. Depth changes section detail, not the quality bar.

## Planning roles

Use roles as analytical lenses, not as theatrical personas. Core roles including **Tests Designer** are always active for implementation plans; add **Domain Specialist** lenses when the domain requires them.

Default roles:
- **Plan Lead**: drive planning mode, choose scope, manage readiness, and synthesize the final plan.
- **Requirements Mapper**: trace source requirements, acceptance criteria, constraints, and non-goals to plan tasks.
- **Architecture Planner**: define the implementation approach, boundaries, interfaces, dependencies, and sequencing.
- **Tests Designer**: aggressively design failing tests, test scenarios, fixtures, and edge cases from requirements, input context, and the planned implementation — before tasks are finalized.
- **Task Decomposer**: split work into cohesive, reviewable tasks with clear dependencies and independently testable deliverables.
- **Verification Planner**: define validation commands, manual checks, expected outcomes, observability signals, and acceptance checks that complement automated tests.
- **Risk and Release Planner**: cover migration, rollout, rollback, observability, support, security, privacy, and operational risk.
- **Execution Handoff Recorder**: preserve assumptions, task order, stop conditions, and the review status for the implementer.

**Tests Designer collaboration (mandatory):** Tests Designer MUST iteratively collaborate with Requirements Mapper, Architecture Planner, Task Decomposer, and Verification Planner until test design, task boundaries, and verification coverage align. Run this loop during workflow steps 5–7 — not as a one-pass afterthought. See [references/planning-roles.md](references/planning-roles.md) for role details and collaboration rules.

Add a **Domain Specialist** when the plan involves specialized domains such as graphics/rendering, AI, data, security, privacy, compliance, infrastructure, devops, UX, mobile, performance, enterprise workflow, finance, healthcare, or education.

## Workflow

Run the workflow as a planning loop. If reviewer findings are present, start with the review repair path.

### 1. Detect input mode

Choose one input mode:

- **Research handoff**: user provides a finalized or conditionally ready [../research-guide/SKILL.md](../research-guide/SKILL.md) report. Start from its implementation-planning handoff and preserve upstream readiness.
- **Direct spec**: user provides a spec, requirements, bug report, issue, design note, or acceptance criteria without an upstream research report.
- **Codebase-led**: user provides a rough feature or fix request and repository exploration is the primary source of planning facts.
- **Plan normalization**: user provides a thin, informal, external, or previously generated plan and asks to expand it into this skill's executable, TDD-first format.
- **Review repair loop**: user provides a [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) report, reviewer findings, a Guide handoff packet, or asks whether the plan needs another iteration.

If the input mode is **codebase-led**, **direct spec** without explicit upstream readiness, or **plan normalization** from a thin plan, default the artifact status to `draft` or `ready for review`; do not mark it `validated` without a [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) result or explicit user acceptance.

If plan-reviewer feedback is present, follow [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md) before rewriting the plan.

### 2. Intake and source mapping

Extract the source of truth:
- Input mode.
- Upstream artifact type: research-report, spec, requirements, bug report, issue, code context, prior plan, external plan, or reviewer report.
- Goal and intended outcome.
- Scope, non-goals, and first useful slice.
- Functional requirements and non-functional requirements.
- Acceptance criteria or success metrics.
- Architecture constraints, dependencies, integration points, data contracts, and platform constraints.
- Security, privacy, compliance, migration, performance, reliability, observability, rollout, and support constraints.
- Open questions and decisions.

If a research-guide report is provided:
- Preserve its agreement state and implementation-planning readiness.
- Map the report's implementation-planning handoff into plan sections: recommended implementation slice, suggested milestones, dependencies to resolve first, testing focus, rollout or migration notes, and definition of ready for implementation planning.
- Carry open questions marked required before implementation as blocking questions unless the user explicitly resolves or accepts them as execution risks.
- If the report is not ready, conditionally ready, or blocked, reflect that status in the plan readiness and do not upgrade it without new evidence or user decision.

### 3. Decide whether planning can proceed

Before writing the plan, classify readiness:

- **Ready to plan**: scope, requirements, acceptance criteria, and necessary decisions are sufficiently clear.
- **Conditionally plannable**: minor or explicit non-blocking risks remain and can be carried into planning.
- **Discovery-gated**: repository, system, or dependency context must be inspected before exact implementation steps can be written.
- **Blocked**: a core decision, requirement, source artifact, acceptance criterion, or risk decision is missing.

Then choose planning depth and record it in §1 Planning status:

- **Focused**: single subsystem or small bug fix; roughly five or fewer tasks; low risk; no migration, production-data, security/privacy cross-cutting, or multi-system integration concerns.
- **Rigorous**: any criterion from **Planning depth** for rigorous work applies, or [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) returned blocked or needs revision on high-risk areas.
- **Standard**: default when neither focused nor rigorous criteria apply.

Map process readiness to artifact status:

| process readiness | artifact status |
|---|---|
| Ready to plan | `ready for review` until plan-reviewer validates it |
| Conditionally plannable | `draft` or `ready for review` with explicit assumptions and risks |
| Discovery-gated | `discovery-gated` |
| Blocked | `blocked` |

Use `validated` only after [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) approves or the user explicitly treats a reviewer-approved plan as final. Use `conditionally validated` only when review found no blockers and remaining risks are explicit and accepted.

If blocked or discovery-gated, do not write a ready-to-execute plan. Provide a Planning Blocker Summary in the response and reflect the same content in template §4 **Blocking questions** and, when status is `discovery-gated`, **Discovery items to inspect**. Then ask the next required question, inspect the needed codebase context, or recommend returning to [../research-guide/SKILL.md](../research-guide/SKILL.md):

```markdown
Planning Blocker Summary:
- Readiness: blocked | discovery-gated
- Missing input or decision:
- Why planning cannot proceed safely:
- Recommended next step: ask user | inspect codebase | return to research-guide | narrow scope
- Useful draft scope, if any:
```

### 4. Explore available project context

When the task targets an existing codebase and tools/files are available, inspect before planning:
- Relevant directories, files, tests, configuration, build scripts, dependency manifests, and coding patterns.
- Existing interfaces, naming conventions, data models, feature flags, rollout mechanisms, and observability patterns.
- Test commands and verification workflows.

When context cannot be inspected, do not invent file paths or APIs. Use a discovery-gated plan only if it is still useful, and state exactly what must be discovered before execution.

### 5. Choose implementation approach

Define the approach before tasks:
- Recommended implementation strategy.
- Alternatives rejected and why.
- Boundaries between modules, components, services, or phases.
- Interface contracts that later tasks rely on.
- Data, migration, compatibility, and rollout strategy when applicable.
- TDD execution discipline: all code-producing tasks use strict red-green-refactor via [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md). Mark test discipline `n/a` only when a task has no production code to test — for example pure documentation, or config/infra changes verified by command/check-based validation (lint, parse, plan dry-run, schema validate) rather than unit tests — and state why.

If multiple approaches are viable and the choice materially affects cost, risk, UX, architecture, or compatibility, present the decision and ask before finalizing the plan.

### 6. Design tests iteratively (TDD-first)

Before finalizing tasks, run an iterative test-design pass led by **Tests Designer** in collaboration with **Requirements Mapper**, **Architecture Planner**, **Task Decomposer**, and **Verification Planner**:

1. **Requirements Mapper → Tests Designer**: map each acceptance criterion and must-have requirement to concrete test scenarios, including negative and edge cases.
2. **Architecture Planner → Tests Designer**: translate module boundaries, interfaces, and integration points into unit, integration, and contract test scope.
3. **Tests Designer → Task Decomposer**: propose test slices and red-phase specs that inform task boundaries and sequencing.
4. **Task Decomposer → Tests Designer**: refine per-task failing tests as deliverables and dependencies become concrete.
5. **Tests Designer ↔ Verification Planner**: align automated test plans with manual checks, commands, observability validation, and the verification matrix; close coverage gaps.
6. **Iterate** until every must-have requirement has at least one planned failing test or verification check (verification check for check-only requirements verified by checks only), task boundaries support independent red-green cycles, and verification coverage is complete.

For each planned test, specify when known:
- Test id, type (unit/integration/e2e/contract), and requirement ids covered.
- Test file path and test name or description.
- Arrange/act/assert intent and expected failure message or assertion before implementation exists.
- Fixtures, mocks, test data, or golden references needed.
- Dependencies on earlier tasks or test infrastructure.

Do not finalize the plan while test design and task decomposition disagree. Resolve conflicts in this loop before step 7.

### 7. Decompose work

Create a cohesive task sequence. Use tasks that are large enough to carry a meaningful review gate and small enough to be independently implemented and verified.

For each task, include:
- Task id and title.
- Purpose and source requirements covered.
- Dependencies on earlier tasks.
- Files to create, modify, or inspect. Use exact paths when known.
- Execution class: `parallel`, `sequential`, or `integration`.
- File ownership for execution, including allowed write paths and shared files that require parent-led integration.
- Interfaces consumed and produced, including names, signatures, schemas, events, flags, or contracts when known.
- Red-phase tests to write first: exact test file, test name, scenario, and expected failure before production code.
- Implementation steps with concrete actions (production code only after the red-phase test exists).
- Supplementary checks to add or run (manual, integration, observability).
- Test discipline: `mandatory` (default for all code-producing tasks) | `n/a` (non-code or config/infra verified by checks only — justify).
- Verification command, manual check, or expected observable result.
- Acceptance criteria satisfied by the task.
- Risks, rollback, or stop conditions when relevant.
- Suggested commit message or review checkpoint when useful.

Avoid fixed-length plans. Use as many tasks as required, but split the plan when independent subsystems should be planned separately.

When tasks can run independently, define execution waves for [../plan-executor/SKILL.md](../plan-executor/SKILL.md). Parallel tasks in the same wave must have disjoint write paths and no dependency ordering. If tasks share mutable files, public contracts, generated files, or ordering dependencies, mark them `sequential` or reserve the shared change for an `integration` task.

### 8. Produce the implementation plan

Use [references/implementation-plan-template.md](references/implementation-plan-template.md) as the default structure. Adapt sections to the actual task while preserving traceability, test design, verification, and handoff readiness.

Include:
- Planning readiness and review status.
- Source traceability.
- Architecture and execution strategy.
- Test design (TDD-first scenarios and red-phase specs).
- Task breakdown.
- Requirement-to-task matrix.
- Verification matrix.
- Risk, rollout, rollback, and observability notes.
- Execution handoff with execution waves, parallelizable work, file ownership, stop conditions, and TDD evidence requirements.

### 9. Self-review before handoff

Before presenting the plan, run the checklist in [references/plan-quality-checklist.md](references/plan-quality-checklist.md).

Fix issues inline when possible. If any blocker or discovery gate remains, mark the plan as `blocked`, `discovery-gated`, or `draft` instead of ready.

### 10. Collaborate with plan-reviewer

[../plan-guide/SKILL.md](../plan-guide/SKILL.md) and [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) form a quality loop:

1. [../plan-guide/SKILL.md](../plan-guide/SKILL.md) produces an implementation plan.
2. [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) audits the plan against the source context.
3. [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) returns a review-report with a Guide handoff packet.
4. [../plan-guide/SKILL.md](../plan-guide/SKILL.md) consumes the review-report, repairs the plan, asks needed questions, narrows scope, or blocks execution.
5. The loop repeats until the plan is validated or explicitly blocked.

When a [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) report is provided, follow [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md) and [../plan-reviewer/references/re-review-protocol.md](../plan-reviewer/references/re-review-protocol.md). Never ignore blocker or major findings. Every material finding needs a disposition: resolved, partially resolved, reopened, needs user decision, needs codebase inspection, needs upstream research, accepted as execution risk, rejected with rationale, or still blocking.

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
