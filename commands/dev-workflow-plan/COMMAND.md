---
name: dev-workflow-plan
description: Run the Plan phase loop (plan-guide → plan-reviewer) to acceptance or escalation on an existing or bootstrapped dev-workflow run. Loads the dev-workflow-orchestrator skill's Phase 2 procedure.
---

# Dev Workflow Plan

Run **only the Plan phase** (Loop 2) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 2 procedure and the `plan-guide` / `plan-reviewer` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.ai/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** procedure for Phase 2 (Plan). Treat `/dev-workflow-plan`
   as the explicit start signal — proceed without asking for a second confirmation.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.ai/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.ai/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, require `--from <path>`
     pointing at a research report. Verify the file is non-empty (if empty, report
     "`--from <path>`: file is empty" and stop before invoking plan-guide). Create a
     feature slug (kebab-case), create `.ai/workflow/<slug>/`, copy the external report
     to `10-research-report.md`, and write a minimal `00-run-manifest.md` with
     `Run status: in-progress`, `Current phase: plan`, all phases `not-started` except
     Plan (`in-progress`). Never use `skipped` or `fragment` as status values — they
     fail `manifest_checks.py`. Structural validation of the research report is delegated
     to `plan-guide`'s existing input validation.

3. **Read or write the manifest**:
   - If the run dir exists, read `00-run-manifest.md`.
   - If bootstrapping, write the minimal manifest described in step 2.

4. **Run the Phase 2 loop** (doer → checker → revise) per the orchestrator skill.
   This procedure mirrors the orchestrator skill's `Within a phase (the loop)` — if the
   orchestrator's procedure changes, update all four `/dev-workflow-*` commands:
   - **Record baseline**: `python .ai/tools/dev-workflow/record_baseline.py --phase plan --run-dir .ai/workflow/<slug>`
   - **Pre-flight**: `python .ai/tools/dev-workflow/check_pre_phase.py --phase plan --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Doer pass**: invoke `plan-guide` as a named pass with input `10-research-report.md` and output `20-implementation-plan.md`.
   - **Checker pass**: invoke `plan-reviewer` as a named pass with input `20-implementation-plan.md` and output `21-plan-review.md`. The checker must include `root-cause-phase` on every finding.
   - **Post-flight**: `python .ai/tools/dev-workflow/check_post_phase.py --phase plan --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Read verdict** from the `## Verdict` heading in `21-plan-review.md`.
   - **Route**:
     - `validated` or `conditionally validated` → run `python .ai/tools/dev-workflow/validate_phase.py --phase plan --run-dir .ai/workflow/<slug>`. If validation passes, update manifest (phase status `accepted`) and stop with a summary. If validation fails, handle per the orchestrator's validation rules.
     - `needs revision` with `root-cause-phase: local` → increment round counter. On round > 1, copy `21-plan-review.md` to `21-plan-review-r1.md` so the fresh-context checker sees prior findings and preserves finding ids. Loop back to the doer pass. Round cap is 3; on cap, escalate.
     - `needs revision` with `root-cause-phase: upstream` (research) → write a backward handoff packet `back-plan-to-research-<n>.md` using the format in the dev-workflow-orchestrator skill's `references/backward-handoff-format.md` (resolve the path from the installed orchestrator skill root, e.g. `.ai/skills/dev-workflow-orchestrator/references/backward-handoff-format.md`), validate it with `python .ai/tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir .ai/workflow/<slug>`, update manifest (Research phase status `backward-edge-received`, increment backward edge count), print the finding and the recommended next step (instruct the user to run `/dev-workflow-research <slug>` to resolve the Research issue), then stop. Backward edge cap is 2 per phase.
     - `blocked` → escalate immediately with a blocker summary and stop.
   - **Update manifest** after every step.

5. **Enforce Plan mode**: read-only source access; write only to `20-*.md` and `21-*.md`
   artifacts; no editing source, tests, configs, or committing.

## Optional arguments

- `<slug>` — existing run directory under `.ai/workflow/`.
- `--from <path> <slug>` — when no run dir exists, bootstraps a new run from an external research report at `<path>`.

## Output

- Phase started, round number
- Verdict from plan-reviewer
- Backward edge created and routed (if any)
- Validation results
- Final summary: manifest phase status, terminal artifact path (`20-implementation-plan.md`)

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
