---
name: dev-workflow-research
description: Run the Research phase loop (research-guide → research-reviewer) to acceptance
  or escalation on an existing or bootstrapped dev-workflow run. Loads the dev-workflow-orchestrator
  skill's Phase 1 procedure.
---

# Dev Workflow Research

Run **only the Research phase** (Loop 1) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 1 procedure and the `research-guide` / `research-reviewer` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.ai/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** procedure for Phase 1 (Research). Treat
   `/dev-workflow-research` as the explicit start signal — proceed without asking for a
   second confirmation.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.ai/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.ai/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, create a feature slug
     (kebab-case) from the user's argument, create `.ai/workflow/<slug>/`, write
     `01-feature-brief.md` from the argument, and write a minimal `02-requirement-ledger.md`
     with required sections `# Requirement Ledger`, `## Outcome`, `## Scope`,
     `## Acceptance criteria`, `## Assumptions` (these sections come from
     `artifact_checks.py` `PHASE_ARTIFACTS["clarify"]` — the phase that produces this
     artifact — not `PHASE_ARTIFACTS["research"]`). Skip the Clarify phase.

3. **Read or write the manifest**:
   - If the run dir exists, read `00-run-manifest.md`.
   - If bootstrapping, write a minimal `00-run-manifest.md` with `Run status: in-progress`,
     `Current phase: research`, all phases `not-started` except Research (`in-progress`),
     and the artifact registry seeded with `01-feature-brief.md` and `02-requirement-ledger.md`.
     Never use `skipped` or `fragment` as status values — they fail `manifest_checks.py`.

4. **Run the Phase 1 loop** (doer → checker → revise) per the orchestrator skill.
   This procedure mirrors the orchestrator skill's `Within a phase (the loop)` — if the
   orchestrator's procedure changes, update all four `/dev-workflow-*` commands:
   - **Record baseline**: `python .ai/tools/dev-workflow/record_baseline.py --phase research --run-dir .ai/workflow/<slug>`
   - **Pre-flight**: `python .ai/tools/dev-workflow/check_pre_phase.py --phase research --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Doer pass**: invoke `research-guide` as a named pass with input `02-requirement-ledger.md` and output `10-research-report.md`.
   - **Checker pass**: invoke `research-reviewer` as a named pass with input `10-research-report.md` and output `11-research-review.md`. The checker must include `root-cause-phase` on every finding.
   - **Post-flight**: `python .ai/tools/dev-workflow/check_post_phase.py --phase research --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Read verdict** from the `## Verdict` heading in `11-research-review.md`.
   - **Route**:
     - `ready` or `conditionally ready` → run `python .ai/tools/dev-workflow/validate_phase.py --phase research --run-dir .ai/workflow/<slug>`. If validation passes, update manifest (phase status `accepted`) and stop with a summary. If validation fails, handle per the orchestrator's validation rules.
     - `needs revision` with `root-cause-phase: local` → increment round counter. On round > 1, copy `11-research-review.md` to `11-research-review-r1.md` so the fresh-context checker sees prior findings and preserves finding ids. Loop back to the doer pass. Round cap is 5; on cap, escalate.
     - `needs revision` with `root-cause-phase: upstream` (clarify) → write a backward handoff packet `back-research-to-clarify-<n>.md` using the format in `references/backward-handoff-format.md`, validate it with `python .ai/tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir .ai/workflow/<slug>`, update manifest (Clarify phase status `backward-edge-received`, increment backward edge count), print the finding and the recommended next step (since no `/dev-workflow-clarify` command exists, instruct the user to run `/dev-workflow` to resolve the Clarify issue, or resolve it manually), then stop. Backward edge cap is 2 per phase.
     - `blocked` → escalate immediately with a blocker summary and stop.
   - **Update manifest** after every step.

5. **Enforce Research mode**: read-only source access; write only to `10-*.md` and `11-*.md`
   artifacts; no editing source, tests, configs, or committing.

## Optional arguments

- `<slug>` — existing run directory under `.ai/workflow/`.
- `<requirement text>` — when no run dir exists, bootstraps a new run with the text as the feature brief.

## Output

- Phase started, round number
- Verdict from research-reviewer
- Backward edge created and routed (if any)
- Validation results
- Final summary: manifest phase status, terminal artifact path (`10-research-report.md`)

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
