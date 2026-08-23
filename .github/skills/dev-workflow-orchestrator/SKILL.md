---
name: dev-workflow-orchestrator
description: Orchestrate the full development workflow — clarify → research → plan
  → implement → code-review → commit — with bounded loops, backward edges for upstream
  root causes, artifact contracts, and mode enforcement. Use when the user wants to
  run the complete dev workflow on a requirement or feature, resume an in-progress
  workflow run, or continue a workflow after a backward edge or escalation. Triggers
  on prompts to run the dev workflow, start a full development cycle, clarify-research-plan-implement-review-commit
  a feature, or resume a workflow run — even when the user doesn't say 'orchestrator'.
  Does not trigger for individual phase tasks (use the phase-specific skill directly),
  git mechanics alone (use git-guide), or code diff review without the full workflow
  (use code-reviewer).
---

# dev-workflow-orchestrator wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/dev-workflow-orchestrator/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/dev-workflow-orchestrator` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/dev-workflow-orchestrator/`.
- Keep only GitHub Copilot-specific information in this wrapper.
