---
name: verdict-first
description: 'Shape chat responses for a reader who reviews the work but does not
  do the coding — the agent does. Use when reporting results, verdicts, escalations,
  phase status, or any update where the reader must absorb the outcome fast: lead
  with the result or decision, surface anything needing the user''s input as a structured
  question, no preamble or recap, matter-of-fact errors, restate multi-step state,
  size unstarted work by its shape. Also triggers when the user asks for shorter answers,
  less prose, or ''just tell me the result''. Not for artifact files, which follow
  their templates.'
---

# Verdict First — Claude Code wrapper

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.ai/skills/verdict-first/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the
source of truth for rules, scope boundaries, and the pre-send check. Resolve
`<SKILL_ROOT>` as `../../../.ai/skills/verdict-first` and resolve paths to
`scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

- **Structured questions:** use the `AskUserQuestion` tool for every ask
  covered by rule 2 — never a question embedded in prose.
- **Always-on loading:** this skill's rules apply to every response, not only
  when its description triggers. Claude Code loads project memory
  (`CLAUDE.md`) at session start — the always-on line in `CLAUDE.md`
  pointing at this skill is the load mechanism; the description is a fallback
  for explicit "be brief"-style requests.
- **Restart or reload** the Claude Code session after installing or editing
  this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `.ai/skills/verdict-first/`.
- Keep only Claude Code-specific information in this wrapper.
