---
name: command-creator
description: "Create portable slash commands and Copilot prompts for Cursor, Claude Code, and GitHub Copilot using a shared-first layout, and iteratively improve them. Use when users want to create a command or prompt from scratch, bootstrap under the commands directory and install to .cursor/commands, .claude/commands, and .github/prompts, edit or review an existing command, or explain portable command structure and best practices — even if they do not say \"slash command\" or \"prompt file\" explicitly."
---

# command-creator (Cursor)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, and install workflow:

`../../../.shared/skills/command-creator/SKILL.md`

Resolve `<COMMAND_CREATOR_ROOT>` as `../../../.shared/skills/command-creator`. Resolve paths to `scripts/` and `references/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for content structure and portable conventions.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under `.shared/skills/<name>/`
- Project commands: `.cursor/commands/<name>.md` (plain Markdown, no frontmatter)
- Reload the **Cursor window** after adding, editing, or re-installing skills or commands

## Install or refresh command-creator

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name command-creator --source skills/command-creator --overwrite
```

If bootstrap source exists at `skills/command-creator/`, use that path for `--source` only.

## Scaffolding and validation (user commands)

**Bootstrap path (preferred):** author under `commands/<command-name>/`, then install:

```bash
python <COMMAND_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source commands/<command-name>

python <COMMAND_CREATOR_ROOT>/scripts/install_portable_command.py \
  --root . \
  --name <command-name> \
  --source commands/<command-name> \
  --overwrite
```

**Direct path:** when bootstrap is not used:

```bash
python <COMMAND_CREATOR_ROOT>/scripts/create_command.py \
  --root . \
  --name <command-name> \
  --description "Short description." \
  --body-file /path/to/body.md \
  --overwrite
```

## Cursor command format reminder

- Installed path: `.cursor/commands/<name>.md`
- **No YAML frontmatter** — install strips it from shared bootstrap content
- Invoke as `/command-name` in chat
- Cursor wrappers under `wrappers/cursor/` must also be plain Markdown

## Testing

After install, reload Cursor and type `/` to confirm the command appears. Run a realistic invocation and check output against the command's stated format.
