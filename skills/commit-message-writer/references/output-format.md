# Output Format

## Contents

- [Required structure](#required-structure)
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

<body paragraphs and bullet lists as needed>
```

Rules:

- **Compact** is wrapped in backticks as a single line
- **Verbose** subject matches Compact (without backticks)
- Body uses complete sentences; bullet lists allowed for test/evidence notes

## Suggested command

Include an optional third block when scope is `--staged` or `--working` and the user might
commit immediately:

```markdown
## Suggested command

git commit -m "$(cat <<'EOF'
<verbose subject + body>
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

Example:

```text
Context used: scope=staged; session=yes; context=docs/plans/auth-flow.md; jira=PROJ-456
```

## Quality bar

- **Compact** stands alone in `git log --oneline`
- **Verbose** explains *why*, not only *what*
- Both describe one coherent logical change
- If the diff mixes unrelated work, say so and suggest splitting — do not blend
