# Failure and Guardrails

## Contents

- [On failure](#on-failure)
- [Do not](#do-not)
- [Split commits](#split-commits)
- [Commit phase](#commit-phase)

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

- Run `git commit`, `git push`, or stage files until the user confirms after reviewing the draft
- Use `--no-verify`, amend, or force-push while drafting
- Dump a raw file list as the commit message
- Contradict session context or supplied plan/ticket intent when the diff is ambiguous
- Auto-commit immediately — always draft first; include the commit offer in the same response when scope is staged or working
- Add AI or tool attribution footers — no `Co-authored-by`, `Signed-off-by`, or similar lines
  naming Cursor, Claude, Copilot, ChatGPT, or any other assistant or automation client
- Include non-change content — no assistant sign-offs, drafting disclaimers, or meta-commentary
  in Verbose or Suggested command bodies
- Vary output shape by host — Cursor, Claude Code, and Copilot must return the same envelope
- Open with "This commit …" or dump raw file lists — follow [message-style-contract.md](message-style-contract.md)

## Split commits

When the diff contains unrelated changes (e.g. feature + unrelated formatting + docs typo):

1. Record in `Context used:` with `note=` that the diff mixes unrelated work
2. Suggest logical split points (by concern or directory) in that note or the Verbose body
   when drafting for one slice only
3. Offer to draft separate messages per split if the user wants

Do not blend unrelated intent into one message to "get it done."

## Commit phase

**In the draft response** (staged/working scope): include the commit offer after
`Context used:` in the same response — do not defer to a follow-up turn.

When scope is **commit** or **range**, omit the commit offer — the draft is for review or
rewrite, not an immediate commit.

**After the user confirms** (or they explicitly asked to commit in the invoking message):

1. Stage only when needed and only files in scope
2. Use HEREDOC for multi-line messages
3. Never `--no-verify` unless explicitly requested
4. Follow the user's git commit rules (hooks, signing, etc.)

This skill does not push. Suggest push only when the user asks.
