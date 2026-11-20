---
name: git-merge-guide
description: "Guide complex local Git merges and rebases (including inside an existing worktree): reconstruct intent from local history, resolve semantic conflicts, stage merges without a final commit, continue rebases, review integrated trees, verify affected tests, and emit a merge report. Local-only (never fetch/push). Excludes remote sync, worktree lifecycle, simple single-file conflicts, and final merge commits (git-guide), or standalone diff review (code-reviewer)."
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

Once this skill begins an active merge/rebase, it owns that operation's local Git state through verification and reporting. Operating inside an already-linked worktree is allowed, not worktree lifecycle. Cherry-pick/revert apply only when explicitly requested.

| Task | Path |
|------|------|
| Push/fetch/pull, stash, cherry-pick/revert, worktree lifecycle, simple single-file conflict triage, final merge commit | [../git-guide/SKILL.md](../git-guide/SKILL.md) (+ [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) to draft the message) |
| Structured diff review without an active integration | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Requirement coverage audit unrelated to branch integration | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Root-cause debugging of a single defect outside active integration, or proving a failure is not integration-caused | [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) |
| Plan execution / parallel dispatch during active integration | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) / [../agent-runner/SKILL.md](../agent-runner/SKILL.md) — read-only only; no concurrent writers against the live operation state |
| PR description, sizing, self-review | [../github-guide/SKILL.md](../github-guide/SKILL.md) |

## Workflow and Reference Routing

Run read-only git commands (`log`, `show`, `diff`, `blame`, `reflog`, `status`) with `--no-pager` or `GIT_PAGER=cat` so stdout never blocks on a pager. Load each reference on demand at its gate:

1. **Establish baseline and safety ([references/operation-semantics.md](references/operation-semantics.md), `<SKILL_ROOT>/scripts/collect-git-context.sh`):**
   - Record branch, `HEAD`, status, worktree root (`git rev-parse --show-toplevel` — stay inside that worktree throughout), and immutable baseline SHAs (source tip, target/upstream tip, merge base, rebase replay list) before branch labels move.
   - Resume an active merge/rebase from local metadata/reflog unless asked to abandon it; hand off active `CHERRY_PICK_HEAD` / `REVERT_HEAD` to [../git-guide/SKILL.md](../git-guide/SKILL.md) unless explicitly extended.
   - Stop and ask if unrelated dirty changes exist before starting; report locally missing refs as unavailable (never fetch).
2. **Initiate or resume ([references/operation-semantics.md](references/operation-semantics.md)):**
   - **Merge:** run `git merge --no-commit <target>` (fast-forward is acceptable Git-level completion; still run steps 6–9).
   - **Rebase:** run the exact requested local rebase using commit-preserving flags (`--reapply-cherry-picks --empty=stop` when supported); never infer unrequested squash/fixup/reorder/drop edits.
   - If Git completes cleanly without conflicts, proceed directly to step 6.
3. **Inventory and triage conflicts ([references/conflict-investigation.md](references/conflict-investigation.md)):**
   - Inspect all unmerged paths and index stages (`:1:`, `:2:`, `:3:`). Never use `--ours` / `--theirs` as a shortcut — stage meanings invert during rebase.
   - Group hunks into logical changes and resolve highest-risk classes first: (1) API/type/schema & codegen inputs, (2) behavioral/algorithmic & cross-file architecture, (3) rename/move, modify/delete, add/add, (4) low-risk textual/import overlap.
4. **Reconstruct intent and form a hypothesis ([references/conflict-investigation.md](references/conflict-investigation.md), [references/semantic-resolution.md](references/semantic-resolution.md)):**
   - Establish base behavior, each side's commit intent/invariants, and their interaction (`independent`, `complementary`, `overlapping`, `sequential`, `incompatible`) from local commits, blame, callers, and tests.
   - Choose an explicit resolution mode before editing: adopt one superseded side, compose compatible changes, adapt sequential changes, rewrite fragile combinations, propagate changes to non-conflicted callers/tests/codegen, or stop at the **Ambiguity gate**. Never invent behavior just to make tests pass.
5. **Resolve, focused-test, and advance ([references/semantic-resolution.md](references/semantic-resolution.md), [references/operation-semantics.md](references/operation-semantics.md)):**
   - Implement the logical resolution, inspect the diff for dropped logic or lifetime/error-path regressions, run focused checks, and stage only when coherent (`git --no-pager diff --cached`, `git ls-files -u`).
   - **Rebase:** advance with `GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true git rebase --continue`; investigate each new conflict stop afresh (never blindly reuse prior edits) and stop for permission if a commit becomes empty or would be skipped/dropped.
   - **Merge:** stage the complete resolved tree; **never** run `git merge --continue` or `git commit`.
6. **Mandatory integration code review ([references/integration-code-review.md](references/integration-code-review.md)):**
   - Compare both pre-operation SHA ranges against the integrated tree, focusing on cleanly merged code and cross-branch interactions (semantic value collisions, invariant/lifetime drift, duplicate/dropped side effects, ordering/sync).
   - Stage integration fixes (leaving post-rebase fixes staged and uncommitted rather than amending rebased commits), re-check affected areas, and escalate unresolved product/architecture choices via the **Ambiguity gate**.
7. **Impact-based verification ([references/testing-verification.md](references/testing-verification.md)):**
   - Run all directly and transitively affected local tests plus applicable build, typecheck, static-analysis, lint, format, and codegen checks across both branch change sets and all integration fixes.
   - Any required affected test or check that fails, is skipped, or cannot run forces `NOT VERIFIED`. Fix integration regressions without weakening valid tests; if local evidence proves a failure pre-dates integration, hand off root-cause proof to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) and return here.
8. **Final structural validation ([references/validation.md](references/validation.md)):**
   - Confirm zero unmerged entries, zero stray conflict markers, clean `git --no-pager diff --check`, intact rebase replay history or staged no-commit merge state, and untouched unrelated work.
9. **Report result ([references/merge-report.md](references/merge-report.md)):**
   - Emit the compact inline summary by default (operation/refs, Git state vs `VERIFIED SUCCESS` / `NOT VERIFIED`, logical conflicts, non-conflicted integration bugs fixed, affected verification totals, final local state, remaining user action, `push performed: no`). Produce the 13-section detailed report only when explicitly requested.

## Status terminology

- **VERIFIED SUCCESS** — integration code review is clean, all required affected tests and applicable checks passed, and structural validation passed.
- **NOT VERIFIED** — any required review decision, affected test, check, or structural validation is unresolved, failed, skipped, or blocked (even if Git conflicts are gone or the build compiles).

## Approval gates

- **Allowed within the requested operation:** read-only local inspection; source/test edits and staging for supported resolutions and integration fixes; starting the exact requested local merge (`--no-commit`) or rebase; safe local branch switch when explicitly requested; normal `git rebase` / `git rebase --continue` replay commits; non-destructive local build/test/lint/codegen validation.
- **Never perform under standing authorization:** any remote or network operation (`git push`/force-push, `git fetch`/`pull`/`ls-remote`, hosting APIs/PR lookups, remote tags/releases). Explain local-only scope and require explicit confirmation if separately requested.
- **Require explicit user permission before executing:**
  - `git reset` that moves history or discards index/worktree state, `git clean`, or destructive `git checkout` / `git restore`;
  - `git merge --abort` or `git rebase --abort` when post-start work could be lost;
  - `git rebase --skip` or allowing any commit to be dropped/silently discarded;
  - unrequested interactive rebase edits (squash, fixup, reorder, edit) or amending completed rebase commits to hide post-rebase fixes;
  - deleting branches/tags, overwriting unrelated uncommitted changes, or creating a manual/final merge commit.
  - When uncertain whether an action can lose work or history, treat it as permission-gated.

## Ambiguity gate

Research local commits, blame, callers, and tests first; never ask a raw "ours or theirs" question. When behavior remains genuinely underdetermined, do not stage a speculative resolution — follow the decision template in [references/semantic-resolution.md](references/semantic-resolution.md) (**Decision**, **Evidence**, **Options**, **Recommendation**, **Question**).
