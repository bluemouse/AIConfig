---
name: research-reviewer
description: Run an isolated, fresh-context audit of a research report as a read-only
  subagent, with no access to the researcher's reasoning. Use when independence from
  the doer matters, when dispatched by the dev-workflow orchestrator in native mode,
  or when a fresh-context review of a research report for planning readiness, gaps,
  evidence quality, and risk awareness is needed before implementation planning. Produces
  a structured review-report with a verdict. Does not trigger on brainstorming new
  ideas, codebase learning guides (code-professor), implementation plan authoring
  (plan-guide), plan-reviewer audit, or code diff review.
model: claude-3-5-sonnet
readonly: true
---

# research-reviewer wrapper for Cursor

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.ai/agents/research-reviewer.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, review criteria, verdict format, and response format.

## Cursor-specific information

- Reload the Cursor window after adding or editing this agent so the agent rediscovers it.
- `readonly: true` enforces read-only behavior at the host level — the agent cannot write files outside its allowed artifact path.
- `model: claude-3-5-sonnet` pins a strong reasoning model for review quality. Substitute the current strongest available reasoning model if this identifier is unavailable on the host.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.ai/agents/research-reviewer.md`.
- Keep only Cursor-specific information in this wrapper.
