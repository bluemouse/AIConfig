# Validation Rubric

Use this rubric to assign severity, verdict, confidence, and execution readiness.

## Severity levels

| severity | meaning | execution impact | examples |
|---|---|---|---|
| Blocker | Execution would be unsafe, impossible, or likely to build the wrong thing. | Do not execute. | Missing source requirements, unresolved core decision, critical tasks vague, no verification for critical behavior, code task with no red-phase test plan, destructive migration without rollback, plan contradicts spec. |
| Major | Execution can start only with risky invention or significant clarification. | Revise before execution or accept explicitly as execution risk if narrow. | Missing file/interface details in known codebase, weak task sequencing, incomplete tests for core flow, missing Test design section for plan-guide plans, must-have requirement without planned failing test or verification check, unsupported architecture assumption, missing migration step. |
| Minor | Plan is mostly executable but should improve clarity or coverage. | Can often be fixed before or during implementation. | Manual check could be more precise, low-risk edge case lacks owner, non-critical command lacks expected output. |
| Question | Reviewer needs clarification before assigning severity. | May become major or blocker. | Ambiguous source requirement, uncertain repository pattern, unclear owner of rollout decision. |
| Nit | Editorial or formatting issue with no execution impact. | Does not affect readiness. | Minor wording, duplicate section, inconsistent heading. |

## Verdict rules

| verdict | required conditions |
|---|---|
| Validated | No blocker or major findings. Plan is executable with ordinary implementation judgment. |
| Conditionally validated | No blocker findings. Remaining major risks are explicit, narrow, and accepted or acceptably deferrable. |
| Needs revision | One or more major findings prevent reliable execution, but targeted fixes can make the plan executable. |
| Blocked | One or more blocker findings make execution unsafe, misleading, or impossible. |

Never assign Validated when any of these are absent or contradictory:
- Goal and scope.
- Source traceability for must-have requirements.
- Task breakdown with dependencies.
- Concrete implementation steps.
- Verification for critical behavior.
- TDD test design for code-producing tasks from [../../plan-guide/SKILL.md](../../plan-guide/SKILL.md): Test design section, red-phase specs, and `mandatory` test discipline (or justified `n/a`).
- Risk/rollback handling for high-risk changes.
- Blocking questions resolved or clearly marked as blocking.
- Prior reviewer blockers resolved.

## Confidence levels

| confidence | use when |
|---|---|
| High | Plan and source context are available; findings are grounded in explicit content. |
| Medium | Plan is reviewable but some source, repository, or domain context is missing. |
| Low | Review depends heavily on inferred context or missing source artifacts. |

## Audit categories

### Source alignment

Check:
- Must-have requirements are mapped to tasks, planned failing tests or verification checks, and verification.
- Non-goals are preserved.
- Scope additions are called out.
- Plan does not contradict source decisions or research readiness.
- Bugs have a plausible root-cause path or discovery step.

### Plan completeness

Check:
- Goal, scope, assumptions, and first executable slice are clear.
- Architecture and implementation strategy exist before tasks.
- Dependencies, interfaces, data, migration, rollout, rollback, observability, security, privacy, and support are covered when relevant.

### Task quality

Check:
- Tasks are coherent and independently reviewable.
- Task dependencies are valid.
- Task outputs are consumed consistently later.
- File paths, interfaces, commands, and expected outcomes are exact when known.
- Unknown repository facts are not invented.

### Test design quality

Applies to plans authored by [../../plan-guide/SKILL.md](../../plan-guide/SKILL.md) or claiming TDD-first readiness.

Check:
- Test design section exists with test ids, scenarios, and red-phase expected failures when repository context allows.
- Tests Designer collaboration with Requirements Mapper, Architecture Planner, Task Decomposer, and Verification Planner is reflected — not implied.
- Every must-have requirement maps to at least one planned failing test or verification check and at least one verification step.
- Code-producing tasks list red-phase tests before production implementation steps.
- Test discipline is `mandatory` for code tasks; `n/a` only for non-code or check-only config/infra tasks with justification.
- No vague placeholders such as “add tests” or “handle edge cases” without exact test content.
- Task boundaries support independent red-green-refactor cycles.

### Verification quality

Check:
- Acceptance criteria are testable.
- Verification matrix covers source requirements, planned tests (§6 test ids), and high-risk tasks.
- Commands/checks have expected results.
- Manual checks are reproducible.
- Regression, integration, performance, security, accessibility, migration, and observability checks are included where relevant.

### Execution handoff quality

Check:
- Implementer can execute without reading the entire conversation.
- Stop conditions are explicit.
- Required evidence collection is clear.
- Review checkpoints are sensible.
- Parallelizable and critical-path work are identified when useful.

## Finding format

Every material finding should include:
- id: pr-001, pr-002, etc.
- severity
- affected section/task/source item
- issue
- why it matters for execution
- required fix
- recommended `plan-guide` action
- owner suggestion when useful
