# Artifact Contract

All workflow artifacts live under `.ai/workflow/<feature-slug>/`. The directory is gitignored.

## Naming scheme

Phase-grouped numbered filenames:
- Tens digit = phase (0=meta+clarify, 1=research, 2=plan, 3=implement, 4=review, 5=commit)
- Ones digit = artifact within phase
- `-r2`, `-r3` suffixes for loop rounds
- `back-<from>-<to>-<n>.md` for backward handoff packets

## Artifact registry

| Phase | Artifact | Filename | Producer | Consumer | Type |
|-------|----------|----------|----------|----------|------|
| 0 (meta) | Run manifest | `00-run-manifest.md` | Orchestrator | Orchestrator | State |
| 0 (meta) | Feature brief | `01-feature-brief.md` | Orchestrator | Clarify phase | Input |
| 0 (clarify) | Requirement ledger | `02-requirement-ledger.md` | prompt-clarifier | research-guide | Terminal |
| 1 (research) | Research report | `10-research-report.md` | research-guide | research-reviewer, plan-guide | Terminal |
| 1 (research) | Research review | `11-research-review.md` | research-reviewer | research-guide (loop), orchestrator | Loop output |
| 1 (research) | Research report r2 | `12-research-report-r2.md` | research-guide | research-reviewer | Loop output |
| 2 (plan) | Implementation plan | `20-implementation-plan.md` | plan-guide | plan-reviewer, plan-executor | Terminal |
| 2 (plan) | Plan review | `21-plan-review.md` | plan-reviewer | plan-guide (loop), orchestrator | Loop output |
| 3 (implement) | Implementation report | `30-implementation-report.md` | plan-executor | implementation-auditor, code-reviewer | Terminal |
| 3 (implement) | Implementation audit | `31-implementation-audit.md` | implementation-auditor | plan-executor (loop), orchestrator | Loop output |
| 4 (review) | Code review | `40-code-review.md` | code-reviewer | code-review-resolver (loop), orchestrator | Loop output |
| 4 (review) | Fix report | `41-fix-report.md` | code-review-resolver | code-reviewer (loop), orchestrator | Loop output |
| 5 (commit) | Commit record | `50-commit.md` | git-commit | (terminal) | Terminal |
| (backward) | Backward handoff packet | `back-<from>-<to>-<n>.md` | Any reviewer/auditor | Target phase | Handoff |

## Stage-indexed artifacts (staged mode only)

When `Run mode: staged`, per-stage artifacts use the naming scheme `30-stageN-*`, `31-stageN-*`, `32-stageN-*`, `40-stageN-*`, `41-stageN-*` where N is the 1-indexed stage number. Linear-mode artifacts (without the `stageN` segment) remain valid and unchanged.

| Phase | Artifact | Filename (staged mode) | Producer | Consumer | Type |
|-------|----------|------------------------|----------|----------|------|
| 3 (implement) | Stage implementation report | `30-stageN-implementation-report.md` | plan-executor | implementation-auditor, code-reviewer | Terminal (per stage) |
| 3 (implement) | Stage implementation audit | `31-stageN-implementation-audit.md` | implementation-auditor | plan-executor (loop), orchestrator | Loop output (per stage) |
| 3 (implement) | Stage-exit review | `32-stageN-exit-review.md` | plan-reviewer | orchestrator | Loop output (between stages) |
| 4 (review) | Stage code review | `40-stageN-code-review.md` | code-reviewer | code-review-resolver (loop), orchestrator | Loop output (per stage) |
| 4 (review) | Stage fix report | `41-stageN-fix-report.md` | code-review-resolver | code-reviewer (loop), orchestrator | Loop output (per stage) |
| 4 (review) | Final deep review | `40-final-deep-review.md` | code-reviewer | code-review-resolver (loop), orchestrator | Loop output (after all stages) |
| 4 (review) | Final fix report | `41-final-fix-report.md` | code-review-resolver | code-reviewer (loop), orchestrator | Loop output (after all stages) |

## Boundary rules

- Only the orchestrator writes `00-run-manifest.md`.
- Each phase writes only its own artifacts as defined in the table above.
- Backward handoff packets are write-once by the discovering checker.
- No phase edits another phase's artifacts.
