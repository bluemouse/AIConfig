---
name: python-coding
description: "Write, review, refactor, test, debug, and package modern Python 3.12+ command-line scripts and utilities using project-local toolchain settings. Use when implementing or fixing Python code, designing argparse CLIs, improving scripts, applying type hints, configuring pyproject.toml, ruff, pyright, pytest, or pip/uv workflows, building small utilities, or producing packaging metadata \u2014 even if the user says \"Python help\" or \"fix this script\" without naming a framework."
---

# python-coding wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/python-coding/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/python-coding` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/python-coding/`.
- Keep only GitHub Copilot-specific information in this wrapper.
