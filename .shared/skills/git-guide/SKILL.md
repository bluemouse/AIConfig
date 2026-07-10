---
name: git-guide
description: "Use when running git operations or resolving repo-state issues. Triggers on merge conflicts, rebases, worktrees, feature-worktree create / merge / abandon / cleanup, branch cleanup, push/rebase before a PR, staging and committing (when the user supplies or already has a message), or history rewrites — even when the user doesn't say 'git'. For drafting Conventional Commit messages from diffs, use commit-message-writer."
---

# Git Guidelines

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Git mechanics for commits, pushes, rebases, conflict resolution, and worktree workflows.
Read bundled references on demand — do not load all reference files unless the task
requires them.

## When to Use

- Staging, committing, pushing, or rebasing branches
- Resolving merge or rebase conflicts
- Creating, merging, validating, abandoning, or cleaning up feature worktrees
- Publishing a branch and rebasing onto its base before opening a PR / MR
- Branch cleanup, history rewrites, stash, or repo-state triage

## When NOT to Use

- **Drafting Conventional Commit messages from diffs** — use
  [commit-message-writer](../commit-message-writer/SKILL.md) for message composition,
  type/scope selection, and compact/verbose output
- **Authoring PR descriptions, sizing, or self-review** — use
  [pull-request-guide](../pull-request-guide/SKILL.md)
- **Structured diff review without git operations** — use
  [code-reviewer](../code-reviewer/SKILL.md)
- **Host-specific PR/MR creation** — use `github-guide` or `gitlab-guide` when installed

## Core Principles

- **Message drafting is separate** — use [commit-message-writer](../commit-message-writer/SKILL.md) for Conventional Commit composition; this skill handles git mechanics once a message exists
- **Isolated Development** — use worktrees for feature branches, see [references/worktree-create.md](references/worktree-create.md)
- **Validate Before Merge** — run the project's typecheck/lint/build/test, see [references/worktree-validate.md](references/worktree-validate.md)
- **Publish and Rebase** — push a branch upstream and rebase onto the base before opening a PR / MR, see [references/push.md](references/push.md)

## Commit Operations

- **Stage and commit** — status, stage, commit with a user-supplied or pre-drafted message, optional push; see [references/commit.md](references/commit.md)

## Branch Operations

- **Push + rebase-onto-base** — publish a branch upstream and keep its PR / MR diff scoped to this change; host skills (`github-guide` / `gitlab-guide`, when installed) drive PR/MR creation — see [references/push.md](references/push.md)

## Conflict Resolution

- **Detect and classify** — find conflicts, suggest strategy (ours/theirs/merge), see [references/merge-resolve.md](references/merge-resolve.md)
- **Validate** — run project checks after resolution before staging, see [references/merge-resolve.md](references/merge-resolve.md)

## Worktree Operations

- **Create** — `<worktree>-feature-<name>` directory with branch, see [references/worktree-create.md](references/worktree-create.md)
- **Commit** — commit in a worktree with plan context for the message body, see [references/worktree-commit.md](references/worktree-commit.md)
- **Validate** — pre-merge validation checkpoint, see [references/worktree-validate.md](references/worktree-validate.md)
- **Merge** — merge feature back to source branch, see [references/worktree-merge.md](references/worktree-merge.md)
- **Cleanup** — remove stale and merged worktrees, see [references/worktree-cleanup.md](references/worktree-cleanup.md)
- **Abandon** — document and remove failed feature, see [references/worktree-abandon.md](references/worktree-abandon.md)

## Gotchas

- `git pull` is `fetch` + `merge` — on a shared branch this creates spurious merge commits; prefer `pull --rebase` or `fetch` then explicit merge
- Detached HEAD: committing in this state silently loses commits when you `checkout` away — note the SHA or branch immediately
- `git rebase` rewrites history; force-pushing to a shared branch overwrites teammates' work — never force-push to `main`/`master`
- Hooks in `.git/hooks/` are not version-controlled — share via `core.hooksPath` pointing at a tracked directory
- `.gitignore` only ignores untracked files; already-tracked files need `git rm --cached` to stop tracking

## Progressive Disclosure

### Commit and Branch Operations

- Read [references/commit.md](references/commit.md) — load when staging and committing with a supplied or pre-drafted message
- Read [references/push.md](references/push.md) — load when publishing a branch upstream and rebasing it onto the base before opening a PR / MR
- Read [references/merge-resolve.md](references/merge-resolve.md) — load when detecting and resolving merge conflicts

### Worktree Operations

- Read [references/worktree-create.md](references/worktree-create.md) — load when creating a feature worktree with branch
- Read [references/worktree-commit.md](references/worktree-commit.md) — load when committing inside a feature worktree with plan context
- Read [references/worktree-validate.md](references/worktree-validate.md) — load when running pre-merge validation in a feature worktree
- Read [references/worktree-merge.md](references/worktree-merge.md) — load when merging a feature worktree back to its source branch
- Read [references/worktree-cleanup.md](references/worktree-cleanup.md) — load when removing stale or merged worktrees
- Read [references/worktree-abandon.md](references/worktree-abandon.md) — load when documenting and removing an abandoned feature worktree

## Companion Skills

| Task | Path |
|------|------|
| Draft Conventional Commit messages from diffs | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) |
| PR description, sizing, self-review | [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md) |
| Structured diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| GitHub PR/review delivery (`gh pr create`, post review) | [../github-guide/SKILL.md](../github-guide/SKILL.md) |
