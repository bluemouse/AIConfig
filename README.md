# AI Configuration for Cursor, GitHub Copilot, and Claude Code

This repository provides a **portable, shared-first layout** for AI-assisted development across Cursor, GitHub Copilot, and Claude Code. Tool-specific install folders hold thin wrappers; canonical skill content lives under `.shared/`.

## Repository layout

```
repo/
├── AGENTS.md                          # LLM coding behavioral guidelines
├── skills/                            # Bootstrap skill sources (edit here, then install)
│   ├── skill-creator/                 # Meta: creates and improves skills
│   ├── agent-creator/                 # Meta: creates and improves agents
│   ├── code-review-plus/              # Example: full skill package + custom wrappers
│   ├── cpp-coding/                    # Example: C++20 coding guidelines
│   └── cpp-testing/                   # Example: C++20 GoogleTest/CMake testing
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
| `skills/` | Bootstrap sources for portable skills. Author `SKILL.md` and bundled resources here, optionally add `wrappers/`, then install into `.shared/skills/` + tool wrappers. |
| `.shared/skills/` | Canonical, tool-neutral skill packages. Bundled resources (`scripts/`, `references/`, `assets/`) live here only. |
| `.cursor/skills/`, `.claude/skills/`, `.github/skills/` | Tool-specific wrappers (`SKILL.md` only) that instruct the agent to read the shared skill. |
| `skills-ref/` | Example and reference skills (Android, iOS, shader dev, code review, agent-creator, etc.) for copying or adaptation. |
| `agents-ref/` | Example agent role definitions for reference. |
| `AGENTS.md` | Project-wide behavioral guidelines for coding agents (think first, simplicity, surgical changes). |

## Installed skills

This repo ships bootstrap packages under `skills/` and installs them into the portable layout. Installed skills include:

| Skill | Bootstrap source | Purpose |
| --- | --- | --- |
| `skill-creator` | `skills/skill-creator/` | Create, validate, package, and improve portable skills |
| `agent-creator` | `skills/agent-creator/` | Create, validate, and improve portable custom agents |
| `code-review-plus` | `skills/code-review-plus/` | Structured multi-scope code review |
| `cpp-coding` | `skills/cpp-coding/` | C++20 coding against Core Guidelines |
| `cpp-testing` | `skills/cpp-testing/` | C++20 GoogleTest/CMake testing |

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

## Install a skill from bootstrap (`skills/`)

Use this workflow when a complete skill package already lives under `skills/<name>/` — the pattern used by `code-review-plus`, `cpp-coding`, and `cpp-testing`.

### 1. Author the bootstrap package

Create or edit the bootstrap tree at `skills/<name>/`:

```
skills/<name>/
├── SKILL.md              # Tool-neutral skill (frontmatter: name, description)
├── references/           # Optional: docs loaded on demand
├── scripts/              # Optional: executable helpers
├── assets/               # Optional: templates, binaries, etc.
└── wrappers/             # Optional: custom tool wrappers (not copied to .shared/)
    ├── cursor/SKILL.md
    ├── claude/SKILL.md
    └── github/SKILL.md
```

**Shared `SKILL.md` rules:**

- Keep the body **tool-neutral** — no Cursor/Claude/Copilot-specific mechanics
- Resolve `<SKILL_ROOT>` as the directory containing the skill's `SKILL.md`
- Put bundled resources only under `references/`, `scripts/`, or `assets/`
- Cross-link sibling skills with relative paths (e.g. `../cpp-testing/SKILL.md`) — these resolve after install under `.shared/skills/`

**Custom wrappers (recommended):** add thin wrappers under `skills/<name>/wrappers/{cursor,claude,github}/SKILL.md` that point to `../../../.shared/skills/<name>/SKILL.md`, include discovery/reload notes, and document tool-specific mechanics. If omitted, `install_portable_skill.py` generates minimal default wrappers.

See `skills/code-review-plus/wrappers/` or `skills/cpp-coding/wrappers/` for examples.

### 2. Install into the portable layout

From the repository root (requires `skill-creator` scripts):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name <skill-name> \
  --source skills/<skill-name> \
  --overwrite
```

The script:

1. Copies the bootstrap package to `.shared/skills/<skill-name>/` (excluding `wrappers/`)
2. Writes tool wrappers to `.cursor/skills/<skill-name>/`, `.claude/skills/<skill-name>/`, and `.github/skills/<skill-name>/`
3. Validates all four install paths with `quick_validate.py`

Install multiple related skills in any order when they cross-reference each other — e.g. `cpp-coding` and `cpp-testing` both link via `../<sibling>/SKILL.md`.

### 3. Validate (optional manual check)

```bash
for path in .shared/skills/<skill-name> \
            .cursor/skills/<skill-name> \
            .claude/skills/<skill-name> \
            .github/skills/<skill-name>; do
  python skills/skill-creator/scripts/quick_validate.py "$path"
done
```

### 4. Reload each tool

- **Cursor** — reload the window
- **VS Code + Copilot** — reload the window
- **Claude Code** — restart or reload the session

### 5. Re-install after edits

Edit the bootstrap source under `skills/<name>/`, then re-run the install command. The bootstrap tree remains the reinstall source; `.shared/skills/` and tool wrappers are generated outputs.

**Example — install `cpp-coding` and `cpp-testing`:**

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name cpp-coding --source skills/cpp-coding --overwrite

python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name cpp-testing --source skills/cpp-testing --overwrite
```

## Create a new portable skill (from scratch)

Use the installed **skill-creator** skill (or read `skills/skill-creator/SKILL.md`) when starting with an empty scaffold:

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
