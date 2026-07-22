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

### Custom agents: bootstrap → shared → tool

Agents that ship bootstrap source use the same three-layer pattern as skills. Other agents may still be scaffolded directly into `.shared/agents/` with `create_agent.py`.

1. **Bootstrap** (`agents/<name>/`, source-of-truth when present) — author `AGENT.md` and optional custom tool wrapper templates in `wrappers/{cursor,claude,github}/AGENT.md`.
2. **Shared** (`.shared/agents/<name>.md`, generated) — tool-neutral install output produced by `install_portable_agent.py`.
3. **Tool** (`.cursor/agents/<name>.md`, `.claude/agents/<name>.md`, `.github/agents/<name>.agent.md`, generated) — thin per-tool wrapper pointing at the shared agent, or a custom wrapper from `agents/<name>/wrappers/` when one exists.

**Never hand-edit `.shared/agents/` or tool agent folders for bootstrapped agents.** Edit `agents/<name>/` and re-run `install_portable_agent.py`. For agents without bootstrap source, edit `.shared/agents/<name>.md` directly or regenerate with `create_agent.py`.

Not every agent requires all three tool wrappers. For a partial set (e.g. Cursor only), bootstrap under `agents/<name>/wrappers/` with only the tools you need, install, then validate each installed path individually.

| | Skills | Custom agents (bootstrap) | Custom agents (direct) |
| --- | --- | --- | --- |
| Authoritative source | `skills/<name>/` | `agents/<name>/` | `.shared/agents/<name>.md` |
| Install / scaffold | `install_portable_skill.py` | `install_portable_agent.py` | `create_agent.py` |
| Distribute to another project | `tools/install-skills.py` (copies installed shared + wrappers) | same | same |
| Hand-edit shared layer? | No (regenerated from bootstrap) | No (regenerated from bootstrap) | Yes (canonical) |

Skills are discovered by frontmatter (`name`, `description`); an agent reads the `description` to decide when to load the full `SKILL.md` body. Description wording is load-bearing — `skill-creator`'s eval tooling (`run_eval.py`) tests whether a description reliably triggers on target phrases.

### Skill clusters

Some skills cross-link as companions — install and edit them together when tasks span layers (install order does not matter):

- **C++:** `cpp-coding`, `cpp-memory-guide`, `cpp-testing`, `cpp-performance-guide`, `cmake-dev`
- **GPU rendering:** `gpu-rendering-guide`, `vulkan-dev`, `slang-dev`, `shader-guide`, `glsl-coding`, `usd-hydra2-dev` (Hydra 2.0 scene-index work with `gpu-rendering-guide` for API-agnostic renderer architecture; creative GLSL effects with `shader-guide`, GLSL language/layout with `glsl-coding`)
- **Painting engines:** `mypaint-engine-dev`, `krita-engine-dev` (with `gpu-rendering-guide` for standalone GPU renderer architecture beyond app-specific stroke paths)
- **Qt desktop:** `qt-dev` (with `cpp-coding`, `vulkan-dev`, `gpu-rendering-guide` for non-Qt C++, engine Vulkan, and render-graph work)
- **Python:** `python-coding` (CLI scripts and utilities; standalone — no required companions in this repo)
- **Kotlin/JVM:** `kotlin-coding`, `kotlin-testing`, `gradle-dev` (with `gradle-android-dev` for Android Gradle Plugin builds)
- **Android:** `android-dev`, `android-ndk-dev`, `android-vulkan-dev` (with `kotlin-coding`, `kotlin-testing`, `gradle-android-dev` for language/tests/build; `vulkan-dev` and `gpu-rendering-guide` for generic Vulkan API and renderer architecture)
- **Git workflow:** `commit-message-writer`, `git-guide`, `pull-request-guide`, `code-reviewer`, `github-guide` (craft: commit messages → git mechanics → PR authoring → diff review; delivery on GitHub: `gh pr create`, post review, resolve threads)
- **Codebase learning:** `code-professor`, `plan-guide`, `debugging-guide`, `code-reviewer` (evidence-backed onboarding and architecture guides → plan changes → verified fixes → diff review; defers product research to `research-guide`)
- **Meeting notes:** `minutes-writer` (with `pull-request-guide` and `commit-message-writer` for adjacent authoring tasks; does not create tickets or publish docs unless asked)
- **Research workflow:** `research-guide`, `research-reviewer`, `plan-guide`, `plan-reviewer`, `plan-executor` (interactive discovery and research report → readiness audit → TDD-first implementation plan with Tests Designer → plan audit → execution; defers correctness audit to `implementation-auditor` and diff review to `code-reviewer`)
- **Implementation quality:** `test-driven-dev-guide`, `debugging-guide`, `implementation-auditor`, `code-reviewer` (TDD-first planning enforced by `plan-guide`/`plan-reviewer`, strict TDD during execution via `test-driven-dev-guide` → systematic root-cause debugging → evidence-based correctness audit → structured diff review)
- **Parallel execution:** `agent-runner` (with `code-reviewer`, `git-guide`, `skill-creator`, and `research-plan-harness` as near-misses — defers diff review, git mechanics, skill evals, and harness orchestration respectively)

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

**Scaffold a skill without bootstrap** (writes directly to `.shared/` + tool skills — prefer bootstrap under `skills/<name>/` and the **skill-creator** skill for new skills in this repo):

```bash
python skills/skill-creator/scripts/create_skill.py --root . --name my-skill
```

**Install/refresh a bootstrap agent → shared + tool wrappers:**

```bash
python skills/agent-creator/scripts/install_portable_agent.py \
  --root . --name <agent-name> --source agents/<agent-name> --overwrite
```

Validate bootstrap before install:

```bash
python skills/agent-creator/scripts/quick_validate.py --bootstrap-source agents/<agent-name>
```

**Create/validate a portable agent (direct scaffold):**

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

**Bootstrap and install skills or agents:** use the **skill-creator** and **agent-creator** installed skills. For skills, author under `skills/<name>/` (often from `skills-ref/<name>/` templates), validate, then run `install_portable_skill.py`. For agents, author under `agents/<name>/` or use `create_agent.py` for a direct scaffold, validate, then run `install_portable_agent.py` when using bootstrap source. See [README.md](README.md) for examples.

**Package a shared skill for distribution:**

```bash
python skills/skill-creator/scripts/package_skill.py .shared/skills/my-skill
```

**Copy installed skills and agents to another project** (from this repo root; copies `.shared/` plus tool wrappers — not bootstrap sources):

```bash
python tools/install-skills.py /path/to/other-project
python tools/install-skills.py /path/to/other-project --skills cpp-coding vulkan-dev --override
python tools/install-skills.py /path/to/other-project --bundles core-dev-workflow
python tools/install-skills.py /path/to/other-project --bundles target-bundle
python tools/install-skills.py /path/to/other-project --agents my-agent --uninstall
python tools/install-skills.py   # GUI when no arguments
```

Omit `--skills` and `--agents` to install or uninstall all names discovered under `.cursor/`, `.claude/`, and `.github/`. Use `--bundles` to install workflow skill sets from [tools/bundles.json](tools/bundles.json) or the dynamic `target-bundle` (skills already installed in the target project; documented in [tools/bundles.md](tools/bundles.md)). Without `--override`, existing target paths are skipped. See [README.md](README.md#install-skills-and-agents-to-another-project) for full flag reference.

**Trigger-eval a skill description:**

```bash
cd skills/skill-creator && python -m scripts.run_eval \
  --skill-path ../../.shared/skills/<name> \
  --eval-set ../../skills/<name>/eval-queries.json
```

Example for painting-engine skills: `mypaint-engine-dev` and `krita-engine-dev` ship `eval-queries.json` under their bootstrap paths. `minutes-writer`, `commit-message-writer`, `code-reviewer`, `github-guide`, `research-guide`, `research-reviewer`, `plan-guide`, `plan-reviewer`, `plan-executor`, `implementation-auditor`, `test-driven-dev-guide`, `debugging-guide`, `cpp-coding`, `cpp-performance-guide`, and `agent-runner` ship `eval-queries.json` for description trigger testing. Kotlin/Gradle skills in `skills-ref/` also ship `eval-queries.json` for description trigger testing.

See [README.md](README.md) for install examples and meta-skill usage.

## Editing conventions

- Bootstrap `SKILL.md` bodies must stay **tool-neutral** — no Cursor/Claude/Copilot-specific mechanics in the shared body. Tool-specific mechanics belong in that tool's wrapper under `skills/<name>/wrappers/` or the generated tool skill folder.
- Resolve `<SKILL_ROOT>` / `<SKILL_CREATOR_ROOT>` / `<AGENT_CREATOR_ROOT>` as "the directory containing this skill's SKILL.md" — used throughout skill/agent bodies to reference bundled `references/`, `scripts/`, `assets/` without hardcoding paths.
- Cross-link sibling skills with relative paths from the shared layer (e.g. `../cpp-testing/SKILL.md`), since links only need to resolve after install.
- `.cursor/rules/` (`.mdc` files, frontmatter controls `globs`/`alwaysApply`) is for small always-on or path-scoped rules — keep them composable, not full skills.
- Follow [coding-behavior-guidelines.md](coding-behavior-guidelines.md) when generating or editing any code in this repo or in skill/agent output.
