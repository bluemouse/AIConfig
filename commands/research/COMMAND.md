---
name: research
description: Research phase loop when the user explicitly invokes /research.
---

# Dev Workflow Research

Run **only the Research phase** (Loop 1) of the dev-workflow harness to acceptance or escalation, loading `dev-workflow-orchestrator`, `research-guide`, and `research-reviewer`.

## Steps

1. Read and follow `.agents/skills/dev-workflow-orchestrator/SKILL.md` (**Within a phase (the loop)** for Phase 1); `/research` is the explicit start signal. This command carries only the Research delta — the orchestrator owns baseline, pre/post-flight, doer/checker passes, verdict routing, backward edges, validation handling, and manifest pin refresh (`references/loop-contracts.md`).

2. **Resolve `.agents/workflow/<slug>/`**:
   - **Explicit `<slug>`**: use `.agents/workflow/<slug>/` (if missing, report and stop).
   - **Auto-detect**: if no `<slug>` and one run dir exists under `.agents/workflow/`, use it; if zero or multiple exist (when not bootstrapping), ask for `<slug>`.
   - **Bootstrap**: if no `<slug>` and no run dir exists, derive a kebab-case slug from `$ARGUMENTS`, create `.agents/workflow/<slug>/`, write `01-feature-brief.md`, and write `02-requirement-ledger.md` (`# Requirement Ledger`, `## Outcome`, `## Scope`, `## Acceptance criteria`, `## Assumptions`). Skip Clarify.

3. **Manifest**: read `00-run-manifest.md`, or on bootstrap write it per `.agents/skills/dev-workflow-orchestrator/references/manifest-format.md` with `# Run Manifest`, `## Run metadata` (`Run status: in-progress`, `Current phase: research`), `## Phase status` (Research `in-progress`, others `not-started`), `## Artifact registry` (`01-feature-brief.md`, `02-requirement-ledger.md`), and `## Dispatch log` recording `Dispatch mode: native` or `delegated` per `references/dispatch-modes.md` (default to delegated and say so when uninspectable) plus `Evaluated at: bootstrap`. Never use `skipped` or `fragment`.

4. **Run the Phase 1 loop**:

   | Field | Value |
   | --- | --- |
   | Doer | `research-guide`, input `02-requirement-ledger.md`, output `10-research-report.md` |
   | Checker | `research-reviewer`, input `10-research-report.md`, output `11-research-review.md` |
   | Round cap | 5 |
   | Accept verdicts | `ready`, `conditionally ready` (then `validate_phase.py --phase research`) |
   | Revise verdicts | `needs revision` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Blocked | `blocked` → escalate immediately with a blocker summary and stop |
   | Backward targets | `clarify` only (packet `back-research-to-clarify-<n>.md`; no `/clarify` command — run `/run-dev-workflow` or resolve manually) |
   | Mode | Read-only source access; write only `10-*.md` and `11-*.md`; no editing source, tests, configs, or committing |

## Output and guardrails

- **Output**: phase/round, research-reviewer verdict, backward edge routed (if any), validation result, manifest phase status, and `10-research-report.md`.
- **On failure**: defer pre/post-flight, validation-error, round-cap (5), and backward-edge-cap (2) handling to `dev-workflow-orchestrator`.
- **Do not**: write outside `10-*.md` / `11-*.md`, edit source/tests/configs, commit/push/deploy, skip pre/post-flight or validation rules, or run phases other than Research.
