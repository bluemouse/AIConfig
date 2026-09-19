# Requirement Ledger

The requirement ledger is prompt-clarifier's terminal output: the settled
interpretation of the task, produced after the `CHECK` state passes. Inside the
dev-workflow harness it is the Phase 0 artifact (`02-requirement-ledger.md`)
consumed by research-guide; standalone, it is the confirmation summary you carry
into the handoff.

## Required sections

These sections must be present with concrete content. If any is missing, the
clarifier is not done.

```markdown
# Requirement Ledger

## Outcome
<one to three sentences: what the user wants and why>

## Scope
- In scope: <items>
- Out of scope: <items>

## Acceptance criteria
<observable conditions that make the result correct or complete>

## Assumptions
<what was defaulted without explicit user input, with the reason>
```

## Optional sections

Include these only when the clarifier determined they were material for this
task. Omit sections that are not relevant — do not fill them with placeholders.

```markdown
## Definitions
<operational meanings of vague, overloaded, or domain-specific terms>

## Constraints
<technical, legal, compatibility, performance, cost, time, or dependency limits>

## Environment
<runtime, platform, versions, tools, repository, or deployment context>

## Risk and reversibility
<what could cause harm, data loss, publication, spending, or difficult rollback>

## Authority
<what the AI may decide, change, send, publish, delete, or execute without further approval>
```

## Rules

- The ledger is the clarified version of the feature brief. The feature brief (`01-feature-brief.md`) holds the raw prompt; the ledger holds the settled interpretation.
- Required sections must have concrete content, not placeholders.
- Optional sections are included only when the clarifier determined they were material. An absent optional section means "not relevant for this task," not "missing."
- The clarifier's `CHECK` state must pass before the ledger is written: outcome unambiguous, deliverable known, success evaluable, no unresolved contradictions.
- If the clarifier cannot reach `actionable` (e.g., the user cannot provide a required decision), the ledger is marked `blocked` with the specific blocker.

> **Source of truth.** The dev-workflow harness's canonical template lives at
> `skills/dev-workflow-orchestrator/references/requirement-ledger-template.md`
> (installed as `.ai/skills/dev-workflow-orchestrator/references/requirement-ledger-template.md`).
> This file mirrors it so prompt-clarifier is self-contained when installed
> without the orchestrator. Keep the two in sync when the schema changes.
