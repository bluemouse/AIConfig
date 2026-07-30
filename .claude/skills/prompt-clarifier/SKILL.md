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

# prompt-clarifier (Claude Code)

Read the shared skill first — it is the source of truth for the clarification state
machine, question selection, contradiction handling, and stopping criteria:

`../../../.shared/skills/prompt-clarifier/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/prompt-clarifier/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Claude Code-native** mechanics for asking and inspecting. When this
wrapper and the shared skill disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh prompt-clarifier

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name prompt-clarifier --source skills/prompt-clarifier --overwrite
```

## Asking in Claude Code

There is no structured question widget — questions are plain text and you must **end the
turn** to receive an answer. That makes turn economy the main constraint:

1. Complete the shared skill's INSPECT state before ending a turn. Read, Grep, and Glob
   are cheap; a wasted question round is not.
2. Send the whole current batch in one message using the shared skill's numbered format
   with lettered options, a marked recommendation, and an explicit reply hint such as
   `Reply with defaults, 1c 2a, or your own wording`.
3. Do not end the turn for a question that a default and a stated assumption would cover.
4. When only part of the task is blocked, do the unblocked reversible work first and end
   the turn with both the progress and the remaining question.

## Inspecting before asking

Use Read, Grep, and Glob for anything discoverable in the repository. Dispatch a
read-only subagent when the lookup is broad enough to need its own context, and keep
clarifying other dimensions while it runs.

## Subagent and headless context

- **Subagents** cannot reach the user. When running as a subagent, skip the ASK state,
  apply the shared skill's assumption rules, and return every assumption explicitly in
  the status report along with any blocker that needed a human decision.
- **Headless / `claude -p` runs** are non-interactive for the same reason. Prefer the
  shared skill's STOP output — the exact missing requirement, why it blocks, and the
  smallest decision needed — over guessing on irreversible work.
- Before dispatching subagents yourself, resolve blockers first. An unclear task packet
  multiplies the ambiguity across every agent in the wave.

## Claude.ai (no Claude Code CLI)

Interactive clarification works normally, but repository inspection may be unavailable.
When you cannot inspect, treat facts that would have been discoverable as unknown and ask
for them, or ask the user to paste the relevant file or configuration.

## Wrapper policy

- Edit cross-tool clarification behavior in `../../../.shared/skills/prompt-clarifier/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
