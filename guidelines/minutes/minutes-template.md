# Technology Meeting Minutes Template

Use this as the default structure for minutes from software-development technology meetings. Omit or compress sections only when the sources do not support them or the user asks for a different format.

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

[One or two sentences describing the purpose or context stated in the transcript, agenda, or user instructions. Use `not specified` if unavailable.]

## Summary

[Brief factual summary of the meeting outcomes. Mention major topics, confirmed decisions, unresolved items, significant risks, and important follow-up. Do not include unsupported conclusions.]

## Topics Discussed

### [Topic 1]

- [Concise factual summary of what was discussed.]
- [Relevant technical details, constraints, trade-offs, dependencies, or risks stated in the meeting.]
- [Outcome, if any: confirmed decision, no decision, follow-up required, or deferred.]

### [Topic 2]

- [Continue for each major topic.]

## Decisions

| # | Decision | Context / Rationale | Impact / Notes |
|---|----------|---------------------|----------------|
| D1 | [confirmed decision] | [why it was made, if stated] | [affected system, product area, design, milestone, or stakeholder, if stated] |

If no decisions were confirmed, write: `No confirmed decisions were recorded in the provided transcript.`

## Action Items

| # | Action Item | Owner | Due Date | Notes / Dependencies |
|---|-------------|-------|----------|----------------------|
| A1 | [specific action with expected outcome] | [owner or `not specified`] | [date or `not specified`] | [context, dependency, or source constraint] |

If no action items were assigned, write: `No explicit action items were recorded in the provided transcript.`

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

[Optional. Include only when useful: missing transcript areas, ambiguous speaker names, source conflicts, or support material that was provided but not discussed.]
```

## Style examples

Use this style for source-grounded uncertainty:

- `The transcript does not specify a due date for this action item.`
- `The group discussed this option, but the transcript does not show a final decision.`
- `The agenda lists this topic, but it was not discussed in the provided transcript.`
- `Beta release criteria were listed on the agenda but were not reached because the meeting ran out of time.`
- `The supporting document describes this requirement, but the transcript does not show that it was reviewed in the meeting.`

Use this style for decisions:

- `The team agreed to keep the current API contract for the beta release and revisit the migration plan after performance testing.`
- `No final decision was recorded on the proposed data model change.`

Use this style for action items:

| # | Action Item | Owner | Due Date | Notes / Dependencies |
|---|-------------|-------|----------|----------------------|
| A1 | Validate the proposed implementation change against the regression suite. | not specified | not specified | Follow-up was requested, but the transcript did not assign an owner or date. |
