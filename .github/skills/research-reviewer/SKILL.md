---
name: research-reviewer
description: "Use when reviewing, auditing, or validating a research report produced by research-guide or similar discovery workflows before implementation planning \u2014 assessing completeness, consistency, evidence quality, risk awareness, and planning readiness across product, user, technical, security, data, compliance, operations, or domain-specific concerns. Triggers on prompts to review a research report, validate requirements, audit assumptions, challenge conclusions, find gaps, assign severity, produce required revisions, or decide whether a report is ready for an implementation plan \u2014 even when the user doesn't say 'research review'. Does not trigger on brainstorming new ideas, code diff review, or plan-document lifecycle work."
---

# research-reviewer wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/research-reviewer/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/research-reviewer` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/research-reviewer/`.
- Keep only GitHub Copilot-specific information in this wrapper.
