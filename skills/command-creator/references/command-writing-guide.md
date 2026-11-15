# Command Writing Guide

Cross-tool best practices for portable slash commands (command-skills).

## Purpose

Commands are **explicitly invoked** with `/command-name`. Optimize for clarity, repeatability, and a single focused task — not passive discovery. Commands install as **command-skills** (`.agents/skills/<name>/SKILL.md` with `disable-model-invocation: true`), so every coding agent exposes them as `/<name>` and the model never self-invokes them.

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
2. Validate bootstrap, install as a command-skill, reload, and test `/command-name`

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
| Claude Code | `$ARGUMENTS`, `$0`, `$1` | Set `allowed-tools` in bootstrap `COMMAND.md` frontmatter; it transfers to the installed command-skill |
| GitHub Copilot | `${input:name}`, `${input:name:placeholder}` | Document expected inputs in the body |
| Cursor | User text after `/command` in chat | Document expected trailing input in the body |

## Command-skill frontmatter

Bootstrap `COMMAND.md` accepts `name`, `description`, and optional `allowed-tools`. Descriptions must be ≤120 chars and invocation-gated (state that the user explicitly invokes `/<name>`). Install adds `disable-model-invocation: true` — the model never self-invokes a command.

## Keep commands focused

- One command = one workflow
- Link to skills or rules for large reference material instead of duplicating
- Prefer short, imperative steps over long prose
- State success criteria when output quality matters

## Tool neutrality in the body

Keep the `COMMAND.md` body free of host-specific UI names ("Cursor window", "Claude Code session", "VS Code") — the validator rejects them in both bootstrap and installed bodies. Put host-specific behavior notes in the `## Tool notes` section of the command-creator skill, and reload instructions in install output messages.

## Review criteria

Before marking a command done:

1. **Correctness** — steps match the intended workflow
2. **Completeness** — output format and guardrails are explicit
3. **Efficiency** — no duplicated rules already covered by repo skills or rules
4. **Portability** — bootstrap validates; install produces the command-skill

See also:

- [portable-command-layout.md](portable-command-layout.md)
