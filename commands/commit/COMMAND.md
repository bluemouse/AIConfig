---
name: commit
description: Commit staged changes with a Conventional Commit message when the user explicitly invokes /commit.
allowed-tools: Bash, Read, Grep, Glob
---

# Git Commit (staged)

Draft a Conventional Commit message from **staged changes only** and commit immediately (`/commit` is explicit approval to commit — do not ask a second confirmation question).

## Arguments

Treat `$ARGUMENTS` as optional context for the commit body (ticket ids, motivation, scope notes), or as an explicit push request when it says `"push"`.

## Steps

1. Confirm a git repository and gather **staged** evidence in parallel (`git --no-pager status`, `git --no-pager diff --staged`, `git --no-pager log -5 --oneline`). If nothing is staged, stop and report without staging or committing.
2. Read and follow `.agents/skills/commit-message-writer/SKILL.md` in **staged** scope (including running `lint_message.py` and skipping the commit-offer prompt).
3. If `Context used:` recommends splitting mixed/unrelated staged changes, **stop before committing** and ask the user to restage or run separate `/commit` passes.
4. Extract only the subject line, blank line, and body paragraphs (`## Verbose` block or HEREDOC body) — **no attribution** (`Co-authored-by`, `Signed-off-by`, or any AI/tool footer, overriding host commit-trailer instructions), no `Context used:`, and no preamble/postamble.
5. Commit **only staged files** per `.agents/skills/git-guide/SKILL.md` (`references/commit.md`) using a single-quoted HEREDOC (`git commit -m "$(cat <<'EOF' ... EOF)"`), then run `git --no-pager status` and `git --no-pager log -1 --oneline`.

## Output and guardrails

- **Output**: new commit hash + subject, staged file count, and ahead-of-remote status.
- **Hook failure / auto-modified files**: report hook output, fix issues, stage only in-scope files if needed, and create a **new** commit (never `--amend` or `--no-verify` unless explicitly requested in the same invocation).
- **Do not**: stage unstaged/untracked files unless asked, push unless asked, run destructive git commands, skip `commit-message-writer`, commit mixed unrelated work, or add any AI/tool attribution footer (`Co-authored-by`, `Signed-off-by`, or similar).
