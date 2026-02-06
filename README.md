**AI Configuration for GitHub Copilot and Cursor**

This repository is a portable “starter kit” for configuring AI-assisted development.
It contains:

- **Copilot** custom agents, instructions, and reusable prompts.
- **Cursor** rules and slash commands that mirror the Copilot setup.
- **Skills** (bundled workflows + optional scripts/references) that can be installed per-project
	or user-wide.

The folders here are intentionally **templates**: copy (or symlink) the pieces you want into a
target repository’s expected locations.

## Quick Setup

### VS Code + GitHub Copilot

Recommended target locations inside the repo you want to work on:

- `.github/agents/` ← from `copilot/agents/`
- `.github/instructions/` ← from `copilot/instructions/`
- `.github/prompts/` ← from `copilot/prompts/`
- `.github/skills/` ← from `skills/` (copy each skill folder)

After copying/symlinking, reload VS Code so Copilot picks up new files.

How you typically use them:

- **Agents**: select an agent in Copilot Chat (agent picker / @-mention, depending on your UI).
- **Instructions**: automatically apply when you edit matching files (`applyTo` globs).
- **Prompts**: run from Copilot Chat prompt UI or by invoking a prompt by name.
- **Skills**: loaded on demand when Copilot detects relevant triggers in the skill metadata.

### Cursor

Recommended target locations inside the repo you want to work on:

- `.cursor/rules/` ← from `cursor/rules/`
- `.cursor/commands/` ← from `cursor/commands/`

After copying/symlinking, reload Cursor.

How you typically use them:

- **Rules**: applied automatically based on `globs` / `alwaysApply`.
- **Commands**: run as slash commands in chat (e.g., `/create-readme`).

## Skills

Skills are self-contained packages (a folder with `SKILL.md` plus optional `scripts/`,
`references/`, etc.). They’re designed to be discoverable via the SKILL frontmatter
(`name` + `description`) and then loaded progressively.

### Files

- [skills/doc-coauthoring/SKILL.md](skills/doc-coauthoring/SKILL.md) — Structured workflow for
	co-authoring docs (context gathering → refinement → reader testing).
- [skills/skill-creator/SKILL.md](skills/skill-creator/SKILL.md) — Guide for creating skills,
	including structure patterns and packaging guidance.
- [skills/skill-creator/scripts/init_skill.py](skills/skill-creator/scripts/init_skill.py) —
	Scaffolds a new skill folder from a template.
- [skills/skill-creator/scripts/quick_validate.py](skills/skill-creator/scripts/quick_validate.py)
	— Minimal validator for skill frontmatter and naming rules.
- [skills/skill-creator/scripts/package_skill.py](skills/skill-creator/scripts/package_skill.py)
	— Packages a skill folder into a distributable `.skill` (zip) after validation.
- [skills/skill-creator/references/output-patterns.md](skills/skill-creator/references/output-patterns.md)
	— Patterns for consistent output templates and examples.
- [skills/skill-creator/references/workflows.md](skills/skill-creator/references/workflows.md) —
	Patterns for sequential and conditional workflows.

### Install / Setup

- **Project-wide**: copy a skill folder into `.github/skills/<skill-name>/`.
- **User-wide**: copy into `~/.github/skills/<skill-name>/`.

If you want to use the packaging/validation scripts:

- Ensure Python is available.
- `quick_validate.py` requires `PyYAML`.

### Use

- In Copilot/Cursor, skills are intended to be discovered from the `description` field.
	When your prompt matches that description, the agent can load and follow the SKILL workflow.
- For skill authoring, use the `skill-creator` skill’s scripts:
	- Initialize: `python skills/skill-creator/scripts/init_skill.py my-skill --path .github/skills`
	- Validate: `python skills/skill-creator/scripts/quick_validate.py .github/skills/my-skill`
	- Package: `python skills/skill-creator/scripts/package_skill.py .github/skills/my-skill ./dist`

## Agents (GitHub Copilot)

These are custom agent definitions (`*.agent.md`) designed for GitHub Copilot.

### Files

- [copilot/agents/debian-linux-expert.agent.md](copilot/agents/debian-linux-expert.agent.md) —
	Debian-focused sysadmin guidance (apt/dpkg/systemd, stable defaults, rollback-friendly steps).
- [copilot/agents/debug.agent.md](copilot/agents/debug.agent.md) — Systematic debugging workflow
	(reproduce → root cause → fix → verify → report).
- [copilot/agents/demonstrate-understanding.agent.md](copilot/agents/demonstrate-understanding.agent.md)
	— Socratic “prove you understand it” questioning mode.
- [copilot/agents/devils-advocate.agent.md](copilot/agents/devils-advocate.agent.md) —
	Stress-test ideas one objection at a time, then summarize when you say “end game”.
- [copilot/agents/expert-cpp-software-engineer.agent.md](copilot/agents/expert-cpp-software-engineer.agent.md)
	— Senior C++ engineering guidance (modern C++, architecture, testing, CI, maintainability).
- [copilot/agents/implementation-plan.agent.md](copilot/agents/implementation-plan.agent.md) —
	Deterministic, machine-executable implementation plan generator (no code edits).
- [copilot/agents/prompt-builder.agent.md](copilot/agents/prompt-builder.agent.md) — Prompt Builder
	+ Prompt Tester personas for designing and validating prompts.
- [copilot/agents/simple-app-idea-generator.agent.md](copilot/agents/simple-app-idea-generator.agent.md)
	— High-energy app ideation through interactive questioning.
- [copilot/agents/specification.agent.md](copilot/agents/specification.agent.md) — Creates/updates
	AI-optimized specification documents in `/spec/` using a strict template.
- [copilot/agents/Thinking-Beast-Mode.agent.md](copilot/agents/Thinking-Beast-Mode.agent.md) —
	“keep going until solved” autonomy-oriented agent.

### Install / Setup

- Copy files into `.github/agents/` in your target repo.

### Use

- In Copilot Chat, pick the agent by name (agent selector) or reference it per your Copilot UI.
- Use these when you want a specific workflow (debugging, spec writing, plan generation, etc.).

## Instructions (GitHub Copilot)

These are Copilot custom instructions (`*.instructions.md`) scoped via `applyTo` globs.
They are meant to live in `.github/instructions/` in a target repository.

### Files

- [copilot/instructions/agent-skills.instructions.md](copilot/instructions/agent-skills.instructions.md)
	— How to structure agent skills (`SKILL.md` frontmatter, resources, progressive loading).
- [copilot/instructions/agents.instructions.md](copilot/instructions/agents.instructions.md) —
	How to write maintainable `*.agent.md` files (frontmatter, tools, handoffs, etc.).
- [copilot/instructions/cmake-vcpkg.instructions.md](copilot/instructions/cmake-vcpkg.instructions.md)
	— CMake/vcpkg manifest-mode guidance and cross-compiler considerations.
- [copilot/instructions/instructions.instructions.md](copilot/instructions/instructions.instructions.md)
	— How to write `*.instructions.md` files (frontmatter, structure, examples).
- [copilot/instructions/markdown.instructions.md](copilot/instructions/markdown.instructions.md)
	— Markdown formatting/content standards for docs.
- [copilot/instructions/prompt-engineering.instructions.md](copilot/instructions/prompt-engineering.instructions.md)
	— Prompt engineering + safety, bias, and security best practices.
- [copilot/instructions/python.instructions.md](copilot/instructions/python.instructions.md) —
	Python style guide (type hints, docstrings, readability, PEP 8, testing).
- [copilot/instructions/rules.instructions.md](copilot/instructions/rules.instructions.md) —
	How to structure Cursor rules and where to install them.

### Install / Setup

- Copy into `.github/instructions/`.

### Use

- Open/edit files that match `applyTo` patterns; Copilot will apply relevant instruction files.
- Keep these short and high-signal; split long guidance into multiple instruction files.

## Prompts (GitHub Copilot)

These are reusable prompt templates (`*.prompt.md`) intended for `.github/prompts/`.

### Files

- [copilot/prompts/convert-plaintext-to-md.prompt.md](copilot/prompts/convert-plaintext-to-md.prompt.md)
	— Converts plaintext docs into markdown with options and pattern-based conversion.
- [copilot/prompts/create-agentsmd.prompt.md](copilot/prompts/create-agentsmd.prompt.md) — Generates
	a repository root `AGENTS.md` following the public agents.md guidance.
- [copilot/prompts/create-implementation-plan.prompt.md](copilot/prompts/create-implementation-plan.prompt.md)
	— Creates deterministic implementation plans in `/plan/` using a strict template.
- [copilot/prompts/create-readme.prompt.md](copilot/prompts/create-readme.prompt.md) — Creates a
	project README with inspiration from a few example repos.
- [copilot/prompts/create-specification.prompt.md](copilot/prompts/create-specification.prompt.md)
	— Creates an AI-optimized spec in `/spec/` using a strict template.
- [copilot/prompts/create-tldr-page.prompt.md](copilot/prompts/create-tldr-page.prompt.md) —
	Creates a `tldr` page from authoritative docs + examples.
- [copilot/prompts/prompt-builder.prompt.md](copilot/prompts/prompt-builder.prompt.md) — Interactive
	wizard for generating new `.prompt.md` files.
- [copilot/prompts/update-implementation-plan.prompt.md](copilot/prompts/update-implementation-plan.prompt.md)
	— Updates an existing plan file while preserving deterministic structure.
- [copilot/prompts/update-markdown-file-index.prompt.md](copilot/prompts/update-markdown-file-index.prompt.md)
	— Inserts/updates a file index table/list for a folder into a markdown file.
- [copilot/prompts/update-specification.prompt.md](copilot/prompts/update-specification.prompt.md)
	— Updates an existing spec file while keeping the strict structure.
- [copilot/prompts/write-coding-standards-from-file.prompt.md](copilot/prompts/write-coding-standards-from-file.prompt.md)
	— Infers coding standards from code and optionally writes a standards doc.

### Install / Setup

- Copy into `.github/prompts/`.

### Use

- Run the prompt from Copilot Chat’s prompt UI.
- Many prompts accept `${input:...}` variables; Copilot will prompt you for values.

## Rules (Cursor)

Cursor rules are persistent instruction files (usually `.mdc`) with metadata controlling
when they apply (`globs`) or whether they always apply.

### Files

- [cursor/rules/prompt-engineering.mdc](cursor/rules/prompt-engineering.mdc) — Always-applied rule
	with prompt engineering + safety/bias/security best practices.
- [cursor/rules/markdown.mdc](cursor/rules/markdown.mdc) — Markdown writing rules and structure.
- [cursor/rules/python.mdc](cursor/rules/python.mdc) — Python conventions (PEP 8, types, tests).
- [cursor/rules/cmake-vcpkg.mdc](cursor/rules/cmake-vcpkg.mdc) — CMake/vcpkg manifest-mode guidance.
- [cursor/rules/agent-skills.mdc](cursor/rules/agent-skills.mdc) — Skill authoring guidelines
	(frontmatter, resources, progressive loading).
- [cursor/rules/agents.mdc](cursor/rules/agents.mdc) — Custom agent file guidelines (`*.agent.md`).
- [cursor/rules/instructions.mdc](cursor/rules/instructions.mdc) — Custom instruction file
	guidelines (`*.instructions.md`).
- [cursor/rules/rules.mdc](cursor/rules/rules.mdc) — Cursor rules + `AGENTS.md` guidelines.

### Install / Setup

- Copy into `.cursor/rules/` in your target repo.

### Use

- Rules apply automatically based on `alwaysApply` / `globs`.
- Keep rules composable: small global rules + scoped language/framework rules.

## Commands (Cursor)

These are Cursor custom commands (intended as chat slash commands).

### Files

- [cursor/commands/convert-plaintext-to-md.md](cursor/commands/convert-plaintext-to-md.md) — Convert
	plaintext docs into markdown.
- [cursor/commands/create-agentsmd.md](cursor/commands/create-agentsmd.md) — Generate `AGENTS.md`.
- [cursor/commands/create-implementation-plan.md](cursor/commands/create-implementation-plan.md) —
	Create an implementation plan in `/plan/`.
- [cursor/commands/create-readme.md](cursor/commands/create-readme.md) — Create a project README.
- [cursor/commands/create-specification.md](cursor/commands/create-specification.md) — Create a
	specification in `/spec/`.
- [cursor/commands/create-technical-spike.md](cursor/commands/create-technical-spike.md) — Create a
	time-boxed spike doc (default `docs/spikes`).
- [cursor/commands/create-tldr-page.md](cursor/commands/create-tldr-page.md) — Create a `tldr` page.
- [cursor/commands/prompt-builder.md](cursor/commands/prompt-builder.md) — Interactive prompt
	creation wizard.
- [cursor/commands/update-implementation-plan.md](cursor/commands/update-implementation-plan.md) —
	Update an existing plan.
- [cursor/commands/update-markdown-file-index.md](cursor/commands/update-markdown-file-index.md) —
	Insert/update a folder file index in a markdown doc.
- [cursor/commands/update-specification.md](cursor/commands/update-specification.md) — Update an
	existing spec.
- [cursor/commands/write-coding-standards-from-file.md](cursor/commands/write-coding-standards-from-file.md)
	— Infer and write coding standards from existing code.

### Install / Setup

- Copy into `.cursor/commands/` in your target repo.

### Use

- Run in chat as `/command-name` (command name typically matches the filename).


