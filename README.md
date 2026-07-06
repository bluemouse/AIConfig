# AI Configuration for Cursor, GitHub Copilot, and Claude Code

This repository provides a **portable, shared-first layout** for AI-assisted development across Cursor, GitHub Copilot, and Claude Code.

### Bootstrap skills and tool skills

| Term | Location | Role |
| --- | --- | --- |
| **Bootstrap skill** | `skills/<name>/` | Authoritative source. Edit `SKILL.md`, references, scripts, and optional custom tool skill templates in `wrappers/` here. |
| **Shared skill** | `.shared/skills/<name>/` | Tool-neutral install output — full instructions and bundled resources. |
| **Tool skill** | `.cursor/skills/<name>/`, `.claude/skills/<name>/`, `.github/skills/<name>/` | Thin wrapper per tool that points the agent at the shared skill (or holds tool-specific discovery notes). |

Install a bootstrap skill with `install_portable_skill.py` to generate the shared skill and tool skills. Re-run after edits to `skills/<name>/`.

## Repository layout

```
repo/
├── AGENTS.md                          # Tool-neutral agent guidance (architecture, commands)
├── CLAUDE.md                          # Claude Code-specific guidance
├── coding-behavior-guidelines.md      # LLM coding behavioral guidelines
├── skills/                            # Bootstrap skills (author here, then install)
│   ├── skill-creator/                 # Meta: creates and improves skills
│   ├── agent-creator/                 # Meta: creates and improves agents
│   ├── code-review-plus/              # Structured multi-scope code review
│   ├── cpp-coding/                    # C++20 coding guidelines
│   ├── cpp-memory-guide/              # C++20 memory design and allocators
│   ├── cpp-testing/                   # C++20 GoogleTest/CMake testing
│   ├── gpu-rendering-guide/           # API-agnostic GPU renderer architecture
│   ├── vulkan-dev/                    # Vulkan 1.3 development
│   └── slang-dev/                     # Slang shader development (SPIR-V / MSL)
├── .shared/
│   └── skills/
│       └── <skill-name>/              # Shared skill (canonical content after install)
├── .cursor/
│   ├── commands/                      # Slash commands (e.g. /create-skill-creator)
│   ├── rules/                         # Cursor rules (.mdc)
│   ├── skills/<skill-name>/           # Cursor tool skill → points to .shared/skills/
│   └── agents/                        # Cursor custom agents
├── .claude/
│   └── skills/<skill-name>/           # Claude Code tool skill
└── .github/
    ├── agents/                        # GitHub Copilot custom agents
    └── skills/<skill-name>/           # Copilot tool skill
```

### What each area is for

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Tool-neutral guidance for coding agents (architecture, scripts, editing conventions). |
| `CLAUDE.md` | Claude Code-specific guidance; references `AGENTS.md` for shared repo rules. |
| `skills/` | **Bootstrap skills** — edit here, then install to produce shared + tool skills. |
| `.shared/skills/` | **Shared skills** — tool-neutral packages with full content (`scripts/`, `references/`, `assets/`). |
| `.cursor/skills/`, `.claude/skills/`, `.github/skills/` | **Tool skills** — one wrapper per tool (`SKILL.md` only) that directs the agent to the shared skill. |
| `coding-behavior-guidelines.md` | Project-wide behavioral guidelines for coding agents (think first, simplicity, surgical changes). |

## Bootstrap skills

Bootstrap skills live under `skills/`. Installing one copies content to `.shared/skills/<name>/` and generates tool skills under `.cursor/`, `.claude/`, and `.github/`. This repo includes:

| Skill | Path | Purpose |
| --- | --- | --- |
| `skill-creator` | `skills/skill-creator/` | Create, validate, package, and improve portable skills |
| `agent-creator` | `skills/agent-creator/` | Create, validate, and improve portable custom agents |
| `code-review-plus` | `skills/code-review-plus/` | Structured multi-scope code review |
| `cpp-coding` | `skills/cpp-coding/` | C++20 coding against Core Guidelines |
| `cpp-memory-guide` | `skills/cpp-memory-guide/` | C++20 memory design: RAII, allocators, PMR, sanitizers |
| `cpp-testing` | `skills/cpp-testing/` | C++20 GoogleTest/CMake testing |
| `gpu-rendering-guide` | `skills/gpu-rendering-guide/` | API-agnostic explicit-API renderer architecture |
| `vulkan-dev` | `skills/vulkan-dev/` | Vulkan 1.3 development, validation, and performance triage |
| `slang-dev` | `skills/slang-dev/` | Slang shader authoring and C++ host integration (SPIR-V / MSL) |

### Skill clusters

Several installed skills cross-link as companions — install related skills together when tasks span layers:

| Cluster | Skills | Relationship |
| --- | --- | --- |
| C++ | `cpp-coding`, `cpp-memory-guide`, `cpp-testing` | Style and concurrency → CPU memory/ownership → tests and CMake |
| GPU rendering | `gpu-rendering-guide`, `vulkan-dev`, `slang-dev` | Renderer architecture → `Vk*` implementation → Slang shaders and reflection layout |

`cpp-coding` links to `cpp-memory-guide` for allocation and ownership. `gpu-rendering-guide` links to `vulkan-dev` for concrete Vulkan calls and to `slang-dev` for shader-system work. `slang-dev` links back to both for binding architecture and post-SPIR-V pipeline setup.

### skill-creator

Creates, validates, packages, and iteratively improves portable **skills**.

| Location | Role |
| --- | --- |
| `skills/skill-creator/` | Bootstrap skill (edit scripts and `SKILL.md` here) |
| `.shared/skills/skill-creator/` | Shared skill |
| `.cursor/skills/skill-creator/` | Cursor tool skill |
| `.claude/skills/skill-creator/` | Claude Code tool skill |
| `.github/skills/skill-creator/` | GitHub Copilot tool skill |

### agent-creator

Creates, validates, and iteratively improves portable custom **agents** (`.shared/agents/` + tool wrappers).

| Location | Role |
| --- | --- |
| `skills/agent-creator/` | Bootstrap skill (edit scripts and `SKILL.md` here) |
| `.shared/skills/agent-creator/` | Shared skill |
| `.cursor/skills/agent-creator/` | Cursor tool skill |
| `.claude/skills/agent-creator/` | Claude Code tool skill |
| `.github/skills/agent-creator/` | GitHub Copilot tool skill |

After editing a bootstrap skill, re-install to propagate changes to the shared skill and tool skills (see below).

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

The script copies the bootstrap skill to `.shared/skills/skill-creator/`, generates tool skills, validates all four paths, and prints a summary.

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

The script copies the bootstrap skill to `.shared/skills/agent-creator/`, generates tool skills, validates all four paths, and prints a summary.

Reload each tool after install (same as skill-creator above).

## Install a bootstrap skill

Use this workflow when a complete bootstrap skill already lives under `skills/<name>/`.

### 1. Author the bootstrap skill

Create or edit the bootstrap skill at `skills/<name>/`:

```
skills/<name>/
├── SKILL.md              # Tool-neutral skill (frontmatter: name, description)
├── references/           # Optional: docs loaded on demand
├── scripts/              # Optional: executable helpers
├── assets/               # Optional: templates, binaries, etc.
└── wrappers/             # Optional: custom tool skill templates (not copied to .shared/)
    ├── cursor/SKILL.md
    ├── claude/SKILL.md
    └── github/SKILL.md
```

**Shared `SKILL.md` rules:**

- Keep the body **tool-neutral** — no Cursor/Claude/Copilot-specific mechanics
- Resolve `<SKILL_ROOT>` as the directory containing the skill's `SKILL.md`
- Put bundled resources only under `references/`, `scripts/`, or `assets/`
- Cross-link sibling skills with relative paths (e.g. `../cpp-testing/SKILL.md`) — these resolve after install under `.shared/skills/`

**Custom tool skills (recommended):** add thin wrappers under `skills/<name>/wrappers/{cursor,claude,github}/SKILL.md` that point to `../../../.shared/skills/<name>/SKILL.md`, include discovery/reload notes, and document tool-specific mechanics. If omitted, `install_portable_skill.py` generates minimal default tool skills.

See `skills/code-review-plus/wrappers/` or `skills/cpp-coding/wrappers/` for examples.

### 2. Install (shared skill + tool skills)

From the repository root (requires `skill-creator` scripts):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name <skill-name> \
  --source skills/<skill-name> \
  --overwrite
```

The script:

1. Copies the bootstrap skill to `.shared/skills/<skill-name>/` (excluding `wrappers/`)
2. Writes tool skills to `.cursor/skills/<skill-name>/`, `.claude/skills/<skill-name>/`, and `.github/skills/<skill-name>/`
3. Validates the shared skill and all three tool skills with `quick_validate.py`

Install multiple related skills in any order when they cross-reference each other — e.g. the C++ cluster (`cpp-coding`, `cpp-memory-guide`, `cpp-testing`) or the GPU stack (`gpu-rendering-guide`, `vulkan-dev`, `slang-dev`) link via `../<sibling>/SKILL.md`.

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

Edit the bootstrap skill under `skills/<name>/`, then re-run the install command. The bootstrap skill remains the source of truth; `.shared/skills/` and tool skills are generated outputs.

**Example — install the C++ cluster:**

```bash
for skill in cpp-coding cpp-memory-guide cpp-testing; do
  python skills/skill-creator/scripts/install_portable_skill.py \
    --root . --name "$skill" --source "skills/$skill" --overwrite
done
```

**Example — install the GPU rendering stack:**

```bash
for skill in gpu-rendering-guide vulkan-dev slang-dev; do
  python skills/skill-creator/scripts/install_portable_skill.py \
    --root . --name "$skill" --source "skills/$skill" --overwrite
done
```

## Create a new portable skill (from scratch)

Use the installed **skill-creator** skill (or read `skills/skill-creator/SKILL.md`) when starting with an empty scaffold:

```bash
python skills/skill-creator/scripts/create_skill.py --root . --name my-skill
```

This creates:

- `.shared/skills/my-skill/` — shared skill with placeholder resources
- `.cursor/skills/my-skill/SKILL.md` — Cursor tool skill
- `.claude/skills/my-skill/SKILL.md` — Claude Code tool skill
- `.github/skills/my-skill/SKILL.md` — Copilot tool skill

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

- `.shared/skills/<skill-name>/` — shared skill (full content)

### Cursor

- `.cursor/rules/` — persistent rules (`.mdc`)
- `.cursor/commands/` — slash commands (plain `.md`, no frontmatter)
- `.cursor/skills/<skill-name>/` — Cursor tool skill (wrapper or full standalone skill)
- `.cursor/agents/` — custom agent definitions

Run commands as `/command-name` (filename without extension). Reload Cursor after adding or changing skills, rules, or commands.

### Claude Code

- `.claude/skills/<skill-name>/` — Claude Code tool skill (wrapper or full standalone skill)
- `.claude/agents/` — custom agent definitions (if used)

### VS Code + GitHub Copilot

- `.github/skills/<skill-name>/` — Copilot tool skill (wrapper or full standalone skill)
- `.github/agents/` — custom agents (`*.agent.md`)
- `.github/instructions/` — scoped instructions (`*.instructions.md`, `applyTo` globs)
- `.github/prompts/` — reusable prompt templates (`*.prompt.md`)

Reload VS Code after changes so Copilot picks up new files.

## Skills

Skills are folders with a `SKILL.md` (YAML frontmatter: `name`, `description`) plus optional bundled resources. The agent discovers skills from frontmatter and loads the body progressively when relevant.

**Portable (recommended):** author a **bootstrap skill** under `skills/<name>/`, install to produce a **shared skill** in `.shared/skills/<name>/` and **tool skills** under `.cursor/`, `.claude/`, and `.github/`.

**Standalone:** copy the full skill folder into one tool path (e.g. `.cursor/skills/<name>/` or `~/.cursor/skills/<name>/`) without the shared-first layout.

Package a shared skill for distribution:

```bash
python skills/skill-creator/scripts/package_skill.py .shared/skills/my-skill
```

## Commands (Cursor)

Commands are plain Markdown files in `.cursor/commands/`. The filename becomes the slash command name (e.g. `create-skill-creator.md` → `/create-skill-creator`). No YAML frontmatter — the entire file is the prompt.

| Command | Purpose |
| --- | --- |
| `/create-skill-creator` | Install the skill-creator meta-skill (shared + tool skills) |
| `/create-agent-creator` | Install the agent-creator meta-skill (shared + tool skills) |
| `/create-bootstrap-skill` | Author a bootstrap skill under `skills/<name>/` from one or more templates (no install) |
| `/create-tool-skill` | Install shared + tool skills from one or more bootstrap sources |

**Create a bootstrap skill from templates:**

```text
/create-bootstrap-skill my-skill \
  --base path/to/template/SKILL.md \
  [--base path/to/other-skill/ ...] \
  [--verify https://spec-or-docs-url ...] \
  [--notes "extra requirements"]
```

Use `--base` once for a single template, or repeat it to merge multiple skills into one cohesive bootstrap skill. Add `--verify` URLs or paths for external fact-checking.

**Install shared + tool skills from bootstrap sources:**

```text
/create-tool-skill --source skills/slang-dev

/create-tool-skill \
  --source skills/gpu-rendering-guide \
  --source skills/vulkan-dev \
  --source skills/slang-dev
```

Repeat `--source` to install a cluster of cross-linked companion skills in one batch. After bootstrap edits, re-run `/create-tool-skill` to refresh the install.

## Rules (Cursor)

Rules are `.mdc` files in `.cursor/rules/` with frontmatter controlling `globs` and `alwaysApply`. They apply automatically based on scope. Keep rules small and composable.

## Agents

Portable custom agents use a shared-first layout similar to skills:

- `.shared/agents/<name>.md` — canonical, tool-neutral definition
- `.cursor/agents/<name>.md`, `.claude/agents/<name>.md`, `.github/agents/<name>.agent.md` — tool wrappers

Use **agent-creator** to scaffold and validate new agents.

## Further reading

- `AGENTS.md` — architecture, common commands, and editing conventions for all coding agents
- `CLAUDE.md` — Claude Code-specific discovery, evals, and wrapper workflow
- `coding-behavior-guidelines.md` — Karpathy-inspired behavioral guidelines for coding agents
- `skills/skill-creator/references/` — portable skill layout, JSON schemas, workflow and output patterns
- `skills/agent-creator/references/` — portable agent layout and wrapper templates
