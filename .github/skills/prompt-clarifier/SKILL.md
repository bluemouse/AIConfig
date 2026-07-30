---
name: prompt-clarifier
description: Iteratively clarify ambiguous requirements, definitions, intent, scope,
  constraints, acceptance criteria, environment, risks, and expected outputs before
  or during a task. Use when a prompt has multiple plausible interpretations, uses
  vague or overloaded terms, omits decisions that would materially change the result,
  contains conflicting requirements, or leaves the AI unsure what successful completion
  means. Ask adaptive, high-information questions in small batches, update the working
  interpretation after every answer, and continue until the task is actionable, the
  user accepts explicit assumptions, or safety requires stopping.
---

# prompt-clarifier (GitHub Copilot)

Read the shared skill first — it is the source of truth for the clarification state
machine, question selection, contradiction handling, and stopping criteria:

`../../../.shared/skills/prompt-clarifier/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/prompt-clarifier/`. Resolve paths to
`references/` from that directory.

This wrapper adds **GitHub Copilot / VS Code-native** mechanics. Copilot runs both
interactive chat sessions and non-interactive coding-agent sessions, and the two demand
different behavior from the ASK state.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Reload VS Code** after installing or editing skills so Copilot rediscovers them

## Install or refresh prompt-clarifier

From repo root (or ask the user to run in a terminal):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name prompt-clarifier --source skills/prompt-clarifier --overwrite
```

## Asking in interactive chat

Copilot Chat has no structured question widget — use the shared skill's numbered format
with lettered options, a marked recommendation, and an explicit reply hint. Keep each
question short; chat panes are narrow and long option blocks get skimmed.

Complete the shared skill's INSPECT state with workspace search and file reads before
asking. Open editors, selections, and `#file` / `#selection` references are supplied
context — never ask for what they already contain.

## Non-interactive coding-agent sessions

When Copilot is assigned an issue or runs as a background coding agent, there is no user
to answer. Do not stall waiting for a reply:

1. Apply the shared skill's assumption rules and choose the recommended defaults.
2. Record every assumption in the pull request description, next to what would change if
   the assumption is wrong.
3. Prefer the smallest reversible change when a decision is genuinely undetermined, so a
   reviewer can redirect cheaply.
4. For work that the shared skill's STOP criteria mark unsafe without the missing
   decision — destructive, externally visible, costly, or security-sensitive — leave the
   work undone and state the specific blocker in the pull request or issue comment
   instead of guessing.

## Custom instructions and prompt files

Recurring answers belong in `.github/copilot-instructions.md`, a path-scoped
`*.instructions.md` file, or a `.github/prompts/*.prompt.md` prompt rather than in a
repeated question. When you find yourself asking the same project-level question across
sessions, suggest recording it there.

## Wrapper policy

- Edit cross-tool clarification behavior in `../../../.shared/skills/prompt-clarifier/`
- Edit Copilot-specific mechanics here
- Do not duplicate the full shared skill body in this file
