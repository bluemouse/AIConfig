# Agent guidance

Guidance for coding agents working in this repository. Keep this file **tool-neutral**: tool-specific mechanics live in each tool's own config (e.g. `.cursor/rules/`) and in the `## Tool notes` sections of the bootstrap skills and agents.

Claude Code (v2.1.277+) auto-loads this file as project instructions — but only when no `CLAUDE.md`-family file (`CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md`) exists in this repo or above it. Do not add one; any such file suppresses this file for Claude Code sessions.

## What this repo is

A **portable, single-root layout** for AI-assisted development configuration shared across Cursor, GitHub Copilot, and Claude Code. It contains no application code — only **skills**, **agents**, **commands** (slash prompts), and the tooling that installs them into each tool's config format. Everything here is Markdown (SKILL.md / agent .md / command files with YAML frontmatter where supported) plus small Python scripts that copy/validate that content.

## Core architecture

Understanding paths under `skills/`, `.agents/`, `.claude/`, and `.github/` is required before editing anything.

### Skills: bootstrap → installed

1. **Bootstrap** (`skills/<name>/`, source-of-truth) — author here. Contains `SKILL.md`, optional `references/`, `scripts/`, `assets/`. Tool-specific mechanics live in a `## Tool notes` section of the body (H3 subsections per tool as needed), not in separate per-tool files.
2. **Installed** (`.agents/skills/<name>/`, generated, **untracked**) — verbatim copy of the bootstrap package produced by `install_portable_skill.py`. It is the copy every tool reads; cross-skill links (e.g. `../cpp-coding/SKILL.md`) resolve here. Cursor and GitHub Copilot read it directly; Claude Code discovers it through the `.claude/skills -> ../.agents/skills` bridge symlink the installer creates. Generated output is never committed — regenerate after a clone or a bootstrap edit.

**Never hand-edit `.agents/skills/` for bootstrapped skills.** It is generated output. Edit the bootstrap skill under `skills/<name>/` and re-run the install script — otherwise edits are lost on the next install. The skill directory must be a direct child of a skills root; category subfolders (`skills/<category>/<name>/`) are rejected by the validator.

### Custom agents: bootstrap → dual-target

Agents that ship bootstrap source use the same two-phase pattern as skills. Other agents may still be scaffolded directly with `create_agent.py`.

1. **Bootstrap** (`agents/<name>/`, source-of-truth when present) — author `AGENT.md` here. Tool-specific mechanics live in a `## Tool notes` section of the body.
2. **Installed** (`.claude/agents/<name>.md` + `.github/agents/<name>.agent.md`, generated) — two real copies produced by `install_portable_agent.py`: the Claude/Cursor file is AGENT.md verbatim; the `.agent.md` file is the Copilot transform.

**Never hand-edit the installed agent files for bootstrapped agents.** Edit `agents/<name>/` and re-run `install_portable_agent.py`. For agents without bootstrap source, edit the installed files directly or regenerate with `create_agent.py`.

### Commands: bootstrap → command-skill

1. **Bootstrap** (`commands/<name>/`, source-of-truth) — author `COMMAND.md` here.
2. **Installed** (`.agents/skills/cmd-<name>/SKILL.md`, generated) — a **command-skill**: the command body with `disable-model-invocation: true` in frontmatter, produced by `install_portable_command.py`.

**Never hand-edit installed command-skills for bootstrapped commands.** Edit `commands/<name>/` and re-run `install_portable_command.py`.

Commands are **explicitly invoked** with `/command-name`, unlike skills and agents which load from description; the flag keeps the model from ever self-invoking one. Commands and skills share the `.agents/skills/` namespace — a command name colliding with an existing skill (or a skill install over an existing command-skill) is rejected by the installers.

| | Skills | Custom agents (bootstrap) | Custom agents (direct) | Commands |
| --- | --- | --- | --- | --- |
| Authoritative source | `skills/<name>/` | `agents/<name>/` | `.claude/agents/<name>.md` | `commands/<name>/` |
| Install / scaffold | `install_portable_skill.py` | `install_portable_agent.py` | `create_agent.py` | `install_portable_command.py` |
| Direct scaffold | `create_skill.py` | — | `create_agent.py` | `create_command.py` |
| Install output | `.agents/skills/<name>/` | `.claude/agents/` + `.github/agents/` | same | `.agents/skills/cmd-<name>/SKILL.md` (flagged) |
| Distribute to another project | `tools/installer.py` (copies the installed single-root/dual-target files) | same | same | same |
| Hand-edit install output? | No (regenerated from bootstrap) | No (regenerated from bootstrap) | Yes (canonical) | No (regenerated from bootstrap) |

Skills are discovered by frontmatter (`name`, `description`); an agent reads the `description` to decide when to load the full `SKILL.md` body. Description wording is load-bearing — `skill-creator`'s eval tooling (`run_eval.py`) tests whether a description reliably triggers on target phrases.

### Skill clusters

Some skills cross-link as companions — install and edit them together when tasks span layers (install order does not matter):

- **C++:** `cpp-coding`, `cpp-memory-guide`, `cpp-performance-guide`, `cmake-dev`
- **GPU rendering:** `gpu-rendering-guide`, `vulkan-dev`, `slang-dev`, `shader-guide`, `glsl-coding`, `usd-hydra2-dev` (Hydra 2.0 scene-index work with `gpu-rendering-guide` for API-agnostic renderer architecture; creative GLSL effects with `shader-guide`, GLSL language/layout with `glsl-coding`)
- **Painting engines:** `mypaint-engine-dev`, `krita-engine-dev` (with `gpu-rendering-guide` for standalone GPU renderer architecture beyond app-specific stroke paths)
- **Qt desktop:** `qt-dev`, `qt-ui-guide` (UI/UX design and `.ui` review with `qt-ui-guide`; C++/CMake Widgets implementation with `qt-dev`; with `cpp-coding`, `vulkan-dev`, `gpu-rendering-guide` for non-Qt C++, engine Vulkan, and render-graph work)
- **C#/.NET:** `csharp-coding` (C#/.NET language, LangVersion/SDK selection, minimal build/test verify; standalone — no required companions in this repo)
- **Kotlin/JVM:** `kotlin-coding`, `gradle-dev` (with `gradle-android-dev` for Android Gradle Plugin builds)
- **Android:** `android-dev`, `android-ndk-dev`, `android-vulkan-dev` (with `kotlin-coding`, `gradle-android-dev` for language/tests/build; `vulkan-dev` and `gpu-rendering-guide` for generic Vulkan API and renderer architecture)
- **Git workflow:** `git-guide`, `git-merge-guide`, `code-reviewer`, `techdoc-reviewer`, `github-guide` (craft: commit messages + git mechanics → deep local merge/rebase integration → diff review → documentation truth/sync when reader-visible contracts change; delivery on GitHub: `gh pr create`, PR authoring defaults (description, sizing, self-review), post review, resolve threads; explicit `/` shortcuts: use **command-creator** for portable slash commands)
- **Meta authoring:** `skill-creator`, `agent-creator`, `command-creator` (bootstrap → install for skills, agents, and slash commands/prompts respectively)
- **Codebase learning:** `code-professor`, `tutorial-writer`, `plan-guide`, `debugging-guide`, `code-reviewer` (evidence-backed onboarding and architecture guides → example-driven tutorials and user guides → plan changes → verified fixes → diff review; defers product research to `research-guide`)
- **Meeting notes:** `guidelines-minutes` guideline-skill (source-grounded minutes drafting from transcripts — never invent participants, decisions, dates, or commitments; separate confirmed decisions from discussion with the `not specified` convention; draft-only — no tickets, publishing, or email unless explicitly asked; installs as a skill package, explicit-only via `--guidelines`)
- **Requirement clarification:** `prompt-clarifier` (with `research-guide` for open-ended discovery, `plan-guide` for planning, and `debugging-guide` for defect root cause — clarify blocking decisions, then hand off)
- **Decision deliberation:** `advisory-council`, `devil-advocate` (with `prompt-clarifier` when the decision framing is ambiguous, `research-guide` for open-ended discovery, and `plan-reviewer` for plan audit — council for multi-perspective synthesis with dissent; devil-advocate for single-proposal adversarial review with proceed/rework/reject verdict)
- **Research workflow:** `research-guide`, `research-reviewer`, `plan-guide`, `plan-reviewer`, `plan-executor` (interactive discovery and research report → readiness audit → implementation plan with concrete per-task verification — strict TDD where mandated, stated alternative verification otherwise → plan audit → execution; defers correctness audit to `implementation-auditor` and diff review to `code-reviewer`)
- **Implementation quality:** `test-driven-dev-guide`, `debugging-guide`, `implementation-auditor`, `code-reviewer`, `techdoc-reviewer` (concrete per-task verification planned by `plan-guide`/`plan-reviewer` — strict TDD for `mandatory` tasks via `test-driven-dev-guide` during execution, stated alternative verification for `verification-led` tasks → systematic root-cause debugging → evidence-based correctness audit → structured diff review → documentation verification and synchronization when behavior or contracts change)
- **Dev-workflow harness:** `dev-workflow-orchestrator` plus the phase doer/checker skills (`prompt-clarifier`, `research-guide`/`research-reviewer`, `plan-guide`/`plan-reviewer`, `plan-executor`/`implementation-auditor`, `code-review-resolver`/`code-reviewer`) and the `/run-dev-workflow` + `/research`/`/plan`/`/implement`/`/review` commands — full pipeline via `/run-dev-workflow` or individual phase loops via the per-phase commands; installed/uninstalled as a unit via `--dev-workflow` (`dev-workflow-harness` bundle)
- **Presentation layer:** `guidelines-response` guideline-skill (cross-cutting chat-output shaping — result-first updates, structured questions at escalations, no preamble/recap, matter-of-fact errors, state restatement; installs as a skill package, explicit-only via `--guidelines`; artifact files are exempt)
- **Parallel execution:** `agent-runner` (with `code-reviewer`, `git-guide`, `skill-creator`, and `dev-workflow-orchestrator` as near-misses — defers diff review, git mechanics, skill evals, and harness orchestration respectively)

See [README.md](README.md) for the full bootstrap skill table, cluster relationships, and install examples.

## Common commands

All scripts run from the repository root. There is no package manifest; scripts use only the `yaml` package (must be available in the active Python environment) plus stdlib.

**Install/refresh a bootstrap skill → single-root copy:**

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name <skill-name> --source skills/<skill-name> --overwrite
```

Re-run after every bootstrap edit — copies bootstrap → `.agents/skills/<name>/`, ensures the `.claude/skills` bridge symlink exists, and validates the install.

**Validate a single skill path (bootstrap or installed):**

```bash
python skills/skill-creator/scripts/quick_validate.py <path-to-skill-dir>
```

Run against `.agents/skills/<name>` after inspection or before considering a skill done.

**Scaffold a skill without bootstrap** (writes directly to `.agents/skills/` — prefer bootstrap under `skills/<name>/` and the **skill-creator** skill for new skills in this repo):

```bash
python skills/skill-creator/scripts/create_skill.py --root . --name my-skill
```

**Install/refresh a bootstrap agent → dual-target copies:**

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

**Validate installed agent files:**

```bash
python skills/agent-creator/scripts/quick_validate.py .claude/agents/<name>.md
python skills/agent-creator/scripts/quick_validate.py .github/agents/<name>.agent.md
```

**Install/refresh a bootstrap command → command-skill:**

```bash
python skills/command-creator/scripts/install_portable_command.py \
  --root . --name <command-name> --source commands/<command-name> --overwrite
```

Validate bootstrap before install:

```bash
python skills/command-creator/scripts/quick_validate.py --bootstrap-source commands/<command-name>
```

**Create a portable command (direct scaffold):**

```bash
python skills/command-creator/scripts/create_command.py --root . --name my-command \
  --description "..." --body-file <path> --overwrite
python skills/command-creator/scripts/quick_validate.py --root . --name my-command
```

**Bootstrap and install skills, agents, or commands:** use the **skill-creator**, **agent-creator**, and **command-creator** installed skills. For skills, author under `skills/<name>/`, validate, then run `install_portable_skill.py`. For agents, author under `agents/<name>/` or use `create_agent.py` for a direct scaffold, validate, then run `install_portable_agent.py` when using bootstrap source. For commands, author under `commands/<name>/`, validate, then run `install_portable_command.py`. See [README.md](README.md) for examples.

**Package an installed skill for distribution:**

```bash
python skills/skill-creator/scripts/package_skill.py .agents/skills/my-skill
```

**Copy skills, agents, commands, and scripts to another project** (reads this checkout's generated `.agents/skills/` install and dual-target agent files, plus the tracked `tools/<name>/` script sources — not bootstrap sources; regenerate the local install first on a fresh clone):

```bash
python tools/installer.py /path/to/other-project
python tools/installer.py /path/to/other-project --skills cpp-coding vulkan-dev --override
python tools/installer.py /path/to/other-project --commands commit --override
python tools/installer.py /path/to/other-project --bundles core-dev-workflow
python tools/installer.py /path/to/other-project --bundles target-bundle
python tools/installer.py /path/to/other-project --bundles core-dev-workflow --dry-run
python tools/installer.py /path/to/other-project --guidelines coding-behavior
python tools/installer.py /path/to/other-project --purge-legacy
python tools/installer.py /path/to/other-project --agents my-agent --uninstall
python tools/installer.py /path/to/other-project --commands commit --uninstall
python tools/installer.py   # GUI when no arguments
```

Omit `--skills`, `--agents`, and `--commands` to install or uninstall all names discovered under `.agents/skills/` (skills and command-skills) and the dual-target agent paths. Use `--bundles` to install workflow skill sets from [tools/bundles.json](tools/bundles.json) or the dynamic `target-bundle` (skills, agents, commands, and scripts already installed in the target project; documented in [tools/bundles.md](tools/bundles.md)). Without `--override`, existing target paths are skipped. `--dry-run` previews the selected install, uninstall, or purge without writing anything to the target (the target must already exist). Scripts membership is allowlisted via the `INSTALLABLE_SCRIPTS` tuple in `tools/installer.py` — a tracked subdirectory under `tools/` is installable as scripts only when named there; add to the tuple when adding a scripts package. `--purge-legacy` removes a target's pre-single-root leftovers (`.ai/`, `.cursor/{skills,commands,agents}/`, `.github/prompts/`, `.github/skills/`, `.claude/commands/`, `.agents/guidelines/`, and `.claude/skills/` when it is a real directory) and composes with the kind selectors. See [README.md](README.md#distribute-to-another-project) for full flag reference.

**Trigger-eval a skill description:**

```bash
cd skills/skill-creator && python -m scripts.run_eval \
  --skill-path ../../.agents/skills/<name> \
  --eval-set ../../skills/<name>/eval-queries.json
```

Example for painting-engine skills: `mypaint-engine-dev` and `krita-engine-dev` ship `eval-queries.json` under their bootstrap paths. `git-guide`, `code-reviewer`, `techdoc-reviewer`, `github-guide`, `command-creator`, `research-guide`, `research-reviewer`, `plan-guide`, `plan-reviewer`, `plan-executor`, `implementation-auditor`, `test-driven-dev-guide`, `debugging-guide`, `cpp-coding`, `cpp-performance-guide`, `agent-runner`, `prompt-clarifier`, `advisory-council`, `devil-advocate`, `qt-ui-guide`, and `tutorial-writer` ship `eval-queries.json` for description trigger testing.

See [README.md](README.md) for install examples and meta-skill usage.

## Editing conventions

- Bootstrap `SKILL.md` and `AGENT.md` bodies must stay **tool-neutral** in the main body — tool-specific mechanics belong in a `## Tool notes` section (H2, with `### Claude Code` / `### Cursor` / `### GitHub Copilot` H3 subsections as needed) of the bootstrap body.
- Resolve `<SKILL_ROOT>` / `<SKILL_CREATOR_ROOT>` / `<AGENT_CREATOR_ROOT>` / `<COMMAND_CREATOR_ROOT>` as "the directory containing this skill's SKILL.md" — used throughout skill/agent/command-creator bodies to reference bundled `references/`, `scripts/`, `assets/` without hardcoding paths.
- Cross-link sibling skills with relative paths (e.g. `../cpp-coding/SKILL.md`) — they resolve after install because bootstrap and installed copies sit at the same depth.
- Author guidance by outcome: state the required constraints (safety, authorization, source-of-truth, installation), then useful expertise, then success criteria. Prescribed step sequences are defaults, not requirements — give the reason for each so a capable model can adapt it to the task. Move uncommon detail into references rather than padding the main body. A skill or guideline earns its place: when a simplification is proposed, compare `baseline` (target removed), `current`, and `candidate` arms on correctness and safety first, then efficiency; report uncertainty and the exact tested host/model rather than claiming general benefit. See the skill-creator references for the evaluation mechanics.
- `.cursor/rules/` (`.mdc` files, frontmatter controls `globs`/`alwaysApply`) is for small always-on or path-scoped rules — keep them composable, not full skills.
- Follow [coding-behavior](guidelines/coding-behavior.md) when generating or editing any code in this repo or in skill/agent output.
- Follow [code-comment](guidelines/code-comment.md) when writing or updating code comments or commit messages in this repo or in skill/agent output.
- Follow [minutes](guidelines/minutes.md) when drafting, formatting, or revising meeting minutes in this repo or in skill/agent output.
- Follow [response](guidelines/response.md) on **every response in this repo**: lead with the result or decision, raise every ask via the structured question tool (never a question buried in prose), no preamble/recap/closers, matter-of-fact errors, close with the done/next/for-you status block, size work by shape not clock. Artifact files follow their templates and are exempt. Installed as the skill package `.agents/skills/guidelines-<name>/` (generated, untracked) via `python tools/installer.py . --guidelines <name>` — regenerate after editing a source. This citation loads the tracked source directly, so it works on a fresh clone.
