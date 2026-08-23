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
  plan-guide, plan-executor, code-reviewer, git-commit)
- **Git mechanics alone** — use [../git-guide/SKILL.md](../git-guide/SKILL.md)
- **Code diff review without the full workflow** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Interactive research or brainstorming** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)

## Companion Skills

| Phase | Doer | Checker |
|-------|------|---------|
| Clarify | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) | — (internal state machine) |
| Research | [../research-guide/SKILL.md](../research-guide/SKILL.md) | [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md) |
| Plan | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) | [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) |
| Implement | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Code Review | [../finding-resolver/SKILL.md](../finding-resolver/SKILL.md) | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Commit | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) | — |

## Workflow topology

The workflow is a linear pipeline with backward edges. Each phase contains a bounded loop.

```
clarify → research → plan → implement → code-review → commit
   ↑         ↑          ↑        ↑          ↑
   └─────────┴──────────┴────────┴──────────┘
      backward edges (upstream root causes)
```

Backward edges (6 total):
- Research → Clarify (requirement fundamentally ambiguous)
- Plan → Research (research insufficient)
- Implement → Plan (plan unsafe/impossible)
- Implement → Research (requirement wrong)
- Code Review → Plan (design issue)
- Code Review → Research (approach wrong)

Read [references/artifact-contract.md](references/artifact-contract.md) for the full artifact
registry. Read [references/loop-contracts.md](references/loop-contracts.md) for the five loop
contracts (including the simplified clarify loop). Read [references/backward-handoff-format.md](references/backward-handoff-format.md)
for the backward handoff packet format. Read [references/manifest-format.md](references/manifest-format.md)
for the run manifest format. Read [references/permission-matrix.md](references/permission-matrix.md)
for the per-phase permission matrix. Read [references/requirement-ledger-template.md](references/requirement-ledger-template.md)
for the requirement ledger format.

## Orchestrator procedure

### Starting a run

1. Accept the requirement from the user.
2. Create a feature slug (kebab-case, descriptive).
3. Create the run directory: `.ai/workflow/<slug>/`.
4. Write `00-run-manifest.md` with initial state (current phase: clarify, all phases not-started). Use the template in [references/manifest-format.md](references/manifest-format.md) — it defines the required section headers (`# Run Manifest`, `## Run metadata`, `## Phase status`, `## Artifact registry`).
5. Write `01-feature-brief.md` with the requirement summary.
6. Activate clarify mode (see Mode enforcement below).
7. Record baseline: `python tools/dev-workflow/record_baseline.py --phase clarify --run-dir .ai/workflow/<slug>`. This captures the git HEAD and dirty paths at phase start so mode-enforcement checks can distinguish pre-existing changes from changes made during the phase.
8. Run pre-flight check: `python tools/dev-workflow/check_pre_phase.py --phase clarify --run-dir .ai/workflow/<slug>`.
9. Start Phase 0 (Clarify).

### Resuming a run

1. Read `00-run-manifest.md` from the run directory.
2. Identify: current phase, current round, backward edge counts, phase statuses.
3. Activate the appropriate mode for the current phase.
4. Continue from the current state — do not restart completed phases unless a backward edge requires it.

### Within a phase (the loop)

For the Clarify phase (Phase 0), there is no checker. Run prompt-clarifier as a single named pass:

1. **Record baseline:** Run `record_baseline.py --phase clarify --run-dir <path>`. This captures the git HEAD and dirty paths at phase start.
2. **Pre-flight:** Run `check_pre_phase.py --phase clarify --run-dir <path>`. If it fails, stop and report.
3. **Clarifier pass:** Invoke prompt-clarifier as a named pass. Tell it:
   - The input artifact path (`01-feature-brief.md`).
   - The output artifact path (`02-requirement-ledger.md`).
   - To use the requirement ledger template at `references/requirement-ledger-template.md`.
   - The mode constraints for this phase (read-only, interactive).
4. **Read status:** prompt-clarifier's internal `CHECK` state is the exit condition. If `actionable`, proceed. If `blocked`, escalate immediately.
5. **Post-flight:** Run `check_post_phase.py --phase clarify --run-dir <path>`. If it fails, stop and report.
6. **Validate:** Run `validate_phase.py --phase clarify --run-dir <path>`. If validation passes, update manifest, go forward to Research.
7. **Update manifest** after every step.

For all other phases, run the doer → checker loop:

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
   - **Needs revision** (root-cause-phase = `local`) → increment round counter. If round < cap, loop back to doer pass with the checker's feedback. If round = cap, escalate.
   - **Needs revision** (root-cause-phase = upstream) → create backward handoff packet, route to target phase (see Backward edge below).
   - **Blocked** → escalate immediately.
8. **Update manifest** after every step.

### Backward edge

When a checker finding has `root-cause-phase` set to an earlier phase:

1. Check the backward edge count for the target phase in the manifest (< 2?).
2. Create a backward handoff packet at `back-<from>-<to>-<n>.md` using the format in [references/backward-handoff-format.md](references/backward-handoff-format.md).
3. Validate the packet: `python tools/dev-workflow/validate_backward_edge.py --packet <path> --run-dir <path>`.
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
- Run tests and builds.
- No committing, pushing, deploying, or destructive commands.
- The auditor (implementation-auditor) is read-only within this phase.

### Code review mode

- Write source only to fix review findings (via finding-resolver).
- Write to `40-*.md` and `41-*.md` artifacts.
- Run tests and builds.
- No committing, pushing, deploying, or scope expansion beyond findings.
- code-reviewer is read-only within this phase.

### Commit mode

- No source edits.
- Stage and commit only (via git-commit command).
- Write to `50-*.md` artifact.
- No push unless the user explicitly asks.

## Dispatch model

- All phases use named passes at the orchestrator level.
- The orchestrator invokes each skill as a named pass with explicit input/output paths.
- The doer never reads the checker's verdict — only the orchestrator does.
- The checker owns the loop verdict; the orchestrator owns phase transitions and backward edges.
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

## Quality bar

- Never skip the pre-flight or post-flight checks.
- Never let a phase write outside its allowed artifacts.
- Never let the doer read the checker's verdict.
- Never proceed past a validation error without a recorded justification.
- Never exceed the backward edge cap of 2 without escalating to the user.
- Always update the manifest after every step.
- Always run the phase validation after a loop exits accepted.
