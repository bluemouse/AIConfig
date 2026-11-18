---
name: review
description: Code Review phase loop when the user explicitly invokes /review.
---

# Dev Workflow Review

Run **only the Code Review phase** (Loop 4) of the dev-workflow harness to acceptance or
escalation, without driving the full pipeline. Loads the `dev-workflow-orchestrator`
skill's Phase 4 procedure and the `code-review-resolver` / `code-reviewer` skills.

## Steps

1. Read and follow the **dev-workflow-orchestrator** skill
   (`.agents/skills/dev-workflow-orchestrator/SKILL.md` or the installed tool skill), specifically
   the **Within a phase (the loop)** standard procedure for Phase 4 (Code Review). Treat
   `/review` as the explicit start signal — proceed without asking for a second
   confirmation. This command carries only the Code-Review-phase delta; the orchestrator
   owns the loop mechanics and its `references/loop-contracts.md` owns the contract
   details.

2. **Resolve the run directory** (one of):
   - **Explicit slug**: if the user passes `<slug>`, use `.agents/workflow/<slug>/`.
   - **Auto-detect**: if no slug is given and exactly one run dir exists under
     `.agents/workflow/`, use it. If zero or multiple run dirs exist, error and ask the user
     to pass an explicit `<slug>`.
   - **Bootstrap**: if no slug is given and no run dir exists, first check the working
     tree: if `git diff --stat` produces no output (clean working tree), report "No
     changes to review — working tree is clean" and stop. Otherwise, create a feature
     slug (kebab-case), create `.agents/workflow/<slug>/`, synthesize
     `30-implementation-report.md` from the working-tree diff with the heading
     `# Implementation Report` plus a one-paragraph summary, a files-changed list from
     `git diff --stat`, and a `## Verification status` section with the body `unverified`.
     Write a minimal `00-run-manifest.md` (`Run status: in-progress`, `Current phase:
     code-review`, all phases `not-started` except Code Review `in-progress`) plus a
     `## Dispatch log` section recording `Dispatch mode: native` or `delegated` per the
     orchestrator's capability detection; default to delegated and say so when
     uninspectable. Never use `skipped` or `fragment` as status values — they fail
     `manifest_checks.py`.

3. **Run the Phase 4 loop** with this delta:

   | Field | Value |
   | --- | --- |
   | Ordering | **Round 1: checker first** (code-reviewer runs on a clean pass — there are no findings to resolve yet); round > 1: doer first, then checker re-reviews |
   | Doer | `code-review-resolver`, input findings from `40-code-review.md` (and the working-tree diff), output `41-fix-report.md` |
   | Checker | `code-reviewer`, input `30-implementation-report.md` (and the working-tree diff), output `40-code-review.md` |
   | Round cap | 5 |
   | Accept verdicts | `ready to commit`, `ready with notes` (then `validate_phase.py --phase code-review`) |
   | Revise verdicts | `needs revision` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Backward targets | `plan` or `research` (packet `back-code-review-to-<target>-<n>.md` → user runs `/plan <slug>` or `/research <slug>`) and `clarify` (`back-code-review-to-clarify-<n>.md` → no `/clarify` command; `/run-dev-workflow` or manual) |
   | Blocked | code-reviewer emits no `blocked` verdict (an empty or unreachable diff yields `ready to commit`); if the artifact nonetheless carries one, treat it as an invalid verdict: report the mismatch and stop |
   | Mode | Write source only to fix review findings (via code-review-resolver); write to `40-*.md` and `41-*.md`; run tests and builds; no committing, pushing, deploying, or scope expansion beyond findings |

4. **Output**: phase started and round number; verdict from code-reviewer; backward
   edge created and routed (if any); validation results; final summary (manifest phase
   status, terminal artifact `40-code-review.md`).

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
