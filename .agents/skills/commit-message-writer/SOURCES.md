# Sources

## Conventional Commits 1.0.0

- **URL:** https://www.conventionalcommits.org/en/v1.0.0/
- **Last reviewed:** 2026-07-06
- **Used for:** message grammar baseline (`SKILL.md` → message rules)
- **Aspects extracted:** `<type>[optional scope]: <description>` structure, the
  `feat`/`fix` plus extended type set, breaking change via `!` or
  `BREAKING CHANGE:` footer

## Cursor commit-message command (repository)

- **Path:** `.cursor/commands/commit-message.md`
- **Last reviewed:** 2026-07-06
- **Used for:** scope modes (staged, working, commit, range), output envelope,
  draft-first workflow with commit offer on confirmation (`SKILL.md`)

## git-guide commit reference (synthesis metadata)

- **Path:** `skills/git-guide/references/commit.md`
- **Last reviewed:** 2026-07-06
- **Used for:** cross-check type detection patterns; **not** copied
  auto-commit behavior
- **Aspects extracted:** explicit boundary — commit-message-writer drafts and
  commits on confirmation; git-guide handles commit when the user already
  supplied a message or needs push/staging mechanics
