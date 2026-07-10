---
name: plan-reviewer
description: "Use when reviewing, auditing, or validating an implementation plan before execution by a developer, engineer, or AI agent \u2014 checking correctness, completeness, consistency with source research/spec/requirements, task decomposition, file precision, testability, risk controls, and execution readiness. Triggers on prompts to review an implementation plan, validate a work plan, audit plan tasks, approve execution readiness, or produce a Guide handoff packet \u2014 even when the user doesn't say 'plan review'. Does not trigger on brainstorming, research-report review, writing plans, or code diff review."
---

# plan-reviewer wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/plan-reviewer/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/plan-reviewer` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/plan-reviewer/`.
- Keep only Claude Code-specific information in this wrapper.
