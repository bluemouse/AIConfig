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

Companion skills cross-link via `../<sibling>/SKILL.md` — edit and install related skills together when changes span layers (install order does not matter). Full skill catalog, cluster map, and workflow bundle definitions live in [README.md](README.md#skill-clusters) and [tools/bundles.md](tools/bundles.md).

## Common commands

All scripts run from the repository root using stdlib + `yaml` (`pytest -q` runs the full repository test suite).

**Validate & install bootstrap skills (`skills/<name>/` → `.agents/skills/<name>/`):**

```bash
python skills/skill-creator/scripts/quick_validate.py skills/<skill-name>
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name <skill-name> --source skills/<skill-name> --overwrite
python skills/skill-creator/scripts/quick_validate.py .agents/skills/<skill-name>
```

Re-run after every bootstrap edit; creates `.claude/skills -> ../.agents/skills` and excludes non-runtime test/eval/provenance files. Direct scaffold (only when not bootstrapping): `python skills/skill-creator/scripts/create_skill.py --root . --name my-skill`. Package archive: `python skills/skill-creator/scripts/package_skill.py .agents/skills/my-skill`.

**Validate & install bootstrap agents (`agents/<name>/` → `.claude/agents/` + `.github/agents/`):**

```bash
python skills/agent-creator/scripts/quick_validate.py --bootstrap-source agents/<agent-name>
python skills/agent-creator/scripts/install_portable_agent.py \
  --root . --name <agent-name> --source agents/<agent-name> --overwrite
python skills/agent-creator/scripts/quick_validate.py --root . --name <agent-name>
```

Direct scaffold: `python skills/agent-creator/scripts/create_agent.py --root . --name my-agent --description "..." --instructions-file <path> --overwrite`.

**Validate & install bootstrap commands (`commands/<name>/` → `.agents/skills/cmd-<name>/`):**

```bash
python skills/command-creator/scripts/quick_validate.py --bootstrap-source commands/<command-name>
python skills/command-creator/scripts/install_portable_command.py \
  --root . --name <command-name> --source commands/<command-name> --overwrite
python skills/command-creator/scripts/quick_validate.py --root . --name <command-name>
```

Direct scaffold: `python skills/command-creator/scripts/create_command.py --root . --name my-command --description "..." --body-file <path> --overwrite`.

**Refresh local scripts/guidelines or distribute to another project (`tools/installer.py`):**

```bash
# Regenerate local untracked .agents/tools/dev-workflow/ and .agents/skills/guidelines-*/ in this repo
python tools/installer.py . --scripts dev-workflow --override
python tools/installer.py . --guidelines coding-behavior response code-comment minutes --override

# Distribute installed assets to another project (regenerate local installs first on a fresh clone)
python tools/installer.py /path/to/other-project --bundles core-dev-workflow --dry-run
python tools/installer.py /path/to/other-project --dev-workflow --override
python tools/installer.py /path/to/other-project --purge-legacy
python tools/installer.py   # GUI when no arguments
```

Scripts membership is allowlisted via `INSTALLABLE_SCRIPTS` in `tools/installer.py`; guidelines are explicit-only (`--guidelines`). Full CLI flag and bundle reference: [README.md](README.md#distribute-to-another-project) and [tools/bundles.md](tools/bundles.md).

**Trigger-eval a skill description** (41 of 45 bootstrap skills ship `skills/<name>/eval-queries.json`):

```bash
cd skills/skill-creator && python -m scripts.run_eval \
  --skill-path ../../.agents/skills/<name> \
  --eval-set ../../skills/<name>/eval-queries.json
```

## Editing conventions

- Bootstrap `SKILL.md` and `AGENT.md` bodies must stay **tool-neutral** in the main body — tool-specific mechanics belong in a `## Tool notes` section (H2, with `### Claude Code` / `### Cursor` / `### GitHub Copilot` H3 subsections as needed) of the bootstrap body.
- Resolve `<SKILL_ROOT>` / `<SKILL_CREATOR_ROOT>` / `<AGENT_CREATOR_ROOT>` / `<COMMAND_CREATOR_ROOT>` as "the directory containing this skill's SKILL.md" — used throughout skill/agent/command-creator bodies to reference bundled `references/`, `scripts/`, `assets/` without hardcoding paths.
- Cross-link sibling skills with relative paths (e.g. `../cpp-coding/SKILL.md`) — they resolve after install because bootstrap and installed copies sit at the same depth.
- Author guidance by outcome: state the required constraints (safety, authorization, source-of-truth, installation), then useful expertise, then success criteria. Prescribed step sequences are defaults, not requirements — give the reason for each so a capable model can adapt it to the task. Move uncommon detail into references rather than padding the main body. A skill or guideline earns its place: when a simplification is proposed, compare `baseline` (target removed), `current`, and `candidate` arms on correctness and safety first, then efficiency; report uncertainty and the exact tested host/model rather than claiming general benefit. See the skill-creator references for the evaluation mechanics.
- `.cursor/rules/` (`.mdc` files, frontmatter controls `globs`/`alwaysApply`) is for small always-on or path-scoped rules — keep them composable, not full skills.
- Follow [coding-behavior](guidelines/coding-behavior.md) when generating or editing any code in this repo or in skill/agent output.
- Follow [code-comment](guidelines/code-comment.md) when writing or updating code comments or commit messages in this repo or in skill/agent output.
- Follow [minutes](guidelines/minutes.md) when drafting, formatting, or revising meeting minutes in this repo or in skill/agent output.
- Follow [response](guidelines/response.md) on **every response in this repo** (artifact files follow their templates and are exempt; regenerate local `.agents/skills/guidelines-<name>/` packages via `python tools/installer.py . --guidelines <name> --override` after editing a source).
