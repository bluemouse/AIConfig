# Failure and Guardrails

## Contents

- [On failure](#on-failure)
- [Do not](#do-not)
- [Split commits](#split-commits)
- [Optional commit phase](#optional-commit-phase)

## On failure

| Condition | Action |
| --- | --- |
| Not a git repo | Say so; do not fabricate a message |
| Invalid `<sha>` or empty range | Show git error output |
| No changes for `--staged` / `--working` | Report clean tree / empty index; do not invent a message |
| Context path missing | List missing paths; continue with available context if the user agrees |
| Jira MCP unavailable | Use ticket id in text only; note that live ticket details were not fetched |
| Ambiguous scope | Ask one clarifying question before analyzing |

## Do not

- Run `git commit`, `git push`, or stage files unless the user explicitly requests a commit afterward
- Use `--no-verify`, amend, or force-push while drafting
- Dump a raw file list as the commit message
- Contradict session context or supplied plan/ticket intent when the diff is ambiguous
- Auto-commit immediately — unlike some git automation flows, this skill always drafts first

## Split commits

When the diff contains unrelated changes (e.g. feature + unrelated formatting + docs typo):

1. State that the diff mixes unrelated work
2. Suggest logical split points (by concern or directory)
3. Offer to draft separate Compact/Verbose pairs per split if the user wants

Do not blend unrelated intent into one message to "get it done."

## Optional commit phase

When the user explicitly asks to commit (same or follow-up message):

1. Use the **verbose** message unless they choose compact
2. Stage only if needed and only files in scope
3. Use HEREDOC for multi-line messages
4. Never `--no-verify` unless explicitly requested
5. Follow the user's git commit rules (hooks, signing, etc.)

This skill does not push. Suggest push only when the user asks.
