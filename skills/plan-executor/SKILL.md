---
name: plan-executor
description: "Execute a provided implementation plan on the current git branch — decomposing independent units, dispatching concurrent subagents via agent-runner when supported, integrating results, running verifications, and producing an implementation report. Use when asked to implement/execute/run a written or approved plan, decompose a plan into units and execute them, implement a plan and verify the changes, or carry out plan tasks on the current branch without creating a new one. Does not trigger on plan authoring (plan-guide), plan audit (plan-reviewer), ad-hoc parallel dispatch without a plan, active merge/rebase integration (git-merge-guide), correctness audit (implementation-auditor), or diff review (code-reviewer)."
---

# Plan Executor

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`, and resolve `references/` paths from it.

Execute a provided implementation plan on the current git branch — dividing independent units across concurrent subagents when supported and always finishing with a review-ready implementation report. State at the start that `plan-executor` is active (and [../agent-runner/SKILL.md](../agent-runner/SKILL.md) when dispatching concurrent units).

## Primary Directive and Boundaries

Execute an implementation plan and produce an implementation report — do not author plans, run a full pre-execution plan audit, dispatch ad-hoc parallel tasks without a plan, or review code diffs.

**When NOT to use:**
- **Plan authoring or repair** → [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Pre-execution plan audit** → [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Generic parallel dispatch without a plan** → [../agent-runner/SKILL.md](../agent-runner/SKILL.md)
- **Post-execution correctness audit or diff review** → [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) or [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Codebase learning guides without a plan** → [../code-professor/SKILL.md](../code-professor/SKILL.md)
- **Commit, push, branch, worktree, or active merge/rebase integration** → [../git-guide/SKILL.md](../git-guide/SKILL.md) or [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md)

## Non-Negotiable Rules

- Require a readable implementation plan (inline or file path); ask for it if missing.
- Stay on the current git branch — never create, switch, or rename branches unless explicitly asked.
- Never commit, push, deploy, migrate production data, run destructive commands, or use unapproved secrets/external writes unless explicitly asked.
- Inspect `git status --short` before editing; stop and ask if unrelated dirty files overlap planned write paths, otherwise preserve them untouched.
- Follow the plan unless unsafe, impossible, internally inconsistent, or contradicted by repository state (prefer the plan's intent with a safer repo-consistent path over blind wording).
- Run stated and touched-area verifications, and produce an implementation report even if execution is partial or blocked.

## Workflow

### 1. Load, scope, and sanity-check the plan

1. Read the plan's intended outcome, target files, dependencies, test discipline, and verification commands; record current branch and `git status --short`.
2. **Stage scope (staged mode only):** If a stage scope is provided (e.g., `--stage stage-2`), read and execute only that stage's §10 `Stage breakdown` tasks and emit a stage-indexed report (`30-stageN-implementation-report.md`); otherwise execute the full plan. All non-negotiable rules still apply.
3. Sanity-check for missing prerequisites, contradictory steps, hidden broad refactors, or write overlaps before editing (lightweight execution check, not a full `plan-reviewer` audit).
4. Stop only when a gap makes execution unsafe or likely wrong (settle requirement-level ambiguity in the parent session via [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) or return to [../plan-guide/SKILL.md](../plan-guide/SKILL.md) — never pass ambiguity to a subagent); otherwise record a conservative assumption.

### 2. Partition into execution units and waves

Split work into cohesive units classified as **`parallel`** (strictly disjoint write paths and no ordering dependency), **`sequential`** (ordered dependency or shared mutable files), or **`integration`** (parent-led glue, docs, conflict resolution, and cross-unit checks). Execute wave by wave; if tasks are tightly coupled or share mutable files on the current branch, run them sequentially and note why in the report.

### 3. Dispatch concurrent waves (`agent-runner`)

When ≥2 `parallel` units exist in a wave and the host supports isolated subagents, follow [../agent-runner/SKILL.md](../agent-runner/SKILL.md) to launch the wave in a single batch using [references/execution-unit-template.md](references/execution-unit-template.md) (which defines the required plan/stage context, file ownership, branch/commit prohibitions, verification commands, and `Status`/`Findings`/`Changes`/`Verification`/`Risks` return contract). Keep integration authority in the parent session, inspect every subagent diff, and reject or redo out-of-scope edits, skipped verifications, or unrequested refactors. When concurrent subagents are unavailable, execute sequentially in dependency order and label it honestly.

### 4. Implement and integrate

Apply each task's planned test discipline:
- **`mandatory`** (or code tasks omitting discipline — note the assumption): strict red-green-refactor via [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md), observing the failing test before production edits.
- **`verification-led`**: run the plan's stated verification command and record the observed result (neither silently substitute TDD nor skip verification).
- **`n/a`**: run the stated non-code/config checks without TDD.

After each wave, inspect diffs for ownership violations or churn, resolve unit-level glue in the parent (hand off active git merge/rebase conflicts to [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md), restricting subagents to read-only while active), and run targeted wave checks.

### 5. Run final verification

- Run all plan-specified verification commands plus relevant touched-area test/build/lint/typecheck commands in **sync terminal mode** (never `&`/`nohup`/`disown`; use `timeout` only as a hang safety net; prefer concise output flags and quote only failing summaries + root-cause errors).
- On failure: fix obvious within-scope execution mistakes first; if the root cause is unclear, switch to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md); if the plan itself contradicts the repo or is unsafe, stop and return an execution-blocker report to [../plan-guide/SKILL.md](../plan-guide/SKILL.md). Do not expand scope endlessly on persistent out-of-scope failures.

### 6. Produce the implementation report

Format the report per [references/implementation-report-template.md](references/implementation-report-template.md) (summary, execution units/waves, `Files changed`, behavior/interface changes, verification table, assumptions, risks, and review focus). Suggest [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) when requirement-level proof is needed before [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md). Return the report in chat unless the user or orchestrator specifies an output file path.
