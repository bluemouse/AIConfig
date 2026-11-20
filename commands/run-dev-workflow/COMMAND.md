---
name: run-dev-workflow
description: Full dev-workflow pipeline when the user explicitly invokes /run-dev-workflow.
---

# Dev Workflow

Start the full development workflow on a requirement or feature. This command loads the
`dev-workflow-orchestrator` skill, which orchestrates the 6-phase pipeline (clarify →
research → plan → implement → code-review → commit) with bounded loops, backward
edges for upstream root causes, artifact contracts, and mode enforcement.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.agents/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill). Treat
   `/run-dev-workflow` as the explicit start signal — proceed to orchestrate the workflow
   without asking for a second confirmation.

2. Accept the requirement or feature description from the user's message (the text after
   `/run-dev-workflow`). If no requirement is provided, ask the user to describe what they want
   to build.

3. Follow the orchestrator skill's **Starting a run** procedure:
   - Create a feature slug and `.agents/workflow/<slug>/`.
   - Write `00-run-manifest.md` (per `.agents/skills/dev-workflow-orchestrator/references/manifest-format.md`) and `01-feature-brief.md`.
   - Activate clarify mode, record the baseline (`python .agents/tools/dev-workflow/record_baseline.py --phase clarify --run-dir .agents/workflow/<slug>`), run the pre-flight check, and start Phase 0 (Clarify).

4. Continue following the orchestrator skill through all phases, loops, backward edges, and validation checks until the workflow completes or escalates.

5. **Stage-aware mode detection (after Plan phase):** Read `Execution mode` from `20-implementation-plan.md` §10. If `Execution mode: staged`, set `Run mode: staged` in `00-run-manifest.md` (`## Run metadata`) so Implement uses the staged iterator (per-stage implement → audit → review → commit, between-stage exit review, and final deep review). Otherwise default to `Run mode: linear`.

## Optional arguments

Treat `$ARGUMENTS` after `/run-dev-workflow` as the requirement or feature description, or if it names a phase to resume (e.g., "resume from plan"), read `00-run-manifest.md` and continue from that phase.

## Output and guardrails

- **Output**: ongoing phase/round updates, checker verdicts, backward edges, validation results, and final summary with commit hash (when completed).
- **On failure**: if `.agents/workflow/<slug>/` already exists, ask whether to resume or use a new slug; defer pre/post-flight, validation-error, loop-cap, and backward-edge-cap (2) handling to `dev-workflow-orchestrator`.
- **Do not**: skip pre/post-flight checks, write outside phase-allowed artifacts, proceed past an unoverridden validation error, exceed the backward-edge cap (2), or commit/push/deploy before Phase 5 (Commit) with explicit user authorization.
