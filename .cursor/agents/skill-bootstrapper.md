---
name: skill-bootstrapper
model: composer-2.5[fast=true]
description: Bootstrap, review, and install portable skills from templates in one run. Use when creating a new skill from skills-ref or bootstrap templates, automating bootstrap authoring plus install_portable_skill.py, or replacing separate bootstrap and install steps — even if the user says create a skill without naming the pipeline.
---

# skill-bootstrapper wrapper for Cursor

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.shared/agents/skill-bootstrapper.md`

Before doing agent work, read that shared file and treat it as the source of truth for the
role, task boundaries, workflow phases, and response format.

## Cursor-specific information

- **Reload the Cursor window** after install completes so the agent and new tool skills
  rediscover.
- Run Python scripts from the **repository root** via the shell tool:
  `skills/skill-creator/scripts/quick_validate.py` and
  `skills/skill-creator/scripts/install_portable_skill.py`.
- Fetch `--verify` URLs with web search or doc fetch when available.
- Read `.cursor/commands/create-bootstrap-skill.md` and `.cursor/commands/create-tool-skill.md`
  from the repo when executing bootstrap and install phases — they are the authoritative
  command specs.
- Use `@`-attached paths and workspace-relative paths as the user provides them.
- Do not commit unless the user explicitly asks; suggest `/commit-message` when they want to
  commit staged skill files.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.shared/agents/skill-bootstrapper.md`.
- Keep only Cursor-specific information in this wrapper.
