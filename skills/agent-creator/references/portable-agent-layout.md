# Portable Agent Layout

Use this guide when creating or reviewing agents that should work across GitHub Copilot, Cursor, and Claude Code.

## Directory structure

```text
repo/
  .shared/
    agents/
      code-reviewer.md
  .claude/
    agents/
      code-reviewer.md
  .cursor/
    agents/
      code-reviewer.md
  .github/
    agents/
      code-reviewer.agent.md
```

`.shared/agents/<name>.md` is the canonical source of truth. The three tool-specific files are wrappers that point back to the shared file and add local integration notes.

## Shared agent template

```markdown
---
name: code-reviewer
description: Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request.
---

You are a senior code reviewer.

When invoked:

1. Read the relevant changes and surrounding context.
2. Evaluate against the criteria below.
3. Report findings in the output format specified.

Review focus:

1. Correctness bugs
2. API misuse
3. Resource leaks
4. Race conditions
5. Security issues
6. Missing tests or edge cases
7. Maintainability problems

When reporting findings:

- Group issues by severity: critical, high, medium, low.
- Cite the relevant file, function, or code region when possible.
- Explain why each issue matters.
- Suggest a concrete fix.
- Do not rewrite large files unless explicitly asked.
- Do not comment on style-only preferences unless they affect readability or maintainability.

If no significant issues are found, say so and list any minor observations separately.
```

Keep shared agents tool-neutral. Do not embed reload steps, subagent spawn commands, or vendor-specific frontmatter in the shared file.

## Wrapper template

Use the same `name` and `description` frontmatter in each wrapper unless the user asks for tool-specific frontmatter.

```markdown
---
name: code-reviewer
description: Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request.
---

# code-reviewer wrapper for Cursor

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.shared/agents/code-reviewer.md`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, review criteria, and response format.

## Cursor-specific information

Reload the Cursor window after adding or editing this agent so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `../../.shared/agents/code-reviewer.md`.
- Keep only Cursor-specific information in this wrapper.
```

## Tool-specific paths

| Tool | Wrapper path |
| --- | --- |
| Claude Code | `.claude/agents/<name>.md` |
| Cursor | `.cursor/agents/<name>.md` |
| GitHub Copilot | `.github/agents/<name>.agent.md` |

Relative path from any wrapper to the shared agent:

`../../.shared/agents/<name>.md`

## Worked example

Scaffold a portable agent in a repository:

```bash
python skills/agent-creator/scripts/create_agent.py \
  --root /path/to/repo \
  --name code-reviewer \
  --description "Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request." \
  --instructions-file /tmp/code-reviewer-body.md \
  --overwrite
```

This creates:

- `.shared/agents/code-reviewer.md`
- `.cursor/agents/code-reviewer.md`
- `.claude/agents/code-reviewer.md`
- `.github/agents/code-reviewer.agent.md`

Validate immediately:

```bash
python skills/agent-creator/scripts/quick_validate.py --root /path/to/repo --name code-reviewer
```

Or validate each file:

```bash
python skills/agent-creator/scripts/quick_validate.py .shared/agents/code-reviewer.md
python skills/agent-creator/scripts/quick_validate.py .cursor/agents/code-reviewer.md
python skills/agent-creator/scripts/quick_validate.py .claude/agents/code-reviewer.md
python skills/agent-creator/scripts/quick_validate.py .github/agents/code-reviewer.agent.md
```

Then edit the shared file for cross-tool behavior and expand each wrapper with tool-native spawn mechanics, reload steps, and optional frontmatter (`model`, `tools`, `readonly`, etc.). Re-run validation after substantive edits.

## Notes on portability

- Reference-based wrappers reduce duplication but depend on the tool following the wrapper instruction to read the shared file.
- If the user needs maximum standalone behavior, generate copy-based wrappers with the full shared body inlined in each tool file instead of reference wrappers.
- Repo-root `agents-ref/` can hold reference templates. User-created portable agents belong in `.shared/agents/`.
- Add tool-specific frontmatter such as `model`, `tools`, or `readonly` only in wrappers when the user explicitly wants per-tool variants.

## Quality checklist

Before finishing, confirm the agent meets the three bars from the shared skill:

| Bar | Question |
| --- | --- |
| Correctness | Is the role accurate? Are capabilities realistic? Are success criteria verifiable? |
| Completeness | Are edge cases, output format, and boundaries documented? |
| Efficiency | Is the shared file lean? Are tool-native shortcuts in wrappers, not duplicated in shared? |
