---
name: minutes-writer
description: Draft source-grounded meeting minutes and recaps for software and technology meetings from transcripts, chat logs, notes, agendas, and supporting materials. Use when asked for minutes, MoM, meeting summary, meeting recap, or to write up, format, revise, or validate engineering meeting notes — including design reviews, architecture discussions, planning, incident follow-ups, and decision meetings. Separate confirmed decisions from discussion, capture action items with owners and due dates when stated, and never invent participants, decisions, dates, or commitments. Does not create Jira tickets, publish to Confluence, or send email unless explicitly asked.
---

# Minutes Writer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Create clear, professional, source-grounded meeting minutes for software-development
technology meetings. Produce minutes that help attendees and non-attending stakeholders
understand what was discussed, what was decided, what remains open, and who is responsible
for follow-up.

## Primary Directive

Your job is to **draft, format, revise, or validate meeting minutes**, not to create
tickets, publish documents, or send email.

Do not create Jira/Linear tickets, publish to Confluence/Notion, send email, or run host
MCP workflows unless the user explicitly requests that in the same or a follow-up message.

## When to Use

- Drafting minutes from a meeting transcript, chat log, or notes
- Writing a meeting summary, recap, or MoM for an engineering or technology meeting
- Formatting rough notes into professional minutes with decisions and action items
- Revising existing minutes to separate decisions from discussion or improve fidelity
- Validating minutes against a transcript or supporting materials
- Producing output variants (brief, decision-oriented, or executive summary)

## When NOT to Use

- **Jira/Linear ticket creation from notes** — use Atlassian or host task-capture tooling
  when available; offer formatted minutes first if the user also wants a record
- **PR/MR authoring** — use [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md)
- **Commit messages** — use [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md)
- **Action-item-only extraction** with no minutes structure — say so; offer full minutes
  or defer to task-capture tooling
- **General narrative summary** with no metadata, decisions, or action sections — not this
  skill unless the user wants conventional minutes format

## Companion Skills

Minutes are a source of decisions, not the end of the trail. After producing minutes, the
recorded decisions and action items can feed downstream lifecycle work (this skill only
writes the record; it does not create tickets, publish docs, or send messages):

| Downstream use | Skill |
| --- | --- |
| Product/scope decisions into a research report | [../research-guide/SKILL.md](../research-guide/SKILL.md) |
| Constraints and action items into an implementation plan | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) |
| Commitments as verification criteria | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Delivery notes for a PR/MR | [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md) |

## Purpose

This skill applies to general technology-topic meetings, not only sync meetings. Example
meeting types include architecture discussions, product/design reviews, engineering
planning, implementation reviews, technical decision meetings, incident follow-ups, roadmap
reviews, dependency reviews, and release or migration discussions.

Stakeholders may include software developers, product designers, software architects, and
related engineering or product roles.

## Input handling

- Expect a meeting transcript as the primary input whenever available.
- Accept supporting materials such as agendas, slides, design documents, product
  requirements, tickets, issue links, chat logs, attendee lists, diagrams, notes, and user
  instructions.
- If no transcript or source material is available, ask for source material rather than
  drafting plausible minutes.
- If the transcript is partial or low quality, state the limitation and produce only
  source-supported minutes.

Details: [failure-and-guardrails.md](references/failure-and-guardrails.md)

## Source hierarchy

1. Treat the meeting transcript as the primary evidence source for what happened in the
   meeting.
2. Use supporting materials to clarify context, agenda order, names, acronyms, issue IDs,
   design references, requirements, and pre-read material.
3. Do not present supporting-material content as meeting discussion unless the transcript
   shows it was discussed or the user explicitly asks for a combined meeting-plus-material
   summary.
4. If sources conflict, prefer the transcript for meeting events and note the discrepancy
   only if it affects the minutes.
5. Use `not specified` for missing metadata, owners, dates, or decisions rather than
   inferring them.

## Workflow

Every invocation follows six phases. Read the matching reference **before** executing each
phase (see [Reference routing](#reference-routing)).

### 1. Parse and confirm

- Inventory inputs: transcript, agenda, slides, design documents, tickets, chat logs,
  attendee list, and user instructions.
- If no transcript or source material is available, stop and ask for source material.
- If scope is ambiguous (multiple meetings, wrong date), ask one clarifying question.

Details: [failure-and-guardrails.md](references/failure-and-guardrails.md)

### 2. Extract metadata

Extract meeting title, date, time, location or channel, facilitator, participants,
absentees (when stated), minute taker, and source materials.

### 3. Map topics and outcomes

Build a topic map from the transcript. Group related segments into agenda-style topics
rather than following every speaker turn. Identify outcomes separately from discussion:

- confirmed decisions
- action items and owners
- due dates and milestones
- open questions
- risks, blockers, dependencies, and assumptions
- design, architecture, product, or implementation trade-offs
- user-impact, compatibility, performance, security, quality, release, or operational notes
- agenda items listed in supporting materials but not reached or discussed in the transcript

### 4. Draft

Draft minutes using the default structure in [minutes-template.md](references/minutes-template.md).
Pick the output variant from the table below. Adapt sections only when unsupported by the
sources or when the user asks for a variant.

Review [worked-example.md](references/worked-example.md) for fidelity patterns before
drafting.

| User request | Mode |
| --- | --- |
| default / "minutes" | Full template |
| "brief", "short", "compact recap" | Same sections, compressed topic summaries |
| "decisions", "decision log" | Emphasize Decisions, Action Items, Open Questions |
| "executive summary", "for leadership" | Add brief executive summary; reduce implementation detail |

Details: [minutes-template.md](references/minutes-template.md),
[worked-example.md](references/worked-example.md)

### 5. Fidelity pass

Read [source-fidelity-checklist.md](references/source-fidelity-checklist.md) and verify
every item. Fix any red flags before returning.

Details: [source-fidelity-checklist.md](references/source-fidelity-checklist.md)

### 6. Return

Return the final minutes only. Do not create tickets, publish documents, or send email
unless the user explicitly asks afterward.

## Content rules

- Never invent meeting content, participants, decisions, owners, deadlines, technical
  details, rationales, commitments, or next steps.
- Preserve important nouns exactly when possible: product names, component names, APIs,
  services, repos, tickets, versions, metrics, release names, platform names, design names,
  and customer or user segment names.
- Distinguish confirmed decisions from proposals, options, assumptions, unresolved
  discussion, and deferred topics.
- Do not convert a suggestion into a decision unless the transcript clearly shows
  agreement, approval, confirmation, or selection.
- Do not convert general discussion into an action item unless a follow-up task is
  assigned, accepted, or clearly requested.
- Mark missing owners, dates, deadlines, and metadata as `not specified`.
- Include uncertainty plainly when needed, such as `the transcript does not specify the
  owner` or `the group discussed the option, but no final decision was recorded`.
- Avoid adding background knowledge that is not in the transcript, supporting materials, or
  user instructions.

## Professional style

- Write in a neutral, concise, business-professional style.
- Use a conventional minutes format with meeting metadata, summary, topics, decisions,
  action items, risks, open questions, and next steps.
- Prefer structured topic summaries over speaker-by-speaker chronology.
- Use past tense for discussion and present or future tense for action items.
- Avoid editorial commentary, sentiment, speculation, and evaluative language.
- Attribute comments only when attribution matters for accountability, ownership,
  disagreement, decision authority, or follow-up.
- Avoid excessive verbatim quotes. Quote only short language needed to preserve a decision,
  requirement, risk, or commitment exactly.
- Use clear headings, concise bullets, and tables for decisions, actions, risks, and
  questions.

## Technology-meeting priorities

Capture the items that matter most after a software-development technology meeting:

- architecture decisions, design constraints, alternatives, and rationale
- API, data model, integration, performance, reliability, security, compatibility,
  migration, observability, or rollout implications
- product/design constraints, user-experience impacts, user research inputs, and
  unresolved design questions
- engineering dependencies, blockers, ownership boundaries, sequencing, and delivery risks
- release, milestone, beta, migration, incident, quality, or operational impacts stated
  in the meeting
- follow-up validation needed, including experiments, prototypes, performance checks,
  design reviews, stakeholder reviews, or ticket updates

## Reference routing

| Task | Read |
| --- | --- |
| No source material, partial transcript, conflicts, scope ambiguity | [failure-and-guardrails.md](references/failure-and-guardrails.md) |
| Default minutes structure, section order, style examples | [minutes-template.md](references/minutes-template.md) |
| Fidelity patterns, decision vs discussion, `not specified` usage | [worked-example.md](references/worked-example.md) |
| Pre-return verification, red flags | [source-fidelity-checklist.md](references/source-fidelity-checklist.md) |

## Quick completion checklist

Before returning meeting minutes:

1. **Source material** — transcript or notes confirmed; limitations stated if partial
2. **Metadata** — title, date, participants, and sources extracted; absentees when stated
3. **Outcomes separated** — decisions, actions, risks, and open questions distinct from
   discussion
4. **Fidelity** — checklist passed; no red flags; agenda-not-discussed items noted
5. **Safety** — no invented content; no tickets/publish/email unless explicitly requested

## Default output expectations

Produce minutes with these qualities:

- enough context for attendees and stakeholders to understand the outcome without
  rereading the transcript
- no unsupported claims beyond the provided transcript and materials
- clear separation between discussion, decisions, action items, risks or blockers, open
  questions, and next steps
- action items that include owner and due date when stated, or `not specified` when absent
- concise topic summaries that preserve important technical detail without transcript-like
  verbosity

## Resources

- [failure-and-guardrails.md](references/failure-and-guardrails.md) — Errors, guardrails, confidentiality
- [minutes-template.md](references/minutes-template.md) — Default structure and style examples
- [worked-example.md](references/worked-example.md) — Fidelity patterns with sample source and output
- [source-fidelity-checklist.md](references/source-fidelity-checklist.md) — Pre-return verification
- [SOURCES.md](SOURCES.md) — Provenance and reference notes
