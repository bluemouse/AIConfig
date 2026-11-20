---
name: review
description: Code Review phase loop when the user explicitly invokes /review.
---

# Dev Workflow Review

Run **only the Code Review phase** (Loop 4) of the dev-workflow harness to acceptance or escalation, loading `dev-workflow-orchestrator`, `code-review-resolver`, and `code-reviewer`.

## Steps

1. Read and follow `.agents/skills/dev-workflow-orchestrator/SKILL.md` (**Within a phase (the loop)** for Phase 4); `/review` is the explicit start signal. This command carries only the Code Review delta — the orchestrator owns loop mechanics, validation handling, and manifest pin refresh (`references/loop-contracts.md`).

2. **Resolve `.agents/workflow/<slug>/` and manifest**:
   - **Explicit `<slug>`**: use `.agents/workflow/<slug>/` and read `00-run-manifest.md` (if missing, report and stop).
   - **Auto-detect**: if no `<slug>` and one run dir exists under `.agents/workflow/`, use it; if zero or multiple exist (when not bootstrapping), ask for `<slug>`.
   - **Bootstrap**: if no `<slug>` and no run dir exists, first check `git status --porcelain`: if it produces no output (clean working tree), report "No changes to review — working tree is clean" and stop. Otherwise, create `.agents/workflow/<slug>/`, synthesize `30-implementation-report.md` with `# Implementation Report`, a summary paragraph, an explicit `## Files changed` section (populated from `git status --short` / `git diff HEAD --stat`), and `## Verification status` (`unverified`). Write `00-run-manifest.md` per `.agents/skills/dev-workflow-orchestrator/references/manifest-format.md` with `# Run Manifest`, `## Run metadata` (`Run status: in-progress`, `Current phase: code-review`), `## Phase status` (Code Review `in-progress`, others `not-started`), `## Artifact registry` (`30-implementation-report.md`), and `## Dispatch log` recording `Dispatch mode: native` or `delegated` per `references/dispatch-modes.md` (default to delegated and say so when uninspectable) plus `Evaluated at: bootstrap`. Never use `skipped` or `fragment`.

3. **Run the Phase 4 loop**:

   | Field | Value |
   | --- | --- |
   | Ordering | **Round 1: checker first** (`code-reviewer` runs first; round > 1: `code-review-resolver` applies fixes, then `code-reviewer` re-reviews) |
   | Doer | `code-review-resolver`, input findings from `40-code-review.md` (and working-tree diff), output `41-fix-report.md` |
   | Checker | `code-reviewer`, input `30-implementation-report.md` (and working-tree diff), output `40-code-review.md` |
   | Round cap | 5 |
   | Accept verdicts | `ready to commit`, `ready with notes` (then `validate_phase.py --phase code-review`) |
   | Revise verdicts | `needs revision` — `local` loops to the round cap; non-local creates a backward packet per Backward targets |
   | Backward targets | `implement`, `plan`, or `research` (`back-code-review-to-<target>-<n>.md` → `/implement <slug>`, `/plan <slug>`, or `/research <slug>`) and `clarify` (`back-code-review-to-clarify-<n>.md` → `/run-dev-workflow` or manual) |
   | Blocked | `code-reviewer` emits no `blocked` verdict; if an artifact carries one, report the invalid verdict and stop |
   | Mode | Write source only to fix review findings (via `code-review-resolver`); write `40-*.md` and `41-*.md`; run tests/builds; no committing, pushing, deploying, or scope expansion |

## Output and guardrails

- **Output**: phase/round, code-reviewer verdict, backward edge routed (if any), validation result, manifest phase status, and `40-code-review.md`.
- **On failure**: on bootstrap with a clean working tree (`git status --porcelain` empty), report "No changes to review — working tree is clean" and stop; defer pre/post-flight, validation-error, round-cap (5), and backward-edge-cap (2) handling to `dev-workflow-orchestrator`.
- **Do not**: write outside finding fixes and `40-*.md` / `41-*.md`, expand scope beyond findings, commit/push/deploy, skip pre/post-flight or validation rules, or run phases other than Code Review.
