# commit: Stage and Commit Changes

Git mechanics for staging and committing. Message composition — type, scope, subject,
body — belongs to [commit-message-writer](../../commit-message-writer/SKILL.md). Use that
skill first when the user needs a message drafted from the diff; return here for the git
commands once the message is ready.

## Contents

- [Goal](#goal)
- [Core Workflow](#core-workflow)
- [Implementation Steps](#implementation-steps)
- [Output](#output)
- [Error Handling](#error-handling)
- [Gotchas](#gotchas)

## Goal

- Stage and commit changes with a user-supplied or pre-drafted message
- Support optional push after commit
- Never auto-commit without explicit user approval unless the user asked to commit

## Core Workflow

1. **Navigate** — change to the specified path if one was provided
2. **Check Status** — detect uncommitted changes and unpushed commits
3. **Resolve Message** — use the user-provided message, or draft one via
   [commit-message-writer](../../commit-message-writer/SKILL.md) before proceeding
4. **Stage and Commit** — `git add` (scoped or `-A` per user intent) then `git commit`
5. **Push** (optional) — push to specified remote and branch

## Implementation Steps

1. `cd <path>` (if specified)
2. `git status --porcelain` to detect changes
3. If no message provided, stop and route to
   [commit-message-writer](../../commit-message-writer/SKILL.md) — do not invent a message
   in this reference
4. If message provided: use it directly (HEREDOC for multi-line bodies)
5. Stage: `git add <paths>` or `git add -A` per user scope
6. Commit: `git commit -m "<message>"` (or HEREDOC for multi-line)
7. Push if requested:
   - Remote: `git config branch.<branch>.remote` or specified, default `origin`
   - Branch: specified or `git branch --show-current`
   - `git push <remote> HEAD:<branch>`
   - GitLab only: `git push -o ci.skip <remote> HEAD:<branch>` skips CI on that push —
     omit `-o ci.skip` when CI should run

## Output

```
Commit: /path/to/repo
Changed: 14 files (+588, -210)

Committed: feat(api): add rate-limit middleware (a3b2c1d)
Pushed: origin/feature/rate-limit
```

## Error Handling

- Error if not in a git repository
- Warning if no changes to commit (working tree clean)
- Error if commit fails (show git error)
- Warning if push fails (show git error; commit already succeeded)
- Error if specified path doesn't exist
- Warning if a very large number of files changed (suggest splitting commits and using
  [commit-message-writer](../../commit-message-writer/SKILL.md) per slice)

## Gotchas

- Default mode must not commit without user approval — confirm intent before `git commit`
- Pushing with `-o ci.skip` is GitLab-specific; on GitHub or other hosts use a plain push
- Mixed-intent working trees should be split into separate commits — draft each message
  with [commit-message-writer](../../commit-message-writer/SKILL.md)
- A stale `branch.<branch>.plan` git config can inject irrelevant plan context into
  worktree commits — clear it when starting unrelated work
