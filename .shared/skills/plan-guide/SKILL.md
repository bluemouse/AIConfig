---
name: plan-guide
description: "Use when turning a research report, spec, requirements, bug report, or technical context into an executable implementation plan — decomposing work into ordered tasks, mapping requirements to implementation, defining verification and acceptance checks, or revising a plan from plan-reviewer findings before execution. Triggers on prompts to write an implementation plan, create a task breakdown, map requirements to tasks, define verification for a feature, or repair a plan from reviewer feedback — even when the user doesn't say 'plan'. Does not trigger on interactive research, research-report audit, code implementation, or code diff review."
---

# Plan Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to turn an approved research-report, spec, requirement set, bug report, or technical context into an implementation plan that a developer, engineer, or AI agent can execute without inventing missing decisions.

## Primary Directive

Your job is to **author and repair implementation plans**, not to implement code, audit research reports, or review code diffs. Do not claim a plan is ready when source context, requirements, decisions, or verification criteria are missing.

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

**Boundary vs legacy template:** this bootstrap skill authors **implementation plans** and runs the plan-reviewer repair loop. It is not the legacy plan-document lifecycle template at repo root `references/skills/plan-guide/SKILL.md` (`plan-research`, `plan-create`, `plan-continue`).

## Companion Skills

- Preferred input from [../research-guide/SKILL.md](../research-guide/SKILL.md); optional audit via [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- Quality loop with [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
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
- Make every must-have requirement traceable to at least one task and one verification step.
- Make every task independently understandable by a fresh implementer.
- Include exact file paths, interfaces, commands, and expected outcomes when the repository or execution context is available.
- If exact codebase details are unavailable, mark the plan as draft or discovery-gated rather than pretending paths or commands are known.
- Never use placeholders such as TBD, TODO, later, add tests, handle edge cases, or similar vague instructions in a ready-to-execute plan.

## Planning roles

Use roles as analytical lenses, not as theatrical personas. Select the roles needed for the current plan or repair iteration.

Default roles:
- **Plan Lead**: drive planning mode, choose scope, manage readiness, and synthesize the final plan.
- **Requirements Mapper**: trace source requirements, acceptance criteria, constraints, and non-goals to plan tasks.
- **Architecture Planner**: define the implementation approach, boundaries, interfaces, dependencies, and sequencing.
- **Task Decomposer**: split work into cohesive, reviewable tasks with clear dependencies and independently testable deliverables.
- **Verification Planner**: define tests, validation commands, expected outcomes, and acceptance checks.
- **Risk and Release Planner**: cover migration, rollout, rollback, observability, support, security, privacy, and operational risk.
- **Execution Handoff Recorder**: preserve assumptions, task order, stop conditions, and the review status for the implementer.

Add a **Domain Specialist** when the plan involves specialized domains such as graphics/rendering, AI, data, security, privacy, compliance, infrastructure, devops, UX, mobile, performance, enterprise workflow, finance, healthcare, or education. Use [references/planning-roles.md](references/planning-roles.md) for role details.

## Workflow

Run the workflow as a planning loop. If reviewer findings are present, start with the review repair path.

### 1. Detect input mode

Choose one mode:

**New plan**: user provides a research-report, spec, requirements, bug report, issue, design note, codebase context, or rough feature description.

**Review repair loop**: user provides a [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) report, reviewer findings, a Guide handoff packet, or asks whether the plan needs another iteration.

If plan-reviewer feedback is present, follow [references/reviewer-feedback-loop.md](references/reviewer-feedback-loop.md) before rewriting the plan.

### 2. Intake and source mapping

Extract the source of truth:
- Upstream artifact type: research-report, spec, requirements, bug report, issue, code context, prior plan, or reviewer report.
- Goal and intended outcome.
- Scope, non-goals, and first useful slice.
- Functional requirements and non-functional requirements.
- Acceptance criteria or success metrics.
- Architecture constraints, dependencies, integration points, data contracts, and platform constraints.
- Security, privacy, compliance, migration, performance, reliability, observability, rollout, and support constraints.
- Open questions and decisions.

If a research-guide report is provided, preserve its agreement state and implementation-planning readiness. If the report is not ready, conditionally ready, or blocked, reflect that status in the plan readiness.

### 3. Decide whether planning can proceed

Before writing the plan, classify readiness:

- **Ready to plan**: scope, requirements, acceptance criteria, and necessary decisions are sufficiently clear.
- **Conditionally plannable**: minor or explicit non-blocking risks remain and can be carried into planning.
- **Discovery-gated**: repository, system, or dependency context must be inspected before exact implementation steps can be written.
- **Blocked**: a core decision, requirement, source artifact, acceptance criterion, or risk decision is missing.

If blocked, do not write a ready-to-execute plan. Provide a Planning Blocker Summary and ask the next required question or recommend returning to [../research-guide/SKILL.md](../research-guide/SKILL.md).

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
- Testing and validation strategy.
- Test discipline per task: decide whether each task should be built test-first. Mark it `mandatory` (write and observe a failing test before production code), `suggested`, `optional`, or `n/a` (for example non-code or config-only tasks). Default risky, logic-heavy, or bug-fix tasks to `mandatory` so the executor knows to apply strict red-green-refactor via [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md).

If multiple approaches are viable and the choice materially affects cost, risk, UX, architecture, or compatibility, present the decision and ask before finalizing the plan.

### 6. Decompose work

Create a cohesive task sequence. Use tasks that are large enough to carry a meaningful review gate and small enough to be independently implemented and verified.

For each task, include:
- Task id and title.
- Purpose and source requirements covered.
- Dependencies on earlier tasks.
- Files to create, modify, or inspect. Use exact paths when known.
- Interfaces consumed and produced, including names, signatures, schemas, events, flags, or contracts when known.
- Implementation steps with concrete actions.
- Tests or checks to add or run.
- Test discipline: `mandatory` | `suggested` | `optional` | `n/a`.
- Verification command, manual check, or expected observable result.
- Acceptance criteria satisfied by the task.
- Risks, rollback, or stop conditions when relevant.
- Suggested commit message or review checkpoint when useful.

Avoid fixed-length plans. Use as many tasks as required, but split the plan when independent subsystems should be planned separately.

### 7. Produce the implementation plan

Use [references/implementation-plan-template.md](references/implementation-plan-template.md) as the default structure. Adapt sections to the actual task while preserving traceability, verification, and handoff readiness.

Include:
- Planning readiness and review status.
- Source traceability.
- Architecture and execution strategy.
- Task breakdown.
- Requirement-to-task matrix.
- Verification matrix.
- Risk, rollout, rollback, and observability notes.
- Execution handoff with stop conditions.

### 8. Self-review before handoff

Before presenting the plan, run the checklist in [references/plan-quality-checklist.md](references/plan-quality-checklist.md).

Fix issues inline when possible. If any blocker remains, mark the plan as blocked or draft instead of ready.

### 9. Collaborate with plan-reviewer

[../plan-guide/SKILL.md](../plan-guide/SKILL.md) and [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) form a quality loop:

1. [../plan-guide/SKILL.md](../plan-guide/SKILL.md) produces an implementation plan.
2. [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) audits the plan against the source context.
3. [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) returns a review-report with a Guide handoff packet.
4. [../plan-guide/SKILL.md](../plan-guide/SKILL.md) consumes the review-report, repairs the plan, asks needed questions, narrows scope, or blocks execution.
5. The loop repeats until the plan is validated or explicitly blocked.

When a [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) report is provided, never ignore blocker or major findings. Every material finding needs a disposition: resolved, needs user decision, needs codebase inspection, needs upstream research, accepted as execution risk, rejected with rationale, or still blocking.

### 10. End with a plan gate

After each complete plan or repair iteration, end with one gate unless the user explicitly requested only the final artifact:

```markdown
Plan gate: choose one:
1. review: send this plan to [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) before execution
2. iterate: revise the plan on [specific scope, finding, or task area]
3. finalize: accept this plan at the stated readiness level
4. block: stop planning until [specific missing input or decision] is resolved
```

Do not continue into implementation from this skill. If the plan is not validated by [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md), recommend review before execution. If the user insists on execution with unresolved findings, preserve the risks and stop conditions in the handoff.
