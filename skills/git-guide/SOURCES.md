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

## commit-message-writer boundary (repository, superseded by the 2026-11-19 merge)

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
2. Verify the commit-message drafting boundary (commit.md vs commit-message.md) has not drifted
3. Re-run eval-queries against the skill description
4. Bump **Last reviewed** dates above

## Conventional Commits 1.0.0 (merged from commit-message-writer)

- **URL:** https://www.conventionalcommits.org/en/v1.0.0/
- **Last reviewed:** 2026-07-06
- **Used for:** message grammar baseline (`references/commit-message.md` → message rules)
- **Aspects extracted:** `<type>[optional scope]: <description>` structure, the
  `feat`/`fix` plus extended type set, breaking change via `!` or
  `BREAKING CHANGE:` footer

## commit-message-writer skill (repository, merged 2026-11-19)

- **Path:** `skills/commit-message-writer/` (removed by the merge)
- **Last reviewed:** 2026-11-19
- **Used for:**
  - `references/commit-message.md` → scope modes (staged, working, commit, range),
    output envelope, draft-first workflow with commit offer on confirmation
  - `scripts/lint_message.py` → mechanical message lint (portable twin of
    `tools/dev-workflow/checks/message_checks.py`)
  - `evals/evals.json` → behavior evals asserting self-contained messages
- **Aspects extracted:**
  - Self-contained message rule (no ephemeral run-artifact ids or narration)
  - No-attribution rule overriding host footers
  - Style precedence: repo log → these rules → Conventional Commits defaults
