---
name: dev-workflow-orchestrator
description: "Orchestrate the full development workflow — clarify → research → plan → implement → code-review → commit — with bounded loops, backward edges for upstream root causes, artifact contracts, and mode enforcement. Use when the user wants to run the complete dev workflow on a requirement or feature, resume an in-progress workflow run, or continue a workflow after a backward edge or escalation. Triggers on prompts to run the dev workflow, start a full development cycle, clarify-research-plan-implement-review-commit a feature, or resume a workflow run — even when the user doesn't say 'orchestrator'. Does not trigger for individual phase tasks (use the phase-specific skill directly), git mechanics alone (use git-guide), or code diff review without the full workflow (use code-reviewer)."
---

# Dev Workflow Orchestrator

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Orchestrate the 6-phase development workflow: clarify → research → plan → implement →
code-review → commit. The first phase (clarify) has no checker — it uses prompt-clarifier's
internal state machine. The remaining phases each contain a bounded loop (doer → checker →
revise). Backward edges route upstream root causes to earlier phases. The orchestrator owns
state, routing, and integration; the skills own production and checking.

## Primary Directive

Your job is to **orchestrate the workflow**, not to research, plan, implement, review, or
commit yourself. You invoke skills as named passes, read their verdicts, apply the loop
contracts, route backward edges, track state in the manifest, and enforce mode boundaries.
You are the brain; the skills are the producers.

## When to Use

- Running the full dev workflow on a requirement or feature
- Resuming an in-progress workflow run after interruption
- Continuing a workflow after a backward edge or escalation
- The user explicitly asks to run the dev workflow

## When NOT to Use

- **Individual phase tasks** — use the phase-specific skill directly (research-guide,
  plan-guide, plan-executor, code-reviewer, code-review-resolver, commit-message-writer)
- **Git mechanics alone** — use [../git-guide/SKILL.md](../git-guide/SKILL.md)
- **Code diff review without the full workflow** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Interactive research or brainstorming** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)

## Relationship to the dev-workflow guide

This skill automates the pipeline described in the `dev-workflow.md` guide at the repository root. That guide defines the intake classification (which phase to start from based on input type) and the governance tables (Mandatory vs Optional Gates by change class). The orchestrator relies on those decisions; this skill enforces them with artifact contracts and validation scripts. When the harness is not active, the guide's prose describes the same workflow for manual skill-by-skill use.

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

The workflow is a linear pipeline with backward edges. Each phase contains a bounded loop.

```
clarify → research → plan → implement → code-review → commit
   ↑         ↑          ↑        ↑          ↑
   └─────────┴──────────┴────────┴──────────┘
      backward edges (upstream root causes)
```

Backward edges (7 total):
- Research → Clarify (requirement fundamentally ambiguous)
- Plan → Research (research insufficient)
- Implement → Plan (plan unsafe/impossible)
- Implement → Research (requirement wrong)
- Code Review → Plan (design issue)
- Code Review → Research (approach wrong)
- Code Review → Implement (implementation defect rooted in execution approach)

See [References](#references) below for the full reference index — read each one before the step
that uses it.

## Orchestrator procedure

### Starting a run

1. Accept the requirement from the user.
2. Create a feature slug (kebab-case, descriptive).
3. Create the run directory: `.ai/workflow/<slug>/`.
4. Write `00-run-manifest.md` with initial state (current phase: clarify, all phases not-started). Use the template in [references/manifest-format.md](references/manifest-format.md) — it defines the required section headers (`# Run Manifest`, `## Run metadata`, `## Phase status`, `## Artifact registry`).
5. Write `01-feature-brief.md` with the requirement summary.
6. Activate clarify mode (see Mode enforcement below).
7. Record baseline: `python .ai/tools/dev-workflow/record_baseline.py --phase clarify --run-dir .ai/workflow/<slug>`. This captures the git HEAD and dirty paths at phase start so mode-enforcement checks can distinguish pre-existing changes from changes made during the phase.
8. Run pre-flight check: `python .ai/tools/dev-workflow/check_pre_phase.py --phase clarify --run-dir .ai/workflow/<slug>`.
9. Start Phase 0 (Clarify).

### Resuming a run

1. Read `00-run-manifest.md` from the run directory.
2. Identify: current phase, current round, backward edge counts, phase statuses.
3. Activate the appropriate mode for the current phase.
4. Continue from the current state — do not restart completed phases unless a backward edge requires it.

### Within a phase (the loop)

**Mode check:** If `Run mode: staged` and current phase is Implement, run the **staged iterator procedure** (see below) instead of the standard doer → checker loop. The staged iterator *replaces* the top-level Implement phase loop; the existing Loop 3 (plan-executor → implementation-auditor) runs *inside* the iterator per stage as the doer/checker pair. Otherwise, proceed with the Clarify or all-other-phases path below.

#### Staged iterator procedure (staged mode, Implement phase)

When `Run mode: staged`, iterate over the stages declared in plan §10 `Stage breakdown`:

For each stage N (1..total_stages):

1. **Record baseline:** Run `record_baseline.py --phase implement --run-dir <path>`.
2. **Pre-flight:** Run `check_pre_phase.py --phase implement --run-dir <path>`.
3. **Doer pass (stage-scoped):** Invoke `plan-executor` as a named pass with `--stage stage-N`. Tell it:
   - The input artifact path (`20-implementation-plan.md`).
   - The output artifact path (`30-stageN-implementation-report.md`).
   - The stage scope (only execute tasks listed in §10 Stage breakdown for stage-N).
   - The mode constraints for this phase.
4. **Checker pass:** Invoke `implementation-auditor` as a named pass. Tell it:
   - The input artifact path (`30-stageN-implementation-report.md`).
   - The output artifact path (`31-stageN-implementation-audit.md`).
   - To include the `root-cause-phase` field on every finding.
5. **Read verdict:** Read the audit verdict.
6. **Post-flight:** Run `check_post_phase.py --phase implement --run-dir <path>`.
7. **Route audit:**
   - `pass` or `pass with risks` → run `validate_phase.py --phase implement --run-dir <path>`. If validation passes, proceed to review (step 8). If validation fails, handle per validation rules below. (`validate_phase.py` takes no `--stage` argument: it validates the stage-indexed artifacts found on disk, resolving to the first `30-stageN-*`/`31-stageN-*` match. The current stage's own verdict is read at step 5.)
   - `fail` with `root-cause-phase: local` → escalate to full Loop 3 for this stage (increment round counter, cap 3). Loop back to doer pass.
   - `fail` with `root-cause-phase: upstream` → backward edge to Plan or Research.
   - `blocked` → escalate immediately.
8. **Review pass (light):** Invoke `code-reviewer` as a named pass. Tell it:
   - The input artifact path (the stage's diff or commit range).
   - The output artifact path (`40-stageN-code-review.md`).
   - Review effort: `standard` (not `deep` — the final deep review runs after all stages).
   - To include the `root-cause-phase` field on every finding.
9. **Read review verdict:**
   - `ready to commit` or `ready with notes` → proceed to commit (step 10).
   - `needs revision` with `blocker` or `major` findings → escalate to full Loop 4 for this stage (increment round counter, cap 5). Loop back to code-review-resolver.
   - `needs revision` with `root-cause-phase: upstream` → backward edge to Plan or Research.
10. **Per-stage commit:** Invoke `commit-message-writer` to draft the commit message, then `git-guide` to commit (per-stage commit only, no push). Record the commit hash in the manifest's `## Stage status` section.
11. **Stage-exit review (between stages, not after the last stage):** If this is not the last stage, invoke `plan-reviewer` in stage-exit review mode. The last stage skips the stage-exit review because the final deep review (below) provides cumulative validation. Tell it:
    - The input artifacts: `30-stageN-implementation-report.md`, `31-stageN-implementation-audit.md`, `40-stageN-code-review.md`, plan §4 assumptions, §10 stage breakdown for remaining stages.
    - The output artifact path (`32-stageN-exit-review.md`).
    - To emit `plan-current` or `plan-stale` per the stage-exit review contract.
12. **Route stage-exit verdict:**
    - `plan-current` → `plan-guide` performs light refinement of the next stage's task details. Proceed to next stage.
    - `plan-stale` → `plan-guide` performs full re-plan (re-derive remaining stages). `plan-reviewer` re-audits the revised plan. User re-confirms at a plan gate. Then resume from the affected stage.
13. **Update manifest** after every step.

**Backward-edge independence:** In-stage backward edges (e.g., `code-reviewer` `design` finding → `plan-guide`) are root-cause repair of the *current* stage's plan. They do **not** automatically trigger the between-stage stage-exit review. The two mechanisms are independent — backward edges repair root cause in-stage; stage-exit review judges forward-looking plan validity between stages.

#### Final deep review (after all stages commit)

After all stages are committed:

1. Run Loop 4 (code-reviewer → code-review-resolver, cap 5, `deep` effort; round-1 ordering per the Code Review exception — the reviewer runs first to produce findings) on the cumulative commit range (`HEAD~N..HEAD` where N = number of stage commits). Output: `40-final-deep-review.md`.
2. If findings: `code-review-resolver` applies fixes as **new commits on top** (no `git rebase`, no `git commit --amend` — fixes land as new commits on top, no amend/rebase). `code-reviewer` re-reviews the new commit range. Output: `41-final-fix-report.md`.
3. Run `validate_phase.py --phase code-review --run-dir <path>` to validate the final deep review (artifact structure, verdict, mode enforcement, handoff integrity). If validation fails, handle per validation rules below.
4. If a finding is design-level with `root-cause-phase: plan`, create a backward edge to `plan-guide` for root-cause repair.
5. If reader-visible contracts changed, invoke `techdoc-reviewer` (reader-visible contracts changed, invoke techdoc-reviewer).
6. Proceed to terminal delivery: `pull-request-guide` → `github-guide` (PR creation, once).

#### Standard procedure (linear mode, or non-Implement phases in staged mode)

For the Clarify phase (Phase 0), there is no checker. Run prompt-clarifier as a single named pass:

1. **Record baseline:** Run `record_baseline.py --phase clarify --run-dir <path>`. This captures the git HEAD and dirty paths at phase start.
2. **Pre-flight:** Run `check_pre_phase.py --phase clarify --run-dir <path>`. If it fails, stop and report.
3. **Clarifier pass:** Invoke prompt-clarifier as a named pass. Tell it:
   - The input artifact path (`01-feature-brief.md`).
   - The output artifact path (`02-requirement-ledger.md`).
   - To use the requirement ledger template at `<SKILL_ROOT>/references/requirement-ledger-template.md` (resolve `<SKILL_ROOT>` to the installed orchestrator skill directory; the ledger schema is also summarized in the prompt-clarifier skill itself).
   - The mode constraints for this phase (read-only, interactive).
4. **Read status:** prompt-clarifier's internal `CHECK` state is the exit condition. If `actionable`, proceed. If `blocked`, escalate immediately.
5. **Post-flight:** Run `check_post_phase.py --phase clarify --run-dir <path>`. If it fails, stop and report.
6. **Validate:** Run `validate_phase.py --phase clarify --run-dir <path>`. If validation passes, update manifest, go forward to Research.
7. **Update manifest** after every step.

For all other phases, run the doer → checker loop. **Code Review exception:** on round 1, the checker (code-reviewer) runs first to produce findings, then the doer (code-review-resolver) applies fixes. On subsequent rounds (round > 1), the doer runs first (applying fixes from the prior round's findings), then the checker re-reviews. This is because the resolver requires findings as input — there is nothing to resolve on a clean first pass.

1. **Record baseline:** Run `record_baseline.py --phase <name> --run-dir <path>`. This captures the git HEAD and dirty paths at phase start.
2. **Pre-flight:** Run `check_pre_phase.py --phase <name> --run-dir <path>`. If it fails, stop and report.
3. **Doer pass:** Invoke the doer skill as a named pass. Tell it:
   - The input artifact path (from the previous phase's terminal artifact or the requirement ledger for Research).
   - The output artifact path (per the artifact contract).
   - The mode constraints for this phase.
4. **Checker pass:** Invoke the checker skill as a named pass. Tell it:
   - The input artifact path (the doer's output).
   - The output artifact path (per the artifact contract).
   - To include the `root-cause-phase` field on every finding.
5. **Read verdict:** Read the checker's verdict and findings.
6. **Post-flight:** Run `check_post_phase.py --phase <name> --run-dir <path>`. If it fails, stop and report.
7. **Route:** Apply the loop contract:
   - **Accepted** (verdict is in the accept set) → run `validate_phase.py --phase <name> --run-dir <path>`. If validation passes, update manifest, go forward to next phase. If validation fails, handle per validation rules below.
   - **Needs revision** (root-cause-phase = `local`) → increment round counter. If round < cap: when the next round will be round > 1, first copy the current checker artifact to `<name>-r<N>.md` where `<N>` is the round number just completed (e.g. on round 2, copy `11-research-review.md` → `11-research-review-r1.md`; on round 3, copy → `11-research-review-r2.md`) so the fresh-context checker in the next round can see prior findings and preserve finding ids without overwriting earlier rounds; then loop back to doer pass with the checker's feedback, and include all prior `-r1`, `-r2`, … paths in the next round's task packet (native mode) or named-pass context (delegated mode). If round = cap, escalate.
   - **Needs revision** (root-cause-phase = upstream) → create backward handoff packet, route to target phase (see Backward edge below).
   - **Blocked** → escalate immediately.
8. **Update manifest** after every step.

### Backward edge

When a checker finding has `root-cause-phase` set to an earlier phase:

1. Check the backward edge count for the target phase in the manifest (< 2?).
2. Create a backward handoff packet at `back-<from>-to-<to>-<n>.md` (e.g. `back-code-review-to-plan-1.md`) using the format in [references/backward-handoff-format.md](references/backward-handoff-format.md).
3. Validate the packet: `python .ai/tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir <path>`.
4. Update manifest: target phase status = `backward-edge-received`, increment backward edge count.
5. Route to the target phase. The target phase:
   - Reads the backward handoff packet.
   - Fixes the specific issue (not the whole phase).
   - Re-produces its terminal artifact.
   - Re-runs its loop (doer → checker).
6. On acceptance, re-run downstream phases that depended on the changed artifact.
7. If the target phase also hits its cap or the backward edge count reaches 2, escalate to the user.

### Escalation

When a loop cap is hit without converging:

1. Mark the loop `NOT READY` with a blocker summary.
2. Read `root-cause-phase` from the checker's findings.
3. If upstream and backward edge count < 2: send backward edge.
4. If local or backward edge count = 2: stop, present blocker summary, ask user.

When a backward edge also doesn't resolve (target phase cap hit):

1. Stop the workflow.
2. Present the full blocker chain to the user.
3. Ask whether to retry, change scope, or abort.

### Validation handling

After running `validate_phase.py`:

1. Read the findings (errors and warnings).
2. For each **error**: default is to stop and fix. Override allowed only if you can articulate why proceeding is safe — record the override and justification in the manifest's validation log.
3. For each **warning**: default is to continue. Record the warning in the manifest's validation log.
4. All decisions (stop, continue, override) are logged in the manifest.

### Ending a run

1. After Phase 5 (Commit) completes, write `50-commit.md` with the commit hash.
2. Update manifest: status = `completed`, current phase = `done`.
3. Summarize for the user: artifacts created, commit hash, any accepted risks, backward edges that occurred.

## Mode enforcement

Mode is enforced by the orchestrator's per-phase instructions (prevention) and the validation scripts (detection). The mode rules are host-neutral — they are instructions in this skill, not host-specific rule files.

### Clarify mode

- Read-only source access. Inspect the codebase and conversation for context.
- Write only to `02-requirement-ledger.md`.
- Interactive: may ask the user clarifying questions.
- No editing source, tests, configs, or committing.
- No checker — the clarifier's internal `CHECK` state is the exit condition.

### Research mode

- Read-only source access. Inspect the codebase for research.
- Write only to `10-*.md` and `11-*.md` artifacts.
- No editing source, tests, configs, or committing.
- Subagents dispatched by advisory-council (if invoked) are also read-only.

### Plan mode

- Read-only source access. Inspect the codebase for planning.
- Write only to `20-*.md` and `21-*.md` artifacts.
- No editing source, tests, configs, or committing.

### Implement mode

- Write source per the implementation plan.
- Write to `30-*.md` and `31-*.md` artifacts.
- Run tests and builds — in **sync terminal mode** per `coding-behavior-guidelines.md` →
  Terminal execution. Never background builds/tests; a missed completion notification
  stalls the phase.
- No committing, pushing, deploying, or destructive commands.
- The auditor (implementation-auditor) is read-only within this phase.

### Code review mode

- Write source only to fix review findings (via code-review-resolver).
- Write to `40-*.md` and `41-*.md` artifacts.
- Run tests and builds — sync terminal mode, same contract as Implement mode.
- No committing, pushing, deploying, or scope expansion beyond findings.
- code-reviewer is read-only within this phase.

### Commit mode

- No source edits.
- Stage and commit only (via commit-message-writer to draft the message, then git-guide to commit).
- Write to `50-*.md` artifact.
- No push unless the user explicitly asks.

## Dispatch model

- The orchestrator selects a dispatch mode for checker phases per [references/dispatch-modes.md](references/dispatch-modes.md): **native** (spawn the checker as a subagent with a fresh isolated context), **delegated** (invoke the checker skill as a named pass — current behavior), or **simulated** (same as delegated, labeled honestly).
- Evaluate the dispatch mode **once per run** at phase 0 (Clarify) and record it in the manifest's `## Dispatch log` section. Host capability does not change mid-run.
- In **native mode**, the orchestrator constructs a task packet per checker dispatch (objective, input artifact path, output artifact path, read-only scope, verdict format, `root-cause-phase` requirement, prior-round `-r1` review path for rounds > 1) and spawns the checker agent as a subagent. Dispatch is by subagent type, not by agent description.
- In **delegated/simulated mode**, the orchestrator invokes the checker skill as a named pass with explicit input/output paths — the current behavior before the agent conversion.
- The orchestrator reads the verdict from the **on-disk artifact** (`## Verdict` heading), not from the subagent's return message. The artifact is the source of truth; the return message is a convenience (status + summary).
- The doer never reads the checker's verdict — only the orchestrator does.
- The checker owns the loop verdict; the orchestrator owns phase transitions and backward edges.
- If a subagent spawn fails (e.g., the pinned model is unavailable on the host), the orchestrator records the failure in the dispatch log and falls back to delegated mode for that checker. Do not silently retry or block the workflow.
- Phase 3 (Implement) may use real subagents internally via plan-executor + agent-runner. This is invisible to the orchestrator.
- Phase 1 (Research) may use advisory-council internally for consequential decisions. This is invisible to the orchestrator.

## State tracking

The orchestrator reads `00-run-manifest.md` at the start of every turn to know:
- Current phase and round
- Backward edge counts per phase
- Phase statuses
- Artifact registry
- Validation log

The manifest is the orchestrator's memory across turns. Without it, the orchestrator cannot resume. Always update the manifest after every step.

## References

Read each reference before the step that uses it. All paths are relative to `<SKILL_ROOT>`.

| Reference | Read before |
| --- | --- |
| [references/artifact-contract.md](references/artifact-contract.md) | Writing or consuming any phase artifact — the full artifact registry, naming scheme, stage-indexed variants, and boundary rules |
| [references/loop-contracts.md](references/loop-contracts.md) | Running any phase loop — doer/checker pairs, round caps, accept/revise/blocked verdicts, loop 0 (clarify), and the two staged-only loops |
| [references/backward-handoff-format.md](references/backward-handoff-format.md) | Creating a backward handoff packet (Backward edge procedure) |
| [references/manifest-format.md](references/manifest-format.md) | Starting or resuming a run — required manifest section headers (`# Run Manifest`, `## Run metadata`, `## Phase status`, `## Artifact registry`) and valid field values |
| [references/permission-matrix.md](references/permission-matrix.md) | Enforcing phase mode — per-phase read/write/commit permissions, staged-mode additions, and forbidden actions |
| [references/dispatch-modes.md](references/dispatch-modes.md) | Selecting a dispatch mode at phase 0 and constructing a checker task packet |
| [references/requirement-ledger-template.md](references/requirement-ledger-template.md) | The Clarify pass — pass this path to prompt-clarifier as its output template |

> **Installation note.** `tools/installer.py` copies the whole skill directory, so these files ship
> as `<skill-root>/references/*.md` in the target project. When passing a template path to a phase
> skill, pass the resolved path (e.g.
> `.ai/skills/dev-workflow-orchestrator/references/requirement-ledger-template.md`), not the
> bare `references/` form, which only resolves when the reader is already inside the skill root.

## Quality bar

- Never skip the pre-flight or post-flight checks.
- Never let a phase write outside its allowed artifacts.
- Never let the doer read the checker's verdict.
- Never proceed past a validation error without a recorded justification.
- Never exceed the backward edge cap of 2 without escalating to the user.
- Always update the manifest after every step.
- Always run the phase validation after a loop exits accepted.
