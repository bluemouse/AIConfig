---
name: research-guide
description: "Use when interactively researching, brainstorming, or hardening a feature idea, product concept, app design, technical spec, requirement set, architecture direction, or roadmap item before implementation planning \u2014 through iterative agreement gates until a finalized research report is ready. Triggers on prompts to research an idea, brainstorm requirements, explore alternatives, author a spec, clarify trade-offs, validate assumptions, define scope, or produce a research report \u2014 even when the user doesn't say 'research'. Does not trigger on implementation plan authoring, plan-reviewer audit, or code diff review."
---

# research-guide wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/research-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/research-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/research-guide/`.
- Keep only GitHub Copilot-specific information in this wrapper.
