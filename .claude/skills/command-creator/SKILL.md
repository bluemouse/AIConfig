---
name: command-creator
description: Create portable slash commands and Copilot prompts for Cursor, Claude
  Code, and GitHub Copilot using a shared-first layout, and iteratively improve them.
  Use when users want to create a command or prompt from scratch, bootstrap under
  the commands directory and install to .cursor/commands, .claude/commands, and .github/prompts,
  edit or review an existing command, or explain portable command structure and best
  practices — even if they do not say "slash command" or "prompt file" explicitly.
---

# command-creator wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/command-creator/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<COMMAND_CREATOR_ROOT>` as `../../../.shared/skills/command-creator` and resolve paths to `scripts/` and `references/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill or installed commands so the agent rediscovers them.

## Install or refresh command-creator

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name command-creator --source skills/command-creator --overwrite
```

## Scaffolding user commands

**Bootstrap path:**

```bash
python skills/command-creator/scripts/quick_validate.py --bootstrap-source commands/<command-name>

python skills/command-creator/scripts/install_portable_command.py \
  --root . \
  --name <command-name> \
  --source commands/<command-name> \
  --overwrite
```

## Claude command format reminder

- Installed path: `.claude/commands/<name>.md`
- Supports YAML frontmatter: `description`, `argument-hint`, `allowed-tools`, `model`, etc.
- Use `$ARGUMENTS` in the body for user input after `/command-name`
- Put Claude-specific frontmatter overrides in `wrappers/claude/COMMAND.md`

## Skills vs commands

Claude also supports `.claude/skills/` for passive discovery. Use command-creator for explicit `/` shortcuts; migrate to skill-creator when the workflow needs autonomous triggering or bundled resources.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in the bootstrap under `skills/command-creator/`, then reinstall.
- Keep only Claude Code-specific information in this wrapper.
