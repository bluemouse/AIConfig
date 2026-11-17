# Claude Code Command Best Practices

Reference for Claude Code slash commands — host-format background. command-creator installs commands as command-skills at `.agents/skills/cmd-<name>/SKILL.md` (with `disable-model-invocation: true` and optional `allowed-tools` frontmatter), which Claude Code invokes as `/<name>`; the native `.claude/commands/` format below is reference for hand-authored commands.

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

Command-skills carry their frontmatter (`name`, `description`, `disable-model-invocation`, optional `allowed-tools`) directly — there is no wrapper-merge step.

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

## Commands vs skills

Claude Code discovers skills through the `.claude/skills` bridge to `.agents/skills/`; a command-skill is the same file with `disable-model-invocation: true`, so it is slash-invoked only. Use **commands** for explicit shortcuts; drop the flag to migrate to a **skill** with passive discovery. Commands and skills share the `.agents/skills/` namespace — a name collision is rejected at install.

## Reload

Restart or reload the Claude Code session after adding or editing commands.

## Shadowing bundled commands

Custom commands can shadow bundled skills/commands with the same name. Prefer unique kebab-case names to avoid accidental overrides.
