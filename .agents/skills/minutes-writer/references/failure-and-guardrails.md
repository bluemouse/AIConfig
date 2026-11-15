# Failure and Guardrails

## Contents

- [On failure](#on-failure)
- [Do not](#do-not)
- [Confidentiality and sensitive content](#confidentiality-and-sensitive-content)
- [Optional downstream actions](#optional-downstream-actions)

## On failure

| Condition | Action |
| --- | --- |
| No transcript or source material | Stop and ask for source material. Do not draft plausible minutes. |
| Partial or low-quality transcript | State the limitation up front. Produce only source-supported minutes; note gaps in Source Notes when useful. |
| Multiple meetings in one file | Ask which meeting to minute, or offer to split by date/title if clearly separable. |
| Wrong date or meeting identity unclear | Ask one clarifying question before drafting. |
| Sources conflict on facts | Prefer the transcript for meeting events. Note the discrepancy only if it affects the minutes. |
| Supporting material not discussed | Do not present it as meeting discussion. Note in Source Notes if the agenda or doc was provided but not reached. |
| Ambiguous scope (brief vs full, audience) | Ask one clarifying question, or pick the default full template and note the assumption. |
| Attendee names unclear or inconsistent | Use names as stated; note ambiguity in Source Notes rather than guessing roles or attendance. |

## Do not

- Create Jira, Linear, or other tickets from minutes unless the user explicitly requests it
- Publish to Confluence, Notion, or other wikis unless explicitly requested
- Send email or run host MCP publish workflows unless explicitly requested
- Invent participants, decisions, owners, deadlines, technical details, rationales, or commitments
- Convert suggestions or open discussion into confirmed decisions without transcript support
- Convert general discussion into action items without an assigned or accepted follow-up
- Fill missing metadata with plausible values — use `not specified` instead
- Add background knowledge not present in the transcript, supporting materials, or user instructions
- Expand sensitive content beyond what sources support

## Confidentiality and sensitive content

- Preserve the user's confidentiality expectations. Do not broaden distribution scope.
- When sources include credentials, tokens, PII, HR, legal, or customer-identifiable data:
  - Do not repeat secrets verbatim unless the user asks for a full-fidelity internal record
  - Prefer redaction or generalization (`[redacted credential]`, `[customer name withheld]`) when producing shareable minutes
  - Note in Source Notes when content was redacted at your discretion and offer a fuller internal variant if needed
- Do not infer or add sensitive details that are not in the sources.

## Optional downstream actions

When the user explicitly asks after minutes are returned:

1. **Ticket creation** — offer formatted action items suitable for copy-paste; use host task-capture tooling when available
2. **Publish** — offer markdown or wiki-ready output; do not publish without explicit confirmation
3. **Email** — draft a cover note separately if asked; do not send without explicit confirmation

This skill drafts minutes first. Downstream workflows are separate unless the user requests them in the same or a follow-up message.
