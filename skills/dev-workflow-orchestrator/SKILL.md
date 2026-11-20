---
name: dev-workflow-orchestrator
description: "Orchestrate the 6-phase development workflow (clarify → research → plan → implement → code-review → commit) with bounded doer/checker loops, backward edges, artifact contracts, and mode enforcement. Use to start a full feature workflow, resume an interrupted run, or continue after a backward edge or escalation — even without saying 'orchestrator'. Does not trigger for single-phase tasks, standalone git mechanics (git-guide), or standalone diff review (code-reviewer)."
---

# Dev Workflow Orchestrator

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`, and resolve `references/` paths from it.

Orchestrate the 6-phase pipeline (`clarify → research → plan → implement → code-review → commit`) defined in [references/dev-workflow.md](references/dev-workflow.md). Clarify exits via `prompt-clarifier`'s internal `CHECK` state; Research, Plan, Implement, and Code Review each run a bounded doer → checker loop ([references/loop-contracts.md](references/loop-contracts.md)), routing upstream `root-cause-phase` findings via backward edges.

## Primary Directive and Scope

Orchestrate state, routing, and validation — do not research, plan, implement, review, or commit directly. Dispatch doer skills as named passes and checker skills per the recorded dispatch mode ([references/dispatch-modes.md](references/dispatch-modes.md)).

**Use when:** starting a full workflow run, resuming an interrupted run, or continuing after a backward edge or escalation.
**Do not use when:** running a single phase task directly, standalone git mechanics ([../git-guide/SKILL.md](../git-guide/SKILL.md)), standalone diff review ([../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)), or open-ended brainstorming ([../research-guide/SKILL.md](../research-guide/SKILL.md)).

> **Standalone / partial-bundle fallback:** Full script-gated execution requires the `--dev-workflow` (`dev-workflow-harness`) install. If `.agents/tools/dev-workflow/` scripts or `code-review-resolver` are absent (e.g. standalone or `extended-dev-workflow` install without `--dev-workflow`), inform the user to install `--dev-workflow` for automated script-gated enforcement, or run manual artifact/diff checks only if the user explicitly approves.

## Companion Skills

| Phase | Doer | Checker |
|-------|------|---------|
| Clarify | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) | — (internal `CHECK` state) |
| Research | [../research-guide/SKILL.md](../research-guide/SKILL.md) | [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md) |
| Plan | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) | [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) |
| Implement | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Code Review | [../code-review-resolver/SKILL.md](../code-review-resolver/SKILL.md) | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Commit | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) | — |

## Orchestrator procedure

Enforce [references/permission-matrix.md](references/permission-matrix.md) across every phase, artifact naming/boundaries from [references/artifact-contract.md](references/artifact-contract.md), and manifest structure from [references/manifest-format.md](references/manifest-format.md).

### Starting or resuming a run

- **Start:** Classify intake per [references/dev-workflow.md](references/dev-workflow.md), create `.agents/workflow/<slug>/`, write `00-run-manifest.md` (`# Run Manifest`, `## Run metadata`, `## Phase status`, `## Artifact registry`, `## Dispatch log`) and `01-feature-brief.md`, record baseline (`python .agents/tools/dev-workflow/record_baseline.py --phase clarify --run-dir .agents/workflow/<slug>`), run `check_pre_phase.py --phase clarify --run-dir .agents/workflow/<slug>`, and start Phase 0 (Clarify).
- **Resume:** Read `00-run-manifest.md` and continue from the recorded phase/round without restarting accepted phases unless routed by a backward edge.

### Within a phase (the loop)

**Mode check:** If `Run mode: staged` and current phase is Implement, run the **staged iterator** below instead of the standard linear Implement loop. Otherwise use the standard procedure.

#### Staged iterator (staged mode, Implement phase)

Iterate over stages in plan §10 `Stage breakdown` using stage-indexed artifacts (`30/31/32/40/41-stageN-*.md` per [references/artifact-contract.md](references/artifact-contract.md)); update the manifest + manifest pin after each step.

| Step | Action |
| --- | --- |
| 1. Baseline + pre-flight | `record_baseline.py --phase implement --run-dir <path>`; `check_pre_phase.py --phase implement --run-dir <path>` |
| 2. Doer (stage-scoped) | `plan-executor` (`--stage stage-N`) → `30-stageN-implementation-report.md` |
| 3. Checker | `implementation-auditor` (native task packet or named pass) → `31-stageN-implementation-audit.md` (`root-cause-phase` on every finding) |
| 4. Post-flight + route audit | `check_post_phase.py --phase implement --run-dir <path>`. `pass`/`pass with risks` → `validate_phase.py --phase implement --run-dir <path> --stage N` (omit `--stage` only for cumulative final validation, which resolves the highest stage index deterministically) → step 5. `fail`+`local` → in-stage full loop (Loop 3, cap 3) → step 2. `fail`+earlier phase → backward edge. `blocked` → escalate |
| 5. Review (light) | `code-reviewer` (`standard` effort) on stage diff/range → `40-stageN-code-review.md` (`root-cause-phase` on every finding) |
| 6. Route review | `ready to commit`/`ready with notes` → step 7. `needs revision`+`local` → in-stage review loop (cap 3, round-1 reviewer-first) via `code-review-resolver`. `needs revision`+earlier phase → backward edge |
| 7. Per-stage commit | `commit-message-writer` + `git-guide` commit (per-stage only, no push); record hash in manifest `## Stage status` |
| 8. Stage-exit review | Between stages only (skip after final stage): `plan-reviewer` in stage-exit mode over `30/31/40-stageN-*.md`, §4 assumptions, and §10 remaining stages → `32-stageN-exit-review.md` |
| 9. Route exit verdict | `plan-current` → `plan-guide` lightly refines next stage's tasks; advance. `plan-stale` → full re-plan of remaining stages + `plan-reviewer` re-audit + user plan-gate confirmation, then resume |

In-stage backward edges (current-stage root-cause repair) and between-stage exit reviews (forward-looking plan validity) are independent — neither triggers the other.

#### Final deep review (after all stages commit)

1. Run Loop 4 (`code-reviewer` → `code-review-resolver`, cap 5, `deep` effort, round-1 reviewer-first) on the cumulative commit range (`HEAD~N..HEAD`) → `40-final-deep-review.md`.
2. Apply any fixes as **new commits on top** (no amend, no rebase) and re-review → `41-final-fix-report.md`.
3. Run `validate_phase.py --phase code-review --run-dir <path>`; route any `root-cause-phase: plan` design finding via backward edge; invoke `techdoc-reviewer` if reader-visible contracts changed; finish via `github-guide`.

#### Standard procedure (linear mode, or non-Implement phases in staged mode)

- **Clarify (Phase 0, no checker):** Run `record_baseline.py` + `check_pre_phase.py` (`--phase clarify`); invoke `prompt-clarifier` (input `01-feature-brief.md`, output `02-requirement-ledger.md` per `<SKILL_ROOT>/../prompt-clarifier/references/requirement-ledger.md`, read-only interactive). If `CHECK` is `blocked`, escalate immediately; if `actionable`, run `check_post_phase.py` + `validate_phase.py` (`--phase clarify`), update manifest + pin, and advance to Research.
- **Bounded loops (round caps: research 5, plan 3, implement 3, code review 5):** On Code Review round 1, run `code-reviewer` first, then `code-review-resolver` on rounds > 1 before re-review.
  1. **Baseline + pre-flight:** `record_baseline.py --phase <name> --run-dir <path>` and `check_pre_phase.py --phase <name> --run-dir <path>` (stop on failure).
  2. **Doer & checker passes:** run the doer named pass, then dispatch the checker per `## Dispatch log` (native subagent with a task packet per [references/dispatch-modes.md](references/dispatch-modes.md), or delegated named pass), requiring `root-cause-phase` on every finding.
  3. **Post-flight + route** ([references/loop-contracts.md](references/loop-contracts.md)): run `check_post_phase.py --phase <name> --run-dir <path>`, read the on-disk verdict, and route:
     - **Accepted:** run `validate_phase.py --phase <name> --run-dir <path>`; on pass, update manifest + pin (when exiting Plan, read `Execution mode` from `20-implementation-plan.md` §10 and set `Run mode: staged` or `linear` in `## Run metadata`) and advance.
     - **Needs revision (`local`):** if round < cap, before round > 1 copy the current checker artifact to `<name>-r<N>.md` (N = round just completed, e.g. `11-research-review.md` → `11-research-review-r1.md` entering round 2) and pass all `-r<N>` paths in the next round's task packet or named-pass context so findings carry forward by id; loop to doer. If round = cap, escalate.
     - **Needs revision (non-`local`):** if `root-cause-phase` names a strictly **earlier** phase, run Backward edge below; same-phase or later-phase tags are mis-tags — re-derive from the finding instead of creating a packet.
     - **Blocked:** escalate immediately.

### Backward edge, escalation, validation, and completion

- **Backward edge** ([references/backward-handoff-format.md](references/backward-handoff-format.md)): verify target phase's backward-edge count < 2; write `back-<from>-to-<to>-<n>.md`; run `validate_backward_edge.py --packet <path> --run-dir <path>`; mark target `backward-edge-received`, increment count, refresh manifest pin, re-run the target phase's focused repair + loop, and re-run affected downstream phases.
- **Escalation:** at loop cap (`NOT READY`), route to an earlier phase if `root-cause-phase` is strictly earlier and its count < 2 (treat same/later-phase mis-tags as `local`); otherwise (or when backward-edge count reaches 2) stop, report outcome + blocker chain, and ask the user whether to retry, rescope, or abort via a structured question (never buried in prose).
- **Validation handling:** after `validate_phase.py`, stop and fix errors by default (record any justified override in the manifest `## Validation log`); continue on warnings after logging them.
- **Ending a run:** after Phase 5 (Commit), write `50-commit.md`, set manifest `Run status: completed` and `Current phase: done`, refresh the manifest pin, and summarize artifacts, commit hash, accepted risks, and backward edges.

## Dispatch model and state tracking

- **Dispatch** ([references/dispatch-modes.md](references/dispatch-modes.md)): evaluate capability once (Phase 0 or command bootstrap), record `native`, `delegated`, or `simulated` in `## Dispatch log`, always read verdicts from the **on-disk `## Verdict` section** (never the subagent return message; the doer never reads the checker's verdict), and on transient spawn failure retry once before logging and falling back to `delegated` (hung/no-verdict checkers fall back immediately without blocking).
- **Manifest pin refresh:** read `00-run-manifest.md` every turn, update it after every step, and immediately run `python .agents/tools/dev-workflow/record_baseline.py --phase <current-phase> --run-dir <path> --manifest-only` so `check_post_phase.py` accepts orchestrator writes without resetting git HEAD or dirty-path baselines (never run a full `record_baseline.py` mid-phase; doers/checkers never edit the manifest). At phase boundaries, mark superseded round artifacts in `## Artifact registry` or pause cleanly if context limits approach.

## References

All paths resolve relative to `<SKILL_ROOT>` (pass resolved `.agents/skills/...` paths when handing a template path to another skill).

| Reference | Purpose |
| --- | --- |
| [references/dev-workflow.md](references/dev-workflow.md) | Intake classification and change-class governance tables |
| [references/artifact-contract.md](references/artifact-contract.md) | Artifact registry, numbering, stage-indexed variants, boundary rules |
| [references/loop-contracts.md](references/loop-contracts.md) | Loops 0–6 contracts, round caps, verdict sets, escalation rules |
| [references/backward-handoff-format.md](references/backward-handoff-format.md) | Backward handoff packet template and routing rules |
| [references/manifest-format.md](references/manifest-format.md) | `00-run-manifest.md` schema, valid status values, compaction rules |
| [references/permission-matrix.md](references/permission-matrix.md) | Per-phase read/write/commit permissions and staged-mode rules |
| [references/dispatch-modes.md](references/dispatch-modes.md) | Native/delegated/simulated capability detection, task packets, fallbacks |
| [references/checker-subagent-contract.md](references/checker-subagent-contract.md) | Shared fresh-context, verdict, finding, and boundary rules for checker agents |
| [references/reviewer-core/domain-lenses.md](references/reviewer-core/domain-lenses.md) | Shared domain review lenses consumed by research-reviewer and plan-reviewer |
| [references/reviewer-core/producer-feedback-loop.md](references/reviewer-core/producer-feedback-loop.md) | Shared doer/reviewer disposition loop for research and plan phases |
| [references/reviewer-core/re-review-protocol.md](references/reviewer-core/re-review-protocol.md) | Shared multi-round carry-forward and re-review protocol |
| [references/reviewer-core/review-quality-checklist.md](references/reviewer-core/review-quality-checklist.md) | Shared reviewer self-check before emitting a review report |
| [references/reviewer-core/reviewer-roles.md](references/reviewer-core/reviewer-roles.md) | Shared specialist reviewer role activation guidance |
| [../prompt-clarifier/references/requirement-ledger.md](../prompt-clarifier/references/requirement-ledger.md) | Clarify-phase output ledger schema |
