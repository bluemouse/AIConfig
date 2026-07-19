---
name: plan-guide
description: "Use when turning a research report, spec, requirements, bug report, or technical context into an executable implementation plan \u2014 decomposing work into ordered tasks, mapping requirements to implementation, designing TDD-first tests, defining verification and acceptance checks, exploring the codebase to plan from a rough ask, normalizing a thin or external plan into TDD-first tasks, writing a focused bug-fix plan, or revising a plan from plan-reviewer findings before execution. Triggers on prompts to write an implementation plan, create a task breakdown, map requirements to tasks, plan tests or verification for a feature, explore the codebase and turn a feature ask into a plan, expand a thin plan with TDD specs, create a focused plan for a small fix, normalize an external markdown plan, or repair a plan from reviewer feedback \u2014 even when the user doesn't say plan. Does not trigger on interactive research, report audit, learning guides (code-professor), implementation, or diff review."
---

# plan-guide wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/plan-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/plan-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/plan-guide/`.
- Keep only Claude Code-specific information in this wrapper.
