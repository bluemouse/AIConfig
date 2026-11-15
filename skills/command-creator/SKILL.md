---
name: command-creator
description: Create portable slash commands for Cursor, Claude Code, and GitHub Copilot as command-skills, and iteratively improve them. Use when users want to create a command from scratch, bootstrap under the commands directory and install to .agents/skills as an invocation-gated command-skill, edit or review an existing command, or explain portable command structure and best practices — even if they do not say "slash command" or "prompt file" explicitly. Does not trigger on creating skills (skill-creator) or custom agents (agent-creator).
---

# Command Creator

A skill for creating portable slash commands (command-skills) and iteratively improving them.

At a high level, creating a command goes like this:

- Decide what `/command-name` should do, what arguments it accepts, and what output format it returns
- **Choose an authoring path** — bootstrap under `commands/<name>/` (preferred) or direct scaffold with `create_command.py` (see below)
- Write a tool-neutral `COMMAND.md` body
- **Install** when using bootstrap (`install_portable_command.py`); direct scaffold writes the command-skill immediately
- Validate bootstrap, install, reload the coding agent, and test `/command-name`
- Help the user evaluate results for **correctness**, **completeness**, and **efficiency**
- Rewrite bootstrap content based on feedback, then reinstall
- Repeat until satisfied

Commands install as **command-skills**: one `.agents/skills/<name>/SKILL.md` with `disable-model-invocation: true` and an invocation-gated description (≤120 chars, states the user explicitly invokes `/<name>`). Every coding agent exposes it as `/<name>`; the model never self-invokes it.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft command, go straight to review and iterate.

## When NOT to Use

- **Creating a skill** — use [../skill-creator/SKILL.md](../skill-creator/SKILL.md) when the workflow needs passive discovery, autonomous triggering, or bundled resources
- **Creating a custom agent** — use [../agent-creator/SKILL.md](../agent-creator/SKILL.md) for portable custom agents

---

## Communicating with the user

Users may range from experts to people new to slash commands. Match their vocabulary. Briefly explain terms like "bootstrap", "frontmatter", "command-skill", or "kebab-case" when unsure they know them.

If the user provides exact wording for command instructions or the description, use it **verbatim** in generated files.

---

## Creating a command

### Capture intent

Start by understanding intent. If the conversation already contains a workflow to capture, extract the command name, description, steps, output format, and guardrails from history first. Confirm gaps with the user.

Ask:

1. What should `/command-name` do when invoked?
2. Does the user pass arguments after the command? How should they be interpreted?
3. What output format should the agent return?
4. Are there tool-specific needs (host tool restrictions, argument substitution syntax)?
5. Does the command need `allowed-tools` frontmatter (host permission gating)?
6. What must the command **not** do?
7. Is this a command (explicit `/` invocation) or should it be a **skill** (passive discovery)?

### Interview and research

Ask about edge cases, success criteria, examples, and boundaries before writing files.

The questions above are a fixed intake. When the request is ambiguous beyond them — question 7 does not settle command versus skill, the requested guardrails conflict with the workflow, or one request hides several commands — run the clarification loop in [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) before authoring files, and carry its requirement ledger into the command body and `description`.

Check the target repository for existing command conventions. If `commands/` or `.agents/skills/` already exist, match their style.

Read bundled references for tool format rules:

- [portable-command-layout.md](references/portable-command-layout.md)
- [command-writing-guide.md](references/command-writing-guide.md)
- [cursor-command-best-practices.md](references/cursor-command-best-practices.md)
- [claude-command-best-practices.md](references/claude-command-best-practices.md)
- [copilot-prompt-best-practices.md](references/copilot-prompt-best-practices.md)

Use available research tools (MCP, docs search, similar commands in the repo) when helpful — in parallel when your environment allows.

### Choose authoring path

Pick **one** path before writing files. Do not hand-edit installed command-skills (`.agents/skills/<name>/`) when bootstrap source exists — edit bootstrap and reinstall.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained command; repo uses or wants `commands/<name>/`; command will be revised and reinstalled | `commands/<name>/COMMAND.md` | `install_portable_command.py` |
| **Direct** | One-off command without `commands/` bootstrap; quick scaffold into installed layout | `.agents/skills/<name>/SKILL.md` (via script) | `create_command.py` |

**Prefer bootstrap when:**

- The command is part of this repo's portable config
- The user asks to bootstrap, migrate, or reinstall from `commands/<name>/`

**Prefer direct scaffold when:**

- The target project has no `commands/` directory and no plan to add bootstrap source
- The user wants a fast first draft before adopting bootstrap later

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Command behavior | `commands/<name>/COMMAND.md` → reinstall | `.agents/skills/<name>/SKILL.md` |
| Runtime read target | `.agents/skills/<name>/SKILL.md` (install output; do not hand-edit) | Same |

After bootstrap edits, run `install_portable_command.py` before testing in the IDE.

### Bundled scripts

Resolve `<COMMAND_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `scripts/` and `references/` from that directory.

| Script | Path |
| --- | --- |
| Install bootstrap command | `<COMMAND_CREATOR_ROOT>/scripts/install_portable_command.py` |
| Create command (direct) | `<COMMAND_CREATOR_ROOT>/scripts/create_command.py` |
| Validate | `<COMMAND_CREATOR_ROOT>/scripts/quick_validate.py` |

Bootstrap source for this meta-skill may live at `skills/command-creator/`; installed copies live under `.agents/skills/command-creator/`.

**Module scripts:** when running scripts, use the scripts directory as working directory or invoke by full path from repo root.

### Anatomy of a portable command

**Installed layout (command-skill):**

```
repo/
└── .agents/skills/<command-name>/
    └── SKILL.md       # disable-model-invocation: true; invocation-gated description
```

**Bootstrap layout** (when the command ships bootstrap source):

```
repo/
└── commands/<command-name>/
    └── COMMAND.md
```

Commands and skills share the `.agents/skills/` namespace — a command name that collides with an existing skill is rejected. Install writes the single command-skill file; there are no per-tool command outputs.

### Bootstrap and install

Validate bootstrap before install:

```bash
python <COMMAND_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source commands/<command-name>

python <COMMAND_CREATOR_ROOT>/scripts/install_portable_command.py \
  --root . \
  --name <command-name> \
  --source commands/<command-name> \
  --overwrite
```

On success, report the command-skill path and the reload instruction (restart or reload the coding agent session so `/<name>` is rediscovered).

### Direct scaffold

When bootstrap is not used:

```bash
python <COMMAND_CREATOR_ROOT>/scripts/create_command.py \
  --root . \
  --name <command-name> \
  --description "Short description for tool UIs." \
  --body-file /path/to/body.md \
  --overwrite
```

The body file should contain tool-neutral Markdown **without** frontmatter.

### Command-skill rules

- Bootstrap `COMMAND.md` frontmatter: required `name`, `description`; optional `allowed-tools` (transfers to the installed command-skill verbatim)
- Bootstrap body must be tool-neutral — no host UI mechanics or host names (the validator rejects them)
- Description: ≤120 chars, invocation-gated ("... when the user explicitly invokes /<name>.")
- Install writes `.agents/skills/<name>/SKILL.md` with `disable-model-invocation: true` — the model never self-invokes a command

### Command writing guide

Follow [command-writing-guide.md](references/command-writing-guide.md):

- One command = one focused workflow
- Numbered steps, explicit output format, guardrails
- Use `$ARGUMENTS` (the invoking host substitutes it) when the command accepts user input
- Migrate to skill-creator when the workflow needs passive discovery or bundled resources

### Test and iterate

After install:

1. Restart or reload the coding agent session so `/<name>` is rediscovered
2. Invoke `/command-name` with a realistic prompt
3. Check output against the stated format and guardrails
4. Edit bootstrap (or direct paths), reinstall, and retest

Objective commands (fixed workflows, checklists) benefit from concrete test invocations. Subjective commands (tone, design taste) rely on qualitative review.

### Review and improve

When reviewing an existing command:

1. Read bootstrap `COMMAND.md` if present; otherwise read the installed command-skill
2. Check format rules (frontmatter keys, description length, invocation gating, body neutrality)
3. Evaluate correctness, completeness, and efficiency
4. Prefer editing bootstrap and reinstalling over patching installed files

### Related skills

| Task | Skill |
| --- | --- |
| Passive discovery, bundled scripts, eval loops | [../skill-creator/SKILL.md](../skill-creator/SKILL.md) |
| Custom agents with dual-target layout | [../agent-creator/SKILL.md](../agent-creator/SKILL.md) |
| Commit message drafting (often a command candidate) | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) |
| Settling an ambiguous request before authoring | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) |

### Reference files

- [portable-command-layout.md](references/portable-command-layout.md) — paths, install comparison, templates
- [command-writing-guide.md](references/command-writing-guide.md) — cross-tool authoring checklist
- [cursor-command-best-practices.md](references/cursor-command-best-practices.md)
- [claude-command-best-practices.md](references/claude-command-best-practices.md)
- [copilot-prompt-best-practices.md](references/copilot-prompt-best-practices.md)

### Core loop summary

Capture intent → choose bootstrap vs direct → author tool-neutral `COMMAND.md` → validate → install as command-skill → reload → test `/command-name` → iterate → expand test cases when stable.

## Tool notes

Commands install as command-skills at `.agents/skills/<name>/SKILL.md` with `disable-model-invocation: true` — every host exposes them as `/<name>` and the model never self-invokes them. After install, restart or reload the coding agent session so `/<name>` is rediscovered.

### Claude Code

- The installed command-skill carries `allowed-tools` frontmatter when the bootstrap `COMMAND.md` declares it — Claude Code enforces it as a permission gate during command execution.
- Use `$ARGUMENTS` in the body for user input after `/command-name`; the invoking host substitutes it.
- `disable-model-invocation: true` keeps the model from triggering the command autonomously; only an explicit `/<name>` invocation loads it.

### Cursor

- Commands are invoked as `/command-name` in chat; the command-skill frontmatter is preserved and `disable-model-invocation: true` prevents autonomous model invocation.
- Use `$ARGUMENTS` in the body for user input; the invoking host substitutes it.

### GitHub Copilot

- Commands are invoked as `/command-name` in Copilot Chat from the command-skill.
- `.github/copilot-instructions.md` remains always-on repository guidance and is not created by command-creator; command-skills are task-specific and manually invoked.
