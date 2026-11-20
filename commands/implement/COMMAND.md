---
name: implement
description: Implement phase loop when the user explicitly invokes /implement.
---

# Dev Workflow Implement

Run **only the Implement phase** (Loop 3) of the dev-workflow harness to acceptance or escalation, loading `dev-workflow-orchestrator`, `plan-executor`, and `implementation-auditor`.

## Steps

1. Read and follow `.agents/skills/dev-workflow-orchestrator/SKILL.md` (**Within a phase (the loop)** for Phase 3, including the staged iterator when `Run mode: staged`); `/implement` is the explicit start signal. This command carries only the Implement delta — the orchestrator owns loop mechanics, validation handling, and manifest pin refresh (`references/loop-contracts.md`).

2. **Resolve `.agents/workflow/<slug>/` and manifest**:
   - **Explicit `<slug>`**: use `.agents/workflow/<slug>/` and read `00-run-manifest.md` (if missing, report and stop).
   - **Auto-detect**: if no `<slug>` and one run dir exists under `.agents/workflow/`, use it; if zero or multiple exist (when not bootstrapping), ask for `<slug>`.
   - **Bootstrap**: if no `<slug>` and no run dir exists, require `--from <path>` pointing at a non-empty implementation plan (if empty, report "`--from <path>`: file is empty" and stop before invoking `plan-executor`). Create `.agents/workflow/<slug>/`, copy the plan to `20-implementation-plan.md`, and write `00-run-manifest.md` per `.agents/skills/dev-workflow-orchestrator/references/manifest-format.md` with `# Run Manifest`, `## Run metadata` (`Run status: in-progress`, `Current phase: implement`, and `Run mode: staged` if `20-implementation-plan.md` §10 sets `Execution mode: staged`, else `Run mode: linear`), `## Phase status` (Implement `in-progress`, others `not-started`), `## Artifact registry` (`20-implementation-plan.md`), and `## Dispatch log` recording `Dispatch mode: native` or `delegated` per `references/dispatch-modes.md` (default to delegated and say so when uninspectable) plus `Evaluated at: bootstrap`. Never use `skipped` or `fragment`.

3. **Run the Phase 3 loop**:

   | Field | Value |
   | --- | --- |
   | Doer | `plan-executor`, input `20-implementation-plan.md`, output `30-implementation-report.md` |
   | Checker | `implementation-auditor`, input `30-implementation-report.md`, output `31-implementation-audit.md` |
   | Round cap | 3 |
   | Accept verdicts | `pass`, `pass with risks` (then `validate_phase.py --phase implement`) |
   | Revise verdicts | `fail` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Blocked | `blocked` → escalate immediately with a blocker summary and stop |
   | Backward targets | `plan` or `research` (`back-implement-to-<target>-<n>.md` → `/plan <slug>` or `/research <slug>`) and `clarify` (`back-implement-to-clarify-<n>.md` → `/run-dev-workflow` or manual) |
   | Mode | Write source per the plan; run tests and builds; write only `30-*.md` and `31-*.md`; no committing, pushing, deploying, or destructive commands |

## Output and guardrails

- **Output**: phase/round, implementation-auditor verdict, backward edge routed (if any), validation result, manifest phase status, and `30-implementation-report.md`.
- **On failure**: if `--from <path>` is empty, report "`--from <path>`: file is empty" and stop; defer pre/post-flight, validation-error, round-cap (3), and backward-edge-cap (2) handling to `dev-workflow-orchestrator`.
- **Do not**: write outside planned source and `30-*.md` / `31-*.md`, commit/push/deploy, run destructive commands, skip pre/post-flight or validation rules, or run phases other than Implement.
