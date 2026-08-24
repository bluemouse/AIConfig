---
name: implementation-auditor
description: "Run an isolated, fresh-context audit of an implementation as a read-only subagent, with no access to the implementer's reasoning. Use when independence from the doer matters, when dispatched by the dev-workflow orchestrator in native mode, or when a fresh-context correctness audit of requirement coverage and test/build evidence is needed after code changes, bug fixes, or plan execution. Produces a compact evidence-weighted audit report with a verdict. Does not trigger on active local merge/rebase integration verification (git-merge-guide), diff review (code-reviewer), plan authoring (plan-guide), pre-execution plan audit (plan-reviewer), plan execution (plan-executor), codebase learning guides (code-professor), or strict TDD coaching (test-driven-dev-guide)."
model: gpt-4o
---

# implementation-auditor wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.ai/agents/implementation-auditor.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, audit criteria, verdict format, and response format.

## GitHub Copilot-specific information

- Reload VS Code after adding or editing this agent so Copilot rediscovers it.
- GitHub Copilot `.agent.md` files do not expose a native `readonly` frontmatter field. Read-only enforcement is **instruction-only** (the shared agent body's Boundaries section) plus detection via the dev-workflow `check_post_phase.py` validation script, which catches forbidden writes in all modes.
- `model: gpt-4o` pins a strong reasoning model for audit quality. Substitute the current strongest available reasoning model if this identifier is unavailable on the host.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.ai/agents/implementation-auditor.md`.
- Keep only GitHub Copilot-specific information in this wrapper.
