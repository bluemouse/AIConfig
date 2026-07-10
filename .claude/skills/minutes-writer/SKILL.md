---
name: minutes-writer
description: "Draft source-grounded meeting minutes and recaps for software and technology meetings from transcripts, chat logs, notes, agendas, and supporting materials. Use when asked for minutes, MoM, meeting summary, meeting recap, or to write up, format, revise, or validate engineering meeting notes \u2014 including design reviews, architecture discussions, planning, incident follow-ups, and decision meetings. Separate confirmed decisions from discussion, capture action items with owners and due dates when stated, and never invent participants, decisions, dates, or commitments. Does not create Jira tickets, publish to Confluence, or send email unless explicitly asked."
---

# minutes-writer wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/minutes-writer/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/minutes-writer` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/minutes-writer/`.
- Keep only Claude Code-specific information in this wrapper.
