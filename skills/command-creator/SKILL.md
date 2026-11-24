---
name: command-creator
description: "Create and iteratively improve portable slash commands for Claude Code and GitHub Copilot as invocation-gated command-skills (bootstrap under commands/ and install to .agents/skills). Use to author a slash command or prompt file from scratch, edit or validate a command, or explain command-skill structure. Does not trigger on skills (skill-creator) or custom agents (agent-creator)."
---

# Command Creator

Flow: capture intent → choose bootstrap (`commands/<name>/COMMAND.md`, preferred) or direct scaffold (`create_command.py`) → write a tool-neutral `COMMAND.md` body → validate and install → reload session and test `/<name>` → iterate.

Shared authoring rules — bootstrap vs direct choice, authoritative-edit rule, intake, manual description tuning, output summary, and the iterate loop — live in [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md); this file carries only the command-specific delta.

Commands install as **command-skills**: `.agents/skills/cmd-<name>/SKILL.md` (`cmd-` directory prefix keeps them distinct in the shared `.agents/skills/` namespace, while frontmatter `name` keeps the slash command `/<name>`) with `disable-model-invocation: true` and an invocation-gated description (≤120 chars, stating the user explicitly invokes `/<name>`). Collisions between command and skill names are rejected.

## When NOT to Use

- **Creating a skill** (passive discovery, autonomous triggering, bundled resources) → [../skill-creator/SKILL.md](../skill-creator/SKILL.md)
- **Creating a custom agent** → [../agent-creator/SKILL.md](../agent-creator/SKILL.md)

---

## Creating a command

### Intake, paths, and bundled scripts

Follow [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md). Command-specific intake: what `/<name>` does, `$ARGUMENTS` interpretation, expected output format, optional `allowed-tools` permission gate, explicit guardrails ("Do not"), and whether explicit `/` invocation fits better than a passive skill (clarify via [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) if ambiguous; see [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) as a common command target).

| Path | Authoritative source | Install / scaffold | Installed target |
| --- | --- | --- | --- |
| **Bootstrap** | `commands/<name>/COMMAND.md` | `install_portable_command.py` | `.agents/skills/cmd-<name>/SKILL.md` |
| **Direct** | Installed command-skill (via script) | `create_command.py` | `.agents/skills/cmd-<name>/SKILL.md` |

Resolve `<COMMAND_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md` (`scripts/install_portable_command.py`, `scripts/create_command.py`, `scripts/quick_validate.py` — invoke by full path from repo root or from the `scripts/` directory).

### Bootstrap and direct commands

- **Bootstrap (preferred):** validate `commands/<command-name>/COMMAND.md` before installing:

```bash
python <COMMAND_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source commands/<command-name>
python <COMMAND_CREATOR_ROOT>/scripts/install_portable_command.py \
  --root . --name <command-name> --source commands/<command-name> --overwrite
```

- **Direct scaffold** (`--body-file` holds tool-neutral Markdown **without** frontmatter):

```bash
python <COMMAND_CREATOR_ROOT>/scripts/create_command.py \
  --root . --name <command-name> \
  --description "Run <workflow> when the user explicitly invokes /<command-name>." \
  --body-file <body.md> --overwrite
```

Report the installed `.agents/skills/cmd-<name>/SKILL.md` path and remind the user to reload/restart the coding agent session so `/<name>` is rediscovered.

### Command-skill and writing rules

Follow [command-writing-guide.md](references/command-writing-guide.md) and [portable-command-layout.md](references/portable-command-layout.md):
- **Frontmatter:** required `name` (kebab-case ≤64 chars) and `description` (≤120 chars, invocation-gated: `"... when the user explicitly invokes /<name>."`); optional `allowed-tools` (copied verbatim to the installed command-skill). Install injects `disable-model-invocation: true`.
- **Body:** one focused workflow with numbered steps, `$ARGUMENTS` where user input is accepted, explicit output format, and guardrails — strictly tool-neutral (no host UI or IDE product names; the validator rejects them).
- **Test and iterate:** follow [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md), reloading the session after each reinstall before testing `/<name>`.

### Reference files

- [portable-command-layout.md](references/portable-command-layout.md) — paths, install comparison, templates
- [command-writing-guide.md](references/command-writing-guide.md) — cross-tool authoring checklist
- [claude-command-best-practices.md](references/claude-command-best-practices.md), [copilot-prompt-best-practices.md](references/copilot-prompt-best-practices.md)
- [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md) — shared authoring skeleton

## Tool notes

Every host exposes `.agents/skills/cmd-<name>/SKILL.md` as `/<name>` while `disable-model-invocation: true` prevents autonomous self-invocation; reload/restart the session after install so `/<name>` is rediscovered, and use `$ARGUMENTS` for trailing user input.

### Claude Code

- Enforces `allowed-tools` frontmatter (when declared in bootstrap `COMMAND.md`) as a permission gate during `/<name>` execution.

### GitHub Copilot

- Exposes `/<name>` in Copilot Chat from the command-skill; `.github/copilot-instructions.md` remains separate always-on repository guidance.
