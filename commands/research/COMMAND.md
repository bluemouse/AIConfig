---
name: research
description: Research phase loop when the user explicitly invokes /research.
---

# Dev Workflow Research

Run **only the Research phase** (Loop 1) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 1 procedure and the `research-guide` / `research-reviewer` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.agents/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** standard procedure for Phase 1 (Research). Treat
   `/research` as the explicit start signal — proceed without asking for a second
   confirmation. This command carries only the Research-phase delta; the orchestrator
   owns the loop mechanics (baseline, pre-flight, doer/checker passes, post-flight,
   verdict routing, backward edges, manifest pin refresh) and its
   `references/loop-contracts.md` owns the contract details.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.agents/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.agents/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, create a feature slug
     (kebab-case) from the user's argument, create `.agents/workflow/<slug>/`, write
     `01-feature-brief.md` from the argument, and write a minimal `02-requirement-ledger.md`
     with the required sections (`# Requirement Ledger`, `## Outcome`, `## Scope`,
     `## Acceptance criteria`, `## Assumptions` — per `artifact_checks.py`
     `PHASE_ARTIFACTS["clarify"]`). Skip the Clarify phase.

3. **Read or write the manifest**: if the run dir exists, read `00-run-manifest.md`;
   if bootstrapping, write a minimal one (`Run status: in-progress`, `Current phase:
   research`, all phases `not-started` except Research `in-progress`, artifact registry
   seeded with `01-feature-brief.md` and `02-requirement-ledger.md`) plus a `## Dispatch
   log` section recording `Dispatch mode: native` or `delegated` per the orchestrator's
   capability detection (`references/dispatch-modes.md`); default to delegated and say
   so when the capability cannot be inspected, and record `Evaluated at: bootstrap`.
   Never use `skipped` or `fragment` as status values — they fail `manifest_checks.py`.

4. **Run the Phase 1 loop** with this delta:

   | Field | Value |
   | --- | --- |
   | Doer | `research-guide`, input `02-requirement-ledger.md`, output `10-research-report.md` |
   | Checker | `research-reviewer`, input `10-research-report.md`, output `11-research-review.md` |
   | Round cap | 5 |
   | Accept verdicts | `ready`, `conditionally ready` (then `validate_phase.py --phase research`) |
   | Revise verdicts | `needs revision` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Blocked | `blocked` → escalate immediately with a blocker summary and stop |
   | Backward targets | `clarify` only (packet `back-research-to-clarify-<n>.md`; no `/clarify` command exists — instruct the user to run `/run-dev-workflow` or resolve manually) |
   | Mode | Read-only source access; write only `10-*.md` and `11-*.md`; no editing source, tests, configs, or committing |

5. **Output**: phase started and round number; verdict from research-reviewer; backward
   edge created and routed (if any); validation results; final summary (manifest phase
   status, terminal artifact `10-research-report.md`).

## On failure

| Condition | Action |
| --- | --- |
| Run directory not found | Report and stop |
| Pre-flight check fails | Report the missing artifacts and stop |
| Validation error (non-overridable) | Report the error and stop |
| Loop cap (5) hit with no backward edge available | Present blocker summary and ask the user |
| Backward edge cap (2) hit | Present the blocker chain and ask the user |

## Do not

- Skip the pre-flight or post-flight checks
- Let the phase write outside its allowed artifacts (`10-*.md`, `11-*.md`)
- Proceed past a validation error without a recorded justification
- Exceed the backward edge cap of 2 without escalating to the user
- Commit, push, or deploy
- Run phases other than Research
