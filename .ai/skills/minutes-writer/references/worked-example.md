# Worked Example — Fidelity Patterns

Use this file before drafting to calibrate decision vs discussion separation, action-item
grounding, and `not specified` usage. The sample is abbreviated; real transcripts may be
longer.

## Sample source (excerpt)

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

## Good minutes patterns

### Metadata and uncertainty

Use stated facts; mark gaps plainly:

```markdown
**Date:** not specified  
**Facilitator:** Alex  
**Participants:** Alex, Jordan, Sam  
```

### Discussion vs decision

**Discussion (past tense, no decision implied):**

- Jordan described v2 as fixing an idempotency bug but requiring two additional sprints.
- Sam asked how mobile clients on v1.2 would be affected.

**Decision (only when transcript shows agreement):**

| # | Decision | Context / Rationale | Impact / Notes |
|---|----------|---------------------|----------------|
| D1 | Ship the Payments service beta on v1 and revisit v2 after performance testing. | Jordan proposed v1 for beta; Alex asked for objections; Sam agreed. | Mobile clients on v1.2 can remain on v1.2 through beta if the contract is unchanged. |

**Not a decision (label correctly):**

- The group did not reach a decision on error-code mapping; Alex deferred it to the next architecture sync.

### Action items

| # | Action Item | Owner | Due Date | Notes / Dependencies |
|---|-------------|-------|----------|----------------------|
| A1 | Write up the rollout checklist for the beta release. | Jordan | not specified | Alex requested this follow-up; the transcript does not specify a due date. |

When no action was assigned:

`No explicit action items were recorded in the provided transcript.`

### Agenda not reached

- Error-code mapping was listed for discussion but was not reached; Alex scheduled it for the next week's architecture sync.

## Anti-patterns to avoid

| Bad pattern | Why it fails | Better |
| --- | --- | --- |
| "The team decided to adopt v2 after beta." | Transcript shows v1 for beta, v2 deferred | Match D1 above |
| Action owner "Sam" for the checklist | Jordan accepted the task | Owner: Jordan |
| Due date "Friday" | Not stated in transcript | Due Date: not specified |
| "Sam raised concerns about security." | Security not mentioned | Omit or quote only what was said |
| Summary adds latency SLO targets | Not in sources | Omit unsupported metrics |

## Quick fidelity check

Before returning, confirm:

1. Every decision row maps to agreement, confirmation, or explicit selection in the source
2. Every owner and due date appears in the transcript or is `not specified`
3. Deferred or undiscussed agenda items appear in Topics or Source Notes
4. The summary does not add outcomes, risks, or technical details absent from the sources
