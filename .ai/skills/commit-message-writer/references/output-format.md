# Output Format

Apply [message-style-contract.md](message-style-contract.md) § Cross-assistant rules. The
response envelope is **identical on Cursor, Claude Code, and Copilot** — no host-specific
variations.

## Contents

- [Required structure](#required-structure)
- [Cross-assistant envelope](#cross-assistant-envelope)
- [Suggested command](#suggested-command)
- [Context used line](#context-used-line)
- [Commit offer](#commit-offer)
- [Quality bar](#quality-bar)

## Required structure

Return exactly this markdown structure:

````markdown
## Verbose

```text
<subject line>

<body paragraphs; bullets only per message-style-contract.md>
```

## Suggested command

```bash
git commit -m "$(cat <<'EOF'
<subject + body — change-related content only; no Co-authored-by or tool footers>
EOF
)"
```
````

Rules:

- **Verbose** — wrap the full message (subject, blank line, body) in a single ` ```text `
  fenced block so chat UIs show a copy control
- **Suggested command** — wrap the HEREDOC `git commit` one-liner in a ` ```bash ` fenced
  block for the same reason
- **Body** — prose paragraphs by default; use bullet lists only when
  [message-style-contract.md](message-style-contract.md) § When bullets are allowed
- Message text inside fences is **change-related only** — motivation, approach, impact,
  breaking changes, test/evidence notes, and cited ticket ids
- Never append `Co-authored-by`, `Signed-off-by`, or any footer attributing an AI client or
  coding assistant (for example `Co-authored-by: Cursor <cursoragent@cursor.com>`)

## Cross-assistant envelope

The assistant response must contain **only** these blocks, in order:

1. `## Verbose`
2. `## Suggested command` (optional; staged/working scope only)
3. `Context used:` line
4. Commit offer question (staged/working scope only; see [Commit offer](#commit-offer))

Do not add introductory text, explanations of Conventional Commits, tool-specific notes,
or closing commentary beyond the commit offer. When scope is ambiguous, the diff mixes
unrelated work, or the diff was sampled due to size, record that in `Context used:` with a
`note=` field — do not place caveats before `## Verbose`.

Example with split suggestion:

```text
Context used: scope=staged; session=yes; note=diff mixes refactor and docs — consider split
```

## Suggested command

Include when scope is `--staged` or `--working` and the user might commit immediately.
Use the structure shown in [Required structure](#required-structure) — the command must
be inside a ` ```bash ` fence, not bare inline text.

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

## Commit offer

When scope is **staged** or **working**, end the response by asking whether to proceed with
`git commit` using the generated message. Keep the question short and actionable — for
example:

```text
Proceed with git commit using this message?
```

Do not run `git commit` until the user confirms. When scope is **commit** or **range**,
omit the commit offer (the draft is for review or rewrite, not an immediate commit).

## Quality bar

- **Verbose** and **Suggested command** are each in a fenced code block (`text` / `bash`)
  so users can copy with one click
- **Subject** is a valid Conventional Commit line suitable for `git log --oneline`
- **Body** follows the style contract (prose-first) and explains *why*, not only *what*
- Message describes one coherent logical change
- Output shape is the same regardless of host assistant
- If the diff mixes unrelated work, record a split suggestion in `Context used:` (`note=`)
  — do not blend unrelated intent into one message
