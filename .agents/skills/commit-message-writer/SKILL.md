---
name: commit-message-writer
description: Draft git commit messages in Conventional Commits format from staged changes, the working tree, a single commit, or a commit range — subject line plus body. Use when the user asks for a commit message, conventional commit, draft commit msg, write commit message for staged/unstaged changes, message for last commit or commit range, or /commit-message-style requests — even if they do not say "conventional commits". Ends by asking whether to proceed with git commit using the generated message; does not commit without explicit confirmation.
---

# Commit Message Writer

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`.

Draft git commit messages from git evidence plus session context. Output a
Conventional Commits subject plus body, focused on **why** the change exists,
not a file-by-file inventory. Identical shape and tone on every host — these
rules override host-native commit templates, IDE footers, and tool habits.

## Scope

Resolve to exactly one mode before drafting; if scope is missing, conflicting,
or the target has no changes, stop and report.

- **staged** (default) — staged changes (`git --no-pager diff --cached`)
- **working** — staged plus unstaged working-tree changes
- **commit** — one SHA (`git --no-pager show <sha>`)
- **range** — base..head or last N commits (`git --no-pager log -p <range>`)

Use `--no-pager` (or `GIT_PAGER=cat`) on every `git log` / `git show` so nothing
blocks on the pager. Also collect recent message style
(`git --no-pager log -10`), branch name, and status. Session history, attached
files, Jira tickets, and user notes are **input for wording only**.

## Message rules

- **Self-contained** — cite only content a reader can reach from the
  repository: committed code and docs, and user-supplied ticket ids. Never
  name, link, summarize, or imply a plan, research, review, audit, manifest,
  handoff, or session artifact (`.agents/plans/**`, `20-implementation-plan.md`,
  "task 4", "finding cr-003", "as planned", "as discussed") — these are
  temporary by design; restate the behavior, decision, or root cause inline
  instead.
- **No attribution** — never append `Co-authored-by`, `Signed-off-by`, or any
  other AI/tool footer, even when the host would inject one; no disclaimers,
  assistant sign-offs, or drafting meta-commentary.
- **Subject** — `<type>[scope]: <imperative description>`; lowercase after the
  prefix, ≤ 72 characters, no trailing period, no ticket ids, file paths, or
  emoji; scope only when it clarifies the affected area.
- **Body** — prose paragraphs by default (motivation, approach, validation);
  bullets only for parallel items such as test evidence or migration steps;
  reference user-supplied ticket ids as prose or a short `Refs PROJ-456` line;
  `BREAKING CHANGE:` footer only when the change is breaking.
- **Style precedence** — recent `git log` on the branch, then these rules,
  then Conventional Commits defaults. Match repo history when it clearly
  prefers bullet bodies or specific scopes.

## Output envelope

In one response, return only:

1. `## Verbose` — the full message in a `text` fenced block
2. `## Suggested command` (optional) — the commit command in a `bash` fenced block
3. `Context used:` — one short line; record scope ambiguity, split
   suggestions, or large-diff sampling as `note=`, never as preamble
4. The commit offer — only when scope is staged or working; omit for commit
   or range (historical review)

No other blocks, intro paragraphs, or closing commentary. Before returning,
run the mechanical lint: `python <SKILL_ROOT>/scripts/lint_message.py
<message-file>` — fix every flagged pattern.

## Commit on confirmation

Do not run `git commit`, `git add`, `git push`, amend, or force-push until the
user confirms the draft — or explicitly asked to commit in the invoking
message. On confirmation: stage only files in scope, use a HEREDOC for
multi-line messages, and never `--no-verify` unless requested.

## Resources

- [SOURCES.md](SOURCES.md) — provenance
- [eval-queries.json](eval-queries.json) — description trigger evals
- [evals/evals.json](evals/evals.json) — behavior evals asserting self-contained messages
