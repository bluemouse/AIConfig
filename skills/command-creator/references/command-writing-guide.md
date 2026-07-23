# Command Writing Guide

Cross-tool best practices for portable slash commands and Copilot prompts.

## Purpose

Commands are **explicitly invoked** with `/command-name`. Optimize for clarity, repeatability, and a single focused task — not passive discovery.

Use commands when:

- The user runs the same workflow repeatedly from chat
- The task has a clear start, steps, and output format
- The prompt fits in one readable Markdown file

Migrate to a **skill** when:

- The agent should load instructions autonomously from description alone
- The workflow needs bundled `scripts/`, `references/`, or `assets/`
- The content exceeds what belongs in a slash prompt

## Authoring order

1. Write tool-neutral `COMMAND.md` first — steps, output format, guardrails
2. Add wrappers only for real per-tool differences (tool restrictions, agent mode, argument hints)
3. Validate bootstrap, install, reload, and test `/command-name` in each IDE

## Structure checklist

Every command should include:

- **Title** — what the command does in one line
- **Steps** — numbered, actionable instructions
- **Output** — expected response shape (markdown sections, code fences, tables)
- **Do not** — guardrails and out-of-scope actions

Optional sections:

- **Examples** — sample input/output pairs
- **Context** — when to use vs a related skill or command
- **Arguments** — how user input after `/command` is interpreted

## Argument placeholders

| Tool | Syntax | Notes |
| --- | --- | --- |
| Claude Code | `$ARGUMENTS`, `$0`, `$1` | Set `argument-hint` in Claude wrapper frontmatter |
| GitHub Copilot | `${input:name}`, `${input:name:placeholder}` | Set `argument-hint` in GitHub wrapper frontmatter |
| Cursor | User text after `/command` in chat | Document expected trailing input in the body |

## Keep commands focused

- One command = one workflow
- Link to skills or rules for large reference material instead of duplicating
- Prefer short, imperative steps over long prose
- State success criteria when output quality matters

## Tool neutrality in shared body

Keep the shared `COMMAND.md` body free of tool-specific UI names ("Cursor window", "Claude Code session", "VS Code"). Put reload notes and tool keys in wrappers or in command-creator install output messages.

## Review criteria

Before marking a command done:

1. **Correctness** — steps match the intended workflow
2. **Completeness** — output format and guardrails are explicit
3. **Efficiency** — no duplicated rules already covered by repo skills or rules
4. **Portability** — bootstrap validates; install produces all four paths

See also:

- [cursor-command-best-practices.md](cursor-command-best-practices.md)
- [claude-command-best-practices.md](claude-command-best-practices.md)
- [copilot-prompt-best-practices.md](copilot-prompt-best-practices.md)
