---
name: dev-workflow
description: Run the full development workflow — research → plan → implement → code-review
  → commit — on a requirement or feature, with bounded loops, backward edges, and
  validation. Loads the dev-workflow-orchestrator skill.
agent: agent
---

# Dev Workflow

Start the full development workflow on a requirement or feature. This command loads the
`dev-workflow-orchestrator` skill, which orchestrates the 5-phase pipeline with bounded
loops, backward edges for upstream root causes, artifact contracts, and mode enforcement.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.shared/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill). Treat
   `/dev-workflow` as the explicit start signal — proceed to orchestrate the workflow
   without asking for a second confirmation.

2. Accept the requirement or feature description from the user's message (the text after
   `/dev-workflow`). If no requirement is provided, ask the user to describe what they want
   to build.

3. Follow the orchestrator skill's **Starting a run** procedure:
   - Create a feature slug.
   - Create `.ai/workflow/<slug>/`.
   - Write `00-run-manifest.md` and `01-feature-brief.md`.
   - Activate research mode.
   - Run the pre-flight check.
   - Start Phase 1 (Research loop).

4. Continue following the orchestrator skill through all phases, loops, backward edges, and
   validation checks until the workflow completes or escalates.

## Optional arguments

If the user adds text after `/dev-workflow`, treat it as the requirement or feature
description. If they mention a specific phase to resume from (e.g., "resume from plan"),
read the existing run manifest and continue from that phase.

## Output

The orchestrator provides ongoing updates as each phase progresses:
- Phase started, round number
- Verdict from each checker
- Backward edges created and routed
- Validation results
- Final summary with commit hash (if completed)

## On failure

| Condition | Action |
| --- | --- |
| Run directory already exists for the slug | Ask whether to resume or start fresh with a new slug |
| Pre-flight check fails | Report the missing artifacts and stop |
| Validation error (non-overridable) | Report the error and stop |
| Loop cap hit with no backward edge available | Present blocker summary and ask the user |
| Backward edge cap hit | Present the blocker chain and ask the user |

## Do not

- Skip the pre-flight or post-flight checks
- Let a phase write outside its allowed artifacts
- Proceed past a validation error without a recorded justification
- Exceed the backward edge cap of 2 without escalating to the user
- Commit, push, or deploy unless the workflow reaches Phase 5 (Commit) and the user has
  explicitly authorized the commit
