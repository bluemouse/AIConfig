---
name: plan-executor
description: "Use when executing a provided implementation plan in the current git working tree — decomposing it into independent units, dispatching concurrent subagents through agent-runner when possible, integrating on the current branch without creating or switching branches unless explicitly requested, running verifications, and producing an implementation report. Triggers on prompts to implement a written plan, execute plan tasks, or run an approved implementation plan on the current branch. Does not trigger on plan authoring, plan-reviewer audit, generic parallel dispatch without a plan, post-execution correctness audit (implementation-auditor), or post-implementation diff review."
---

# Plan Executor

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Execute a provided implementation plan against the current git branch. Prefer dividing the plan into independent execution units and running those units concurrently with subagents; always finish with a review-ready implementation report.

## Primary Directive

Your job is to **execute an implementation plan and produce an implementation report**, not to author plans, run a full pre-execution plan audit, dispatch generic parallel work without a plan, or review code diffs.

## When to Use

- The user supplies an implementation plan (inline or as a file path) to execute
- Running approved plan tasks on the current git branch without creating or switching branches unless explicitly requested
- Decomposing a plan into units, optionally parallelizing via [../agent-runner/SKILL.md](../agent-runner/SKILL.md), and integrating results
- Producing an implementation report for testing, debugging, and later code review

## When NOT to Use

- **Plan authoring or repair** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Pre-execution plan audit** — use [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Generic parallel dispatch without a plan** — use [../agent-runner/SKILL.md](../agent-runner/SKILL.md)
- **Post-implementation diff review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Post-execution correctness audit** — use
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
- **Codebase learning or architecture guides without a plan** — use
  [../code-professor/SKILL.md](../code-professor/SKILL.md)
- **Commit, push, branch, or worktree operations** — use [../git-guide/SKILL.md](../git-guide/SKILL.md)

## Overview

At the start, state that you are using the `plan-executor` skill. If concurrent subagents are available and two or more independent units exist, state that you are also using [../agent-runner/SKILL.md](../agent-runner/SKILL.md) for parallel execution.

## Non-Negotiable Rules

- Require an implementation plan as input, either inline or as a readable file path. If no plan is available, ask for it.
- Implement on the current git branch. Do not create, switch, or rename branches unless the user explicitly asks.
- Do not commit, push, deploy, migrate production data, or run destructive commands unless the user explicitly asks.
- Protect existing user work. Inspect the working tree before editing and do not overwrite unrelated uncommitted changes.
- Follow the plan unless it is unsafe, impossible, internally inconsistent, or conflicts with current repository state.
- Run the plan's stated verifications and the smallest relevant repository verifications needed to prove integration.
- Generate an implementation report even when execution is partial or blocked.

## Workflow

### 1. Load and review the plan

1. Read the full plan and identify the intended outcome, required files, dependencies, and verification steps.
2. Review critically before editing. Look for missing prerequisites, contradictory steps, unsafe actions, broad refactors hidden inside small tasks, or dependencies that prevent parallelization. This is a lightweight execution sanity check — not a substitute for [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md).
3. Stop for clarification only when the blocker would make implementation unsafe or likely wrong. Otherwise, make a conservative assumption and record it in the report.
4. Create a visible todo list or equivalent execution tracker from the plan.

### 2. Establish baseline

Before editing, inspect repository state:

- Current branch name.
- `git status --short` or equivalent.
- Existing uncommitted changes that appear unrelated to the plan.
- Relevant project commands from the plan, README, package files, build files, or existing CI config.

If unrelated user changes overlap files required by the plan, stop and ask how to proceed. If they do not overlap, continue and avoid touching them.

### 3. Divide the plan into execution units

Decompose the plan into units that are independently implementable. A good unit has:

- One clear objective.
- A bounded file/module ownership set.
- Minimal need for global context.
- Its own local verification command or inspection target.
- No write overlap with another concurrent unit.

Classify units as:

- **parallel**: can run at the same time with disjoint write scopes and no dependency ordering.
- **sequential**: depends on another unit's result or shares write ownership.
- **integration**: final parent-led glue, conflict resolution, cleanup, docs, and verification.

Use waves when needed: run all independent units in the current wave concurrently, integrate their results, then run the next dependent wave.

On the current branch, parallel units require strictly disjoint write paths. If units share mutable files or ordering dependencies, run them sequentially and explain why in the report.

Do not force parallelism. If the plan is tightly coupled, execute sequentially and explain why in the report.

### 4. Dispatch concurrent units with agent-runner

If two or more independent units exist and the host supports isolated subagents, read and follow [../agent-runner/SKILL.md](../agent-runner/SKILL.md) to dispatch all units in the same concurrent batch. Apply its wave sequencing, blocked/failed handling, and integration rules.

For each subagent, provide a self-contained task packet. Use [references/execution-unit-template.md](references/execution-unit-template.md) when composing the packet. Include:

- The relevant plan excerpt and exact unit objective.
- Allowed file ownership and files explicitly out of scope.
- Current branch constraint: work on the current branch context; do not create branches, commit, push, or deploy.
- Required commands or tests for that unit.
- Expected structured return matching the `agent-runner` contract: `Status` (`completed`, `blocked`, or `failed`), `Findings`, `Changes`, `Verification`, and `Risks`.

Parent responsibilities:

- Dispatch all agents for a parallel wave together, not one after another.
- Keep integration authority in the parent session.
- Review each agent's diff before accepting it.
- Reject or redo agent work that exceeds scope, edits shared files unexpectedly, skips verification, or makes unexplained broad changes.

If concurrent subagents are unavailable, execute the units directly in dependency order. Do not describe sequential work as parallel.

### 5. Implement and integrate

Before implementing a unit, read the plan's test discipline for its tasks. For tasks marked `mandatory` (the default for all code-producing work from [../plan-guide/SKILL.md](../plan-guide/SKILL.md)), apply strict red-green-refactor by following [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md): write and observe a failing test before the production change. For `n/a` tasks (non-code or check-only config/infra with justification), follow the plan's verification steps without TDD. If the plan omits test discipline on a code task, treat it as `mandatory` and note the assumption in the report.

For direct or parent-led work:

1. Mark the active unit as in progress.
2. Make the smallest plan-consistent change.
3. Run local verification for the unit when available.
4. Mark the unit complete only after verification or a recorded reason verification could not run.

For subagent work:

1. Read every subagent result fully.
2. Inspect diffs for ownership violations, conflicts, hidden refactors, generated files, and formatting-only churn.
3. Resolve conflicts in the parent session.
4. Run a targeted verification after each integration wave if the repo supports it.

### 6. Run final verification

After all units are integrated:

- Run every verification command specified by the plan.
- Run the most relevant existing test/build/lint/typecheck commands for touched areas.
- Prefer targeted verification first, then broader verification when cost is reasonable.
- If verification fails, first retry within the plan's scope: re-read the failing task, correct an obvious execution mistake, and rerun.
- If the failure is not an obvious execution mistake and its cause is unclear, switch to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root cause, apply the minimal fix, then resume execution.
- If the plan itself is unsafe, impossible, internally inconsistent, or contradicts the repository, stop and return to [../plan-guide/SKILL.md](../plan-guide/SKILL.md) with an execution-blocker report instead of forcing the plan through.
- If verification remains blocked or failing after these steps, stop expanding scope and report the exact failure, likely cause, and next debugging step.

### 7. Produce implementation report

Use [references/implementation-report-template.md](references/implementation-report-template.md) for the final report. Include enough detail for later testing, debugging, and code review:

- Branch and working-tree summary.
- Plan units executed, including parallel waves and subagents used.
- Files changed and why.
- Behavior/API/config/schema changes.
- Verification commands and outcomes.
- Known failures, skipped checks, assumptions, risks, and review focus areas.
- Suggested next manual tests or code-review checkpoints.
- When requirement-level proof is needed beyond the integration report, suggest
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) before
  [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md).

Do not create a report file in the repository unless the user or plan asks for one. Otherwise, provide the report in the final response.

## Stop Conditions

Stop and ask for help when:

- The implementation plan is missing or unreadable.
- The plan requires secrets, credentials, production access, deployment, destructive data operations, or external writes not explicitly authorized.
- The current working tree contains overlapping user changes that would be overwritten.
- The plan is ambiguous in a way that could produce the wrong architecture or public API.
- Required verification repeatedly fails for reasons outside the plan's scope.

## Quality Bar

- Preserve the plan's intent over incidental wording when repository evidence shows a safer equivalent path.
- Keep changes reviewable: small diffs, no unrelated cleanup, no opportunistic rewrites.
- Prefer existing project conventions over new patterns.
- Keep subagent scopes narrow; broad agents produce broad, risky diffs.
- Treat tests and reports as part of implementation, not an afterthought.

## Companion Skills

| Task | Path |
| --- | --- |
| Plan authoring and repair | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) |
| Pre-execution plan audit | [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md) |
| Parallel subagent dispatch | [../agent-runner/SKILL.md](../agent-runner/SKILL.md) |
| Post-implementation diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Post-execution correctness audit | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Commit, push, branch, worktree | [../git-guide/SKILL.md](../git-guide/SKILL.md) |
