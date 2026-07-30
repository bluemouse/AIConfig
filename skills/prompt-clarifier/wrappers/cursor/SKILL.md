---
name: prompt-clarifier
description: Iteratively clarify ambiguous requirements, definitions, intent, scope, constraints, acceptance criteria, environment, risks, and expected outputs before or during a task. Use when a prompt has multiple plausible interpretations, uses vague or overloaded terms, omits decisions that would materially change the result, contains conflicting requirements, or leaves the AI unsure what successful completion means. Ask adaptive, high-information questions in small batches, update the working interpretation after every answer, and continue until the task is actionable, the user accepts explicit assumptions, or safety requires stopping.
---

# prompt-clarifier (Cursor)

Read the shared skill first — it is the source of truth for the clarification state
machine, question selection, contradiction handling, and stopping criteria:

`../../../.shared/skills/prompt-clarifier/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/prompt-clarifier/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Cursor-native** mechanics for asking and inspecting. When this
wrapper and the shared skill disagree on mechanics, follow this wrapper for Cursor;
follow the shared skill for when to ask, what to ask, and when to stop.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under
  `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the
  agent rediscovers them

## Install or refresh prompt-clarifier

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name prompt-clarifier --source skills/prompt-clarifier --overwrite
```

## Asking in Cursor

Use the **AskQuestion tool** for the shared skill's ASK state whenever the question set
is a small number of discrete decisions. It renders selectable options and collects
structured answers, which is more reliable than options listed in prose.

1. One question object per decision — do not pack several decisions into one prompt
   string.
2. Put the recommended option **first** and append `(Recommended)` to its label, matching
   the shared skill's default-marking rule.
3. Add `Not sure - use the recommended default` as an option when a safe default exists.
   The user can always answer freely through "Other".
4. Set `allow_multiple: true` only for genuinely multi-select decisions such as scope
   sets or platform targets.
5. Fall back to the shared skill's numbered-text format when a question needs an
   open-ended answer (a threshold, an example and non-example, an exact definition) or
   when the options cannot be made mutually distinct.

Keep the batch size from the shared skill: one to three decisions per turn by default,
up to five only when independent and easy to answer together.

## Inspecting before asking

The shared skill's INSPECT state expects cheap discovery first. In Cursor, prefer Read,
Grep, and Glob over asking about anything discoverable in the workspace — file layout,
existing conventions, dependency versions, build configuration. Attached context, open
files, and recently viewed files count as supplied facts; never ask for something the
user already provided there.

Dispatch an `explore` subagent through the Task tool when resolving the question would
otherwise take many searches, and continue clarifying other dimensions while it runs.

## Modes

- In **Plan mode**, clarification and plan drafting happen together — front-load the
  blocking decisions before proposing the plan, and record accepted defaults in the plan
  itself.
- Switching to Plan mode with `SwitchMode` is often better than a long clarification
  round when the task turns out to be large or architecture-shaped.
- In **read-only modes**, still apply the authority rules: confirm before proposing
  actions the current mode cannot perform.

## Subagent context

Subagents launched with the Task tool cannot ask the user anything. When you are running
as a subagent, do not enter the ASK state — apply the shared skill's assumption rules,
state each assumption explicitly in your returned report, and flag any blocker that
genuinely required a human decision.

## Wrapper policy

- Edit cross-tool clarification behavior in `../../../.shared/skills/prompt-clarifier/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
