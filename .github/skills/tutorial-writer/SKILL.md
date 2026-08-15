---
name: tutorial-writer
description: Write, revise, and review example-driven technical tutorials, getting-started
  guides, practical walkthroughs, API or SDK lessons, and user guides for software
  products, libraries, frameworks, developer tools, and technical concepts. Use when
  a reader needs to achieve a concrete outcome, from a beginner quickstart through
  realistic or production use. Build a progressive, runnable example; show observable
  results; use only source-backed technical claims; and critique existing guides for
  learning flow, accuracy, and verification.
---

# tutorial-writer wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/tutorial-writer/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/tutorial-writer` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/tutorial-writer/`.
- Keep only GitHub Copilot-specific information in this wrapper.
