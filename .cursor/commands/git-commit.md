# Git Commit (staged)

Draft a commit message from **staged changes only**, then commit. Invoking `/git-commit` is explicit approval to commit after the message is drafted — do not ask for a second confirmation.

## Steps

1. Confirm the workspace root is a git repository.

2. Gather git evidence for **staged scope only** (run in parallel where possible):
   - `git status`
   - `git diff --staged`
   - `git log -5 --oneline` (for message style)

3. If there are no staged changes, stop and report — do not stage files or commit.

4. Read and follow the **commit-message-writer** skill (`.shared/skills/commit-message-writer/SKILL.md` or the installed tool skill). Use scope **staged** only. Run phases 1–4 (parse, gather evidence, compose, output) — treat `/git-commit` as the explicit commit request exception in that skill's Primary Directive. **Do not** emit or wait on the commit-offer question; proceed to commit once the draft is ready.

5. Extract the final commit text (subject line, blank line, body) from the draft:
   - Prefer the ` ```text ` block under `## Verbose`, or the HEREDOC body inside `## Suggested command` under ` ```bash `.
   - Never include `Context used:`, the commit-offer question, or any assistant preamble/postamble in the committed message.
   - The committed message must contain **only change-related content** — no tool attribution footers (`Co-authored-by`, `Signed-off-by`, or similar).

6. If the draft's `Context used:` line includes a split suggestion (`note=` mentioning unrelated or mixed work), or the staged diff clearly mixes unrelated concerns, **stop before committing**. Summarize the split recommendation and ask the user to restage or run separate `/git-commit` invocations — do not auto-commit a blended message.

7. Commit **only staged files** — do not run `git add` unless the user explicitly asked to stage additional paths in the same invocation. For git mechanics and hook behavior, follow **git-guide** (`.shared/skills/git-guide/SKILL.md`, `references/commit.md`):
   ```bash
   git commit -m "$(cat <<'EOF'
   <subject line>

   <body paragraphs>
   EOF
   )"
   ```

8. Run `git status` after commit and report the new commit hash (`git log -1 --oneline`).

## Optional arguments

If the user adds text after `/git-commit`, treat it as extra context for the commit message (ticket ids, motivation, scope notes). If they explicitly ask to **push**, push only after a successful commit and only to the current branch's configured remote — never force-push.

## Output

Brief summary:
- Commit hash and subject line
- Files committed (count from staged stat)
- Whether the branch is ahead of remote (do not push unless asked)

## On failure

| Condition | Action |
| --- | --- |
| Commit rejected by a hook | Report hook output; fix the issue and create a **new** commit — never amend a failed or rejected commit |
| Hook auto-modifies files | Fix any remaining issues, stage only what belongs in scope if needed, then create a **new** commit |
| Nothing staged | Stop and report — do not stage or commit |

Never use `--no-verify` unless the user explicitly requested it in the same invocation.

## Do not

- Commit unstaged or untracked files
- Push to remote unless explicitly requested in the same invocation
- Run `git commit --amend`, `--no-verify`, or any destructive git commands
- Skip commit-message-writer and invent a message without reading the staged diff
- Add AI or assistant attribution lines to the commit message
- Commit when commit-message-writer recommends splitting unrelated staged work
