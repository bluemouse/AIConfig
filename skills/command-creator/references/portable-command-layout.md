# Portable Command Layout

Use this guide when creating or reviewing portable slash commands that should work across Claude Code and GitHub Copilot.

## Two-phase workflow

Portable commands use **two phases**:

1. **Bootstrap** — Author tool-neutral content under `commands/<name>/`. This is the source of truth when bootstrap exists.
2. **Install** — Run `install_portable_command.py` to write the command-skill at `.agents/skills/cmd-<name>/SKILL.md` with `disable-model-invocation: true`.

Do not hand-edit installed command-skills for bootstrapped commands — edit bootstrap and reinstall.

For one-off commands without bootstrap source, use `create_command.py` to scaffold directly into the installed layout (direct path).

## Command-skills

A command installs as a single **command-skill**: `.agents/skills/cmd-<name>/SKILL.md` with frontmatter

```yaml
name: <name>
description: <≤120 chars, invocation-gated — "Use only when the user explicitly invokes /<name> ...">
disable-model-invocation: true
```

plus the command body. Every coding agent exposes it as `/<name>`; the model never self-invokes it. Commands and skills share the `.agents/skills/` namespace — a command name colliding with an existing skill is rejected.

## Commands vs skills vs agents

| | Skills | Agents | Commands |
| --- | --- | --- | --- |
| Discovery | Passive (description triggers load) | Passive (description triggers load) | Explicit (`/command-name`) |
| Install output | `.agents/skills/<name>/` directory | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` | `.agents/skills/cmd-<name>/SKILL.md` (flagged) |
| Model self-invocation | Allowed | Allowed | Blocked (`disable-model-invocation: true`) |
| Bootstrap file | `SKILL.md` | `AGENT.md` | `COMMAND.md` |

## Directory structure

**Installed layout (command-skill):**

```text
repo/
  .agents/
    skills/
      cmd-code-review/
        SKILL.md
```

**Bootstrap layout** (when the command ships bootstrap source):

```text
repo/
  commands/
    code-review/
      COMMAND.md
```

`.agents/skills/cmd-<name>/SKILL.md` is the install output. Install builds the command-skill frontmatter from the bootstrap `COMMAND.md` and copies the body verbatim; `allowed-tools`, when declared in bootstrap frontmatter, transfers verbatim.

## Shared command template

```markdown
---
name: code-review
description: Review staged changes when the user explicitly invokes /code-review. Returns a findings-first report.
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

## Validation rules

- `name` — kebab-case, ≤64 chars, matches the bootstrap directory name
- `description` — ≤120 chars and invocation-gated (states the user explicitly invokes the command)
- Body — tool-neutral: no host names or host UI mechanics
- Bootstrap frontmatter keys: `name`, `description`, optional `allowed-tools`
- Installed command-skill frontmatter keys: `name`, `description`, `disable-model-invocation` (always `true`), optional `allowed-tools`

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
  --description "Short invocation-gated description." \
  --body-file /path/to/body.md \
  --overwrite
```

## Validation

```bash
python skills/command-creator/scripts/quick_validate.py --bootstrap-source commands/<command-name>
python skills/command-creator/scripts/quick_validate.py --root . --name <command-name>
python skills/command-creator/scripts/quick_validate.py .agents/skills/cmd-<command-name>/SKILL.md
```

## Reload requirements

After install, tell the user to restart or reload the coding agent session so `/<command-name>` is rediscovered.

## Migration to skills

When a command grows into passive discovery, bundled scripts, or large reference material, migrate to a portable skill under `skills/<name>/` using skill-creator instead of extending the command further (drop `disable-model-invocation` so the model can discover it).
