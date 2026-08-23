# GitHub Copilot Prompt Best Practices

Reference for `.github/prompts/<name>.prompt.md` prompt files (VS Code, Visual Studio, JetBrains).

**Official docs:** [Use prompt files in VS Code](https://code.visualstudio.com/docs/agent-customization/prompt-files)

## Format

| Rule | Detail |
| --- | --- |
| Location | `.github/prompts/<name>.prompt.md` |
| Invocation | `/name` in Copilot Chat |
| Extension | Must end with `.prompt.md` |
| Frontmatter | Optional YAML configuration |

## Common frontmatter keys

| Key | Purpose |
| --- | --- |
| `description` | Short summary for prompt picker |
| `name` | Slash name (defaults to filename stem) |
| `argument-hint` | Input hint in chat field |
| `agent` | `ask`, `agent`, `plan`, or custom agent name |
| `model` | Override model for this prompt |
| `tools` | List of allowed tools or tool sets |

Install defaults `agent: agent` when no GitHub wrapper overrides it.

## Body syntax

- Markdown instructions for the task
- `${input:variableName}` or `${input:variableName:placeholder}` for user inputs
- `#tool:toolName` to reference specific tools in prose
- Relative Markdown links to workspace files for shared guidelines

Example:

```markdown
---
description: Generate unit tests for the selected code
agent: agent
tools: ['search/codebase', 'edit']
argument-hint: [test framework]
---

Generate unit tests using ${input:framework:jest} for the selected code.

Follow project test conventions in [TESTING.md](../TESTING.md).

Return only the test file contents unless asked otherwise.
```

## Prompt files vs other Copilot customization

| Mechanism | Scope | Invocation |
| --- | --- | --- |
| `.github/copilot-instructions.md` | Repository-wide, always on | Automatic |
| `.github/instructions/*.instructions.md` | Path-scoped via `applyTo` | Automatic |
| `.github/prompts/*.prompt.md` | Task-specific | Manual `/name` |

Use prompt files for repeatable tasks; use instructions for persistent project conventions.

## Reload

Reload VS Code after adding or editing prompt files so Copilot rediscovers them.

## Public preview note

Copilot prompt files are in public preview and may change. Validate behavior in the target IDE after install.
