# Input and Scope

## Contents

- [Goal](#goal)
- [Structured input](#structured-input)
- [Natural language fallback](#natural-language-fallback)
- [Context sources](#context-sources)
- [Phase 1 checklist](#phase-1-checklist)

## Goal

Resolve **what git evidence to read** and **what extra context to merge** before drafting
messages.

## Structured input

Parse the user's message. Support structured flags (preferred) and natural language
(fallback).

**Structured form:**

```text
commit-message-writer \
  [--staged | --working | --commit <sha> | --range <rev-range>] \
  [--context <path-or-text> ...] \
  [--jira <ticket-id> ...] \
  [--notes "<free-text context>"]
```

| Argument | Default | Meaning |
| --- | --- | --- |
| *(none)* | `--staged` | Changes currently in the index |
| `--staged` | — | Staged changes only (`git diff --cached`) |
| `--working` | — | All tracked changes vs `HEAD` — staged and unstaged (`git diff HEAD`) |
| `--commit <sha>` | — | One existing commit (`git show <sha>`) |
| `--range <rev-range>` | — | Combined diff and log for a commit range (e.g. `abc123..def456`, `main..HEAD`, `HEAD~3..HEAD`) |
| `--context` | — | Extra context: attached file path, URL, design doc, plan, ticket link, or inline text |
| `--jira` | — | Jira ticket id(s) (e.g. `PROJ-123`); fetch details via Atlassian MCP when available |
| `--notes` | — | Free-text context (intent, constraints, rollout notes) not captured elsewhere |

**Examples:**

```text
commit-message-writer
commit-message-writer --working
commit-message-writer --commit abc1234
commit-message-writer --range main..HEAD
commit-message-writer --staged --context @docs/plans/auth-flow.md --jira PROJ-456 \
  --notes "Part 2 of JWT migration; no API break"
```

## Natural language fallback

Infer scope from prose:

| User phrasing | Resolved scope |
| --- | --- |
| "staged", "what I staged", "in the index" | `--staged` |
| "everything I've changed", "working tree", "all my changes" | `--working` |
| "last commit", "HEAD commit" | `--commit HEAD` |
| "commits since main", "branch vs main", `main..HEAD` | `--range` |

Treat `@`-attached files as `--context`. Confirm ambiguous scope before analyzing.

## Context sources

Collect context from all available sources, in priority order when they conflict:

1. **Session history** — design decisions, implementation steps, tradeoffs, test results
   from the current conversation
2. **`--context`** paths — read attached or referenced files
3. **`--jira`** tickets — load title, description, acceptance criteria via Atlassian MCP
   when the plugin is available
4. **`--notes`** and remaining user prose after flags

Session context often explains *why* a change was made when the diff alone looks mechanical.
Prefer session and ticket intent over inferring from filenames alone.

## Phase 1 checklist

1. Confirm git repository: `git rev-parse --is-inside-work-tree`
2. Resolve scope to exactly one mode; default `--staged`
3. Collect all context sources listed above
4. If scope is missing, conflicting, or the target has no changes — report and stop
