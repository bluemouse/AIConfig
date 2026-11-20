---
name: plan
description: Plan phase loop when the user explicitly invokes /plan.
---

# Dev Workflow Plan

Run **only the Plan phase** (Loop 2) of the dev-workflow harness to acceptance or escalation, loading `dev-workflow-orchestrator`, `plan-guide`, and `plan-reviewer`.

## Steps

1. Read and follow `.agents/skills/dev-workflow-orchestrator/SKILL.md` (**Within a phase (the loop)** for Phase 2); `/plan` is the explicit start signal. This command carries only the Plan delta — the orchestrator owns loop mechanics, validation handling, and manifest pin refresh (`references/loop-contracts.md`).

2. **Resolve `.agents/workflow/<slug>/` and manifest**:
   - **Explicit `<slug>`**: use `.agents/workflow/<slug>/` and read `00-run-manifest.md` (if missing, report and stop).
   - **Auto-detect**: if no `<slug>` and one run dir exists under `.agents/workflow/`, use it; if zero or multiple exist (when not bootstrapping), ask for `<slug>`.
   - **Bootstrap**: if no `<slug>` and no run dir exists, require `--from <path>` pointing at a non-empty research report (if empty, report "`--from <path>`: file is empty" and stop). Create `.agents/workflow/<slug>/`, copy the report to `10-research-report.md`, and write `00-run-manifest.md` per `.agents/skills/dev-workflow-orchestrator/references/manifest-format.md` with `# Run Manifest`, `## Run metadata` (`Run status: in-progress`, `Current phase: plan`), `## Phase status` (Plan `in-progress`, others `not-started`), `## Artifact registry` (`10-research-report.md`), and `## Dispatch log` recording `Dispatch mode: native` or `delegated` per `references/dispatch-modes.md` (default to delegated and say so when uninspectable) plus `Evaluated at: bootstrap`. Never use `skipped` or `fragment`.

3. **Run the Phase 2 loop**:

   | Field | Value |
   | --- | --- |
   | Doer | `plan-guide`, input `10-research-report.md`, output `20-implementation-plan.md` |
   | Checker | `plan-reviewer`, input `20-implementation-plan.md`, output `21-plan-review.md` |
   | Round cap | 3 |
   | Accept verdicts | `validated`, `conditionally validated` (then `validate_phase.py --phase plan`) |
   | Revise verdicts | `needs revision` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Blocked | `blocked` → escalate immediately with a blocker summary and stop |
   | Backward targets | `research` (`back-plan-to-research-<n>.md` → `/research <slug>`) and `clarify` (`back-plan-to-clarify-<n>.md` → `/run-dev-workflow` or manual) |
   | Mode | Read-only source access; write only `20-*.md` and `21-*.md`; no editing source, tests, configs, or committing |

## Output and guardrails

- **Output**: phase/round, plan-reviewer verdict, backward edge routed (if any), validation result, manifest phase status, and `20-implementation-plan.md`.
- **On failure**: if `--from <path>` is empty, report "`--from <path>`: file is empty" and stop; defer pre/post-flight, validation-error, round-cap (3), and backward-edge-cap (2) handling to `dev-workflow-orchestrator`.
- **Do not**: write outside `20-*.md` / `21-*.md`, edit source/tests/configs, commit/push/deploy, skip pre/post-flight or validation rules, or run phases other than Plan.
