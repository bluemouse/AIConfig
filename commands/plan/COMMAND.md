---
name: plan
description: Plan phase loop when the user explicitly invokes /plan.
---

# Dev Workflow Plan

Run **only the Plan phase** (Loop 2) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 2 procedure and the `plan-guide` / `plan-reviewer` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.agents/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** standard procedure for Phase 2 (Plan). Treat `/plan`
   as the explicit start signal — proceed without asking for a second confirmation.
   This command carries only the Plan-phase delta; the orchestrator owns the loop
   mechanics and its `references/loop-contracts.md` owns the contract details.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.agents/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.agents/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, require `--from <path>`
     pointing at a research report. Verify the file is non-empty (if empty, report
     "`--from <path>`: file is empty" and stop). Create a feature slug (kebab-case),
     create `.agents/workflow/<slug>/`, copy the external report to
     `10-research-report.md`, and write a minimal `00-run-manifest.md` (`Run status:
     in-progress`, `Current phase: plan`, all phases `not-started` except Plan
     `in-progress`) plus a `## Dispatch log` section recording `Dispatch mode: native`
     or `delegated` per the orchestrator's capability detection; default to delegated
     and say so when uninspectable; record `Evaluated at: bootstrap`. Never use
     `skipped` or `fragment` as status values — they fail `manifest_checks.py`.
     Structural validation of the research report is delegated to plan-guide's input
     validation.

3. **Run the Phase 2 loop** with this delta:

   | Field | Value |
   | --- | --- |
   | Doer | `plan-guide`, input `10-research-report.md`, output `20-implementation-plan.md` |
   | Checker | `plan-reviewer`, input `20-implementation-plan.md`, output `21-plan-review.md` |
   | Round cap | 3 |
   | Accept verdicts | `validated`, `conditionally validated` (then `validate_phase.py --phase plan`) |
   | Revise verdicts | `needs revision` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Blocked | `blocked` → escalate immediately with a blocker summary and stop |
   | Backward targets | `research` (packet `back-plan-to-research-<n>.md` → user runs `/research <slug>`) and `clarify` (`back-plan-to-clarify-<n>.md` → no `/clarify` command; `/run-dev-workflow` or manual) |
   | Mode | Read-only source access; write only `20-*.md` and `21-*.md`; no editing source, tests, configs, or committing |

4. **Output**: phase started and round number; verdict from plan-reviewer; backward
   edge created and routed (if any); validation results; final summary (manifest phase
   status, terminal artifact `20-implementation-plan.md`).

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
- Let the phase write outside its allowed artifacts (`20-*.md`, `21-*.md`)
- Proceed past a validation error without a recorded justification
- Exceed the backward edge cap of 2 without escalating to the user
- Commit, push, or deploy
- Run phases other than Plan
