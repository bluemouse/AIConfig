---
name: git-merge-guide
description: "Guide complex local Git merges and rebases end-to-end: initiate operations, reconstruct intent from local history, resolve semantic conflicts, stage fixes without creating the final merge commit, continue rebases, review cleanly merged code for cross-branch integration bugs, run impact-based verification, and report results. Use when a local merge/rebase needs intent reconstruction, semantic resolution, combined-tree review, affected-test verification, or a merge report — even without saying git. Local evidence only; never fetch/push. Ask when intent is ambiguous; require permission before destructive ops. Does not trigger on push/fetch/pull, worktree lifecycle, simple single-file conflict triage (git-guide), cherry-pick/revert, final merge commits (git-guide), commit messages (commit-message-writer), diff review (code-reviewer), audits (implementation-auditor), plan execution (plan-executor), parallel dispatch (agent-runner), or debugging outside active integration (debugging-guide)."
---

# Git Merge Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Resolve merges and rebases as an integration engineer, not as a conflict-marker remover. Treat the unit of resolution as a logical code change, not a hunk. A clean textual merge is not evidence that the two branches compose correctly.

## Primary Directive

Your job is to **integrate two branch change sets correctly in the local repository** —
semantic conflict resolution, integration review of cleanly merged code, impact-based
verification, and accurate reporting — not to run general git mechanics, push/fetch,
manage worktrees, draft commit messages, or perform open-ended code review.

## When to Use

- Starting or continuing a local merge or rebase with conflicts or integration risk
- Reconstructing intent from local history to resolve textual, API, or behavioral conflicts
- Reviewing the combined tree for cross-branch semantic bugs in non-conflicted code
- Running impact-based tests and checks before declaring an integration verified
- Reporting merge/rebase results, including detailed merge reports on request
- Finishing an in-progress conflicted merge or rebase the user already started

## Boundary vs git-guide

Use this skill when the request is a **complex local integration**, not general Git
mechanics. Prefer [../git-guide/SKILL.md](../git-guide/SKILL.md) for simple triage only.

| Signal | Owner |
| --- | --- |
| Single-file or mechanical conflict (lockfile, imports, formatting) with no cross-branch semantic risk | `git-guide` |
| Intent reconstruction, API/behavioral conflict, or multi-file architectural integration | `git-merge-guide` |
| Active merge/rebase with verification, integration review, or merge report | `git-merge-guide` |
| Push/fetch/pull, stash, cherry-pick/revert, worktree create/merge/abandon/cleanup | `git-guide` |
| Final merge commit after integration is staged | `git-guide` (+ `commit-message-writer` if needed) |

Once this skill begins an active merge/rebase operation, it owns that operation's local Git
state through verification and reporting.

## When NOT to Use

- **Push, fetch, pull, or remote publication** — use
  [../git-guide/SKILL.md](../git-guide/SKILL.md); this skill is local-only
- **Worktree create, merge-back, abandon, or cleanup** — use
  [../git-guide/SKILL.md](../git-guide/SKILL.md). Operating inside an already-linked
  worktree during integration is allowed; this skill does not own worktree lifecycle.
- **Simple single-file conflict triage** — use
  [../git-guide/SKILL.md](../git-guide/SKILL.md)
- **Creating the final merge commit** — use
  [../git-guide/SKILL.md](../git-guide/SKILL.md); draft the message with
  [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) when needed
- **Cherry-pick or revert in progress** — use
  [../git-guide/SKILL.md](../git-guide/SKILL.md) unless the user explicitly extends this
  skill to that sequencer operation
- **Drafting Conventional Commit messages** — use
  [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md)
- **Structured diff review without an active merge/rebase integration** — use
  [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Post-implementation correctness audit or requirement coverage unrelated to branch integration** — use
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
- **Plan execution or generic parallel dispatch** — use
  [../plan-executor/SKILL.md](../plan-executor/SKILL.md) or
  [../agent-runner/SKILL.md](../agent-runner/SKILL.md)
- **Root-cause debugging of a single defect outside an active merge/rebase integration** — use
  [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)

## Core contract

- Operate only on the local repository and local terminal state. Do not browse the web, query hosting services, fetch, pull, push, or otherwise contact remotes.
- Initiate a requested merge or rebase when no operation is active and the request identifies the operation and target clearly.
- Fully drive a rebase, including commits created by normal `git rebase` / `git rebase --continue`, until it completes or a user decision is required.
- For a merge, use a no-commit workflow. Resolve and stage the complete merge result but do not create the final merge commit — even when the user asks to "finish the merge." Report that the merge is resolved and staged; creating the commit is a separate `git-guide` action.
- Never create unrelated/manual commits. Never push.
- Preserve unrelated local work exactly. Do not silently stash, reset, clean, restore, or overwrite it.
- Ask before destructive, history-discarding, or unrelated-work-overwriting actions. See "Approval gates" below.
- Ask when local evidence cannot establish intended behavior or multiple materially different correct resolutions remain plausible.
- Explain ambiguous choices with evidence, consequences, and a recommendation before asking the user to decide.
- Do not declare the integration successful merely because Git completed or conflicts disappeared. Require a clean integration review and passing impact-based verification first.

## Load the supporting guidance

- Read [references/operation-semantics.md](references/operation-semantics.md) before initiating or continuing a merge/rebase, especially for rebase stage semantics, replay baselines, and commit-dropping behavior.
- Read [references/conflict-investigation.md](references/conflict-investigation.md) whenever any nontrivial conflict exists or intent is not immediately obvious.
- Read [references/semantic-resolution.md](references/semantic-resolution.md) for behavioral/API/architectural conflicts, cross-file interactions, or any resolution requiring code changes beyond straightforward text integration.
- Read [references/integration-code-review.md](references/integration-code-review.md) after every conflict is resolved and its focused checks pass. Use it to review non-conflicted code for cross-branch semantic interactions.
- Read [references/testing-verification.md](references/testing-verification.md) to discover and run all directly or indirectly affected tests before declaring success.
- Read [references/validation.md](references/validation.md) for final structural Git and operation-state validation.
- Read [references/merge-report.md](references/merge-report.md) when reporting the result. Generate the detailed report only when the user explicitly requests it; otherwise return the compact inline summary.
- Run `<SKILL_ROOT>/scripts/collect-git-context.sh` when useful to collect a read-only snapshot of operation state and unmerged index stages.

## Workflow

### 1. Establish repository, baseline, and safety state

Before modifying anything:

1. Confirm the working directory is inside the intended Git repository and identify its root.
2. Determine whether a merge, rebase, cherry-pick, revert, or other sequencer operation is already active. If cherry-pick or revert is active, this skill does not cover those operations by default — explain that and hand off to [../git-guide/SKILL.md](../git-guide/SKILL.md) unless the user explicitly asks to apply this integration workflow to the in-progress operation.
3. If operating inside a linked worktree, confirm the worktree root with `git rev-parse --show-toplevel` and stay in that worktree for the entire operation. Do not switch to another checkout mid-integration. Record worktree-specific branch/HEAD state; baseline SHAs may differ from the primary checkout — see [references/operation-semantics.md](references/operation-semantics.md).
4. Record the current branch, `HEAD`, status, untracked files, staged changes, unstaged changes, and unmerged paths.
5. Record stable SHAs needed for later integration review and reporting: pre-operation branch tip, requested target/upstream tip, relevant merge base, and expected rebase replay list when applicable. Do not rely on branch labels that will move during the operation.
6. If an operation is already active, reconstruct the best available baseline from local Git metadata/reflog/history and continue that operation unless the user explicitly asked to abandon or replace it. Do not guess missing identities.
7. If no operation is active and unrelated local changes exist, do not start a merge/rebase that could mix with them. Ask the user how to handle the dirty state unless the request already gives explicit instructions.
8. Resolve branch names and target refs locally. If a required ref is absent, report that it is unavailable locally; do not fetch it.
9. For a requested operation on another local branch, switch to that branch only when the working tree is safe to switch.

Prefer explicit local commands such as `git status`, `git rev-parse`, `git branch`, `git log`, `git show`, `git diff`, `git merge-base`, `git ls-files -u`, `git blame`, and `git reflog`.

### 2. Initiate or resume the requested operation

- For a requested non-fast-forward merge, use `git merge --no-commit` so the resolved result can remain staged without creating the merge commit.
- Accept an unavoidable fast-forward merge as Git-level completion: it creates no merge commit. Still perform integration review and verification before calling the integration successful.
- For a requested rebase, start the exact requested local rebase. Prefer settings that prevent silent dropping of commits when supported; see [references/operation-semantics.md](references/operation-semantics.md).
- Treat the normal rewritten commits created by the explicitly requested rebase as authorized by that rebase request.
- Do not infer a more destructive interactive-rebase plan. Squash, fixup, reorder, edit, or drop commits only when explicitly requested or separately approved.

If Git completes without conflicts, skip conflict resolution but still perform integration code review, impact-based verification, structural validation, and reporting.

### 3. Build a conflict inventory

Before editing conflicted files:

1. List all unmerged paths and inspect index stages.
2. Classify conflicts by logical relationship, not merely by file:
   - straightforward textual overlap;
   - rename/move;
   - add/add;
   - modify/delete;
   - generated artifact;
   - binary/submodule;
   - API/type/schema contract;
   - behavioral/algorithmic;
   - cross-file architectural interaction.
3. Group conflicts that implement the same logical change. Analyze them together.
4. Identify likely high-risk conflicts first so apparently easy edits do not erase evidence needed to understand them.

Do not use `--ours` or `--theirs` as a reasoning shortcut. Their meanings differ by operation, especially during rebase.

#### Large integration triage

When many files or logical conflicts are present, prioritize by integration risk rather than file order:

1. API/type/schema contracts and generated-source inputs
2. Behavioral, algorithmic, and cross-file architectural conflicts
3. Rename/move, modify/delete, and add/add identity conflicts
4. Straightforward textual overlap, imports, and formatting-only hunks

Resolve high-risk groups first while preserving evidence in overlapping files. Batch similar low-risk conflicts only when their intentions are already established. Do not skip integration code review or impact-based verification to save time.

### 4. Reconstruct intent for every nontrivial conflict

For each logical conflict, establish:

- relevant base behavior before either competing change;
- what each side intended to add, fix, remove, or refactor;
- assumptions and invariants introduced by each side;
- whether intentions are independent, complementary, overlapping, superseding, sequential, or incompatible;
- which callers, tests, types, configuration, generated code, or neighboring code constrain the resolution.

Use local history aggressively: inspect commits that touched the affected code, commit messages, file history, blame, parent versions, and nearby commits. Search the repository for call sites, tests, analogous implementations, comments, and generated sources.

### 5. Form a resolution hypothesis before editing

State internally what the integrated code must do and how it preserves the relevant intentions. Then choose one resolution mode:

- **Adopt one side** only when local evidence shows the other change was superseded, irrelevant, or intentionally removed.
- **Combine both changes** when their intentions are compatible.
- **Rewrite the affected implementation** when mechanical combination would be incorrect or fragile.
- **Propagate integration changes** into non-conflicted callers/tests/types when required to make both intentions work together.
- **Ask the user** when intended behavior remains genuinely ambiguous or requires a product/architecture choice not recoverable from local evidence.

Never invent unrelated behavior merely to make tests pass.

### 6. Resolve and focused-test every logical conflict

1. Make the smallest coherent implementation that satisfies the resolution hypothesis; use a larger scoped rewrite when correctness requires it.
2. Remove conflict markers only as a consequence of implementing intended behavior.
3. Check the resolved diff immediately for accidental deletion, duplicated logic, stale branches, changed error handling, altered ownership/lifetime behavior, and mismatched API assumptions.
4. Run focused tests/checks that exercise the resolved behavior when available. Add or adapt a focused regression/integration test when it materially increases confidence.
5. Investigate failures as evidence of an integration defect or wrong hypothesis; do not weaken tests merely to obtain green results.
6. Stage the resolved files only after the logical conflict is coherent and its focused checks are acceptable.
7. Re-check `git diff --cached` and unmerged entries after staging.

These focused checks are an intermediate conflict-resolution gate only. They do not replace final impact-based verification.

### 7. Continue until all Git conflicts are resolved

For a rebase:

1. Confirm the current stop has no unresolved index entries and its focused conflict checks are acceptable.
2. Run normal `git rebase --continue` without invoking an interactive editor when the existing commit message can be preserved.
3. If the next replayed commit conflicts, restart the conflict inventory and intent investigation for that commit. Do not blindly reuse the previous resolution.
4. If Git wants to skip/drop a commit or a commit becomes empty, stop and follow the approval rules in [references/operation-semantics.md](references/operation-semantics.md).
5. Repeat until the rebase completes.

For a merge:

1. Resolve every logical conflict and run focused conflict checks.
2. Stage the complete intended merge result.
3. Do not run `git merge --continue` or `git commit`; either would create the final merge commit.
4. Leave the repository in the resolved merge state for later review and verification.

Do not report success yet.

### 8. Perform integration code review

After all conflicts are resolved and focused conflict checks pass, follow [references/integration-code-review.md](references/integration-code-review.md).

Review the complete integration with special focus on code Git merged without textual conflicts. Compare both original change sets against the final integrated tree and build an interaction map across changed symbols, callers/callees, shared state, contracts, lifetime/ownership, concurrency, asynchronous dependencies, configuration, generated artifacts, and tests.

Look for semantic collisions, precondition/postcondition drift, dependency and ordering bugs, async/concurrency bugs, stale API assumptions, duplicated or missing side effects, state-machine inconsistencies, cache/invalidation bugs, schema/serialization mismatches, platform/configuration gaps, and obsolete tests, plus any repository-specific integration risks discovered during review.

For each defect found:

1. Determine the two-branch interaction that causes it.
2. Fix it as an integration fix, including non-conflicted files when necessary.
3. Add/adapt focused tests where useful.
4. Stage the fix.
5. Re-review the affected semantic neighborhood and run focused checks.
6. Record the fix for the final summary/report.

For a completed rebase, leave post-rebase integration fixes staged and uncommitted. Do not amend/rewrite rebased commits merely to hide integration-review fixes.

If a correct fix requires an unresolved product/architecture decision, use the ambiguity gate.

### 9. Run impact-based testing and verification

Follow [references/testing-verification.md](references/testing-verification.md).

Discover tests affected directly or indirectly by **either original branch change set plus all integration fixes**. Use repository-local dependency information, call sites, build/test target relationships, component boundaries, configuration, asynchronous/runtime dependencies, and test organization to expand the impacted set.

Run the narrowest defensible affected set first, then broaden to dependent/component/integration/subsystem suites. If impact cannot be bounded confidently, broaden further, up to the full local test suite when necessary.

All required affected tests must pass before declaring `VERIFIED SUCCESS`. A required affected test that fails, is skipped, cannot run, or remains blocked means the integration is `NOT VERIFIED`.

When verification exposes a bug:

1. investigate it as an integration defect;
2. fix it without weakening valid tests;
3. perform a focused integration review of the affected semantic area;
4. update the affected-test set if the fix broadens impact;
5. rerun the relevant verification until all required affected tests pass.

If local evidence shows the failure is **not** caused by branch interaction — for example,
it reproduces on a pre-integration SHA or has no plausible two-branch cause — hand off to
[../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root cause, then return
here to resume integration coordination and reporting.

Also run applicable repository-local compile/typecheck, static analysis, lint, formatting/check-format, code generation consistency, and build checks required by the affected areas.

### 10. Perform final structural validation

Follow [references/validation.md](references/validation.md):

- verify no unresolved index entries remain;
- scan intended source files for accidental conflict markers;
- run `git diff --check` and inspect final staged/current diffs;
- verify rebase replay integrity or resolved merge metadata as applicable;
- confirm unrelated work remains untouched;
- capture final branch, `HEAD`, staged/unstaged/untracked state.

Only call the integration `VERIFIED SUCCESS` when integration code review has no unresolved defects/decisions, all required affected tests pass, applicable checks pass, and final structural validation is clean.

### 11. Report the result

Follow [references/merge-report.md](references/merge-report.md).

By default, return a compact inline summary highlighting:

- operation and refs;
- Git operation state versus integration verification state;
- number/nature of logical conflicts;
- non-conflicted integration bugs found and fixed;
- additional integration changes/fixes;
- affected tests/checks run and results;
- final local Git state and remaining user action.

Generate the detailed merge report only when the user explicitly requests a merge report or detailed report. Provide it inline by default unless the user asks for a file.

Do not push or offer to push automatically.

## Skill routing

Use this order when adjacent skills apply:

1. **During active integration** — this skill owns merge/rebase state, conflict resolution,
   integration review, affected-test verification, and reporting.
2. **Unclear verification failure** — [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
   proves root cause; return here afterward.
3. **Requirement or acceptance-criteria proof** — after integration verification,
   [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) audits requirement
   coverage separately.
4. **Optional final diff review** — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
   performs a read-only quality review; it does not replace integration review here.
5. **Final merge commit, push, or worktree mechanics** —
   [../git-guide/SKILL.md](../git-guide/SKILL.md) (+ `commit-message-writer` for message drafting).

While a merge/rebase operation is active, [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
and [../agent-runner/SKILL.md](../agent-runner/SKILL.md) may run **read-only** investigation
only. Do not allow concurrent writers against the live operation state.

## Status terminology

Keep Git mechanics separate from integration correctness:

- **Git operation: COMPLETED** - a rebase/fast-forward finished mechanically.
- **Merge state: RESOLVED AND STAGED** - a no-commit merge has no unresolved entries and awaits the user's final merge commit.
- **Integration verification: VERIFIED SUCCESS** - integration review is clean and every required affected test/check passed.
- **Integration verification: NOT VERIFIED** - any required review decision, affected test, check, or structural validation is unresolved, failed, skipped, or blocked.

Never describe an integration as successful based only on `git rebase` completion, compilation, or absence of conflict markers.

## Approval gates

### Always allowed within the requested operation

Perform these without extra permission when safe and relevant:

- read-only local Git/repository inspection;
- editing source and tests to implement well-supported conflict resolutions and integration fixes;
- staging intended resolutions/fixes with `git add` or equivalent index updates;
- starting the exact requested local merge or rebase;
- switching to the explicitly requested local branch when the tree is safe;
- normal rebase commits produced by `git rebase` / `git rebase --continue`;
- running local build, test, typecheck, static-analysis, lint, format, codegen, or validation commands that do not publish or destructively modify unrelated work.

### Never perform under this skill's standing authorization

Do not contact remotes or publish anything:

- `git push` or force-push;
- `git fetch`, `git pull`, `git ls-remote`, or hosting-service/API/network lookups;
- creating releases or remote branches/tags.

If the user separately asks for one of these, explain that it is outside this skill's local-only merge/rebase workflow and require explicit confirmation according to the surrounding environment's safety rules.

### Require explicit user permission

Stop before actions that intentionally discard, overwrite, or additionally rewrite work/history, including:

- `git reset` modes that move history or discard index/worktree state;
- `git clean`;
- destructive `git checkout` / `git restore` of existing changes;
- `git merge --abort`, `git rebase --abort`, or equivalent abort/reset recovery when additional work could be lost;
- `git rebase --skip`;
- dropping commits, or allowing a rebase to silently discard an existing commit;
- adding squash/fixup/reorder/edit operations not already explicitly requested;
- deleting branches or tags;
- overwriting unrelated uncommitted changes;
- creating a manual/final merge commit;
- amending or rewriting completed rebase commits to absorb post-rebase integration fixes.

When unsure whether an action could lose unrelated work or history, treat it as permission-gated.

## Ambiguity gate

Ask only after doing enough local research to make the question precise. Do not ask the user to choose "ours or theirs" without explaining semantics.

Present:

1. **Conflict/decision:** what behavior cannot be inferred.
2. **Evidence:** what local history and code indicate about each intention.
3. **Options:** materially different implementations and consequences.
4. **Recommendation:** the option best supported by correctness, history, and integration goals.
5. **Question:** ask the user to choose or clarify the missing intent.

Continue independent analysis only when it cannot corrupt or invalidate the pending decision. Do not stage a speculative resolution for the ambiguous logical conflict.

## Companion Skills

| Task | Path |
|------|------|
| Push, fetch, final merge commit, worktree lifecycle, simple conflict triage | [../git-guide/SKILL.md](../git-guide/SKILL.md) |
| Draft Conventional Commit messages from diffs | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) |
| Optional read-only final diff review after integration | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Requirement coverage audit after integration verification | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Root-cause debugging when failure cause is unclear | [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) |
| Plan execution during active integration (read-only only) | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
| Parallel dispatch during active integration (read-only only) | [../agent-runner/SKILL.md](../agent-runner/SKILL.md) |
| PR description, sizing, self-review | [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md) |
