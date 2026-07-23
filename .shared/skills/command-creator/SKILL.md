---
name: command-creator
description: Create portable slash commands and Copilot prompts for Cursor, Claude Code, and GitHub Copilot using a shared-first layout, and iteratively improve them. Use when users want to create a command or prompt from scratch, bootstrap under the commands directory and install to .cursor/commands, .claude/commands, and .github/prompts, edit or review an existing command, or explain portable command structure and best practices — even if they do not say "slash command" or "prompt file" explicitly.
---

# Command Creator

A skill for creating portable slash commands and Copilot prompts and iteratively improving them.

At a high level, creating a command goes like this:

- Decide what `/command-name` should do, what arguments it accepts, and what output format it returns
- **Choose an authoring path** — bootstrap under `commands/<name>/` (preferred) or direct scaffold with `create_command.py` (see below)
- Write a tool-neutral shared `COMMAND.md` and tool-specific wrapper overrides only when needed
- **Install** when using bootstrap (`install_portable_command.py`); direct scaffold writes installed paths immediately
- Validate bootstrap, install to all three tools, reload each IDE, and test `/command-name`
- Help the user evaluate results for **correctness**, **completeness**, and **efficiency**
- Rewrite bootstrap content and wrappers based on feedback, then reinstall
- Repeat until satisfied

**Tool-specific execution** (reload steps, frontmatter keys such as `allowed-tools`, `agent`, or `tools`, and IDE-specific argument syntax) lives in your **tool wrapper** — read it after this shared skill. Do not assume a particular IDE unless your wrapper documents it.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft command, go straight to review and iterate.

---

## Communicating with the user

Users may range from experts to people new to slash commands. Match their vocabulary. Briefly explain terms like "bootstrap", "frontmatter", "prompt file", or "kebab-case" when unsure they know them.

If the user provides exact wording for command instructions or the description, use it **verbatim** in generated files.

---

## Creating a command

### Capture intent

Start by understanding intent. If the conversation already contains a workflow to capture, extract the command name, description, steps, output format, and guardrails from history first. Confirm gaps with the user.

Ask:

1. What should `/command-name` do when invoked?
2. Does the user pass arguments after the command? How should they be interpreted?
3. What output format should the agent return?
4. Are there tool-specific needs (Claude tool restrictions, Copilot agent mode, Cursor-only notes)?
5. Should wrappers override frontmatter for any tool?
6. What must the command **not** do?
7. Is this a command (explicit `/` invocation) or should it be a **skill** (passive discovery)?

### Interview and research

Ask about edge cases, success criteria, examples, and boundaries before writing files.

Check the target repository for existing command conventions. If `commands/`, `.cursor/commands/`, or `.github/prompts/` already exist, match their style.

Read bundled references for tool format rules:

- [portable-command-layout.md](references/portable-command-layout.md)
- [command-writing-guide.md](references/command-writing-guide.md)
- [cursor-command-best-practices.md](references/cursor-command-best-practices.md)
- [claude-command-best-practices.md](references/claude-command-best-practices.md)
- [copilot-prompt-best-practices.md](references/copilot-prompt-best-practices.md)

Use available research tools (MCP, docs search, similar commands in the repo) when helpful — in parallel when your environment allows.

### Choose authoring path

Pick **one** path before writing files. Do not hand-edit installed layers (`.shared/commands/`, tool command paths) when bootstrap source exists — edit bootstrap and reinstall.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained command; repo uses or wants `commands/<name>/`; command will be revised and reinstalled | `commands/<name>/COMMAND.md` + optional `wrappers/<tool>/COMMAND.md` | `install_portable_command.py` |
| **Direct** | One-off command without `commands/` bootstrap; quick scaffold into installed layout | `.shared/commands/<name>.md` (via script) | `create_command.py` |

**Prefer bootstrap when:**

- The command is part of this repo's portable config
- The user asks to bootstrap, migrate, or reinstall from `commands/<name>/`

**Prefer direct scaffold when:**

- The target project has no `commands/` directory and no plan to add bootstrap source
- The user wants a fast first draft before adopting bootstrap later

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Cross-tool behavior | `commands/<name>/COMMAND.md` → reinstall | `.shared/commands/<name>.md` |
| Tool-only overrides | `commands/<name>/wrappers/<tool>/COMMAND.md` → reinstall | Edit installed tool files (no bootstrap to reinstall) |
| Runtime read target | Installed tool paths (Cursor/Claude/Copilot) | Same |

After bootstrap edits, run `install_portable_command.py` before testing in the IDE.

### Bundled scripts

Resolve `<COMMAND_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `scripts/` and `references/` from that directory.

| Script | Path |
| --- | --- |
| Install bootstrap command | `<COMMAND_CREATOR_ROOT>/scripts/install_portable_command.py` |
| Create command (direct) | `<COMMAND_CREATOR_ROOT>/scripts/create_command.py` |
| Validate | `<COMMAND_CREATOR_ROOT>/scripts/quick_validate.py` |

Bootstrap source for this meta-skill may live at `skills/command-creator/`; installed copies live under `.shared/skills/command-creator/`.

**Module scripts:** when running scripts, use the scripts directory as working directory or invoke by full path from repo root.

### Anatomy of a portable command

**Installed layout:**

```
repo/
├── .shared/commands/<command-name>.md       # Tool-neutral prompt (install output)
├── .cursor/commands/<command-name>.md       # Plain Markdown (no frontmatter)
├── .claude/commands/<command-name>.md       # Claude slash command
└── .github/prompts/<command-name>.prompt.md # Copilot prompt file
```

**Bootstrap layout** (when the command ships bootstrap source):

```
repo/
└── commands/<command-name>/
    ├── COMMAND.md
    └── wrappers/
        ├── cursor/COMMAND.md    # optional; plain Markdown append
        ├── claude/COMMAND.md    # optional; frontmatter overrides + append
        └── github/COMMAND.md    # optional; frontmatter overrides + append
```

Install **always** writes all three tool paths plus the shared file.

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

On success, report these paths and reload instructions for Cursor, Claude Code, and VS Code + Copilot.

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

### Shared command rules

- Bootstrap `COMMAND.md` frontmatter: required `name`, `description` only
- Shared body must be tool-neutral — no Cursor/Claude/Copilot UI mechanics
- Cursor wrappers: plain Markdown only, no frontmatter
- Claude/GitHub wrappers: frontmatter for tool keys; body appends to shared content
- `name` and `description` sync from bootstrap on every install

### Command writing guide

Follow [command-writing-guide.md](references/command-writing-guide.md):

- One command = one focused workflow
- Numbered steps, explicit output format, guardrails
- Use `$ARGUMENTS` (Claude) or `${input:var}` (Copilot) when the command accepts user input
- Migrate to skill-creator when the workflow needs passive discovery or bundled resources

### Test and iterate

After install:

1. Reload each tool (see tool wrapper for specifics)
2. Invoke `/command-name` with a realistic prompt
3. Check output against the stated format and guardrails
4. Edit bootstrap (or direct paths), reinstall, and retest

Objective commands (fixed workflows, checklists) benefit from concrete test invocations. Subjective commands (tone, design taste) rely on qualitative review.

### Review and improve

When reviewing an existing command:

1. Read bootstrap `COMMAND.md` if present; otherwise read installed tool files
2. Check format rules per tool (Cursor: no frontmatter; Copilot: `.prompt.md` suffix)
3. Evaluate correctness, completeness, and efficiency
4. Prefer editing bootstrap and reinstalling over patching installed files

### Related skills

| Task | Skill |
| --- | --- |
| Passive discovery, bundled scripts, eval loops | [../skill-creator/SKILL.md](../skill-creator/SKILL.md) |
| Custom agents with shared-first layout | [../agent-creator/SKILL.md](../agent-creator/SKILL.md) |
| Commit message drafting (often a command candidate) | [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md) |

### Reference files

- [portable-command-layout.md](references/portable-command-layout.md) — paths, install comparison, templates
- [command-writing-guide.md](references/command-writing-guide.md) — cross-tool authoring checklist
- [cursor-command-best-practices.md](references/cursor-command-best-practices.md)
- [claude-command-best-practices.md](references/claude-command-best-practices.md)
- [copilot-prompt-best-practices.md](references/copilot-prompt-best-practices.md)

### Core loop summary

Capture intent → choose bootstrap vs direct → author tool-neutral `COMMAND.md` → add wrappers only when needed → validate → install → reload → test `/command-name` → iterate → expand test cases when stable.
