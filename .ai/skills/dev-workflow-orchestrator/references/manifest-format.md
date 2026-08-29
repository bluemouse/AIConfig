# Run Manifest Format

The run manifest is the orchestrator's state file. It tracks the entire run so the orchestrator knows where it is and can resume after interruption. The orchestrator reads it at the start of every turn and updates it after every step.

## Template

```markdown
# Run Manifest

## Run metadata
- Feature slug: <slug>
- Created: <ISO timestamp>
- Last updated: <ISO timestamp>
- Current phase: <research | plan | implement | code-review | commit | done>
- Run status: <in-progress | completed | blocked | abandoned>
- Run mode: <linear | staged> (default: linear; set to `staged` when plan §10 declares `Execution mode: staged`)
- Git baseline at phase start: <HEAD sha or 'no-git'>

## Input
- Requirement: <brief description>
- Feature brief: 01-feature-brief.md

## Phase status

### Phase 0: Clarify
- Status: <not-started | in-progress | accepted | backward-edge-received>
- Terminal artifact: 02-requirement-ledger.md
- Backward edges received: <0 | 1 | 2>

### Phase 1: Research
- Status: <not-started | in-progress | loop-active | accepted | backward-edge-received>
- Current round: <1 | 2 | 3 | 4 | 5>
- Terminal artifact: 10-research-report.md
- Backward edges received: <0 | 1 | 2>

### Phase 2: Plan
- Status: <not-started | in-progress | loop-active | accepted | backward-edge-received>
- Current round: <1 | 2 | 3>
- Terminal artifact: 20-implementation-plan.md
- Backward edges received: <0 | 1 | 2>

### Phase 3: Implement
- Status: <not-started | in-progress | loop-active | accepted | backward-edge-received>
- Current round: <1 | 2 | 3>
- Terminal artifact: 30-implementation-report.md
- Backward edges received: <0 | 1 | 2>

### Phase 4: Code Review
- Status: <not-started | in-progress | loop-active | accepted | backward-edge-received>
- Current round: <1 | 2 | 3 | 4 | 5>
- Backward edges received: <0 | 1 | 2>

### Phase 5: Commit
- Status: <not-started | in-progress | completed>
- Terminal artifact: 50-commit.md

## Stage status
[Include only when Run mode is `staged`. Tracks per-stage progress in the staged iterator.]

- Current stage: <stage-1 | stage-2 | ... | done>
- Total stages: <N>

### Stage 1
- Status: <not-started | in-progress | implement | audit | review | commit | stage-exit | accepted | failed>
- Task ids: <pg-001, pg-002>
- Implementation report: 30-stage1-implementation-report.md
- Implementation audit: 31-stage1-implementation-audit.md
- Code review: 40-stage1-code-review.md
- Stage-exit review: 32-stage1-exit-review.md
- Commit hash: <sha or 'not-committed'>
- Stage-exit verdict: <plan-current | plan-stale | n/a>

### Stage 2
- Status: <not-started | in-progress | implement | audit | review | commit | stage-exit | accepted | failed>
- Task ids: <pg-003>
- Implementation report: 30-stage2-implementation-report.md
- Implementation audit: 31-stage2-implementation-audit.md
- Code review: 40-stage2-code-review.md
- Stage-exit review: 32-stage2-exit-review.md
- Commit hash: <sha or 'not-committed'>
- Stage-exit verdict: <plan-current | plan-stale | n/a>

### Final deep review
- Status: <not-started | in-progress | accepted | failed>
- Commit range: <HEAD~N..HEAD>
- Code review: 40-final-deep-review.md
- Fix report: 41-final-fix-report.md (if findings)

## Artifact registry
| Artifact | Path | Phase | Status |
|----------|------|-------|--------|
| Feature brief | 01-feature-brief.md | 0 | final |
| Research report | 10-research-report.md | 1 | final |
| Research review | 11-research-review.md | 1 | final |
| ... | ... | ... | ... |

## Backward edge log
| # | From | To | Finding id | Packet path | Resolved |
|---|------|----|-----------|-------------|----------|
| 1 | implement | plan | pr-003 | back-impl-to-plan-1.md | yes |
| 2 | code-review | research | cr-007 | back-code-review-to-research-1.md | in-progress |

## Validation log
| Phase | Check | Severity | Finding | Orchestrator decision | Justification |
|-------|-------|----------|---------|----------------------|---------------|
| research | validate_phase | error | Missing required section | stopped | — |
| research | validate_phase | warning | Missing optional section | continued | Section not relevant for this feature |

## Dispatch log
- Dispatch mode: <native | delegated | simulated>
- Evaluated at: phase 0
- Notes: <e.g., "Copilot Chat — no subagent API, fell back to delegated">
```

## Rules

- Only the orchestrator writes this file. Phases read it for context but never edit it.
- The orchestrator updates `Last updated` and the relevant phase status after every step.
- `Current phase` is the phase the orchestrator is about to run or is currently running.
- `Backward edges received` tracks the cap of 2 per phase.
- The `Validation log` records every validation decision (stop, continue, override) with justification.
