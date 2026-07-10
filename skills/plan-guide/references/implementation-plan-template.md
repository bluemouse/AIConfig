# Implementation Plan Template

Use this structure for a plan that should be executable by a developer, engineer, or AI agent. Adapt section depth to scope, but do not omit traceability, task details, verification, and readiness.

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
| source id / section | requirement, decision, or constraint | plan coverage | verification coverage |
|---|---|---|---|
|  |  | task ids | test/check ids |

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
- Alternatives rejected:

## 6. Work breakdown

### Task pg-001: [Concrete task title]
- Purpose:
- Source requirements covered:
- Depends on:
- Files to create:
- Files to modify:
- Interfaces consumed:
- Interfaces produced:
- Implementation steps:
  1. [Concrete action.]
  2. [Concrete action.]
- Tests/checks:
  - [Exact test/check to add or run when known.]
- Verification:
  - Command/check: `[exact command or manual check]`
  - Expected result: [observable result]
- Acceptance criteria satisfied:
- Risks and rollback:
- Stop conditions:
- Suggested commit/review checkpoint:

[Repeat tasks with stable ids.]

## 7. Verification matrix
| id | type | command or check | expected result | covers |
|---|---|---|---|---|
| v-001 | unit/integration/e2e/manual/performance/security/observability |  |  | requirement/task ids |

## 8. Risk, rollout, and rollback
| risk | likelihood | impact | mitigation | rollback or fallback | owner/phase |
|---|---|---|---|---|---|
|  | high/medium/low | high/medium/low |  |  |  |

## 9. Execution handoff
- Recommended execution order:
- Parallelizable work:
- Critical path:
- Required preflight checks:
- Stop conditions:
- Evidence the implementer must collect:
- Review checkpoints:
- Post-implementation validation:

## 10. Reviewer feedback status
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
