# Git operation semantics and safety

Use this reference before starting or continuing a merge/rebase.

## Contents

- [Detect the active operation](#1-detect-the-active-operation)
- [Record a stable integration baseline](#2-record-a-stable-integration-baseline)
- [Understand index stages](#3-understand-index-stages)
- [Starting a merge](#4-starting-a-merge)
- [Starting a rebase](#5-starting-a-rebase)
- [Continuing a rebase](#6-continuing-a-rebase)
- [Empty or skipped commits](#7-empty-or-skipped-commits)
- [Dirty working tree](#8-dirty-working-tree)
- [Abort and recovery](#9-abort-and-recovery)
- [Worktrees](#10-worktrees)
- [Cherry-pick and revert](#11-cherry-pick-and-revert)

## 1. Detect the active operation

Use Git's own paths rather than guessing from status text alone. Useful probes include:

```bash
git rev-parse --git-path MERGE_HEAD
git rev-parse --git-path REBASE_HEAD
git rev-parse --git-path rebase-merge
git rev-parse --git-path rebase-apply
git rev-parse --git-path CHERRY_PICK_HEAD
git rev-parse --git-path REVERT_HEAD
```

Check whether the returned files/directories exist. Also inspect `git status --porcelain=v2 --branch` and `git status` for human-readable sequencer state.

Do not start a second merge/rebase on top of an active sequencer operation unless the user explicitly directs recovery and the action is safe.

## 2. Record a stable integration baseline

Before starting a new operation, record immutable SHAs for later semantic review, test-impact analysis, and reporting. At minimum capture:

- original current/source branch tip;
- requested merge target or rebase upstream tip;
- relevant merge base;
- expected rebase replay commits and their order when rebasing.

Useful commands include:

```bash
git rev-parse HEAD
git rev-parse <target-or-upstream>
git merge-base HEAD <target-or-upstream>
git log --reverse --format='%H %s' <upstream>..HEAD
```

For `rebase --onto`, derive and record the exact replay range from the requested old base/branch. Do not assume the simple `<upstream>..HEAD` range.

If the operation is already active, reconstruct the baseline from local metadata such as `ORIG_HEAD`, `MERGE_HEAD`, `REBASE_HEAD`, rebase state files, reflog, and local history. Mark any reconstruction uncertainty rather than inventing a SHA relationship.

Keep these SHAs available after branch labels move so the post-conflict integration review can compare both original change sets against the final tree.

## 3. Understand index stages

For an unmerged path, inspect:

```bash
git ls-files -u -- path/to/file
git show :1:path/to/file   # stage 1: base where available
git show :2:path/to/file   # stage 2
git show :3:path/to/file   # stage 3
```

For a normal two-head merge:

- stage 1 is the merge base version;
- stage 2 is the current `HEAD` side (commonly called ours);
- stage 3 is the merged-in side (commonly called theirs).

For a rebase, do not transfer those human labels naively. Git checks out the rebased/upstream state and replays commits onto it. During a conflict, stage 2 is generally the already-rebased/upstream side, while stage 3 represents the commit being replayed. Therefore `--ours` can mean the upstream/rebased state and `--theirs` the replayed commit, which is the opposite of what users often expect.

Always identify actual commits and behavior before using ours/theirs terminology.

## 4. Starting a merge

Use a no-commit merge when the user wants the result local and uncommitted:

```bash
git merge --no-commit <target>
```

`--no-commit` cannot stop a fast-forward because no merge commit is created. A successful fast-forward is therefore an acceptable completed local merge unless the user explicitly required a merge commit shape.

If a merge conflicts, resolve and stage all intended changes but do not run `git merge --continue` or `git commit`.

This skill always leaves non-fast-forward merges **resolved and staged**. Creating the final
merge commit is outside this skill — the user or [../../git-guide/SKILL.md](../../git-guide/SKILL.md)
creates it separately, optionally drafting the message with
[../../commit-message-writer/SKILL.md](../../commit-message-writer/SKILL.md).

## 5. Starting a rebase

A requested rebase authorizes the rewritten commits inherently produced by that rebase. It does not authorize additional history editing such as drop, squash, fixup, reorder, or skip unless explicitly requested.

Before starting, record the commits expected to replay, for example:

```bash
git log --reverse --oneline <upstream>..HEAD
```

For more complicated `--onto` requests, derive the replay range from the exact requested old base/branch rather than assuming `<upstream>..HEAD`.

Prefer rebase options that prevent silent commit loss when supported by the installed Git. In modern Git, consider:

```bash
git rebase --reapply-cherry-picks --empty=stop <upstream>
```

Use only options actually supported by the local Git version. `--reapply-cherry-picks` avoids preemptively dropping commits that appear to be clean cherry-picks of upstream. `--empty=stop` stops when a replayed commit becomes empty so the user can decide whether it should be dropped or kept.

If those options are unavailable, monitor Git output and compare the expected replay list to the resulting history. Treat any proposed or observed skipped/dropped commit as a decision requiring user permission unless the user explicitly requested that behavior.

## 6. Continuing a rebase

After resolving and staging the current stop:

```bash
GIT_EDITOR=true git rebase --continue
```

Use a noninteractive editor setting only when preserving the existing replayed commit message is appropriate. If Git legitimately requires a new commit message or the user requested an edit, do not silently invent one without understanding why.

After each continue:

1. inspect the new `HEAD` and status;
2. detect whether another conflict occurred;
3. identify the replayed commit associated with the new stop;
4. perform a fresh semantic investigation.

Do not assume repeated conflicts have identical intent. Rerere-like patterns may be similar but later commits can depend on earlier transformations.

## 7. Empty or skipped commits

An empty replay can mean several different things:

- the change is already present upstream;
- an earlier conflict resolution incorporated the same behavior;
- the commit's behavior was accidentally lost;
- the commit only reverted something no longer present;
- the resolution intentionally superseded it.

Do not automatically run `git rebase --skip`. Investigate the original patch (`git show <commit>`) and the current tree. Explain whether keeping an empty commit, dropping it, or changing the earlier resolution best preserves intent. Ask the user before discarding the commit.

## 8. Dirty working tree

Do not automatically use `--autostash`, `git stash`, `reset`, `clean`, checkout/restore, or temporary commits to make the tree clean. First identify the dirty paths and whether they are part of the requested work. Ask how to preserve unrelated work unless the user already provided explicit instructions.

## 9. Abort and recovery

Abort commands can restore operation-start state and may interfere with edits made after the operation began. Never abort automatically. If the operation appears unrecoverable, explain the current state, the likely effects of aborting, and any safer alternatives before asking permission.

## 10. Worktrees

When the integration runs inside a linked worktree:

- confirm the worktree root with `git rev-parse --show-toplevel` and remain in that checkout for the entire operation;
- do not switch to the primary repository checkout or another worktree mid-merge/rebase;
- record branch, `HEAD`, and baseline SHAs from the worktree context — they may differ from the main checkout on the same branch name;
- when switching branches is required, verify the tree is clean enough for the worktree and that unrelated work in other checkouts is not affected.

For worktree create, merge-back, abandon, or cleanup mechanics, use [../../git-guide/SKILL.md](../../git-guide/SKILL.md).

## 11. Cherry-pick and revert

This skill targets merge and rebase integration by default. Cherry-pick and revert are different sequencer operations with their own replay semantics.

If `CHERRY_PICK_HEAD` or `REVERT_HEAD` is active when the skill loads:

- explain that cherry-pick/revert is out of scope unless the user explicitly asks to apply this integration workflow to that operation;
- hand off to [../../git-guide/SKILL.md](../../git-guide/SKILL.md) for standard cherry-pick/revert mechanics;
- do not silently treat an active cherry-pick or revert as a merge or rebase.
