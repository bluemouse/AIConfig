# Agent guidance

Guidance for coding agents working in this repository. Tool-specific notes live in each tool's config file (e.g. `CLAUDE.md` for Claude Code).

## What this repo is

A **portable, shared-first layout** for AI-assisted development configuration shared across Cursor, GitHub Copilot, and Claude Code. It contains no application code — only **skills**, **agents**, and the tooling that installs them into each tool's config format. Everything here is Markdown (SKILL.md / agent .md files with YAML frontmatter) plus small Python scripts that copy/validate that content.

## Core architecture

Understanding paths under `skills/`, `.shared/`, `.cursor/`, `.claude/`, and `.github/` is required before editing anything.

### Skills: bootstrap → shared → tool

1. **Bootstrap** (`skills/<name>/`, source-of-truth) — author here. Contains `SKILL.md`, optional `references/`, `scripts/`, `assets/`, and optional `wrappers/{cursor,claude,github}/SKILL.md` (custom per-tool wrapper templates; not copied to `.shared/`).
2. **Shared** (`.shared/skills/<name>/`, generated) — tool-neutral install output produced by `install_portable_skill.py`. Full content lives here; cross-skill links (e.g. `../cpp-testing/SKILL.md`) resolve at this layer.
3. **Tool** (`.cursor/skills/<name>/`, `.claude/skills/<name>/`, `.github/skills/<name>/`, generated) — thin per-tool wrapper pointing at the shared skill, or a custom wrapper from `skills/<name>/wrappers/` if one exists.

**Never hand-edit `.shared/skills/` or tool skill folders.** They are generated output. Edit the bootstrap skill under `skills/<name>/` and re-run the install script — otherwise edits are lost on the next install.

### Custom agents: shared → tool

Custom agents use **two** layers — no bootstrap directory:

- **Shared:** `.shared/agents/<name>.md` (canonical, tool-neutral) — edit this file directly
- **Tool:** `.cursor/agents/<name>.md`, `.claude/agents/<name>.md`, `.github/agents/<name>.agent.md` — wrappers generated or synced via `create_agent.py` (see `skills/agent-creator/scripts/create_agent.py`)

Not every agent requires all three tool wrappers. For example, **`skill-bootstrapper`** ships with shared + Cursor wrapper only (`.shared/agents/skill-bootstrapper.md`, `.cursor/agents/skill-bootstrapper.md`) — validate those paths individually rather than with `quick_validate.py --root . --name skill-bootstrapper`, which expects all four files.

| | Skills | Custom agents |
| --- | --- | --- |
| Authoritative source | `skills/<name>/` (bootstrap) | `.shared/agents/<name>.md` |
| Install / scaffold | `install_portable_skill.py` | `create_agent.py` |
| Distribute to another project | `tools/install-skills.py` (copies installed shared + wrappers) | same |
| Hand-edit shared layer? | No (regenerated from bootstrap) | Yes (canonical) |

Skills are discovered by frontmatter (`name`, `description`); an agent reads the `description` to decide when to load the full `SKILL.md` body. Description wording is load-bearing — `skill-creator`'s eval tooling (`run_eval.py`) tests whether a description reliably triggers on target phrases.

### Skill clusters

Some skills cross-link as companions — install and edit them together when tasks span layers (install order does not matter):

- **C++:** `cpp-coding`, `cpp-memory-guide`, `cpp-testing`, `cmake-dev`
- **GPU rendering:** `gpu-rendering-guide`, `vulkan-dev`, `slang-dev`, `shader-guide`, `glsl-coding`, `usd-hydra2-dev` (Hydra 2.0 scene-index work with `gpu-rendering-guide` for API-agnostic renderer architecture; creative GLSL effects with `shader-guide`, GLSL language/layout with `glsl-coding`)
- **Painting engines:** `mypaint-engine-dev`, `krita-engine-dev` (with `gpu-rendering-guide` for standalone GPU renderer architecture beyond app-specific stroke paths)
- **Qt desktop:** `qt-dev` (with `cpp-coding`, `vulkan-dev`, `gpu-rendering-guide` for non-Qt C++, engine Vulkan, and render-graph work)
- **Python:** `python-coding` (CLI scripts and utilities; standalone — no required companions in this repo)
- **Kotlin/JVM:** `kotlin-coding`, `kotlin-testing`, `gradle-dev` (with `gradle-android-dev` for Android Gradle Plugin builds)
- **Android:** `android-dev`, `android-ndk-dev`, `android-vulkan-dev` (with `kotlin-coding`, `kotlin-testing`, `gradle-android-dev` for language/tests/build; `vulkan-dev` and `gpu-rendering-guide` for generic Vulkan API and renderer architecture)
- **Git workflow:** `commit-message-writer`, `git-guide`, `pull-request-guide` (with `code-review-plus` for review-only tasks)

See [README.md](README.md) for the full bootstrap skill table, cluster relationships, and install examples.

## Common commands

All scripts run from the repository root. There is no package manifest; scripts use only the `yaml` package (must be available in the active Python environment) plus stdlib.

**Install/refresh a bootstrap skill → shared + tool skills:**

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name <skill-name> --source skills/<skill-name> --overwrite
```

Re-run after every bootstrap edit — copies bootstrap → `.shared/skills/<name>/` (excluding `wrappers/`), regenerates the three tool skills, and validates all four paths.

**Validate a single skill path (shared or tool):**

```bash
python skills/skill-creator/scripts/quick_validate.py <path-to-skill-dir>
```

Run against `.shared/skills/<name>` and each tool skill path after inspection or before considering a skill done.

**Scaffold a skill without bootstrap** (writes directly to `.shared/` + tool skills — prefer bootstrap under `skills/<name>/` and `/create-bootstrap-skill` for new skills in this repo):

```bash
python skills/skill-creator/scripts/create_skill.py --root . --name my-skill
```

**Create/validate a portable agent:**

```bash
python skills/agent-creator/scripts/create_agent.py --root . --name my-agent \
  --description "..." --instructions-file <path> --overwrite
python skills/agent-creator/scripts/quick_validate.py --root . --name my-agent
```

For agents with only some tool wrappers (e.g. Cursor-only), validate each existing file:

```bash
python skills/agent-creator/scripts/quick_validate.py .shared/agents/<name>.md
python skills/agent-creator/scripts/quick_validate.py .cursor/agents/<name>.md
```

**Automate bootstrap + install (Cursor):** use the **skill-bootstrapper** custom agent (`.shared/agents/skill-bootstrapper.md`, `.cursor/agents/skill-bootstrapper.md`). It reads templates from `skills-ref/<name>/` or other `--base` paths, writes bootstrap output to `skills/<name>/`, validates, self-reviews, and calls `install_portable_skill.py` in one session. Manual alternative: `/create-bootstrap-skill` then `/create-tool-skill` (see [README.md](README.md)).

**Package a shared skill for distribution:**

```bash
python skills/skill-creator/scripts/package_skill.py .shared/skills/my-skill
```

**Copy installed skills and agents to another project** (from this repo root; copies `.shared/` plus tool wrappers — not bootstrap sources):

```bash
python tools/install-skills.py /path/to/other-project
python tools/install-skills.py /path/to/other-project --skills cpp-coding vulkan-dev --override
python tools/install-skills.py /path/to/other-project --agents skill-bootstrapper --uninstall
python tools/install-skills.py   # GUI when no arguments
```

Omit `--skills` and `--agents` to install or uninstall all names discovered under `.cursor/`, `.claude/`, and `.github/`. Without `--override`, existing target paths are skipped. See [README.md](README.md#install-skills-and-agents-to-another-project) for full flag reference.

**Trigger-eval a skill description:**

```bash
cd skills/skill-creator && python -m scripts.run_eval \
  --skill-path ../../.shared/skills/<name> \
  --eval-set ../../skills/<name>/eval-queries.json
```

Example for painting-engine skills: `mypaint-engine-dev` and `krita-engine-dev` ship `eval-queries.json` under their bootstrap paths. Kotlin/Gradle skills in `skills-ref/` also ship `eval-queries.json` for description trigger testing.

See [README.md](README.md) for Cursor slash commands (`/create-bootstrap-skill`, `/create-tool-skill`, etc.) that wrap these workflows.

## Editing conventions

- Bootstrap `SKILL.md` bodies must stay **tool-neutral** — no Cursor/Claude/Copilot-specific mechanics in the shared body. Tool-specific mechanics belong in that tool's wrapper under `skills/<name>/wrappers/` or the generated tool skill folder.
- Resolve `<SKILL_ROOT>` / `<SKILL_CREATOR_ROOT>` / `<AGENT_CREATOR_ROOT>` as "the directory containing this skill's SKILL.md" — used throughout skill/agent bodies to reference bundled `references/`, `scripts/`, `assets/` without hardcoding paths.
- Cross-link sibling skills with relative paths from the shared layer (e.g. `../cpp-testing/SKILL.md`), since links only need to resolve after install.
- `.cursor/rules/` (`.mdc` files, frontmatter controls `globs`/`alwaysApply`) is for small always-on or path-scoped rules — keep them composable, not full skills.
- Follow [coding-behavior-guidelines.md](coding-behavior-guidelines.md) when generating or editing any code in this repo or in skill/agent output.
