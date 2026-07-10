---
name: plan-executor
description: "Use when executing a provided implementation plan in the current git working tree \u2014 decomposing it into independent units, dispatching concurrent subagents through agent-runner when possible, integrating on the current branch without creating or switching branches unless explicitly requested, running verifications, and producing an implementation report. Triggers on prompts to implement a written plan, execute plan tasks, or run an approved implementation plan on the current branch. Does not trigger on plan authoring, plan-reviewer audit, generic parallel dispatch without a plan, or post-implementation diff review."
---

# plan-executor wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/plan-executor/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/plan-executor` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/plan-executor/`.
- Keep only GitHub Copilot-specific information in this wrapper.
