---
name: dev-workflow-review
description: Run the Code Review phase loop (code-review-resolver → code-reviewer)
  to acceptance or escalation on an existing or bootstrapped dev-workflow run. Loads
  the dev-workflow-orchestrator skill's Phase 4 procedure.
agent: agent
---

# Dev Workflow Review

Run **only the Code Review phase** (Loop 4) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 4 procedure and the `code-review-resolver` / `code-reviewer` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.ai/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** procedure for Phase 4 (Code Review). Treat
   `/dev-workflow-review` as the explicit start signal — proceed without asking for a
   second confirmation.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.ai/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.ai/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, first check the working
     tree: if `git diff --stat` produces no output (clean working tree), report "No
     changes to review — working tree is clean" and stop before synthesizing the report.
     Otherwise, create a feature slug (kebab-case), create `.ai/workflow/<slug>/`, and
     synthesize `30-implementation-report.md`
     from the working-tree diff with the required heading `# Implementation Report` plus
     minimal sections: a one-paragraph summary, a files-changed list from `git diff --stat`,
     and a `## Verification status` section with the body `unverified`. Write a minimal
     `00-run-manifest.md` with `Run status: in-progress`, `Current phase: code-review`,
     all phases `not-started` except Code Review (`in-progress`). Never use `skipped` or
     `fragment` as status values — they fail `manifest_checks.py`.

3. **Read or write the manifest**:
   - If the run dir exists, read `00-run-manifest.md`.
   - If bootstrapping, write the minimal manifest described in step 2.

4. **Run the Phase 4 loop** (doer → checker → revise) per the orchestrator skill.
   This procedure mirrors the orchestrator skill's `Within a phase (the loop)` — if the
   orchestrator's procedure changes, update all four `/dev-workflow-*` commands:
   - **Round-1 ordering (Code Review exception):** on round 1 the checker runs
     first — there are no findings to resolve on a clean first pass. On round > 1 the
     doer runs first (applying the prior round's fixes), then the checker re-reviews.
   - **Record baseline**: `python .ai/tools/dev-workflow/record_baseline.py --phase code-review --run-dir .ai/workflow/<slug>`
   - **Pre-flight**: `python .ai/tools/dev-workflow/check_pre_phase.py --phase code-review --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Checker pass (round 1)**: invoke `code-reviewer` as a named pass with input `30-implementation-report.md` (and the working-tree diff) and output `40-code-review.md`. The checker must include `root-cause-phase` on every finding.
   - **Doer pass**: invoke `code-review-resolver` as a named pass with the findings from `40-code-review.md` (and the working-tree diff) and output `41-fix-report.md`. On round > 1 the doer runs first, applying the prior round's findings, then the checker re-reviews.
   - **Post-flight**: `python .ai/tools/dev-workflow/check_post_phase.py --phase code-review --run-dir .ai/workflow/<slug>`. If it fails, stop and report.
   - **Read verdict** from the `## Verdict` heading in `40-code-review.md`.
   - **Route**:
     - `ready to commit` or `ready with notes` → run `python .ai/tools/dev-workflow/validate_phase.py --phase code-review --run-dir .ai/workflow/<slug>`. If validation passes, update manifest (phase status `accepted`) and stop with a summary. If validation fails, handle per the orchestrator's validation rules.
     - `needs revision` with `root-cause-phase: local` → increment round counter. On round > 1, copy `40-code-review.md` to `40-code-review-r1.md` so the fresh-context checker sees prior findings and preserves finding ids. Loop back to the doer pass. Round cap is 5; on cap, escalate.
     - `needs revision` with `root-cause-phase: upstream` (plan or research) → write a backward handoff packet `back-code-review-to-<target>-<n>.md` using the format in the dev-workflow-orchestrator skill's `references/backward-handoff-format.md` (resolve the path from the installed orchestrator skill root, e.g. `.ai/skills/dev-workflow-orchestrator/references/backward-handoff-format.md`), validate it with `python .ai/tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir .ai/workflow/<slug>`, update manifest (target phase status `backward-edge-received`, increment backward edge count), print the finding and the recommended next step (instruct the user to run `/dev-workflow-plan <slug>` for plan issues or `/dev-workflow-research <slug>` for research issues), then stop. Backward edge cap is 2 per phase.
     - `blocked` → escalate immediately with a blocker summary and stop.
   - **Update manifest** after every step.

5. **Enforce Code Review mode**: write source only to fix review findings (via
   `code-review-resolver`); write to `40-*.md` and `41-*.md` artifacts; run tests and builds;
   no committing, pushing, deploying, or scope expansion beyond findings.

## Optional arguments

- `<slug>` — existing run directory under `.ai/workflow/`.
- When no slug is given and no run dir exists, bootstraps from the working-tree diff.

## Output

- Phase started, round number
- Verdict from code-reviewer
- Backward edge created and routed (if any)
- Validation results
- Final summary: manifest phase status, terminal artifact path (`40-code-review.md`)

## On failure

| Condition | Action |
| --- | --- |
| Run directory not found | Report and stop |
| Clean working tree (no diff) on bootstrap | Report "No changes to review — working tree is clean" and stop |
| Pre-flight check fails | Report the missing artifacts and stop |
| Validation error (non-overridable) | Report the error and stop |
| Loop cap (5) hit with no backward edge available | Present blocker summary and ask the user |
| Backward edge cap (2) hit | Present the blocker chain and ask the user |

## Do not

- Skip the pre-flight or post-flight checks
- Let the phase write outside its allowed artifacts (`40-*.md`, `41-*.md`) and finding fixes
- Proceed past a validation error without a recorded justification
- Exceed the backward edge cap of 2 without escalating to the user
- Commit, push, deploy, or expand scope beyond findings
- Run phases other than Code Review
