---
name: plan-guide
description: "Use when turning a research report, spec, requirements, bug report, or technical context into an executable implementation plan \u2014 decomposing work into ordered tasks, mapping requirements to implementation, defining verification and acceptance checks, or revising a plan from plan-reviewer findings before execution. Triggers on prompts to write an implementation plan, create a task breakdown, map requirements to tasks, define verification for a feature, or repair a plan from reviewer feedback \u2014 even when the user doesn't say 'plan'. Does not trigger on interactive research, research-report audit, code implementation, or code diff review."
---

# plan-guide wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/plan-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/plan-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/plan-guide/`.
- Keep only GitHub Copilot-specific information in this wrapper.
