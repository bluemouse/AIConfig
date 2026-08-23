# Plan Quality Checklist

Run this checklist before presenting an implementation plan or after applying reviewer feedback.

## Source alignment

- Every must-have requirement maps to one or more tasks.
- Every task maps back to a source requirement, decision, bug cause, risk, or implementation necessity.
- Non-goals are not accidentally implemented.
- The plan does not expand scope without calling out the expansion.
- The plan preserves upstream research-guide readiness and unresolved questions.
- Research-guide implementation-planning handoff details are mapped into the plan when available.

## Completeness

- Input mode, planning depth, artifact status, and execution recommendation are stated.
- Goal, scope, non-goals, and first executable slice are explicit.
- Architecture or implementation strategy is stated before task steps.
- Dependencies and sequencing are clear.
- Interfaces, contracts, schemas, flags, or API names are named when known.
- Data, migration, rollout, rollback, observability, security, privacy, and support concerns are addressed when relevant.
- Open questions are classified as blocking or non-blocking.
- Blocked or discovery-gated plans document blockers clearly: either a Planning Blocker Summary in the response, or template §4 **Blocking questions** and, when status is `discovery-gated`, **Discovery items to inspect** filled with concrete content.

## Task quality

- Tasks are cohesive and independently reviewable.
- Each task has a concrete deliverable and verification path.
- Task dependencies do not conflict or reference outputs that are never produced.
- Names, paths, types, commands, and interfaces are consistent across tasks.
- Large independent subsystems are split into separate plans or phases.
- Each task has an execution class: `parallel`, `sequential`, or `integration`.
- Parallel execution waves have disjoint file ownership; shared files are reserved for sequential or integration tasks.

## Precision and no-placeholder scan

Reject or revise the plan if it contains:
- TBD, TODO, later, future work without an owner or gate.
- Add tests, handle edge cases, implement validation, update docs, or similar vague steps without exact content.
- Similar to previous task without repeating the required details.
- File paths, commands, functions, types, or schemas that are invented without inspection or clearly labeled as assumptions in a draft plan.
- A ready status while blocker questions remain.
- A `validated` or `conditionally validated` status without plan-reviewer approval or explicit user acceptance.

## Test design and TDD quality

- TDD is mandatory for every code-producing task: red-phase failing test(s) are specified before production implementation steps.
- Tests Designer collaboration with Requirements Mapper, Architecture Planner, Task Decomposer, and Verification Planner is reflected in the plan — not implied.
- Every must-have requirement maps to at least one planned failing test or verification check and at least one verification step.
- Planned tests name test file paths, test identifiers, scenarios, and expected failure or assertion intent when the repository context allows.
- Test discipline is `mandatory` for code tasks; `n/a` appears only for non-code tasks or config/infra tasks verified by command/check-based validation, with explicit justification.
- Task boundaries support independent red-green-refactor cycles per [../../test-driven-dev-guide/SKILL.md](../../test-driven-dev-guide/SKILL.md).
- Edge cases, negative paths, and regression scenarios from the source context are covered in test design — not deferred.

## Verification quality

- Acceptance criteria are testable.
- Verification matrix covers requirements, planned tests, and high-risk tasks.
- Commands include expected outcomes when known.
- Manual checks are specific enough for another person to reproduce.
- Performance, security, accessibility, migration, observability, and rollback checks are included when relevant.

## Review loop readiness

If a `plan-reviewer` report was provided:
- Every blocker and major finding has a disposition.
- No unresolved blocker appears in a plan marked ready, validated, or conditionally validated.
- Major findings accepted as execution risks are explicit and user-accepted.
- The plan includes a reviewer feedback status section.
- A re-review recommendation is stated.

## Final readiness labels

Use:
- **Validated** only after `plan-reviewer` approves or the user explicitly treats a reviewer-approved plan as final.
- **Ready for review** when the plan is complete but has not yet been audited.
- **Conditionally validated** when review found no blockers and remaining risks are explicit and accepted.
- **Draft** when useful planning exists but codebase/source details still need inspection.
- **Discovery-gated** when repository, system, or dependency context must be inspected before exact implementation steps can be written.
- **Blocked** when execution would require inventing core decisions or missing context.
