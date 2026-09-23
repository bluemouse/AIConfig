---
name: dev-workflow-implement
description: Run the Implement phase loop (plan-executor → implementation-auditor)
  to acceptance or escalation on an existing or bootstrapped dev-workflow run. Loads
  the dev-workflow-orchestrator skill's Phase 3 procedure.
---

# Dev Workflow Implement

Run **only the Implement phase** (Loop 3) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 3 procedure and the `plan-executor` / `implementation-auditor` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.ai/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** procedure for Phase 3 (Implement). Treat
   `/dev-workflow-implement` as the explicit start signal — proceed without asking for a
   second confirmation.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.ai/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.ai/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, require `--from <path>`
     pointing at an implementation plan. Verify the file is non-empty (if empty, report
     "`--from <path>`: file is empty" and stop before invoking plan-executor). Create a
     feature slug (kebab-case), create `.ai/workflow/<slug>/`, copy the external plan
     to `20-implementation-plan.md`, and write a minimal `00-run-manifest.md` with
     `Run status: in-progress`, `Current phase: implement`, all phases `not-started` except
     Implement (`in-progress`), and a `## Dispatch log` section recording
     `Dispatch mode: delegated` (recorded at bootstrap — command-bootstrapped
     runs skip phase 0; the default is delegated because the command host's
     subagent capability is unknown at bootstrap time). Never use `skipped` or
     `fragment` as status values — they fail `manifest_checks.py`. Structural
     validation of the plan is delegated to `plan-executor`'s existing input
     validation.

3. **Read or write the manifest**:
   - If the run dir exists, read `00-run-manifest.md`.
   - If bootstrapping, write the minimal manifest described in step 2.

4. **Run the Phase 3 loop** (doer → checker → revise) per the orchestrator skill.
   This procedure mirrors the orchestrator skill's `Within a phase (the loop)` — if the
   orchestrator's procedure changes, update all four `/dev-workflow-*` commands:
   - **Record baseline**: `python .ai/tools/dev-workflow/record_baseline.py --phase implement --run-dir .ai/workflow/<slug>`
   - **Pre-flight**: `python .ai/tools/dev-workflow/check_pre_phase.py --phase implement --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Doer pass**: invoke `plan-executor` as a named pass with input `20-implementation-plan.md` and output `30-implementation-report.md`.
   - **Checker pass**: first read the `## Dispatch log` section of `00-run-manifest.md`; if it records `Dispatch mode: native`, dispatch `implementation-auditor` as a subagent per the orchestrator's native-mode task packet; otherwise (delegated/simulated, or the manifest has no dispatch log — default to delegated and say so) invoke `implementation-auditor` as a named pass with input `30-implementation-report.md` and output `31-implementation-audit.md`. The checker must include `root-cause-phase` on every finding.
   - **Post-flight**: `python .ai/tools/dev-workflow/check_post_phase.py --phase implement --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Read verdict** from the `## Verdict` heading in `31-implementation-audit.md`.
   - **Route**:
     - `pass` or `pass with risks` → run `python .ai/tools/dev-workflow/validate_phase.py --phase implement --run-dir .ai/workflow/<slug>`. If validation passes, update manifest (phase status `accepted`) and stop with a summary. If validation fails, handle per the orchestrator's validation rules.
     - `fail` with `root-cause-phase: local` → increment round counter. On round > 1, copy `31-implementation-audit.md` to `31-implementation-audit-r<N>.md` where N is the round just completed (round 2 → `-r1`, round 3 → `-r2`) so the fresh-context checker sees prior findings and preserves finding ids, and include all prior `-r1`, `-r2`, … paths in the next round's context. Loop back to the doer pass. Round cap is 3; on cap, escalate.
     - `fail` with `root-cause-phase: upstream` (plan or research) → write a backward handoff packet `back-implement-to-<target>-<n>.md` using the format in the dev-workflow-orchestrator skill's `references/backward-handoff-format.md` (resolve the path from the installed orchestrator skill root, e.g. `.ai/skills/dev-workflow-orchestrator/references/backward-handoff-format.md`), validate it with `python .ai/tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir .ai/workflow/<slug>`, update manifest (target phase status `backward-edge-received`, increment backward edge count), print the finding and the recommended next step (instruct the user to run `/dev-workflow-plan <slug>` for plan issues or `/dev-workflow-research <slug>` for research issues), then stop. Backward edge cap is 2 per phase.
     - `blocked` → escalate immediately with a blocker summary and stop.
   - **Update manifest** after every step.

5. **Enforce Implement mode**: write source per the implementation plan; run tests and
   builds; write to `30-*.md` and `31-*.md` artifacts; no committing, pushing, deploying,
   or destructive commands.

## Optional arguments

- `<slug>` — existing run directory under `.ai/workflow/`.
- `--from <path> <slug>` — when no run dir exists, bootstraps a new run from an external implementation plan at `<path>`.

## Output

- Phase started, round number
- Verdict from implementation-auditor
- Backward edge created and routed (if any)
- Validation results
- Final summary: manifest phase status, terminal artifact path (`30-implementation-report.md`)

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
