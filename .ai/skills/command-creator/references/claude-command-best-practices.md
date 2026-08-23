# Claude Code Command Best Practices

Reference for `.claude/commands/<name>.md` slash commands.

**Official docs:** [Slash Commands](https://code.claude.com/docs/en/slash-commands)

## Format

| Rule | Detail |
| --- | --- |
| Location | `.claude/commands/<name>.md` |
| Invocation | `/name` (filename without `.md`) |
| Body | Markdown prompt executed when invoked |
| Frontmatter | Optional YAML metadata block |

## Common frontmatter keys

| Key | Purpose |
| --- | --- |
| `description` | Shown in `/` menu; synced from bootstrap on install |
| `argument-hint` | Hint for expected trailing arguments |
| `allowed-tools` | Restrict tools (e.g. `Read, Grep, Glob`) |
| `model` | Pin a model for this command |
| `disable-model-invocation` | User-only invocation when `true` |
| `context` | Run in isolated subagent when set to `fork` |

Put tool-specific keys in `wrappers/claude/COMMAND.md` — install merges them over shared defaults.

## Arguments

Use placeholders in the body:

- `$ARGUMENTS` — all text after the command name
- `$0`, `$1` — positional arguments

Example:

```markdown
---
description: Review a specific file path
argument-hint: [file-path]
allowed-tools: Read, Grep
---

Review the file at $ARGUMENTS for correctness and style issues.
```

## Skills vs legacy commands

Claude Code also supports `.claude/skills/<name>/SKILL.md` with the same slash invocation plus passive discovery. Use **commands** for explicit shortcuts; migrate to **skills** when the workflow needs autonomous triggering or bundled resources.

If both a skill and command share a name, the skill takes precedence.

## Reload

Restart or reload the Claude Code session after adding or editing commands.

## Shadowing bundled commands

Custom commands can shadow bundled skills/commands with the same name. Prefer unique kebab-case names to avoid accidental overrides.
