# Stage-Exit Review Contract

This document defines the input contract, comparison surface, verdict semantics, and evidence threshold for the `plan-reviewer` stage-exit review mode used in staged dev-workflow runs.

## Purpose

Between implementation stages, `plan-reviewer` runs a stage-exit review to judge whether the completed stage's implementation has invalidated any plan assumptions for the remaining stages. This is a **forward-looking** check — it asks "is the plan for future stages still valid given what just happened?" — not a root-cause repair of the current stage (that is handled by in-stage backward edges).

## Input contract

The stage-exit review consumes:

1. **Completed stage artifacts:**
   - `30-stageN-implementation-report.md` — the stage's implementation report (what was built)
   - `31-stageN-implementation-audit.md` — the stage's audit (was the requested behavior built with evidence)
   - `40-stageN-code-review.md` — the stage's code review (is the diff safe to commit)

2. **Plan context for remaining stages:**
   - Plan §4 **Assumptions and decisions** — the assumptions the plan made about interfaces, dependencies, architecture, data contracts, and acceptance criteria
   - Plan §10 **Stage breakdown** — the ordered list of remaining stages with their task ids, commit checkpoints, and verification targets

3. **Run manifest context:**
   - `00-run-manifest.md` — current stage number, `Run mode: staged`, stage statuses

## Comparison surface

The stage-exit review compares the completed stage's implementation reality against the plan's assumptions for remaining stages. Specifically:

- **Interfaces:** Did the completed stage implement interfaces as the plan assumed? If the implementation chose a different valid approach (e.g., a different parameter order, a renamed function, a different return type), does that contradict what remaining stages expect to consume?
- **Dependencies:** Did the completed stage introduce, remove, or change a dependency that remaining stages rely on?
- **Architecture decisions:** Did the completed stage make an architecture decision that contradicts what the plan assumed for remaining stages (e.g., a different module boundary, a different data flow)?
- **Data contracts:** Did the completed stage produce or consume a data contract (schema, format, API) that differs from what the plan assumed?
- **Acceptance criteria:** Did the completed stage reveal that an acceptance criterion for a remaining stage is impossible, redundant, or already satisfied?

## Verdict semantics

The stage-exit review emits exactly one verdict:

### `plan-current`

The completed stage's implementation does **not** contradict any plan assumption for remaining stages. Task details (file paths, exact function names, verification commands) may need refinement, but the plan's architecture, interfaces, dependencies, data contracts, and acceptance criteria for remaining stages still hold.

**Routing:** `plan-guide` performs light refinement of the next stage's task details only. No `plan-reviewer` re-audit of the full plan. Proceed to the next stage.

### `plan-stale`

The completed stage's implementation **contradicts** at least one plan assumption for a remaining stage. The contradiction must be explicit and evidenced — not merely "details changed" or "the implementation looks different."

**Evidence threshold for `plan-stale`:**

A `plan-stale` verdict requires the reviewer to cite:
1. The specific plan assumption that is contradicted (from plan §4 or §10).
2. The specific evidence from the completed stage's artifacts (implementation report, audit, or code review) that contradicts it.
3. Why the contradiction affects a remaining stage (not just the completed stage).

If the reviewer cannot cite all three, the verdict must be `plan-current`, not `plan-stale`.

**Routing:** `plan-guide` performs a full re-plan: re-derive remaining stages (architecture, stage boundaries, acceptance criteria, task decomposition) using the completed stage's implementation as new input. `plan-reviewer` re-audits the revised plan before execution resumes.

## Boundary: `plan-current` vs. `plan-stale`

| situation | verdict | rationale |
|---|---|---|
| Implementation used a different function name than the plan specified | `plan-current` | Detail change; the interface contract (what the function does) is unchanged |
| Implementation chose a different parameter order for an internal function | `plan-current` | Detail change; internal functions are not plan assumptions |
| Implementation changed a public API signature that remaining stages consume | `plan-stale` | Assumption contradiction; remaining stages expect the old signature |
| Implementation added a new dependency not in the plan | `plan-stale` | Assumption contradiction; remaining stages may need to account for the new dependency |
| Implementation revealed that a planned interface is impossible to build as specified | `plan-stale` | Assumption contradiction; remaining stages that consume the interface are affected |
| Implementation completed faster than expected and merged two stages | `plan-stale` | Stage boundary contradiction; remaining stage structure is affected |
| Implementation used a different test framework than planned | `plan-current` | Detail change; test framework is not a plan assumption unless it affects remaining stages' test design |
| Implementation revealed a security constraint not in the plan | `plan-stale` | Assumption contradiction; remaining stages may need security changes |

## Output artifact

The stage-exit review produces `32-stageN-exit-review.md` with:

```markdown
# Stage-Exit Review: Stage N

## Verdict
plan-current | plan-stale

## Completed stage summary
[Brief summary of what the completed stage produced]

## Comparison
[For each plan assumption checked, state whether it holds or is contradicted]

## Evidence (required if verdict is plan-stale)
[For each contradiction: the plan assumption, the evidence from stage artifacts, and the impact on remaining stages]

## Recommendation
[If plan-current: light refinement notes for next stage's task details]
[If plan-stale: what plan-guide should re-derive and why]
```

## Relationship to in-stage backward edges

In-stage backward edges (e.g., `code-reviewer` `design` finding → `plan-guide`) are **root-cause repair** of the current stage's plan. They fire during a stage's quality gates.

The stage-exit review is a **forward-looking** check that fires **between stages**, after the current stage has passed all its quality gates and committed.

The two mechanisms are independent:
- An in-stage backward edge does **not** automatically trigger a stage-exit review.
- A stage-exit review does **not** create a backward edge; it routes to `plan-guide` for forward-looking refinement or re-planning.
