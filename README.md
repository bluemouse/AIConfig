# AI Configuration for Cursor, GitHub Copilot, and Claude Code

This repository provides a **portable, shared-first layout** for AI-assisted development across Cursor, GitHub Copilot, and Claude Code. Tool-specific install folders hold thin wrappers; canonical skill content lives under `.shared/`.

## Repository layout

```
repo/
├── AGENTS.md                          # LLM coding behavioral guidelines
├── skills/                            # Bootstrap / meta skill sources (edit here, then install)
│   ├── skill-creator/                 # skill-creator bootstrap package
│   └── agent-creator/                 # agent-creator bootstrap package
├── skills-ref/                        # Reference skill packages (not installed by default)
├── agents-ref/                        # Reference agent definitions (not installed by default)
├── .shared/
│   └── skills/
│       └── <skill-name>/              # Canonical skill content (scripts, references, SKILL.md)
├── .cursor/
│   ├── commands/                      # Slash commands (e.g. /create-skill-creator)
│   ├── rules/                         # Cursor rules (.mdc)
│   ├── skills/<skill-name>/           # Cursor wrappers → point to .shared/skills/
│   └── agents/                        # Cursor custom agents
├── .claude/
│   └── skills/<skill-name>/           # Claude Code wrappers
└── .github/
    ├── agents/                        # GitHub Copilot custom agents
    └── skills/<skill-name>/           # Copilot wrappers
```

### What each area is for

| Path | Purpose |
| --- | --- |
| `skills/` | Bootstrap sources for meta packages like `skill-creator` and `agent-creator`. Edit here, then install into the portable layout. |
| `.shared/skills/` | Canonical, tool-neutral skill packages. Bundled resources (`scripts/`, `references/`, `assets/`) live here only. |
| `.cursor/skills/`, `.claude/skills/`, `.github/skills/` | Tool-specific wrappers (`SKILL.md` only) that instruct the agent to read the shared skill. |
| `skills-ref/` | Example and reference skills (Android, iOS, shader dev, code review, agent-creator, etc.) for copying or adaptation. |
| `agents-ref/` | Example agent role definitions for reference. |
| `AGENTS.md` | Project-wide behavioral guidelines for coding agents (think first, simplicity, surgical changes). |

## Installed skills

This repo ships and installs two meta-skills:

### skill-creator

Creates, validates, packages, and iteratively improves portable **skills**.

| Location | Role |
| --- | --- |
| `skills/skill-creator/` | Bootstrap source (edit scripts and `SKILL.md` here) |
| `.shared/skills/skill-creator/` | Installed canonical skill |
| `.cursor/skills/skill-creator/` | Cursor wrapper |
| `.claude/skills/skill-creator/` | Claude Code wrapper |
| `.github/skills/skill-creator/` | GitHub Copilot wrapper |

### agent-creator

Creates, validates, and iteratively improves portable custom **agents** (`.shared/agents/` + tool wrappers).

| Location | Role |
| --- | --- |
| `skills/agent-creator/` | Bootstrap source (edit scripts and `SKILL.md` here) |
| `.shared/skills/agent-creator/` | Installed canonical skill |
| `.cursor/skills/agent-creator/` | Cursor wrapper |
| `.claude/skills/agent-creator/` | Claude Code wrapper |
| `.github/skills/agent-creator/` | GitHub Copilot wrapper |

After editing a bootstrap source, re-install to propagate changes to the portable layout (see below).

## Install skill-creator

**Option A — Cursor slash command**

In Cursor chat, run:

```
/create-skill-creator
```

**Option B — install script**

From the repository root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name skill-creator \
  --source skills/skill-creator \
  --overwrite
```

The script copies the bootstrap package to `.shared/skills/skill-creator/`, generates tool wrappers, validates all four paths, and prints a summary.

Reload each tool after install:

- **Cursor** — reload the window
- **VS Code + Copilot** — reload the window
- **Claude Code** — restart or reload the session

## Install agent-creator

Requires **skill-creator** (or at least its `install_portable_skill.py`) to install into the portable layout.

**Option A — Cursor slash command**

In Cursor chat, run:

```
/create-agent-creator
```

**Option B — install script**

From the repository root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name agent-creator \
  --source skills/agent-creator \
  --overwrite
```

The script copies the bootstrap package to `.shared/skills/agent-creator/`, generates tool wrappers, validates all four paths, and prints a summary.

Reload each tool after install (same as skill-creator above).

## Create a new portable skill

Use the installed **skill-creator** skill (or read `skills/skill-creator/SKILL.md`) and scaffold with:

```bash
python skills/skill-creator/scripts/create_skill.py --root . --name my-skill
```

This creates:

- `.shared/skills/my-skill/` — shared skill with placeholder resources
- `.cursor/skills/my-skill/SKILL.md` — Cursor wrapper
- `.claude/skills/my-skill/SKILL.md` — Claude Code wrapper
- `.github/skills/my-skill/SKILL.md` — Copilot wrapper

Validate before and after editing:

```bash
python skills/skill-creator/scripts/quick_validate.py .shared/skills/my-skill
python skills/skill-creator/scripts/quick_validate.py .cursor/skills/my-skill
```

For a standalone skill in one location (personal install or single-tool copy):

```bash
python skills/skill-creator/scripts/init_skill.py my-skill --path ~/.cursor/skills
```

See `skills/skill-creator/references/portable-skill-layout.md` for path conventions and wrapper templates.

## Create a new portable agent

Use the installed **agent-creator** skill (or read `skills/agent-creator/SKILL.md`). Draft tool-neutral instructions, then scaffold:

```bash
python skills/agent-creator/scripts/create_agent.py \
  --root . \
  --name my-agent \
  --description "What the agent does and when to use it." \
  --instructions-file /path/to/instructions-body.md \
  --overwrite
```

This creates:

- `.shared/agents/my-agent.md` — shared, tool-neutral agent definition
- `.cursor/agents/my-agent.md` — Cursor wrapper
- `.claude/agents/my-agent.md` — Claude Code wrapper
- `.github/agents/my-agent.agent.md` — GitHub Copilot wrapper

Validate immediately:

```bash
python skills/agent-creator/scripts/quick_validate.py --root . --name my-agent
```

See `skills/agent-creator/references/portable-agent-layout.md` for path conventions and wrapper templates.

## Standard install paths

When adding assets to this repo or another project, use these locations:

### Shared (all tools)

- `.shared/skills/<skill-name>/` — canonical skill package

### Cursor

- `.cursor/rules/` — persistent rules (`.mdc`)
- `.cursor/commands/` — slash commands (plain `.md`, no frontmatter)
- `.cursor/skills/<skill-name>/` — skill wrapper or full standalone skill
- `.cursor/agents/` — custom agent definitions

Run commands as `/command-name` (filename without extension). Reload Cursor after adding or changing skills, rules, or commands.

### Claude Code

- `.claude/skills/<skill-name>/` — skill wrapper or full standalone skill
- `.claude/agents/` — custom agent definitions (if used)

### VS Code + GitHub Copilot

- `.github/skills/<skill-name>/` — skill wrapper or full standalone skill
- `.github/agents/` — custom agents (`*.agent.md`)
- `.github/instructions/` — scoped instructions (`*.instructions.md`, `applyTo` globs)
- `.github/prompts/` — reusable prompt templates (`*.prompt.md`)

Reload VS Code after changes so Copilot picks up new files.

## Skills

Skills are folders with a `SKILL.md` (YAML frontmatter: `name`, `description`) plus optional bundled resources. The agent discovers skills from frontmatter and loads the body progressively when relevant.

**Portable (recommended):** keep full instructions and resources in `.shared/skills/<name>/`; wrappers in tool folders point back to the shared skill.

**Standalone:** copy the full skill folder into one tool path (e.g. `.cursor/skills/<name>/` or `~/.cursor/skills/<name>/`).

Package a shared skill for distribution:

```bash
python skills/skill-creator/scripts/package_skill.py .shared/skills/my-skill
```

## Commands (Cursor)

Commands are plain Markdown files in `.cursor/commands/`. The filename becomes the slash command name (e.g. `create-skill-creator.md` → `/create-skill-creator`). No YAML frontmatter — the entire file is the prompt.

## Rules (Cursor)

Rules are `.mdc` files in `.cursor/rules/` with frontmatter controlling `globs` and `alwaysApply`. They apply automatically based on scope. Keep rules small and composable.

## Agents

Portable custom agents use a shared-first layout similar to skills:

- `.shared/agents/<name>.md` — canonical, tool-neutral definition
- `.cursor/agents/<name>.md`, `.claude/agents/<name>.md`, `.github/agents/<name>.agent.md` — tool wrappers

Use **agent-creator** to scaffold and validate new agents. Reference examples are in `agents-ref/`.

## Reference material

- `skills-ref/` — skill packages you can copy, adapt, or install into your own projects
- `agents-ref/` — agent role templates
- `skills/skill-creator/references/` — portable skill layout, JSON schemas, workflow and output patterns
- `skills/agent-creator/references/` — portable agent layout and wrapper templates

These reference folders are not wired into the portable install layout unless you install them explicitly.
