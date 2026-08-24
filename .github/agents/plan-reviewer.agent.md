---
name: plan-reviewer
description: Run an isolated, fresh-context audit of an implementation plan as a read-only
  subagent, with no access to the planner's reasoning. Use when independence from
  the doer matters, when dispatched by the dev-workflow orchestrator in native mode,
  or when a fresh-context review of an implementation plan for correctness, completeness,
  TDD test design, task decomposition, file precision, testability, risk controls,
  and execution readiness is needed before execution. Produces a structured review-report
  with a verdict. Does not trigger on brainstorming, research-report review, codebase
  learning guides (code-professor), writing plans, or code diff review.
model: gpt-4o
---

# plan-reviewer wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.ai/agents/plan-reviewer.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, review criteria, verdict format, and response format.

## GitHub Copilot-specific information

- Reload VS Code after adding or editing this agent so Copilot rediscovers it.
- GitHub Copilot `.agent.md` files do not expose a native `readonly` frontmatter field. Read-only enforcement is **instruction-only** (the shared agent body's Boundaries section) plus detection via the dev-workflow `check_post_phase.py` validation script, which catches forbidden writes in all modes.
- `model: gpt-4o` pins a strong reasoning model for review quality. Substitute the current strongest available reasoning model if this identifier is unavailable on the host.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.ai/agents/plan-reviewer.md`.
- Keep only GitHub Copilot-specific information in this wrapper.
