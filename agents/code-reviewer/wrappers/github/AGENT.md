---
name: code-reviewer
description: "Run an isolated, fresh-context review of a code diff as a read-only subagent, with no access to the author's reasoning. Use when independence from the doer matters, when dispatched by the dev-workflow orchestrator in native mode, or when a fresh-context findings-first review of git diffs and commits for correctness, safety, maintainability, and test coverage is needed after implementation or before a pull request. Produces a structured review-report with a verdict. Does not trigger on active local merge/rebase integration review (git-merge-guide) or codebase learning guides (code-professor)."
---

# code-reviewer wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.ai/agents/code-reviewer.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, review criteria, verdict format, and response format.

## GitHub Copilot-specific information

- Reload VS Code after adding or editing this agent so Copilot rediscovers it.
- GitHub Copilot `.agent.md` files do not expose a native `readonly` frontmatter field. Read-only enforcement is **instruction-only** (the shared agent body's Boundaries section) plus detection via the dev-workflow `check_post_phase.py` validation script, which catches forbidden writes in all modes.
- No `model` frontmatter is set, so the agent runs on the user's currently selected Copilot chat model. Add a `model` field only if this agent must run on a specific model.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.ai/agents/code-reviewer.md`.
- Keep only GitHub Copilot-specific information in this wrapper.
