---
name: code-reviewer
description: Run an isolated, fresh-context review of a code diff as a read-only subagent,
  with no access to the author's reasoning. Use when independence from the doer matters,
  when dispatched by the dev-workflow orchestrator in native mode, or when a fresh-context
  findings-first review of git diffs and commits for correctness, safety, maintainability,
  and test coverage is needed after implementation or before a pull request. Produces
  a structured review-report with a verdict. Does not trigger on active local merge/rebase
  integration review (git-merge-guide) or codebase learning guides (code-professor).
model: claude-3-5-sonnet
tools: Read, Grep, Glob, Bash
---

# code-reviewer wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.ai/agents/code-reviewer.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, review criteria, verdict format, and response format.

## Claude Code-specific information

- Restart or reload the Claude Code session after adding or editing this agent.
- `tools: Read, Grep, Glob, Bash` restricts the agent to read-only investigation plus command execution for evidence gathering. Write tools (Edit, Write) are excluded to enforce read-only behavior at the host level.
- `model: claude-3-5-sonnet` pins a strong reasoning model for review quality. Substitute the current strongest available reasoning model if this identifier is unavailable on the host.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.ai/agents/code-reviewer.md`.
- Keep only Claude Code-specific information in this wrapper.
