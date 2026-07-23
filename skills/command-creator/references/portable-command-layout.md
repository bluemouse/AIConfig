# Portable Command Layout

Use this guide when creating or reviewing slash commands and Copilot prompts that should work across Cursor, Claude Code, and GitHub Copilot.

## Two-phase workflow

Portable commands use **two phases**:

1. **Bootstrap** — Author tool-neutral content under `commands/<name>/` (plus optional custom wrappers). This is the source of truth when bootstrap exists.
2. **Install** — Run `install_portable_command.py` to copy `COMMAND.md` to `.shared/commands/<name>.md` and install tool outputs under `.cursor/`, `.claude/`, and `.github/`.

Do not hand-edit `.shared/commands/` or tool command folders for bootstrapped commands — edit bootstrap and reinstall.

For one-off commands without bootstrap source, use `create_command.py` to scaffold directly into the installed layout (direct path).

## Commands vs skills vs agents

| | Skills | Agents | Commands |
| --- | --- | --- | --- |
| Discovery | Passive (description triggers load) | Passive (description triggers load) | Explicit (`/command-name`) |
| Shared install output | `.shared/skills/<name>/` directory | `.shared/agents/<name>.md` | `.shared/commands/<name>.md` |
| Tool outputs | Thin pointer wrappers | Thin pointer wrappers | Format-transformed prompts |
| Install coverage | Always all three tools | Only wrappers present under `wrappers/` | Always all three tools |
| Bootstrap file | `SKILL.md` | `AGENT.md` | `COMMAND.md` |

## Directory structure

**Installed layout:**

```text
repo/
  .shared/
    commands/
      code-review.md
  .cursor/
    commands/
      code-review.md
  .claude/
    commands/
      code-review.md
  .github/
    prompts/
      code-review.prompt.md
```

**Bootstrap layout** (when the command ships bootstrap source):

```text
repo/
  commands/
    code-review/
      COMMAND.md
      wrappers/
        cursor/
          COMMAND.md
        claude/
          COMMAND.md
        github/
          COMMAND.md
```

`.shared/commands/<name>.md` is the tool-neutral install output with frontmatter (`name`, `description`). Install transforms that content into tool-specific formats:

- **Cursor** — body only (frontmatter stripped)
- **Claude Code** — frontmatter + body; optional wrapper overrides for `allowed-tools`, `model`, `argument-hint`, etc.
- **GitHub Copilot** — `.prompt.md` with frontmatter + body; optional wrapper overrides for `agent`, `model`, `tools`, etc.

## Shared command template

```markdown
---
name: code-review
description: Review staged changes and return a findings-first report with severity labels.
---

# Code Review

Review the staged git diff and return findings ordered by severity.

## Steps

1. Run `git diff --staged` and read the changed files.
2. Evaluate correctness, safety, and maintainability.
3. Return findings with file references.

## Output

Findings-first markdown report. Use `Critical`, `Warning`, and `Note` labels.

## Do not

- Commit, push, or rewrite history unless explicitly asked.
```

## Wrapper rules

Add wrappers only when a tool needs different behavior:

| Wrapper | Format | Purpose |
| --- | --- | --- |
| `wrappers/cursor/COMMAND.md` | Plain Markdown, **no frontmatter** | Append Cursor-only instructions |
| `wrappers/claude/COMMAND.md` | YAML frontmatter + body | Override Claude keys; append Claude-only instructions |
| `wrappers/github/COMMAND.md` | YAML frontmatter + body | Override Copilot keys; append Copilot-only instructions |

Install merges wrapper frontmatter over shared defaults. `name` and `description` always sync from bootstrap `COMMAND.md`.

## Install commands

Validate bootstrap before install:

```bash
python skills/command-creator/scripts/quick_validate.py --bootstrap-source commands/<command-name>

python skills/command-creator/scripts/install_portable_command.py \
  --root . \
  --name <command-name> \
  --source commands/<command-name> \
  --overwrite
```

Direct scaffold (no bootstrap):

```bash
python skills/command-creator/scripts/create_command.py \
  --root . \
  --name <command-name> \
  --description "Short description for tool UIs." \
  --body-file /path/to/body.md \
  --overwrite
```

## Validation

```bash
python skills/command-creator/scripts/quick_validate.py --bootstrap-source commands/<command-name>
python skills/command-creator/scripts/quick_validate.py --root . --name <command-name>
python skills/command-creator/scripts/quick_validate.py .shared/commands/<command-name>.md
python skills/command-creator/scripts/quick_validate.py .cursor/commands/<command-name>.md
python skills/command-creator/scripts/quick_validate.py .claude/commands/<command-name>.md
python skills/command-creator/scripts/quick_validate.py .github/prompts/<command-name>.prompt.md
```

## Reload requirements

After install, tell the user to reload each tool:

- **Cursor** — reload window
- **Claude Code** — restart or reload session
- **VS Code + Copilot** — reload window

## Migration to skills

When a command grows into passive discovery, bundled scripts, or large reference material, migrate to a portable skill under `skills/<name>/` using skill-creator instead of extending the command further.
