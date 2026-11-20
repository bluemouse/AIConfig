---
description: "Load when drafting, formatting, revising, or validating meeting minutes, MoM, or meeting recaps from transcripts, chat logs, notes, or agendas — never-invent fidelity, confirmed-decisions vs discussion separation, and the `not specified` convention."
---

# Source-Grounded Meeting Minutes

Drafting minutes is a core capability; these rules exist because the real failure
modes are fabrication and overreach. They apply whenever producing minutes, MoM,
or a meeting recap from a transcript, chat log, notes, agenda, or supporting
materials.

## Never invent

- Never invent participants, decisions, owners, dates, deadlines, technical
  details, rationales, or commitments.
- Mark anything the sources do not state as `not specified` — never fill gaps
  with plausible values.
- No decision without source evidence of agreement, approval, or explicit
  selection; no action item without an assigned or accepted follow-up.
- Do not add background knowledge beyond the transcript, supporting materials,
  and user instructions.

## Separate outcomes from discussion

- Keep confirmed decisions, action items, risks, and open questions in distinct
  sections — do not blur discussion into decisions.
- Record action-item owners and due dates only when stated; otherwise
  `not specified`.
- Label proposals, deferred topics, and unresolved debate as such, and note
  agenda items that were not reached.

## Scope

- Draft from source material; if none exists, ask for it rather than drafting
  plausible minutes.
- Return minutes only — no tickets, publishing, or email unless explicitly
  requested.

## Default structure

Use this structure by default for software-development technology meetings.
Omit or compress sections only when the sources do not support them or the user
asks for a different format.

```markdown
# [Meeting Title] Minutes

**Date:** [date or `not specified`]  
**Time:** [time or `not specified`]  
**Location / Channel:** [room, call, chat, or `not specified`]  
**Facilitator:** [name or `not specified`]  
**Minute Taker:** [name or `not specified`]  
**Participants:** [confirmed attendees, or `not specified`]  
**Source Materials:** [transcript, agenda, slides, docs, tickets, or `not specified`]

## Purpose

[One or two sentences describing the purpose or context stated in the transcript,
agenda, or user instructions. Use `not specified` if unavailable.]

## Summary

[Brief factual summary of the meeting outcomes. Mention major topics, confirmed
decisions, unresolved items, significant risks, and important follow-up. Do not
include unsupported conclusions.]

## Topics Discussed

### [Topic 1]

- [Concise factual summary of what was discussed.]
- [Relevant technical details, constraints, trade-offs, dependencies, or risks
  stated in the meeting.]
- [Outcome, if any: confirmed decision, no decision, follow-up required, or
  deferred.]

### [Topic 2]

- [Continue for each major topic.]

## Decisions

| # | Decision | Context / Rationale | Impact / Notes |
|---|----------|---------------------|----------------|
| D1 | [confirmed decision] | [why it was made, if stated] | [affected system, product area, design, milestone, or stakeholder, if stated] |

If no decisions were confirmed, write: `No confirmed decisions were recorded in
the provided transcript.`

## Action Items

| # | Action Item | Owner | Due Date | Notes / Dependencies |
|---|-------------|-------|----------|----------------------|
| A1 | [specific action with expected outcome] | [owner or `not specified`] | [date or `not specified`] | [context, dependency, or source constraint] |

If no action items were assigned, write: `No explicit action items were recorded
in the provided transcript.`

## Risks, Blockers, Dependencies, and Assumptions

| # | Item | Type | Owner / Area | Status / Notes |
|---|------|------|--------------|----------------|
| R1 | [risk, blocker, dependency, or assumption] | [risk/blocker/dependency/assumption] | [owner or area, if stated] | [current state, impact, mitigation, or next step, if stated] |

## Open Questions

| # | Question | Owner / Area | Follow-up Needed |
|---|----------|--------------|------------------|
| Q1 | [open question] | [owner, team, or `not specified`] | [next step or `not specified`] |

## Next Steps

- [Most important near-term follow-up, grounded in action items or transcript.]
- [Include next meeting details only if stated.]

## Source Notes

[Optional. Include only when useful: missing transcript areas, ambiguous speaker
names, source conflicts, or support material that was provided but not
discussed.]
```

## Calibration and phrasing

- **Uncertainty / unreached agenda:** `"The transcript does not specify a due date."` / `"The group discussed this option without reaching a decision."` / `"Error-code mapping was on the agenda but deferred when time ran out."`
- **Confirmed decision (requires explicit agreement):** `"Ship Payments beta on v1 and revisit v2 after perf testing"` (Alex asked for objections; Sam agreed).
- **Action item:** record only accepted/assigned tasks (`Owner: Jordan`, `Due Date: not specified` when unstated — never invent `"Friday"` or reassign to another speaker).
- **Never fabricate:** do not invert deferred options into post-beta commitments, invent unmentioned topics (e.g. security concerns), or add metrics/SLOs absent from the sources.

## Quick fidelity check

Before returning, confirm:

1. Every decision row maps to agreement, confirmation, or explicit selection in
   the source.
2. Every owner and due date appears in the transcript or is `not specified`.
3. Deferred or undiscussed agenda items appear in Topics or Source Notes.
4. The summary does not add outcomes, risks, or technical details absent from
   the sources.
