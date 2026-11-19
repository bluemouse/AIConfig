---
name: git-guide
description: "Use when running git operations or resolving repo-state issues. Triggers on worktrees, feature-worktree create/merge/abandon/cleanup, branch cleanup, push/rebase before a PR, staging and committing, final merge commits, history rewrites, stash, or simple single-file merge/rebase conflict triage including pick-ours/theirs mechanical resolution — even when the user doesn't say 'git'. Also triggers on drafting a git commit message in Conventional Commits format (subject plus body) from staged changes, the working tree, a single commit, or a commit range — even if the user does not say 'conventional commits'. Does not trigger on end-to-end local merge/rebase integration, semantic conflict resolution, integration review of merged code, impact-based verification, or merge reports — use git-merge-guide. Ends commit-message drafting by asking whether to proceed with git commit using the generated message; does not commit without explicit confirmation."
---

# Git Guidelines

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Git mechanics for commits, pushes, rebases, conflict resolution, and worktree workflows.
Read bundled references on demand — do not load all reference files unless the task
requires them.

## When to Use

- Staging, committing, pushing, or rebasing branches
- Drafting a Conventional Commit message from a diff, commit, or commit range
- Simple single-file or mechanical merge/rebase conflict triage and staging
- Creating the final merge commit after a staged integration result
- Creating, merging, validating, abandoning, or cleaning up feature worktrees
- Publishing a branch and rebasing onto its base before opening a PR / MR
- Branch cleanup, history rewrites, stash, cherry-pick, revert, or repo-state triage

## Boundary vs git-merge-guide

Use this skill for **Git mechanics and simple triage**. Hand off to
[../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md) when the request needs intent
reconstruction, semantic resolution, combined-tree integration review, affected-test
verification, or a merge report.

| Signal | Owner |
| --- | --- |
| Lockfile/import/formatting conflict with obvious mechanical resolution | `git-guide` |
| Semantic, API, behavioral, or multi-file architectural conflict | `git-merge-guide` |
| Active merge/rebase plus verify integrated code or generate merge report | `git-merge-guide` |
| Final merge commit after integration is already staged | `git-guide` |

## When NOT to Use

- **End-to-end local merge/rebase integration** — semantic conflict resolution,
  integration code review of cleanly merged code, impact-based verification, merge
  reports — use [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md)
- **Authoring PR descriptions, sizing, or self-review** — use
  [github-guide](../github-guide/SKILL.md)
- **Structured diff review without git operations** — use
  [code-reviewer](../code-reviewer/SKILL.md)
- **Host-specific PR/MR creation** — use `github-guide` or `gitlab-guide` when installed

## Core Principles

- **Message drafting is built in** — draft the message with
  [references/commit-message.md](references/commit-message.md), then run the commit
  mechanics from [references/commit.md](references/commit.md); do not commit until
  the user confirms the draft (or explicitly asked to commit)
- **Isolated Development** — use worktrees for feature branches only when the current branch is `main`, `master`, or `dev`; always ask the user to confirm before creating — see [references/worktree-create.md](references/worktree-create.md)
- **Validate Before Merge** — run the project's typecheck/lint/build/test, see [references/worktree-validate.md](references/worktree-validate.md)
- **Publish and Rebase** — push a branch upstream and rebase onto the base before opening a PR / MR, see [references/push.md](references/push.md)

## Commit Operations

- **Draft message** — Conventional Commits subject plus body from staged, working, commit, or range scope; self-contained messages, no attribution footers; see [references/commit-message.md](references/commit-message.md)
- **Stage and commit** — status, stage, commit with a user-supplied or pre-drafted message, optional push; see [references/commit.md](references/commit.md)

## Branch Operations

- **Push + rebase-onto-base** — publish a branch upstream and keep its PR / MR diff scoped to this change; host skills (`github-guide` / `gitlab-guide`, when installed) drive PR/MR creation — see [references/push.md](references/push.md)

## Conflict Resolution

- **Simple triage** — single-file or mechanical conflicts (lockfile, imports, formatting);
  classify, resolve, stage, and validate — see [references/merge-resolve.md](references/merge-resolve.md)
- **Deep integration** — semantic conflict resolution, integration review, impact-based
  verification, and merge reports — hand off to
  [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md)

## Worktree Operations

- **Create** — `<worktree>-feature-<name>` directory with branch; only from `main`, `master`, or `dev`, and only after user confirmation — see [references/worktree-create.md](references/worktree-create.md)
- **Commit** — commit in a worktree with plan context restated in the message, see [references/worktree-commit.md](references/worktree-commit.md)
- **Validate** — pre-merge validation checkpoint, see [references/worktree-validate.md](references/worktree-validate.md)
- **Merge** — merge feature back to source branch, see [references/worktree-merge.md](references/worktree-merge.md)
- **Cleanup** — remove stale and merged worktrees, see [references/worktree-cleanup.md](references/worktree-cleanup.md)
- **Abandon** — document and remove failed feature, see [references/worktree-abandon.md](references/worktree-abandon.md)

## Companion Skills

| Task | Path |
|------|------|
| End-to-end merge/rebase integration and verification | [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md) |
| PR description, sizing, self-review | [../github-guide/SKILL.md](../github-guide/SKILL.md) |
| Structured diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| GitHub PR/review delivery (`gh pr create`, post review) | [../github-guide/SKILL.md](../github-guide/SKILL.md) |
