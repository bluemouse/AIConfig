---
description: Load when drafting, formatting, revising, or validating meeting minutes, MoM, or meeting recaps from transcripts, chat logs, notes, or agendas — never-invent fidelity, confirmed-decisions vs discussion separation, and the `not specified` convention.
name: guidelines-minutes
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

## Style examples

Use this style for source-grounded uncertainty:

- `The transcript does not specify a due date for this action item.`
- `The group discussed this option, but the transcript does not show a final
  decision.`
- `The agenda lists this topic, but it was not discussed in the provided
  transcript.`
- `Beta release criteria were listed on the agenda but were not reached because
  the meeting ran out of time.`
- `The supporting document describes this requirement, but the transcript does
  not show that it was reviewed in the meeting.`

Use this style for decisions:

- `The team agreed to keep the current API contract for the beta release and
  revisit the migration plan after performance testing.`
- `No final decision was recorded on the proposed data model change.`

## Worked example

Calibrate decision vs discussion separation, action-item grounding, and `not
specified` usage against this abbreviated sample before drafting.

**Sample source (excerpt)**

**Agenda:** API versioning for the Payments service beta  
**Transcript excerpt:**

```text
Alex (facilitator): Thanks everyone. Goal today is whether we keep v1 for beta or start v2 now.

Jordan: v2 fixes the idempotency bug but needs two more sprints. I'd lean v1 for beta.

Sam: What about mobile clients still on v1.2?

Jordan: They can stay on v1.2 through beta if we don't change the contract.

Alex: Any objections to shipping beta on v1 and revisiting v2 after perf testing?

Sam: Works for me.

Alex: Jordan, can you write up the rollout checklist?

Jordan: Sure.

Alex: We didn't get to error-code mapping — let's carry that to next week's arch sync.

[Meeting ends — no due date stated for the checklist.]
```

**Metadata and uncertainty** — use stated facts; mark gaps plainly:

```markdown
**Date:** not specified  
**Facilitator:** Alex  
**Participants:** Alex, Jordan, Sam  
```

**Discussion (past tense, no decision implied):**

- Jordan described v2 as fixing an idempotency bug but requiring two additional
  sprints.
- Sam asked how mobile clients on v1.2 would be affected.

**Decision (only when the transcript shows agreement):**

| # | Decision | Context / Rationale | Impact / Notes |
|---|----------|---------------------|----------------|
| D1 | Ship the Payments service beta on v1 and revisit v2 after performance testing. | Jordan proposed v1 for beta; Alex asked for objections; Sam agreed. | Mobile clients on v1.2 can remain on v1.2 through beta if the contract is unchanged. |

**Not a decision (label correctly):**

- The group did not reach a decision on error-code mapping; Alex deferred it to
  the next architecture sync.

**Action item:**

| # | Action Item | Owner | Due Date | Notes / Dependencies |
|---|-------------|-------|----------|----------------------|
| A1 | Write up the rollout checklist for the beta release. | Jordan | not specified | Alex requested this follow-up; the transcript does not specify a due date. |

**Agenda not reached:**

- Error-code mapping was listed for discussion but was not reached; Alex
  scheduled it for the next week's architecture sync.

**Anti-patterns to avoid:**

| Bad pattern | Why it fails | Better |
| --- | --- | --- |
| "The team decided to adopt v2 after beta." | Transcript shows v1 for beta, v2 deferred | Match D1 above |
| Action owner "Sam" for the checklist | Jordan accepted the task | Owner: Jordan |
| Due date "Friday" | Not stated in transcript | Due Date: not specified |
| "Sam raised concerns about security." | Security not mentioned | Omit or quote only what was said |
| Summary adds latency SLO targets | Not in sources | Omit unsupported metrics |

## Quick fidelity check

Before returning, confirm:

1. Every decision row maps to agreement, confirmation, or explicit selection in
   the source.
2. Every owner and due date appears in the transcript or is `not specified`.
3. Deferred or undiscussed agenda items appear in Topics or Source Notes.
4. The summary does not add outcomes, risks, or technical details absent from
   the sources.
