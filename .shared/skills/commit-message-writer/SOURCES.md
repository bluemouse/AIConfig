# Sources

## Conventional Commits 1.0.0

- **URL:** https://www.conventionalcommits.org/en/v1.0.0/
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/conventional-commits.md` → format, types, breaking changes, examples
  - `SKILL.md` → workflow phase 3, output standards
- **Aspects extracted:**
  - `<type>[optional scope]: <description>` structure → `references/conventional-commits.md`
  - Types `feat`, `fix`, and extended set (`build`, `chore`, `ci`, `docs`, `perf`, `refactor`, `test`) → `references/conventional-commits.md`
  - Breaking change via `!` or `BREAKING CHANGE:` footer → `references/conventional-commits.md`

## Cursor commit-message command (repository)

- **Path:** `.cursor/commands/commit-message.md`
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Full workflow phases (parse, git evidence, analyze, output, optional commit)
  - `references/input-and-scope.md`, `references/git-evidence.md`, `references/output-format.md`, `references/failure-and-guardrails.md`
  - `SKILL.md` → primary directive, workflow, guardrails
- **Aspects extracted:**
  - Scope modes (`--staged`, `--working`, `--commit`, `--range`) and context flags → `references/input-and-scope.md`
  - Git command tables per scope → `references/git-evidence.md`
  - Compact / Verbose / Suggested command output structure → `references/output-format.md`
  - Cross-assistant style contract → `references/message-style-contract.md`
  - Draft-only safety (no commit unless asked) → `SKILL.md`, `references/failure-and-guardrails.md`

## git-guide commit reference (synthesis metadata)

- **Path:** `skills-ref/git-guide/references/commit.md`
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Cross-check type detection patterns; **not** copied auto-commit behavior
- **Aspects extracted:**
  - Conventional type list alignment → `references/conventional-commits.md`
  - Explicit boundary: this skill drafts only; git-guide handles auto-commit when installed
