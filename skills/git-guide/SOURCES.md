# Sources

## Git worktree workflow (repository synthesis)

- **Path:** `skills-ref/git-guide/` (original template)
- **Last reviewed:** 2026-07-07
- **Used for:**
  - `SKILL.md` → worktree lifecycle, progressive disclosure
  - `references/worktree-*.md` → create, commit, validate, merge, cleanup, abandon
- **Aspects extracted:**
  - `<worktree>-feature-<name>` directory naming → `references/worktree-create.md`
  - `branch.<branch>.mergeBackTo` config association → `references/worktree-create.md`, `references/worktree-merge.md`
  - Plan context via `branch.<branch>.plan` → `references/worktree-commit.md`, `references/worktree-abandon.md`

## Git push and rebase (repository synthesis)

- **Path:** `skills-ref/git-guide/references/push.md`
- **Last reviewed:** 2026-07-07
- **Used for:**
  - `references/push.md` → upstream publish, rebase onto base, force-with-lease
  - `SKILL.md` → publish-and-rebase principle
- **Aspects extracted:**
  - `git push -u origin <branch>` → `references/push.md`
  - `git rebase origin/<base>` + `--force-with-lease` → `references/push.md`
  - GitLab `-o ci.skip` noted as host-specific → `references/push.md`, `references/commit.md`

## Merge conflict resolution (repository synthesis)

- **Path:** `skills-ref/git-guide/references/merge-resolve.md`
- **Last reviewed:** 2026-07-07
- **Used for:**
  - `references/merge-resolve.md` → detect, classify, resolve, validate
- **Aspects extracted:**
  - UU/AA/DD status markers → `references/merge-resolve.md`
  - Tool-agnostic post-resolution validation → `references/merge-resolve.md`

## commit-message-writer boundary (repository)

- **Path:** `skills/commit-message-writer/`
- **Last reviewed:** 2026-07-07
- **Used for:**
  - `references/commit.md` → message drafting delegation
  - `SKILL.md` → When NOT to Use, companion skills table
- **Aspects extracted:**
  - Commit mechanics separated from message composition → `references/commit.md`
  - Conventional Commit drafting owned by commit-message-writer → `SKILL.md`

## Refresh Workflow

1. Re-read upstream git worktree and push/rebase references
2. Verify commit-message-writer boundary has not drifted
3. Re-run eval-queries against the skill description
4. Bump **Last reviewed** dates above
