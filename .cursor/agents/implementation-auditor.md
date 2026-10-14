---
name: implementation-auditor
description: Run an isolated, fresh-context audit of an implementation as a read-only
  subagent, with no access to the implementer's reasoning. Use when independence from
  the doer matters, when dispatched by the dev-workflow orchestrator in native mode,
  or when a fresh-context correctness audit of requirement coverage and test/build
  evidence is needed after code changes, bug fixes, or plan execution. Produces a
  compact evidence-weighted audit report with a verdict. Does not trigger on active
  local merge/rebase integration verification (git-merge-guide), diff review (code-reviewer),
  plan authoring (plan-guide), pre-execution plan audit (plan-reviewer), plan execution
  (plan-executor), codebase learning guides (code-professor), or strict TDD coaching
  (test-driven-dev-guide).
model: inherit
readonly: true
---

# implementation-auditor wrapper for Cursor

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.ai/agents/implementation-auditor.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, audit criteria, verdict format, and response format.

## Cursor-specific information

- Reload the Cursor window after adding or editing this agent so the agent rediscovers it.
- `readonly: true` enforces read-only behavior at the host level — the agent cannot write files outside its allowed artifact path.
- `model: inherit` runs the agent on the parent agent's model (the documented default). Replace with a specific model ID if this agent should run on a specific model.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.ai/agents/implementation-auditor.md`.
- Keep only Cursor-specific information in this wrapper.
