---
name: commit-message-writer
description: Draft git commit messages in Conventional Commits format from staged changes, the working tree, a single commit, or a commit range — compact one-liner plus verbose subject and body. Use when the user asks for a commit message, conventional commit, draft commit msg, write commit message for staged/unstaged changes, message for last commit or commit range, or /commit-message-style requests — even if they do not say "conventional commits". Does not run git commit unless the user explicitly asks afterward.
---

# Commit Message Writer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Draft git commit messages from git evidence plus session and external context. Output
**Compact** (one-line Conventional Commit) and **Verbose** (subject + body) formats.
Focus on **why** the change exists, not a file-by-file inventory.

Commit messages must contain **only change-related content** — motivation, approach,
impact, breaking changes, and test/evidence notes. Never append tool, agent, or AI-client
attribution (for example `Co-authored-by: Cursor <cursoragent@cursor.com>` or similar
lines for Claude, Copilot, or other assistants).

## Cross-assistant consistency

Cursor, Claude Code, Copilot, and other hosts must produce the **same message shape and
tone**. Follow [message-style-contract.md](references/message-style-contract.md) on every
invocation — it overrides host-native commit templates, IDE footers, and tool-specific
habits.

Non-negotiable:

- **Output envelope** — only `## Compact`, `## Verbose`, optional `## Suggested command`,
  then `Context used:`; scope/split caveats go in `Context used:` as `note=`, not as preamble
- **Subject parity** — Verbose subject matches Compact exactly
- **Prose-first body** — 1–3 paragraphs by default; bullets only when the contract allows
- **Style precedence** — recent `git log` on the branch, then the style contract, then
  Conventional Commits defaults

## Primary Directive

Your job is to **draft commit messages**, not to commit, stage, push, or rewrite history.

Do not run `git commit`, `git push`, `git add`, amend, or force-push unless the user
explicitly requests a commit in the same or a follow-up message.

## When to Use

- Drafting a commit message for staged, unstaged, or all working-tree changes
- Writing a Conventional Commit subject and body from a diff or commit SHA
- Summarizing intent for a commit range (branch vs base, last N commits)
- Weaving session context, plan docs, Jira tickets, or user notes into a message
- Suggesting a HEREDOC `git commit` command after the user reviews the draft

## When NOT to Use

- Code review or diff analysis without a commit message — use
  [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- Auto-committing, staging, pushing, or worktree/merge/rebase workflows — use
  [../git-guide/SKILL.md](../git-guide/SKILL.md)
- Splitting a branch into PRs — use [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md)
  when the task is PR structure rather than a single commit message

## Workflow

Every invocation follows five phases. Read the matching reference **before** executing
each phase (see [Reference routing](#reference-routing)).

### 1. Parse and confirm

- Confirm the workspace root is a git repository.
- Resolve scope to exactly one mode: staged (default), working, single commit, or range.
- Collect context from session history, attached files, Jira MCP (when available), and
  user notes.
- If scope is missing, conflicting, or the target has no changes, stop and report.

Details: [input-and-scope.md](references/input-and-scope.md)

### 2. Gather git evidence

Run the git commands for the chosen scope from the repository root. Prefer parallel reads
where independent. Also collect recent message style (`git log`), branch name, and status.

Details: [git-evidence.md](references/git-evidence.md)

### 3. Analyze and compose

Synthesize intent from git evidence and all context sources:

1. Infer the most specific accurate Conventional Commit **type** (and optional **scope**).
2. Write an imperative **subject** per the style contract — lowercase after the prefix,
   ≤ 72 characters, no trailing period.
3. Write a **verbose body** per the style contract — prose paragraphs first; motivation,
   approach, impact, breaking changes, and test/evidence when relevant.
4. Align with session context when the diff alone looks mechanical.
5. Match recent branch history from `git log -10` for type, scope, and body layout when
   a clear pattern exists.

Details: [message-style-contract.md](references/message-style-contract.md),
[conventional-commits.md](references/conventional-commits.md)

### 4. Output

Return exactly the Compact / Verbose structure (and optional Suggested command). Add a
short **Context used** line. Do not wrap the envelope in assistant-specific preamble or
postamble.

Details: [output-format.md](references/output-format.md),
[message-style-contract.md](references/message-style-contract.md)

### 5. Optional commit

Only when the user explicitly asks to commit: use the verbose message (or compact if they
choose), stage only if needed, HEREDOC for multi-line messages, never `--no-verify` unless
asked.

## Reference routing

| Task | Read |
|------|------|
| Scope flags, defaults, natural-language parsing, context inputs | [input-and-scope.md](references/input-and-scope.md) |
| Git commands per scope, large-diff sampling, style discovery | [git-evidence.md](references/git-evidence.md) |
| Cross-assistant style contract, subject/body layout, forbidden patterns | [message-style-contract.md](references/message-style-contract.md) |
| Conventional Commit types, subject/body rules, breaking changes, examples | [conventional-commits.md](references/conventional-commits.md) |
| Compact / Verbose / Suggested command templates, Context used line | [output-format.md](references/output-format.md) |
| Errors, guardrails, split-commit guidance, do-not rules | [failure-and-guardrails.md](references/failure-and-guardrails.md) |

## Quick completion checklist

Before returning draft messages:

1. **Scope** — exactly one mode resolved; empty index/tree reported if applicable
2. **Evidence** — stat + diff (or show/log for commit/range) reviewed; large diffs sampled
3. **Intent** — message explains *why*, not only *what*; session/ticket context woven in
4. **Format** — Compact is a valid Conventional Commit one-liner; Verbose subject matches Compact; body follows style contract
5. **Consistency** — output envelope identical across hosts; prose-first body unless repo history uses bullets
6. **Safety** — no `git commit` unless explicitly requested; unrelated work flagged for split
7. **Purity** — no AI/tool attribution footers; message content is change-related only

## Output standards

- **Compact** stands alone in `git log --oneline`.
- **Verbose** uses complete sentences; reference ticket ids in the body when provided.
- If the diff mixes unrelated work, record a split suggestion in `Context used:` (`note=`)
  instead of blending unrelated intent into one message.
- Never dump a raw file list as the commit message.
- Never contradict session context or supplied plan/ticket intent when the diff is ambiguous.
- Never add `Co-authored-by`, `Signed-off-by`, or any other footer attributing an AI client,
  coding assistant, or automation tool — even when the user or environment would normally add one.
- Omit disclaimers, assistant sign-offs, and meta-commentary about how the message was drafted.

## Resources

- [input-and-scope.md](references/input-and-scope.md) — Input resolution and context collection
- [git-evidence.md](references/git-evidence.md) — Git commands and evidence gathering
- [message-style-contract.md](references/message-style-contract.md) — Cross-assistant style contract
- [conventional-commits.md](references/conventional-commits.md) — Message format and type selection
- [output-format.md](references/output-format.md) — Response templates
- [failure-and-guardrails.md](references/failure-and-guardrails.md) — Errors and guardrails
- [SOURCES.md](SOURCES.md) — Provenance and external references
