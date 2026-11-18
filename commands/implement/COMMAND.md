---
name: implement
description: Implement phase loop when the user explicitly invokes /implement.
---

# Dev Workflow Implement

Run **only the Implement phase** (Loop 3) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 3 procedure and the `plan-executor` / `implementation-auditor` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.agents/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** standard procedure for Phase 3 (Implement). Treat
   `/implement` as the explicit start signal — proceed without asking for a second
   confirmation. This command carries only the Implement-phase delta; the orchestrator
   owns the loop mechanics (including the staged iterator when the manifest records
   `Run mode: staged`) and its `references/loop-contracts.md` owns the contract details.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.agents/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.agents/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, require `--from <path>`
     pointing at an implementation plan. Verify the file is non-empty (if empty, report
     "`--from <path>`: file is empty" and stop before invoking plan-executor). Create a
     feature slug (kebab-case), create `.agents/workflow/<slug>/`, copy the external plan
     to `20-implementation-plan.md`, and write a minimal `00-run-manifest.md` (`Run
     status: in-progress`, `Current phase: implement`, all phases `not-started` except
     Implement `in-progress`) plus a `## Dispatch log` section recording `Dispatch mode:
     native` or `delegated` per the orchestrator's capability detection; default to
     delegated and say so when uninspectable; record `Evaluated at: bootstrap`. Never use
     `skipped` or `fragment` as status values — they fail `manifest_checks.py`.
     Structural validation of the plan is delegated to plan-executor's existing input
     validation.

3. **Run the Phase 3 loop** with this delta:

   | Field | Value |
   | --- | --- |
   | Doer | `plan-executor`, input `20-implementation-plan.md`, output `30-implementation-report.md` |
   | Checker | `implementation-auditor`, input `30-implementation-report.md`, output `31-implementation-audit.md` |
   | Round cap | 3 |
   | Accept verdicts | `pass`, `pass with risks` (then `validate_phase.py --phase implement`) |
   | Revise verdicts | `fail` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Blocked | `blocked` → escalate immediately with a blocker summary and stop |
   | Backward targets | `plan` or `research` (packet `back-implement-to-<target>-<n>.md` → user runs `/plan <slug>` or `/research <slug>`) and `clarify` (`back-implement-to-clarify-<n>.md` → no `/clarify` command; `/run-dev-workflow` or manual) |
   | Mode | Write source per the implementation plan; run tests and builds; write only `30-*.md` and `31-*.md`; no committing, pushing, deploying, or destructive commands |

4. **Output**: phase started and round number; verdict from implementation-auditor;
   backward edge created and routed (if any); validation results; final summary (manifest
   phase status, terminal artifact `30-implementation-report.md`).

## On failure

| Condition | Action |
| --- | --- |
| Run directory not found | Report and stop |
| `--from <path>` file is empty | Report "`--from <path>`: file is empty" and stop |
| Pre-flight check fails | Report the missing artifacts and stop |
| Validation error (non-overridable) | Report the error and stop |
| Loop cap (3) hit with no backward edge available | Present blocker summary and ask the user |
| Backward edge cap (2) hit | Present the blocker chain and ask the user |

## Do not

- Skip the pre-flight or post-flight checks
- Let the phase write outside its allowed artifacts (`30-*.md`, `31-*.md`) and planned source
- Proceed past a validation error without a recorded justification
- Exceed the backward edge cap of 2 without escalating to the user
- Commit, push, deploy, or run destructive commands
- Run phases other than Implement
