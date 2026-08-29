# Loop Contracts

Each loop has a doer (produces), a checker (audits), a round cap, an exit condition, a feedback format, terminal labels, and an escalation path. The Clarify loop (Loop 0) is simplified — it has no checker and uses prompt-clarifier's internal state machine as its exit condition.

## Loop 0: Clarify (simplified — no checker)

| Element | Value |
|---------|-------|
| Doer | prompt-clarifier |
| Checker | none (internal `CHECK` state machine) |
| Round cap | none (the clarifier has no fixed round limit) |
| Exit (accept) | clarifier's `CHECK` state passes — task is `actionable` |
| Exit (blocked) | clarifier cannot reach `actionable` — task is `blocked` |
| Feedback format | interactive dialogue with the user (no findings, no verdict) |
| Terminal labels | `actionable`, `blocked` |
| Escalation | `blocked` → stop, present the specific blocker, ask user |
| Root cause field | n/a (no checker, no findings) |
| Artifact | `02-requirement-ledger.md` (see `requirement-ledger-template.md`) |

## Loop 1: Research

| Element | Value |
|---------|-------|
| Doer | research-guide |
| Checker | research-reviewer |
| Round cap | 5 |
| Exit (accept) | verdict `ready` or `conditionally ready` |
| Exit (revise) | verdict `needs revision` → research-guide revises using handoff packet |
| Exit (blocked) | verdict `blocked` → escalate immediately |
| Feedback format | `rr-NNN` findings + research-guide handoff packet |
| Terminal labels | `ready`, `conditionally ready`, `needs revision`, `blocked`, `NOT READY` (cap hit) |
| Escalation | `NOT READY` → root cause classification → backward edge or ask user |
| Root cause field | `root-cause-phase`: `local` / `research` / `plan` / `implement` / `code-review` |

## Loop 2: Plan

| Element | Value |
|---------|-------|
| Doer | plan-guide |
| Checker | plan-reviewer |
| Round cap | 3 |
| Exit (accept) | verdict `validated` or `conditionally validated` |
| Exit (revise) | verdict `needs revision` → plan-guide revises using Guide handoff packet |
| Exit (blocked) | verdict `blocked` → escalate immediately |
| Feedback format | `pr-NNN` findings + Guide handoff packet |
| Terminal labels | `validated`, `conditionally validated`, `needs revision`, `blocked`, `NOT READY` (cap hit) |
| Escalation | `NOT READY` → root cause classification → backward edge to Research or ask user |
| Root cause field | `root-cause-phase`: `local` / `research` / `plan` / `implement` / `code-review` |

## Loop 3: Implement

| Element | Value |
|---------|-------|
| Doer | plan-executor |
| Checker | implementation-auditor |
| Round cap | 3 |
| Exit (accept) | verdict `pass` or `pass with risks` |
| Exit (revise) | verdict `fail` → plan-executor re-executes |
| Exit (blocked) | verdict `blocked` → escalate immediately |
| Feedback format | `ia-NNN` findings + audit report |
| Terminal labels | `pass`, `pass with risks`, `fail`, `blocked`, `NOT READY` (cap hit) |
| Escalation | `NOT READY` → root cause classification → backward edge to Plan or Research, or ask user |
| Root cause field | `root-cause-phase`: `local` / `research` / `plan` / `implement` / `code-review` |

## Loop 4: Code Review

| Element | Value |
|---------|-------|
| Doer | code-review-resolver |
| Checker | code-reviewer |
| Round cap | 5 |
| Exit (accept) | verdict `ready to commit` or `ready with notes` |
| Exit (revise) | verdict `needs revision` → code-review-resolver applies fixes |
| Feedback format | `cr-NNN` findings + verdict field |
| Terminal labels | `ready to commit`, `ready with notes`, `needs revision`, `NOT READY` (cap hit) |
| Escalation | `NOT READY` → root cause classification → backward edge to Plan or Research, or ask user |
| Root cause field | `root-cause-phase`: `local` / `research` / `plan` / `implement` / `code-review` |

## Loop 5: Stage-Exit Review (staged mode only)

Runs between implementation stages in a staged dev-workflow run. This is a forward-looking plan-validity check, not a root-cause repair.

| Element | Value |
|---------|-------|
| Doer | plan-reviewer (stage-exit mode) |
| Checker | none (single pass, no loop) |
| Round cap | 1 (no loop — binary verdict) |
| Exit (accept) | verdict `plan-current` → light refinement of next stage's task details by plan-guide |
| Exit (revise) | verdict `plan-stale` → full re-plan by plan-guide with plan-reviewer re-audit |
| Feedback format | `32-stageN-exit-review.md` with `## Verdict` heading |
| Terminal labels | `plan-current`, `plan-stale` |
| Escalation | `plan-stale` → plan-guide re-derives remaining stages; user re-confirms at plan gate |
| Root cause field | n/a (forward-looking, not root-cause repair) |
| Artifact | `32-stageN-exit-review.md` (see `stage-exit-review-contract.md` in plan-reviewer references) |

## Loop 6: Final Deep Review (staged mode only)

Runs after all stages commit, on the cumulative commit range. This is the full code review that compensates for per-stage light reviews.

| Element | Value |
|---------|-------|
| Doer | code-review-resolver |
| Checker | code-reviewer |
| Round cap | 5 |
| Exit (accept) | verdict `ready to commit` or `ready with notes` |
| Exit (revise) | verdict `needs revision` → code-review-resolver applies fixes as new commits on top (fixes land as new commits on top, no amend/rebase) |
| Feedback format | `cr-NNN` findings + verdict field |
| Terminal labels | `ready to commit`, `ready with notes`, `needs revision`, `NOT READY` (cap hit) |
| Escalation | `NOT READY` → root cause classification → backward edge to Plan or Research, or ask user |
| Root cause field | `root-cause-phase`: `local` / `research` / `plan` / `implement` / `code-review` |
| Review scope | Cumulative commit range (`HEAD~N..HEAD` where N = number of stage commits) |
| Review effort | `deep` |
| Artifacts | `40-final-deep-review.md`, `41-final-fix-report.md` (if findings) |

## Escalation flow

When a loop hits its round cap without converging:

1. Mark the loop `NOT READY` with a blocker summary.
2. Read the `root-cause-phase` field from the checker's findings.
3. If root-cause-phase is upstream (not `local`) AND backward edge count for target phase < 2:
   - Create a backward handoff packet (see `backward-handoff-format.md`).
   - Route to the target phase with the packet.
   - Target phase fixes the specific issue, re-produces its terminal artifact.
   - Re-run the target phase's loop.
   - On acceptance, re-run downstream phases that depended on the changed artifact.
4. If root-cause-phase is `local` OR backward edge count for target phase = 2:
   - Stop the workflow.
   - Present the blocker summary to the user.
   - Ask whether to retry, change scope, or abort.

For the Clarify loop (Loop 0), there is no round cap and no root-cause-phase field. If the clarifier reaches `blocked`, stop immediately and ask the user — do not attempt a backward edge.

## Backward edge cap

Each phase can receive backward edges at most 2 times. After that, escalate to the user.

The Clarify phase can also receive backward edges (from Research, when the requirement itself is fundamentally ambiguous). The same cap of 2 applies.
