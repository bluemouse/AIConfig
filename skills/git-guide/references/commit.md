# commit: Stage and Commit Changes

Git mechanics for staging and committing. Message composition — type, scope, subject,
body — belongs to [commit-message-writer](../../commit-message-writer/SKILL.md). Use that
skill first when the user needs a message drafted from the diff; return here for the git
commands once the message is ready.

## Rules

- Never auto-commit without explicit user approval — confirm intent before `git commit`.
- If no message is provided, stop and route to
  [commit-message-writer](../../commit-message-writer/SKILL.md) — do not invent a message
  in this reference.
- Stage only what the user scoped (`git add <paths>`, or `-A` when they asked for
  everything); commit with a HEREDOC for multi-line bodies.
- Optional push after commit: resolve the remote via
  `git config branch.<branch>.remote` (default `origin`) and push `HEAD:<branch>`.
- **GitLab only:** `git push -o ci.skip <remote> HEAD:<branch>` skips CI on that push —
  omit `-o ci.skip` on GitHub and other hosts, and omit it when CI should run.
- Mixed-intent working trees should be split into separate commits — draft each message
  with [commit-message-writer](../../commit-message-writer/SKILL.md).
- A stale `branch.<branch>.plan` git config can inject irrelevant plan context into
  worktree commits — clear it when starting unrelated work.
