---
name: dev-workflow-orchestrator
description: "Orchestrate the full development workflow — clarify → research → plan → implement → code-review → commit — with bounded loops, backward edges for upstream root causes, artifact contracts, and mode enforcement. Use when the user wants to run the complete dev workflow on a requirement or feature, resume an in-progress workflow run, or continue a workflow after a backward edge or escalation. Triggers on prompts to run the dev workflow, start a full development cycle, clarify-research-plan-implement-review-commit a feature, or resume a workflow run — even when the user doesn't say 'orchestrator'. Does not trigger for individual phase tasks (use the phase-specific skill directly), git mechanics alone (use git-guide), or code diff review without the full workflow (use code-reviewer)."
---

# Dev Workflow Orchestrator

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Orchestrate the 6-phase development workflow: clarify → research → plan → implement →
code-review → commit. Clarify has no checker — prompt-clarifier's internal state machine is
its exit condition. The remaining phases each contain a bounded loop (doer → checker →
revise). Backward edges route upstream root causes to earlier phases. The orchestrator owns
state, routing, and integration; the skills own production and checking.

## Primary Directive

Your job is to **orchestrate the workflow**, not to research, plan, implement, review, or
commit yourself. You dispatch doer skills as named passes and checker skills per the recorded
dispatch mode (native subagent or named pass — see Dispatch model), read their verdicts, apply the loop
contracts, route backward edges, track state in the manifest, and enforce mode boundaries.

## When to Use

- Running the full dev workflow on a requirement or feature
- Resuming an in-progress workflow run after interruption
- Continuing a workflow after a backward edge or escalation

## When NOT to Use

- **Individual phase tasks** — use the phase-specific skill directly (research-guide,
  plan-guide, plan-executor, code-reviewer, code-review-resolver, commit-message-writer)
- **Git mechanics alone** — use [../git-guide/SKILL.md](../git-guide/SKILL.md)
- **Code diff review without the full workflow** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Interactive research or brainstorming** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)

## Relationship to the dev-workflow guide

This skill automates the pipeline in [references/dev-workflow.md](references/dev-workflow.md), which defines the intake classification (which phase to start from per input type) and the governance tables (Mandatory vs Optional Gates by change class); this skill enforces them with artifact contracts and validation scripts.

## Companion Skills

| Phase | Doer | Checker |
|-------|------|---------|
| Clarify | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) | — (internal state machine) |
| Research | [../research-guide/SKILL.md](../research-guide/SKILL.md) | [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md) |
| Plan | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) | [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) |
| Implement | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Code Review | [../code-review-resolver/SKILL.md](../code-review-resolver/SKILL.md) | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Commit | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) | — |

## Workflow topology

A linear pipeline with bounded per-phase loops; a checker finding with upstream `root-cause-phase` creates a backward edge to that earlier phase. Loop contracts, round caps, and the backward-edge cap live in [references/loop-contracts.md](references/loop-contracts.md).

## Orchestrator procedure

Read [references/permission-matrix.md](references/permission-matrix.md) — per-phase read/write/commit permissions, staged-mode additions, and forbidden actions — before any phase work, and enforce it throughout the phase.

### Starting a run

1. Accept the requirement; classify the intake (which phase to start from) per [references/dev-workflow.md](references/dev-workflow.md).
2. Create a feature slug (kebab-case) and the run directory `.agents/workflow/<slug>/`.
3. Write `00-run-manifest.md` with initial state (current phase: clarify, all phases not-started) using the required section headers from [references/manifest-format.md](references/manifest-format.md) (`# Run Manifest`, `## Run metadata`, `## Phase status`, `## Artifact registry`).
4. Write `01-feature-brief.md` with the requirement summary.
5. Record baseline: `python .agents/tools/dev-workflow/record_baseline.py --phase clarify --run-dir .agents/workflow/<slug>` — captures git HEAD and dirty paths so mode checks can distinguish pre-existing changes from phase-made ones.
6. Run pre-flight: `python .agents/tools/dev-workflow/check_pre_phase.py --phase clarify --run-dir .agents/workflow/<slug>`.
7. Start Phase 0 (Clarify).

### Resuming a run

1. Read `00-run-manifest.md` from the run directory: current phase, current round, backward edge counts, phase statuses.
2. Continue from the current state — do not restart completed phases unless a backward edge requires it.

### Within a phase (the loop)

**Mode check:** If `Run mode: staged` and current phase is Implement, run the **staged iterator** below instead of the standard loop. The staged iterator *replaces* the top-level Implement phase loop; Loop 3 (plan-executor → implementation-auditor) runs *inside* it per stage. Otherwise, use the standard procedure.

#### Staged iterator (staged mode, Implement phase)

Iterate over the stages declared in plan §10 `Stage breakdown`. Per-pass input/output artifact paths follow [references/artifact-contract.md](references/artifact-contract.md) (stage-indexed variants: `30-stageN-*`, `31-stageN-*`, `32-stageN-*`, `40-stageN-*`, `41-stageN-*`). Update the manifest after every step.

| Step | Action |
| --- | --- |
| 1. Baseline + pre-flight | `record_baseline.py --phase implement --run-dir <path>`; `check_pre_phase.py --phase implement --run-dir <path>` |
| 2. Doer (stage-scoped) | `plan-executor` named pass, `--stage stage-N` (execute only stage-N's §10 tasks) → `30-stageN-implementation-report.md` |
| 3. Checker | `implementation-auditor` per the recorded dispatch mode (native subagent task packet or named pass) → `31-stageN-implementation-audit.md`; `root-cause-phase` on every finding |
| 4. Post-flight + route audit | `check_post_phase.py --phase implement --run-dir <path>`. `pass`/`pass with risks` → `validate_phase.py --phase implement --run-dir <path> --stage N` (scoped to the current stage N; omit `--stage` only for cumulative final validation, which resolves the highest stage index deterministically) → step 5. `fail`+`local` → in-stage Loop 3 (cap 3) → step 2. `fail`+non-local → backward edge to the root-cause phase (Research, Clarify, or Plan). `blocked` → escalate |
| 5. Review (light) | `code-reviewer` per the recorded dispatch mode (native subagent task packet or named pass) on the stage's diff/commit range, effort `standard` (the final deep review is cumulative) → `40-stageN-code-review.md`; `root-cause-phase` on every finding |
| 6. Route review | `ready to commit`/`ready with notes` → step 7. `needs revision`+blocker/major → in-stage Loop 4 (cap 5, round-1 reviewer-first) → code-review-resolver. `needs revision`+non-local → backward edge |
| 7. Per-stage commit | `commit-message-writer` drafts, `git-guide` commits (per-stage only, no push); hash → manifest `## Stage status` |
| 8. Stage-exit review | Between stages only (last stage skips it). `plan-reviewer` in stage-exit mode per the recorded dispatch mode (native subagent task packet or named pass) over `30/31/40-stageN-*.md`, §4 assumptions, §10 remaining stages → `32-stageN-exit-review.md` |
| 9. Route exit verdict | `plan-current` → `plan-guide` lightly refines the next stage's tasks; next stage. `plan-stale` → full re-plan of remaining stages, `plan-reviewer` re-audit, user re-confirms at a plan gate, resume from the affected stage |

**Backward-edge independence:** in-stage backward edges repair the *current* stage's plan root cause; the between-stage stage-exit review judges forward-looking plan validity. The two mechanisms are independent — neither triggers the other.

#### Final deep review (after all stages commit)

1. Run Loop 4 (code-reviewer → code-review-resolver, round cap 5, `deep` effort, round-1 reviewer-first ordering) on the cumulative commit range (`HEAD~N..HEAD`, N = number of stage commits), dispatching code-reviewer per the recorded dispatch mode (native subagent task packet or named pass) → `40-final-deep-review.md`.
2. If findings: `code-review-resolver` applies fixes as **new commits on top** (no `git rebase`, no `git commit --amend`); `code-reviewer` re-reviews the new range → `41-final-fix-report.md`.
3. Run `validate_phase.py --phase code-review --run-dir <path>` (artifact structure, verdict, mode enforcement, handoff integrity); on failure, handle per Validation handling below.
4. If a finding is design-level with `root-cause-phase: plan`, create a backward edge to `plan-guide` for root-cause repair.
5. If reader-visible contracts changed, invoke techdoc-reviewer.
6. Proceed to terminal delivery: `github-guide` (PR authoring + creation, once).

#### Standard procedure (linear mode, or non-Implement phases in staged mode)

For the Clarify phase (Phase 0), there is no checker. Run prompt-clarifier as a single named pass:

1. **Baseline + pre-flight:** `record_baseline.py --phase clarify --run-dir <path>`; `check_pre_phase.py --phase clarify --run-dir <path>` — stop and report on failure.
2. **Clarifier pass:** prompt-clarifier as a named pass — input `01-feature-brief.md`, output `02-requirement-ledger.md` using the template at `<SKILL_ROOT>/../prompt-clarifier/references/requirement-ledger.md` (resolve `<SKILL_ROOT>` to the installed orchestrator skill directory); mode constraints: read-only, interactive.
3. **Read status:** prompt-clarifier's internal `CHECK` state is the exit condition. If `actionable`, proceed. If `blocked`, escalate immediately.
4. **Post-flight + validate:** `check_post_phase.py --phase clarify --run-dir <path>` — stop and report on failure; then `validate_phase.py --phase clarify --run-dir <path>`. On pass, update manifest, go forward to Research.
5. **Update manifest** after every step; refresh the manifest pin after the write with `python .agents/tools/dev-workflow/record_baseline.py --phase <current-phase> --run-dir <path> --manifest-only` (see State tracking).

For all other phases, run the doer → checker loop (round caps: research 5, plan 3, implement 3, code review 5). **Code Review exception:** on round 1 the checker (code-reviewer) runs first to produce findings, then the doer (code-review-resolver) applies fixes; on rounds > 1 the doer runs first (applying the prior round's findings), then the checker re-reviews — the resolver needs findings as input.

1. **Baseline + pre-flight:** `record_baseline.py --phase <name> --run-dir <path>`; `check_pre_phase.py --phase <name> --run-dir <path>` — stop and report on failure.
2. **Doer pass:** invoke the doer skill as a named pass with the input artifact path (the previous phase's terminal artifact, or the requirement ledger for Research), the output artifact path (per the artifact contract), and this phase's mode constraints.
3. **Checker pass:** per the recorded dispatch mode — in native mode, spawn the checker agent as a subagent with a task packet per [references/dispatch-modes.md](references/dispatch-modes.md); in delegated/simulated mode, invoke the checker skill as a named pass — with input (the doer's output) and output artifact paths per the artifact contract; require the `root-cause-phase` field on every finding.
4. **Read verdict + post-flight:** read the checker's verdict and findings; `check_post_phase.py --phase <name> --run-dir <path>` — stop and report on failure.
5. **Route:** apply the loop contract ([references/loop-contracts.md](references/loop-contracts.md)):
   - **Accepted** (verdict in the phase's accept set) → run `validate_phase.py --phase <name> --run-dir <path>`. On pass, update manifest, go forward to the next phase; on failure, handle per Validation handling below.
   - **Needs revision** (`root-cause-phase` = `local`) → increment the round counter. If round < cap: when the next round will be round > 1, first copy the current checker artifact to `<name>-r<N>.md` (N = round just completed, e.g. `11-research-review.md` → `11-research-review-r1.md` entering round 2) so the next round's fresh-context checker sees prior rounds' findings — which carry forward by id — without overwriting them; include all `-r<N>` paths in the next round's task packet (native mode) or named-pass context (delegated mode). Loop back to the doer pass with the checker's feedback. If round = cap, escalate.
   - **Needs revision** (`root-cause-phase` is not `local` — e.g. `research`, `clarify`, `plan`, `implement`) → create a backward handoff packet for the target phase, route to it (see Backward edge below). A backward edge routes only to an **earlier** phase; a checker tagging a later-phase or current-phase value other than `local` (e.g. `plan` during Research, `code-review` during Plan) is mis-tagging — treat the value as invalid, re-derive it from the finding, and do not create a packet.
   - **Blocked** → escalate immediately.
6. **Update manifest** after every step; refresh the manifest pin after the write with `python .agents/tools/dev-workflow/record_baseline.py --phase <current-phase> --run-dir <path> --manifest-only` (see State tracking).

### Backward edge

When a checker finding has `root-cause-phase` set to an earlier phase (later-phase values are unroutable mis-tags — re-derive instead of routing):

1. Check the backward edge count for the target phase in the manifest (< 2?).
2. Create a backward handoff packet at `back-<from>-to-<to>-<n>.md` (e.g. `back-code-review-to-plan-1.md`) using [references/backward-handoff-format.md](references/backward-handoff-format.md).
3. Validate the packet: `python .agents/tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir <path>`.
4. Update manifest: target phase status = `backward-edge-received`, increment backward edge count; refresh the manifest pin after the write (`record_baseline.py --phase <current-phase> --run-dir <path> --manifest-only`).
5. Route to the target phase: it reads the packet, fixes the specific issue (not the whole phase), re-produces its terminal artifact, and re-runs its loop (doer → checker).
6. On acceptance, re-run downstream phases that depended on the changed artifact.
7. If the target phase also hits its cap or the backward edge count reaches 2, escalate to the user.

### Escalation

When a loop cap is hit without converging: mark the loop `NOT READY` with a blocker summary; read `root-cause-phase` from the findings. If it names a phase **strictly earlier** than the current one (e.g. `research`, `clarify`, `plan` during Implement) and the backward edge count for that phase < 2, send a backward edge; a same-phase or later-phase value is a mis-tag — treat it as `local`. If it is `local` or the count = 2, stop, present the blocker summary, and ask the user.

Raise every user-facing ask here as a structured question — never a question buried in prose. Report the blocker chain: outcome first, chain after. When a backward edge also doesn't resolve (target phase cap hit): stop the workflow, present the full blocker chain, and ask whether to retry, change scope, or abort — as a structured question.

### Validation handling

After running `validate_phase.py`: for each **error**, default is to stop and fix — override only if you can articulate why proceeding is safe, and record the override and justification in the manifest's validation log; for each **warning**, default is to continue, recording it in the log. All decisions (stop, continue, override) are logged in the manifest.

### Ending a run

1. After Phase 5 (Commit) completes, write `50-commit.md` with the commit hash.
2. Update manifest: status = `completed`, current phase = `done`; refresh the manifest pin after the write (`record_baseline.py --phase <current-phase> --run-dir <path> --manifest-only`).
3. Summarize for the user: artifacts created, commit hash, any accepted risks, backward edges that occurred.

## Dispatch model

Select the checker dispatch mode per [references/dispatch-modes.md](references/dispatch-modes.md) — **native** (checker as a subagent with a fresh isolated context), **delegated** (checker as a named pass), or **simulated** (same as delegated, labeled honestly). Evaluate once per run — at phase 0 (Clarify) for full runs, or at bootstrap for command-bootstrapped runs, applying the same capability detection — record it in the manifest's `## Dispatch log` section, and construct checker task packets per the reference. The orchestrator itself enforces two rules:

- Read the verdict from the **on-disk artifact** (`## Verdict` heading), never from the subagent's return message — the artifact is the source of truth; the return message is a convenience (status + summary). The doer never reads the checker's verdict; the checker owns the loop verdict, the orchestrator owns phase transitions and backward edges.
- If a subagent spawn fails (or a spawned checker returns no verdict within the host's bounded window), classify the cause per dispatch-modes.md: retry the identical dispatch once on a transient failure; otherwise record the failure in the dispatch log and fall back to delegated mode for that checker. Do not block the workflow.

## State tracking

Read `00-run-manifest.md` at the start of every turn for the current phase and round, backward edge counts per phase, phase statuses, artifact registry, and validation log. The manifest is the orchestrator's memory across turns — without it, the orchestrator cannot resume. Always update it after every step, and **refresh the manifest pin after every orchestrator-owned manifest write** (`python .agents/tools/dev-workflow/record_baseline.py --phase <current-phase> --run-dir <path> --manifest-only`): mode enforcement pins the manifest's sha256 against the phase-start snapshot, so a manifest update without a pin refresh trips `check_post_phase.py`'s mode-enforcement error. `--manifest-only` updates only the snapshot's orchestrator-owned entries — never run a full `record_baseline.py` re-record mid-phase, because it would also reset the dirty-path and HEAD baselines that the source-edit and commit checks pin against, laundering any forbidden write made since phase start. Doers and checkers never touch the manifest — if a phase-owned pass appears to have modified it, that is a violation to report, not to re-record.

**Phase-boundary compaction checkpoint:** at each phase boundary, mark superseded round artifacts in the artifact registry and record a compaction note (mid-phase manifest writes are fine as long as the manifest pin is refreshed after each one — see State tracking). If context limits approach mid-run, end the turn at the next phase boundary and resume from the manifest — the run state survives the interruption by design.

## References

Read each reference before the step that uses it. All paths are relative to `<SKILL_ROOT>`.

| Reference | Read before |
| --- | --- |
| [references/dev-workflow.md](references/dev-workflow.md) | Starting a run — intake classification and governance tables this skill enforces |
| [references/artifact-contract.md](references/artifact-contract.md) | Writing or consuming any phase artifact — registry, naming scheme, stage-indexed variants, boundary rules |
| [references/loop-contracts.md](references/loop-contracts.md) | Running any phase loop — doer/checker pairs, round caps, accept/revise/blocked verdicts, loop 0, staged-only loops |
| [references/backward-handoff-format.md](references/backward-handoff-format.md) | Creating a backward handoff packet |
| [references/manifest-format.md](references/manifest-format.md) | Starting or resuming a run — manifest section headers and valid field values |
| [references/permission-matrix.md](references/permission-matrix.md) | Enforcing phase mode — per-phase permissions, staged-mode additions, forbidden actions |
| [references/dispatch-modes.md](references/dispatch-modes.md) | Selecting a dispatch mode at phase 0 and constructing a checker task packet |
| [../prompt-clarifier/references/requirement-ledger.md](../prompt-clarifier/references/requirement-ledger.md) | The Clarify pass — pass this path to prompt-clarifier as its output template |

> **Installation note.** `tools/installer.py` copies the whole skill directory, so these files ship
> as `<skill-root>/references/*.md` in the target project. When passing a template path to a phase
> skill, pass the resolved path (e.g.
> `.agents/skills/prompt-clarifier/references/requirement-ledger.md`), not the
> bare `references/` form, which only resolves when the reader is already inside the skill root.
