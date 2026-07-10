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
├── tools/
│   └── install-skills.py              # Copy installed skills/agents to another project
├── skills/                            # Bootstrap skills (author here, then install)
│   ├── skill-creator/                 # Meta: creates and improves skills
│   ├── agent-creator/                 # Meta: creates and improves agents
│   ├── code-review-plus/              # Structured multi-scope code review
│   ├── commit-message-writer/         # Conventional Commit message drafting from git diffs
│   ├── github-guide/                  # GitHub PR/review delivery via gh CLI and gh api
│   ├── minutes-writer/                # Source-grounded meeting minutes for engineering meetings
│   ├── cpp-coding/                    # C++20 coding guidelines
│   ├── cpp-memory-guide/              # C++20 memory design and allocators
│   ├── cpp-testing/                   # C++20 GoogleTest/CMake testing
│   ├── cmake-dev/                     # CMake 3.20+ target-based builds
│   ├── csharp-coding/                 # C# and .NET coding guidelines
│   ├── gpu-rendering-guide/           # API-agnostic GPU renderer architecture
│   ├── krita-engine-dev/              # Krita brush engines, paintops, stroke scheduling
│   ├── mypaint-engine-dev/            # MyPaint/libmypaint brush engine and tiled surfaces
│   ├── python-coding/                 # Python 3.12+ CLI scripts and utilities
│   ├── qt-dev/                        # Qt 6 Widgets/CMake desktop UI for render tools
│   ├── vulkan-dev/                    # Vulkan 1.3 development
│   └── slang-dev/                     # Slang shader development (SPIR-V / MSL)
├── skills-ref/                        # Staging skill templates (read-only input for skill-bootstrapper)
├── .shared/
│   ├── agents/                        # Shared custom agents (canonical)
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
| `skills-ref/` | **Staging templates** — read-only drafts for **skill-bootstrapper**; output lands in `skills/<name>/`. |
| `.shared/agents/` | **Shared custom agents** — canonical agent definitions (edit directly). |
| `.shared/skills/` | **Shared skills** — tool-neutral packages with full content (`scripts/`, `references/`, `assets/`). |
| `.cursor/skills/`, `.claude/skills/`, `.github/skills/` | **Tool skills** — one wrapper per tool (`SKILL.md` only) that directs the agent to the shared skill. |
| `coding-behavior-guidelines.md` | Project-wide behavioral guidelines for coding agents (think first, simplicity, surgical changes). |
| `tools/install-skills.py` | Copy installed portable skills and agents from this repo into another project (CLI or GUI). |

## Bootstrap skills

Bootstrap skills live under `skills/`. Installing one copies content to `.shared/skills/<name>/` and generates tool skills under `.cursor/`, `.claude/`, and `.github/`. This repo includes:

| Skill | Path | Purpose |
| --- | --- | --- |
| `skill-creator` | `skills/skill-creator/` | Create, validate, package, and improve portable skills |
| `agent-creator` | `skills/agent-creator/` | Create, validate, and improve portable custom agents |
| `code-review-plus` | `skills/code-review-plus/` | Structured multi-scope code review |
| `commit-message-writer` | `skills/commit-message-writer/` | Draft Conventional Commit messages from staged/working diffs, commits, or ranges |
| `minutes-writer` | `skills/minutes-writer/` | Draft source-grounded meeting minutes and recaps from transcripts, notes, and supporting materials |
| `git-guide` | `skills/git-guide/` | Git mechanics: commit, push, rebase, conflicts, worktrees |
| `github-guide` | `skills/github-guide/` | GitHub delivery: `gh pr create`, post structured reviews, resolve threads |
| `pull-request-guide` | `skills/pull-request-guide/` | PR/MR authoring: description, sizing, testing evidence, self-review |
| `cpp-coding` | `skills/cpp-coding/` | C++20 coding against Core Guidelines |
| `cpp-memory-guide` | `skills/cpp-memory-guide/` | C++20 memory design: RAII, allocators, PMR, sanitizers |
| `cpp-testing` | `skills/cpp-testing/` | C++20 GoogleTest/CMake testing |
| `cmake-dev` | `skills/cmake-dev/` | CMake 3.20+ target-based builds, FetchContent, CTest, install/export |
| `csharp-coding` | `skills/csharp-coding/` | C# and .NET coding, toolchain, and testing |
| `gpu-rendering-guide` | `skills/gpu-rendering-guide/` | API-agnostic explicit-API renderer architecture |
| `krita-engine-dev` | `skills/krita-engine-dev/` | Krita brush engines, paintops, stroke scheduling, tiled compositing, canvas/GPU display |
| `mypaint-engine-dev` | `skills/mypaint-engine-dev/` | MyPaint/libmypaint brush engine, `.myb` presets, dab scheduling, tiled surfaces, parity testing |
| `python-coding` | `skills/python-coding/` | Python 3.12+ CLI scripts: argparse, pyproject.toml, ruff, pyright, pytest |
| `qt-dev` | `skills/qt-dev/` | Qt 6 Widgets/CMake desktop UI for Vulkan/Metal render tools |
| `vulkan-dev` | `skills/vulkan-dev/` | Vulkan 1.3 development, validation, and performance triage |
| `slang-dev` | `skills/slang-dev/` | Slang shader authoring and C++ host integration (SPIR-V / MSL) |
| `shader-guide` | `skills/shader-guide/` | Creative GLSL effects: SDF, ray marching, procedural generation, lighting, simulation, post |
| `glsl-coding` | `skills/glsl-coding/` | GLSL language, layouts, OpenGL/Vulkan SPIR-V bindings, maintainability |
| `usd-hydra2-dev` | `skills/usd-hydra2-dev/` | OpenUSD Hydra 2.0 scene indices, schemas, plugins, USD imaging, transparency, dirtying |
| `android-dev` | `skills/android-dev/` | Kotlin Android app layer: Compose, architecture, CameraX/Media3, permissions, release quality |
| `android-ndk-dev` | `skills/android-ndk-dev/` | Android NDK: CMake, JNI, native libraries, memory, debugging, 16 KB page size |
| `android-vulkan-dev` | `skills/android-vulkan-dev/` | Vulkan on Android: surface/swapchain, AHB interop, AVP, wide color, GPU image processing |

### Skill clusters

Several installed skills cross-link as companions — install related skills together when tasks span layers:

| Cluster | Skills | Relationship |
| --- | --- | --- |
| C++ | `cpp-coding`, `cpp-memory-guide`, `cpp-testing`, `cmake-dev` | CMake build graph → style and concurrency → CPU memory/ownership → GoogleTest/CTest |
| GPU rendering | `gpu-rendering-guide`, `vulkan-dev`, `slang-dev`, `shader-guide`, `glsl-coding`, `usd-hydra2-dev` | Renderer architecture → `Vk*` implementation → Slang shaders → creative GLSL effects / GLSL language → OpenUSD Hydra 2.0 scene-index consumption |
| Painting engines | `mypaint-engine-dev`, `krita-engine-dev`, `gpu-rendering-guide` | App-specific stroke/dab paths (MyPaint or Krita) → tiled compositing and parity → GPU surface/display strategy |
| Qt desktop | `qt-dev`, `cpp-coding`, `vulkan-dev`, `gpu-rendering-guide` | Widgets/CMake UI shell → C++ idioms → viewport/Vulkan integration → renderer architecture |
| Kotlin/JVM | `kotlin-coding`, `kotlin-testing`, `gradle-dev`, `gradle-android-dev` | Language/stdlib/API design → test frameworks and flakes → Gradle build engineering → AGP variants, lint, R8 |
| Android | `android-dev`, `android-ndk-dev`, `android-vulkan-dev`, `kotlin-coding`, `kotlin-testing`, `gradle-android-dev`, `vulkan-dev`, `gpu-rendering-guide` | App Kotlin/Compose → NDK/JNI → Android Vulkan → language/tests/AGP → generic Vulkan API → renderer architecture |
| Git workflow | `commit-message-writer`, `git-guide`, `pull-request-guide`, `code-review-plus`, `github-guide` | Draft commit messages → git mechanics (commit/push/rebase/worktrees) → PR authoring → structured diff review → GitHub delivery (`gh pr create`, post review, resolve threads) |
| Meeting notes | `minutes-writer`, `pull-request-guide`, `commit-message-writer` | Source-grounded minutes from transcripts → PR authoring → commit messages (does not create tickets or publish unless asked) |

`cpp-coding` links to `cpp-memory-guide` for allocation and ownership. `cmake-dev` links to `cpp-coding` for source idioms and `cpp-testing` for `gtest_discover_tests` and test targets. `gpu-rendering-guide` links to `vulkan-dev` for concrete Vulkan calls and to `slang-dev` for shader-system work; creative GLSL effects use `shader-guide`; GLSL language and layout rules use `glsl-coding`; for OpenUSD Hydra 2.0 scene-index pipelines, use `usd-hydra2-dev`, which links back to `gpu-rendering-guide` for API-agnostic renderer architecture. `slang-dev` links back to both for binding architecture and post-SPIR-V pipeline setup. `shader-guide` links to `glsl-coding` for GLSL syntax/layout and defers renderer architecture to `gpu-rendering-guide`. `glsl-coding` links to `shader-guide` for creative effect techniques. `mypaint-engine-dev` and `krita-engine-dev` are complementary painting-engine guides (MyPaint/libmypaint vs KDE/krita); each links to `gpu-rendering-guide` for standalone renderer architecture and lists the other as a near-miss. `qt-dev` links to `cpp-coding`, `cpp-testing`, `vulkan-dev`, and `gpu-rendering-guide` for non-Qt C++, tests, engine Vulkan, and render-graph work respectively. `kotlin-coding` links to `kotlin-testing` for test design, `gradle-dev` for Gradle build engineering, and `gradle-android-dev` for AGP builds. `kotlin-testing` defers Gradle wiring to `gradle-dev` and production API design to `kotlin-coding`. `gradle-dev` links to `gradle-android-dev` for AGP and to `kotlin-testing` for Kotlin test patterns. `gradle-android-dev` defers shared Gradle rules to `gradle-dev` and plain JVM test design to `kotlin-testing`. `android-dev` links to `kotlin-coding` for language semantics, `kotlin-testing` for test design, `gradle-android-dev` for AGP builds, `android-ndk-dev` for JNI/C++, and `android-vulkan-dev` for GPU rendering. `android-ndk-dev` links to `cpp-coding`, `cpp-memory-guide`, and `cpp-testing` for C++ implementation. `android-vulkan-dev` links to `vulkan-dev` for generic Vulkan 1.3 API and `gpu-rendering-guide` for renderer architecture. `commit-message-writer` links to `code-review-plus` for review-only tasks and does not auto-commit. `git-guide` handles git mechanics (commit, push, rebase, conflicts, worktrees) and defers message drafting to `commit-message-writer`. `pull-request-guide` owns PR description, sizing, and self-review; it defers git mechanics to `git-guide` and reviewer-side feedback to `code-review-plus`. `github-guide` delivers PRs and reviews on GitHub via `gh` / `gh api`; it defers diff review to `code-review-plus`, PR body craft to `pull-request-guide`, and push/rebase to `git-guide`. `minutes-writer` drafts source-grounded meeting minutes from transcripts and supporting materials; it defers PR authoring to `pull-request-guide` and commit messages to `commit-message-writer`, and does not create Jira tickets or publish to Confluence unless explicitly asked.

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

Install multiple related skills in any order when they cross-reference each other — e.g. the C++ cluster (`cpp-coding`, `cpp-memory-guide`, `cpp-testing`), the Kotlin/Gradle cluster (`kotlin-coding`, `kotlin-testing`, `gradle-dev`, `gradle-android-dev`), or the GPU stack (`gpu-rendering-guide`, `vulkan-dev`, `slang-dev`, `shader-guide`, `glsl-coding`, `usd-hydra2-dev`) link via `../<sibling>/SKILL.md`.

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
for skill in cmake-dev cpp-coding cpp-memory-guide cpp-testing; do
  python skills/skill-creator/scripts/install_portable_skill.py \
    --root . --name "$skill" --source "skills/$skill" --overwrite
done
```

**Example — install the GPU rendering stack:**

```bash
for skill in gpu-rendering-guide vulkan-dev slang-dev shader-guide glsl-coding; do
  python skills/skill-creator/scripts/install_portable_skill.py \
    --root . --name "$skill" --source "skills/$skill" --overwrite
done
```

**Example — install the Kotlin/Gradle cluster:**

```bash
for skill in kotlin-coding kotlin-testing gradle-dev gradle-android-dev; do
  python skills/skill-creator/scripts/install_portable_skill.py \
    --root . --name "$skill" --source "skills-ref/$skill" --overwrite
done
```

(After bootstrapping from `skills-ref/` into `skills/<name>/`, use `--source skills/<name>` instead.)

**Example — install the painting-engine skills:**

```bash
for skill in mypaint-engine-dev krita-engine-dev; do
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

- `.shared/agents/<agent-name>.md` — shared custom agent (canonical)
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

## Install skills and agents to another project

Use **`tools/install-skills.py`** to copy the **installed portable layout** from this repo into another project root. This copies `.shared/skills/<name>/`, `.shared/agents/<name>.md`, and any tool wrappers that exist under `.cursor/`, `.claude/`, and `.github/`. It does **not** install bootstrap sources from `skills/<name>/` — run `install_portable_skill.py` here first, then distribute.

**CLI** (from this repository root):

```bash
# Install all discovered skills and agents
python tools/install-skills.py /path/to/other-project

# Install selected skills or agents
python tools/install-skills.py /path/to/other-project --skills cpp-coding vulkan-dev
python tools/install-skills.py /path/to/other-project --agents skill-bootstrapper

# Replace existing installs in the target
python tools/install-skills.py /path/to/other-project --skills cpp-coding --override

# Remove from the target
python tools/install-skills.py /path/to/other-project --skills cpp-coding --uninstall
python tools/install-skills.py /path/to/other-project --agents skill-bootstrapper --uninstall
```

| Flag | Behavior |
| --- | --- |
| `TARGET` | Destination project root (required in CLI mode) |
| `--skills NAME ...` | Skill slugs to install or uninstall (default: all discovered) |
| `--agents NAME ...` | Agent slugs to install or uninstall (default: all discovered) |
| `--override` | Replace existing paths in the target; without it, skip and report |
| `--uninstall` | Remove the selected skills and agents from the target |
| *(no arguments)* | Open a tkinter GUI with the same options |

Without `--override`, existing paths in the target are skipped. The script refuses to install into this AIConfig repo itself. Reload each tool in the target project after install.

**GUI:**

```bash
python tools/install-skills.py
```

## Skills

Skills are folders with a `SKILL.md` (YAML frontmatter: `name`, `description`) plus optional bundled resources. The agent discovers skills from frontmatter and loads the body progressively when relevant.

**Portable (recommended):** author a **bootstrap skill** under `skills/<name>/`, install to produce a **shared skill** in `.shared/skills/<name>/` and **tool skills** under `.cursor/`, `.claude/`, and `.github/`.

**Standalone:** copy the full skill folder into one tool path (e.g. `.cursor/skills/<name>/` or `~/.cursor/skills/<name>/`) without the shared-first layout.

**Package a shared skill for distribution:**

```bash
python skills/skill-creator/scripts/package_skill.py .shared/skills/my-skill
```

**Copy installed skills and agents to another project** (shared + tool wrappers; see [Install skills and agents to another project](#install-skills-and-agents-to-another-project)):

```bash
python tools/install-skills.py /path/to/other-project
```

## Commands (Cursor)

Commands are plain Markdown files in `.cursor/commands/`. The filename becomes the slash command name (e.g. `create-skill-creator.md` → `/create-skill-creator`). No YAML frontmatter — the entire file is the prompt.

| Command | Purpose |
| --- | --- |
| `/create-skill-creator` | Install the skill-creator meta-skill (shared + tool skills) |
| `/create-agent-creator` | Install the agent-creator meta-skill (shared + tool skills) |
| `/create-bootstrap-skill` | Author a bootstrap skill under `skills/<name>/` from one or more templates (no install) |
| `/create-tool-skill` | Install shared + tool skills from one or more bootstrap sources |
| `/commit-message` | Draft compact and verbose commit messages for staged, working-tree, single-commit, or range scopes (same workflow as the `commit-message-writer` skill) |

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

**Draft commit messages:**

```text
/commit-message

/commit-message --working

/commit-message --range main..HEAD

/commit-message \
  --staged \
  --context @docs/plan.md \
  --jira PROJ-123 \
  --notes "Follow-up to yesterday's API change"
```

Default scope is staged changes. The command returns a compact one-liner and a verbose message; it does not commit unless you ask afterward. The same workflow is available as the installed **`commit-message-writer`** skill in Cursor, Claude Code, and Copilot when you are not using the slash command.

## Rules (Cursor)

Rules are `.mdc` files in `.cursor/rules/` with frontmatter controlling `globs` and `alwaysApply`. They apply automatically based on scope. Keep rules small and composable.

## Agents

Portable custom agents use a shared-first layout similar to skills:

- `.shared/agents/<name>.md` — canonical, tool-neutral definition
- `.cursor/agents/<name>.md`, `.claude/agents/<name>.md`, `.github/agents/<name>.agent.md` — tool wrappers

Use **agent-creator** to scaffold and validate new agents. Not every agent needs all three tool wrappers — some agents ship with only the layers you use (see `skill-bootstrapper` below).

### skill-bootstrapper (Cursor)

Automates the full portable skill pipeline in one agent run: bootstrap from templates → validate → self-review → install to shared + tool skills.

| Location | Role |
| --- | --- |
| `.shared/agents/skill-bootstrapper.md` | Canonical agent instructions |
| `.cursor/agents/skill-bootstrapper.md` | Cursor wrapper (reload window after install) |

Select **skill-bootstrapper** from the Cursor agent picker (reload the window after adding the agent files). Example invocation:

```text
skill-bootstrapper mypaint-engine-dev \
  --base skills-ref/mypaint-engine-dev \
  --verify https://github.com/mypaint/mypaint \
  --verify https://github.com/mypaint/libmypaint \
  --overwrite
```

Default pipeline: bootstrap → review → install. Flags: `--bootstrap-only`, `--skip-review`, `--no-overwrite`. The agent does not commit unless you ask; use `/commit-message` when ready.

Manual alternative: chain `/create-bootstrap-skill` then `/create-tool-skill` in chat.

## Further reading

- `AGENTS.md` — architecture, common commands, and editing conventions for all coding agents
- `CLAUDE.md` — Claude Code-specific discovery, evals, and wrapper workflow
- `coding-behavior-guidelines.md` — Karpathy-inspired behavioral guidelines for coding agents
- `skills/skill-creator/references/` — portable skill layout, JSON schemas, workflow and output patterns
- `skills/agent-creator/references/` — portable agent layout and wrapper templates
