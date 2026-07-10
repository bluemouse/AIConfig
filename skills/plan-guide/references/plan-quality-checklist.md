# Plan Quality Checklist

Run this checklist before presenting an implementation plan or after applying reviewer feedback.

## Source alignment

- Every must-have requirement maps to one or more tasks.
- Every task maps back to a source requirement, decision, bug cause, risk, or implementation necessity.
- Non-goals are not accidentally implemented.
- The plan does not expand scope without calling out the expansion.
- The plan preserves upstream research-guide readiness and unresolved questions.

## Completeness

- Goal, scope, non-goals, and first executable slice are explicit.
- Architecture or implementation strategy is stated before task steps.
- Dependencies and sequencing are clear.
- Interfaces, contracts, schemas, flags, or API names are named when known.
- Data, migration, rollout, rollback, observability, security, privacy, and support concerns are addressed when relevant.
- Open questions are classified as blocking or non-blocking.

## Task quality

- Tasks are cohesive and independently reviewable.
- Each task has a concrete deliverable and verification path.
- Task dependencies do not conflict or reference outputs that are never produced.
- Names, paths, types, commands, and interfaces are consistent across tasks.
- Large independent subsystems are split into separate plans or phases.

## Precision and no-placeholder scan

Reject or revise the plan if it contains:
- TBD, TODO, later, future work without an owner or gate.
- Add tests, handle edge cases, implement validation, update docs, or similar vague steps without exact content.
- Similar to previous task without repeating the required details.
- File paths, commands, functions, types, or schemas that are invented without inspection or clearly labeled as assumptions in a draft plan.
- A ready status while blocker questions remain.

## Verification quality

- Acceptance criteria are testable.
- Verification matrix covers requirements and high-risk tasks.
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
- **Blocked** when execution would require inventing core decisions or missing context.
