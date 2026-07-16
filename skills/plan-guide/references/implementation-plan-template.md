# Implementation Plan Template

Use this structure for a plan that should be executable by a developer, engineer, or AI agent. Adapt section depth to scope, but do not omit traceability, test design, task details, verification, and readiness.

```markdown
# Implementation Plan: [Feature / Fix / Change Name]

## 1. Planning status
- Status: draft | ready for review | validated | conditionally validated | blocked
- Source artifact(s): [research-report / spec / requirements / bug report / codebase context]
- Upstream readiness: ready | conditionally ready | not ready | unknown
- Latest plan-reviewer status: not reviewed | validated | conditionally validated | needs revision | blocked
- Active planning roles/lenses: [list]
- Execution recommendation: do not execute yet | execute after review | execute with accepted risks | blocked

## 2. Goal and scope
### Goal
[One concise statement of the outcome.]

### In scope
- [Specific included behavior/change.]

### Out of scope
- [Explicit non-goal.]

### First executable slice
[Smallest coherent implementation slice if the full scope is large.]

## 3. Source traceability
| source id / section | requirement, decision, or constraint | plan coverage | test ids (§6) | verification ids (§8) |
|---|---|---|---|---|
|  |  | task ids | t-xxx | v-xxx |

## 4. Assumptions and decisions
### Confirmed decisions
- [Decision and source.]

### Planning assumptions
| assumption | confidence | impact if wrong | validation or mitigation |
|---|---|---|---|
|  | high/medium/low |  |  |

### Blocking questions
- [Only include if status is blocked or draft.]

## 5. Implementation strategy
- Recommended approach:
- Architecture/module boundaries:
- Interfaces and contracts:
- Data model or migration notes:
- Compatibility and rollout approach:
- Observability and support approach:
- TDD execution discipline: mandatory for all code-producing tasks via red-green-refactor
- Alternatives rejected:

## 6. Test design (TDD-first)

| test id | type | requirement ids | test file | test name / scenario | red-phase expected failure | fixtures / notes |
|---|---|---|---|---|---|---|
| t-001 | unit/integration/e2e/contract |  |  |  |  |  |

Collaboration notes: [How Tests Designer aligned with Requirements Mapper, Architecture Planner, Task Decomposer, and Verification Planner.]

## 7. Work breakdown

### Task pg-001: [Concrete task title]
- Purpose:
- Source requirements covered:
- Depends on:
- Files to create:
- Files to modify:
- Interfaces consumed:
- Interfaces produced:
- Implementation steps:
  1. Write failing test(s): [test file, name, scenario — must fail before production code.]
  2. [Minimal production change to pass the test.]
  3. [Refactor or integrate as needed.]
- Red-phase tests (write first):
  - [Exact test file, test name, scenario, expected failure.]
- Supplementary checks:
  - [Manual, integration, or observability check when needed.]
- Test discipline: mandatory | n/a (non-code or config/infra verified by checks only — justify)
- Verification:
  - Command/check: `[exact command or manual check]`
  - Expected result: [observable result]
- Acceptance criteria satisfied:
- Risks and rollback:
- Stop conditions:
- Suggested commit/review checkpoint:

[Repeat tasks with stable ids.]

## 8. Verification matrix
| id | type | command or check | expected result | covers |
|---|---|---|---|---|
| v-001 | unit/integration/e2e/manual/performance/security/observability |  |  | requirement/task ids |

## 9. Risk, rollout, and rollback
| risk | likelihood | impact | mitigation | rollback or fallback | owner/phase |
|---|---|---|---|---|---|
|  | high/medium/low | high/medium/low |  |  |  |

## 10. Execution handoff
- Recommended execution order:
- Parallelizable work:
- Critical path:
- Required preflight checks:
- Stop conditions:
- TDD evidence the implementer must collect: failing test output before production code, passing test after each task
- Review checkpoints:
- Post-implementation validation:

## 11. Reviewer feedback status
[Include when a plan-reviewer report was provided.]
- Latest verdict and confidence:
- Findings resolved:
- Findings accepted as execution risks:
- Findings rejected with rationale:
- Remaining blockers or major issues:
- Re-review recommendation:
```

Rules:
- Replace every bracketed prompt with concrete content or remove the line.
- Do not include placeholders in a ready, validated, or conditionally validated plan.
- Mark missing source context as draft, discovery-gated, or blocked.
- Keep task ids stable across review iterations so reviewer findings remain traceable.
