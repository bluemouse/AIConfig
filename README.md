**AI Configuration for GitHub Copilot and Cursor**

This repository documents a portable layout for AI-assisted development with GitHub
Copilot and Cursor. It no longer ships bundled prompts, agents, instructions, rules,
commands, or skills.

## What was removed

The following top-level folders and their contents were deleted:

| Removed path | Previously contained |
| --- | --- |
| `copilot/` | Copilot agents, instructions, and prompts |
| `cursor/` | Cursor rules and slash commands |
| `document-cpp-code/` | C++ documentation skill |
| `tools/` | Conversion scripts (`agents2rules.py`, `instructions2rules.py`, `prompts2commands.py`) |
| `skills/*` | Bundled skill packages (`doc-coauthoring`, `skill-creator`, etc.) |

The `.github/` and `.cursor/` directories remain, but several symlinks under them still
point at the removed `copilot/` and `cursor/` folders and are currently broken. Recreate
those source folders or replace the symlinks with real directories before adding new assets.

## What remains

| Path | Status |
| --- | --- |
| `README.md` | This documentation |
| `.github/agents/` | Symlink → `../copilot/agents/` (broken until `copilot/` is restored) |
| `.github/instructions/` | Symlink → `../copilot/instructions/` (broken) |
| `.github/prompts/` | Symlink → `../copilot/prompts/` (broken) |
| `.github/skills/` | Empty install target for project-wide Copilot skills |
| `.cursor/rules/` | Symlink → `../cursor/rules/` (broken until `cursor/` is restored) |
| `.cursor/commands/` | Symlink → `../cursor/commands/` (broken) |
| `.cursor/skills/` | Empty install target for project-wide Cursor skills |
| `skills/` | Empty placeholder for skill source packages |
| `tools/` | Empty placeholder (conversion scripts removed) |

## Standard install paths

When you add assets to a project (this repo or another), use these locations:

### VS Code + GitHub Copilot

- `.github/agents/` — custom agents (`*.agent.md`)
- `.github/instructions/` — scoped instructions (`*.instructions.md`)
- `.github/prompts/` — reusable prompt templates (`*.prompt.md`)
- `.github/skills/<skill-name>/` — skill packages (`SKILL.md` plus optional resources)

After copying or symlinking, reload VS Code so Copilot picks up new files.

How you typically use them:

- **Agents**: select an agent in Copilot Chat (agent picker or @-mention, depending on your UI).
- **Instructions**: automatically apply when you edit matching files (`applyTo` globs).
- **Prompts**: run from Copilot Chat prompt UI or by invoking a prompt by name.
- **Skills**: loaded on demand when Copilot detects relevant triggers in the skill metadata.

### Cursor

- `.cursor/rules/` — persistent rules (`.mdc`)
- `.cursor/commands/` — slash commands (`.md`)
- `.cursor/skills/<skill-name>/` — skill packages

After copying or symlinking, reload Cursor.

How you typically use them:

- **Rules**: applied automatically based on `globs` / `alwaysApply`.
- **Commands**: run as slash commands in chat (e.g. `/my-command`).
- **Skills**: loaded when the agent matches the skill `description` in your prompt.

## Skills

Skills are self-contained packages: a folder with `SKILL.md` plus optional `scripts/`,
`references/`, and other resources. They are discoverable via the SKILL frontmatter
(`name` + `description`) and loaded progressively when relevant.

### Install

- **Project-wide (Copilot)**: copy a skill folder into `.github/skills/<skill-name>/`.
- **Project-wide (Cursor)**: copy a skill folder into `.cursor/skills/<skill-name>/`.
- **User-wide**: copy into `~/.github/skills/<skill-name>/` or your Cursor user skills location.

### Authoring

Each skill needs a `SKILL.md` with YAML frontmatter (`name`, `description`) and a clear
workflow body. Keep the main file focused; put long references and scripts in sibling
folders so the agent can load them only when needed.

## Agents (GitHub Copilot)

Custom agent definitions are `*.agent.md` files installed under `.github/agents/`.

In Copilot Chat, pick the agent by name or reference it per your Copilot UI.

## Instructions (GitHub Copilot)

Custom instructions are `*.instructions.md` files scoped via `applyTo` globs under
`.github/instructions/`.

Open or edit files that match `applyTo` patterns; Copilot applies relevant instruction
files. Keep instructions short and high-signal; split long guidance into multiple files.

## Prompts (GitHub Copilot)

Reusable prompt templates are `*.prompt.md` files under `.github/prompts/`.

Run the prompt from Copilot Chat’s prompt UI. Many prompts accept `${input:...}`
variables; Copilot will prompt you for values.

## Rules (Cursor)

Cursor rules are persistent instruction files (usually `.mdc`) with metadata controlling
when they apply (`globs`) or whether they always apply.

Rules apply automatically based on `alwaysApply` / `globs`. Keep rules composable: small
global rules plus scoped language or framework rules.

## Commands (Cursor)

Cursor custom commands are markdown files intended as chat slash commands under
`.cursor/commands/`.

Run in chat as `/command-name` (command name typically matches the filename).
