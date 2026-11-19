---
name: git-merge-guide
description: "Guide complex local Git merges and rebases end-to-end: initiate operations, reconstruct intent from local history, resolve semantic conflicts, stage fixes without creating the final merge commit, continue rebases, review cleanly merged code for cross-branch integration bugs, run impact-based verification, and report results. Use when a local merge/rebase needs intent reconstruction, semantic resolution, combined-tree review, affected-test verification, or a merge report — even without saying git. Local evidence only; never fetch/push. Ask when intent is ambiguous; require permission before destructive ops. Does not trigger on push/fetch/pull, worktree lifecycle, simple single-file conflict triage (git-guide), cherry-pick/revert, final merge commits (git-guide), commit-message drafting (git-guide), diff review (code-reviewer), audits (implementation-auditor), plan execution (plan-executor), parallel dispatch (agent-runner), or debugging outside active integration (debugging-guide)."
---

# Git Merge Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Resolve merges and rebases as an integration engineer, not as a conflict-marker remover. Treat the unit of resolution as a logical code change, not a hunk. A clean textual merge is not evidence that the two branches compose correctly.

## Core contract

- Integrate two branch change sets correctly in the local repository — semantic conflict resolution, integration review of cleanly merged code, impact-based verification, accurate reporting — not general git mechanics, worktree management, commit-message drafting, or open-ended code review.
- Operate only on the local repository. Never browse the web, query hosting services, fetch, pull, push, or otherwise contact remotes.
- For a merge, use a no-commit workflow. Resolve and stage the complete merge result but do not create the final merge commit — even when the user asks to "finish the merge." Report that the merge is resolved and staged; creating the commit is a separate `git-guide` action.
- Fully drive a rebase, including commits created by normal `git rebase` / `git rebase --continue`, until it completes or a user decision is required. Never create unrelated/manual commits. Never push.
- Preserve unrelated local work exactly; never silently stash, reset, clean, restore, or overwrite it. Ask before destructive, history-discarding, or unrelated-work-overwriting actions (see "Approval gates").
- Ask when local evidence cannot establish intended behavior or multiple materially different correct resolutions remain plausible; explain the options with evidence, consequences, and a recommendation first.
- Do not declare the integration successful merely because Git completed or conflicts disappeared. Require a clean integration review and passing impact-based verification first.

## Boundary and companions

Use this skill for complex local integration — intent reconstruction, semantic resolution, combined-tree review, affected-test verification, and merge reports. Once it begins an active merge/rebase, this skill owns that operation's local Git state through verification and reporting. Operating inside an already-linked worktree during integration is allowed; this skill does not own worktree lifecycle. Cherry-pick/revert are covered only when the user explicitly extends this skill to them.

| Task | Path |
|------|------|
| Push/fetch/pull, stash, cherry-pick/revert, worktree lifecycle, simple single-file conflict triage, final merge commit, commit-message drafting | [../git-guide/SKILL.md](../git-guide/SKILL.md) |
| Structured diff review without an active integration | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Requirement coverage audit unrelated to branch integration | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Root-cause debugging of a single defect outside active integration, or proving a failure is not integration-caused | [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) |
| Plan execution / parallel dispatch during active integration | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) / [../agent-runner/SKILL.md](../agent-runner/SKILL.md) — read-only only; no concurrent writers against the live operation state |
| PR description, sizing, self-review | [../github-guide/SKILL.md](../github-guide/SKILL.md) |

## Load the supporting guidance

Read each reference at its workflow step:

- [references/operation-semantics.md](references/operation-semantics.md) — merge/rebase initiation, stage semantics, replay baselines, commit-dropping behavior.
- [references/conflict-investigation.md](references/conflict-investigation.md) — nontrivial conflicts or unclear intent.
- [references/semantic-resolution.md](references/semantic-resolution.md) — behavioral/API/architectural conflicts and cross-file interactions.
- [references/integration-code-review.md](references/integration-code-review.md) — combined-tree integration review (step 8).
- [references/testing-verification.md](references/testing-verification.md) — affected-test discovery and verification (step 9).
- [references/validation.md](references/validation.md) — final structural validation (step 10).
- [references/merge-report.md](references/merge-report.md) — reporting (step 11); detailed report only on explicit request.
- `<SKILL_ROOT>/scripts/collect-git-context.sh` — read-only snapshot of operation state and unmerged index stages.

## Workflow

### 1. Establish repository, baseline, and safety state

1. Confirm the working directory is inside the intended Git repository; record branch, `HEAD`, status, untracked files, staged/unstaged changes, and unmerged paths.
2. If a merge/rebase is already active, reconstruct the best available baseline from local metadata/reflog/history and continue it unless the user explicitly asked to abandon or replace it; do not guess missing identities. If cherry-pick or revert is active, hand off to [../git-guide/SKILL.md](../git-guide/SKILL.md) unless the user explicitly extends this workflow to it.
3. If inside a linked worktree, confirm its root with `git rev-parse --show-toplevel`, stay in that worktree for the entire operation, and record worktree-specific branch/HEAD state — baseline SHAs may differ from the primary checkout.
4. Record stable SHAs needed later (pre-operation branch tip, target/upstream tip, merge base, expected rebase replay list); do not rely on branch labels that will move during the operation.
5. If no operation is active and unrelated local changes exist, do not start a merge/rebase that could mix with them; ask how to handle the dirty state unless the request already gives explicit instructions.
6. Resolve branch names and target refs locally; a required ref absent locally is reported unavailable, never fetched. Switch to a requested local branch only when the tree is safe to switch.

Run read-only git commands with `--no-pager` (or `GIT_PAGER=cat`); `git log`, `git show`, `git diff`, `git blame`, and `git reflog` invoke the default pager when stdout is a TTY and will block on stdin if paged.

### 2. Initiate or resume the requested operation

- For a requested non-fast-forward merge, use `git merge --no-commit` so the resolved result can remain staged without creating the merge commit. Accept an unavoidable fast-forward as Git-level completion; still perform integration review and verification.
- Start the exact requested local rebase, preferring settings that prevent silent commit-dropping when supported. Treat the normal rewritten commits created by the explicitly requested rebase as authorized by that request. Do not infer a more destructive interactive-rebase plan; squash, fixup, reorder, edit, or drop commits only when explicitly requested or separately approved.

If Git completes without conflicts, skip conflict resolution but still perform integration code review, impact-based verification, structural validation, and reporting.

### 3. Build a conflict inventory

Before editing conflicted files, list all unmerged paths and inspect index stages. Classify conflicts by logical relationship, not merely by file: textual overlap; rename/move; add/add; modify/delete; generated artifact; binary/submodule; API/type/schema contract; behavioral/algorithmic; cross-file architectural interaction. Group conflicts implementing the same logical change and analyze them together; identify high-risk conflicts first so apparently easy edits do not erase evidence.

Do not use `--ours` or `--theirs` as a reasoning shortcut. Their meanings differ by operation, especially during rebase.

#### Large integration triage

When many files or logical conflicts are present, resolve by integration risk rather than file order: (1) API/type/schema contracts and generated-source inputs; (2) behavioral, algorithmic, and cross-file architectural conflicts; (3) rename/move, modify/delete, and add/add identity conflicts; (4) textual overlap, imports, and formatting-only hunks. Batch similar low-risk conflicts only when their intentions are already established. Do not skip integration code review or impact-based verification to save time.

### 4. Reconstruct intent for every nontrivial conflict

For each logical conflict, establish:

- relevant base behavior before either competing change;
- what each side intended to add, fix, remove, or refactor;
- assumptions and invariants introduced by each side;
- whether intentions are independent, complementary, overlapping, superseding, sequential, or incompatible;
- which callers, tests, types, configuration, generated code, or neighboring code constrain the resolution.

Use local history aggressively: commits that touched the affected code, commit messages, file history, blame, parent versions, nearby commits; search for call sites, tests, analogous implementations, comments, and generated sources.

### 5. Form a resolution hypothesis before editing

State internally what the integrated code must do and how it preserves the relevant intentions, then choose one resolution mode:

- **Adopt one side** only when local evidence shows the other change was superseded, irrelevant, or intentionally removed.
- **Combine both changes** when their intentions are compatible.
- **Rewrite the affected implementation** when mechanical combination would be incorrect or fragile.
- **Propagate integration changes** into non-conflicted callers/tests/types when required to make both intentions work together.
- **Ask the user** when intended behavior remains genuinely ambiguous or requires a product/architecture choice not recoverable from local evidence.

Never invent unrelated behavior merely to make tests pass.

### 6. Resolve and focused-test every logical conflict

1. Implement the smallest coherent resolution the hypothesis allows (a larger rewrite when correctness requires it); remove conflict markers only as a consequence of implementing intended behavior.
2. Check the resolved diff immediately for accidental deletion, duplicated logic, stale branches, changed error handling, altered ownership/lifetime behavior, and mismatched API assumptions.
3. Run focused tests/checks exercising the resolved behavior when available; add or adapt a focused regression/integration test when it materially increases confidence. Investigate failures as evidence of an integration defect or wrong hypothesis; do not weaken tests merely to obtain green results.
4. Stage only after the logical conflict is coherent and its focused checks are acceptable, then re-check `git --no-pager diff --cached` and unmerged entries.

These focused checks are an intermediate gate only; they do not replace final impact-based verification.

### 7. Continue until all Git conflicts are resolved

**Rebase:** at each stop, confirm no unresolved index entries and acceptable focused checks, then run `git rebase --continue` with `GIT_EDITOR=true` and `GIT_SEQUENCE_EDITOR=true` set so any editor invocation returns immediately instead of blocking on stdin. If the next replayed commit conflicts, restart the conflict inventory and intent investigation for that commit — do not blindly reuse the previous resolution. If Git wants to skip/drop a commit or a commit becomes empty, stop and follow the approval rules in [references/operation-semantics.md](references/operation-semantics.md). Repeat until the rebase completes.

**Merge:** resolve every logical conflict, run focused checks, and stage the complete intended merge result. Do not run `git merge --continue` or `git commit`; either would create the final merge commit. Leave the repository in the resolved merge state for later review and verification.

Do not report success yet.

### 8. Perform integration code review

Gate: all Git conflicts resolved and focused conflict checks pass. Follow [references/integration-code-review.md](references/integration-code-review.md) for the combined-tree comparison, interaction-map dimensions, bug classes, and per-defect fix loop. The review itself is mandatory and cannot be shortened: compare both original change sets against the final integrated tree, focusing on code Git merged without textual conflicts. Fix each defect as an integration fix (including non-conflicted files when necessary), stage it, re-review the affected semantic neighborhood with focused checks, and record it for the final summary. For a completed rebase, leave post-rebase integration fixes staged and uncommitted; do not amend/rewrite rebased commits merely to hide integration-review fixes. If a correct fix requires an unresolved product/architecture decision, use the ambiguity gate.

### 9. Run impact-based testing and verification

Gate: every required affected test — discovered per [references/testing-verification.md](references/testing-verification.md) across both original branch change sets plus all integration fixes — must pass, along with applicable repository-local compile/typecheck, static-analysis, lint, formatting, code-generation, and build checks. A required affected test that fails, is skipped, cannot run, or remains blocked means the integration is `NOT VERIFIED`.

When verification exposes a bug: investigate it as an integration defect; fix it without weakening valid tests; re-review the affected semantic area; update the affected-test set if the fix broadens impact; rerun until all required affected tests pass. If local evidence shows the failure is **not** caused by branch interaction — e.g. it reproduces on a pre-integration SHA or has no plausible two-branch cause — hand off to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root cause, then return here to resume integration coordination and reporting.

### 10. Perform final structural validation

Follow [references/validation.md](references/validation.md): no unresolved index entries; no accidental conflict markers in intended source files; `git --no-pager diff --check` clean and final staged/current diffs inspected; rebase replay integrity or resolved merge metadata verified; unrelated work untouched; final branch/`HEAD`/staged/unstaged/untracked state captured.

Only call the integration `VERIFIED SUCCESS` when integration code review has no unresolved defects/decisions, all required affected tests pass, applicable checks pass, and final structural validation is clean.

### 11. Report the result

Follow [references/merge-report.md](references/merge-report.md). Default to a compact inline summary: operation and refs; Git operation state versus integration verification state; number/nature of logical conflicts; non-conflicted integration bugs found and fixed; additional fixes; affected tests/checks and results; final local Git state and remaining user action. Generate the detailed merge report only on explicit request, inline by default. Do not push or offer to push automatically.

## Status terminology

Keep Git mechanics separate from integration correctness. Beyond obvious Git vocabulary, this skill adds two verification states:

- **VERIFIED SUCCESS** — integration review is clean and every required affected test/check passed.
- **NOT VERIFIED** — any required review decision, affected test, check, or structural validation is unresolved, failed, skipped, or blocked.

Never describe an integration as successful based only on `git rebase` completion, compilation, or absence of conflict markers.

## Approval gates

### Always allowed within the requested operation

Without extra permission, when safe and relevant: read-only local inspection; editing source and tests for well-supported resolutions and integration fixes; staging intended resolutions/fixes; starting the exact requested merge/rebase; switching to the explicitly requested branch when the tree is safe; normal rebase commits from `git rebase` / `git rebase --continue`; local build/test/typecheck/static-analysis/lint/format/codegen/validation commands that do not publish or destructively modify unrelated work.

### Never perform under this skill's standing authorization

No remote contact or publication: `git push`/force-push, `git fetch`/`git pull`/`git ls-remote`, hosting-service/API/network lookups, releases or remote branches/tags. If the user separately asks for one, explain it is outside this skill's local-only workflow and require explicit confirmation per the surrounding environment's safety rules.

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

Ask only after enough local research to make the question precise; never ask the user to choose "ours or theirs" without explaining semantics. Present: the conflict/decision (what behavior cannot be inferred), the evidence (what local history and code indicate about each intention), the options (materially different implementations and consequences), a recommendation (best supported by correctness, history, and integration goals), and the question. Continue independent analysis only when it cannot corrupt or invalidate the pending decision. Do not stage a speculative resolution for the ambiguous logical conflict.
