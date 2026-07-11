# Output Format

Apply [message-style-contract.md](message-style-contract.md) § Cross-assistant rules. The
response envelope is **identical on Cursor, Claude Code, and Copilot** — no host-specific
variations.

## Contents

- [Required structure](#required-structure)
- [Cross-assistant envelope](#cross-assistant-envelope)
- [Suggested command](#suggested-command)
- [Context used line](#context-used-line)
- [Quality bar](#quality-bar)

## Required structure

Return exactly this markdown structure:

```markdown
## Compact

`<one-line message>`

## Verbose

<subject line>

<body paragraphs; bullets only per message-style-contract.md>
```

Rules:

- **Compact** is wrapped in backticks as a single line
- **Verbose** subject matches Compact (without backticks)
- **Verbose body** — prose paragraphs by default; use bullet lists only when
  [message-style-contract.md](message-style-contract.md) § When bullets are allowed
- Message text is **change-related only** — motivation, approach, impact, breaking changes,
  test/evidence notes, and cited ticket ids
- Never append `Co-authored-by`, `Signed-off-by`, or any footer attributing an AI client or
  coding assistant (for example `Co-authored-by: Cursor <cursoragent@cursor.com>`)

## Cross-assistant envelope

The assistant response must contain **only** these blocks, in order:

1. `## Compact`
2. `## Verbose`
3. `## Suggested command` (optional; staged/working scope only)
4. `Context used:` line

Do not add introductory text, explanations of Conventional Commits, tool-specific notes,
or closing commentary. When scope is ambiguous, the diff mixes unrelated work, or the diff
was sampled due to size, record that in `Context used:` with a `note=` field — do not place
caveats before `## Compact`.

Example with split suggestion:

```text
Context used: scope=staged; session=yes; note=diff mixes refactor and docs — consider split
```

## Suggested command

Include an optional third block when scope is `--staged` or `--working` and the user might
commit immediately:

```markdown
## Suggested command

git commit -m "$(cat <<'EOF'
<verbose subject + body — change-related content only; no Co-authored-by or tool footers>
EOF
)"
```

Omit **Suggested command** for `--commit` / `--range` (historical or multi-commit review).

## Context used line

After the message blocks, add one short line listing:

- Scope mode (`staged`, `working`, `commit <sha>`, `range <rev-range>`)
- Commit count when range
- Session context used (yes/no)
- Files and ticket ids cited
- Optional `note=` — scope ambiguity, split suggestion, or large-diff sampling caveat

Example:

```text
Context used: scope=staged; session=yes; context=docs/plans/auth-flow.md; jira=PROJ-456
```

## Quality bar

- **Compact** stands alone in `git log --oneline`
- **Verbose** subject equals Compact; body follows the style contract (prose-first)
- **Verbose** explains *why*, not only *what*
- Both describe one coherent logical change
- Output shape is the same regardless of host assistant
- If the diff mixes unrelated work, record a split suggestion in `Context used:` (`note=`)
  — do not blend unrelated intent into one message
