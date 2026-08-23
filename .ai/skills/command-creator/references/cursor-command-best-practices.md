# Cursor Command Best Practices

Reference for `.cursor/commands/<name>.md` slash commands.

**Official docs:** [Cursor Commands](https://docs.cursor.com/en/agent/chat/commands)

## Format

| Rule | Detail |
| --- | --- |
| Location | `.cursor/commands/*.md` |
| Invocation | `/command-name` (filename without `.md`) |
| Frontmatter | **Not supported** — plain Markdown only |
| Filename | kebab-case, descriptive (`code-review.md`, not `cr.md`) |

Install strips frontmatter from shared bootstrap content. Cursor wrapper files under `wrappers/cursor/` must also be plain Markdown with no YAML block.

## Writing effective commands

1. **Single purpose** — one workflow per file
2. **Clear steps** — numbered list the agent can follow in order
3. **Explicit output** — describe sections, labels, or code block types expected
4. **Examples** — show a good response shape when format matters
5. **Guardrails** — "Do not commit", "Do not push", "Ask before deleting"

## Good patterns

```markdown
# Review Staged Changes

Review `git diff --staged` and return a findings-first report.

## Steps

1. Inspect staged changes with git evidence.
2. Flag correctness, safety, and maintainability issues.
3. Order findings by severity.

## Output

Use `Critical`, `Warning`, and `Note` headings. Cite file paths.

## Do not

- Commit or push unless explicitly asked.
```

## Anti-patterns

- YAML frontmatter (breaks Cursor command format)
- Vague instructions ("review my code well")
- Mixing unrelated workflows in one command
- Duplicating large skill bodies — link to a skill instead

## Reload

Reload the Cursor window after adding or editing commands so `/` autocomplete picks up changes.

## Global vs project commands

Project commands live in `.cursor/commands/` (version-controlled). Personal commands can live in `~/.cursor/commands/`. Portable layout in this repo targets project commands only.
