# Question Patterns

Use these patterns selectively. Ask only questions whose answers can change the work.

## Outcome and intent

- `What should be true when this is finished?`
- `Which decision should this output help you make?`
- `Should I explain, recommend, implement, or verify?`
- `Who will use the result, and what will they do with it?`

## Deliverable

- `Which output do you need: a brief answer, a step-by-step plan, working code, or a reusable document?`
- `Should the result be ready to send, ready to implement, or a draft for review?`
- `Is there an existing format or example I should match?`

## Scope

- `Which components are in scope: A, B, both, or another set?`
- `Should I make the smallest targeted change or refactor the surrounding area too?`
- `What must remain unchanged?`
- `Should this cover the common path only or also these edge cases: ...?`

## Definitions

- `By "secure," which property matters here: confidentiality, integrity, availability, or compliance with a named standard?`
- `What is one example that qualifies and one that does not?`
- `What measurable threshold should I use for "fast"?`
- `Does "user" mean an end user, administrator, API client, or all three?`

## Inputs and sources

- `Which source is authoritative when the documents disagree?`
- `May I use public sources, or only the files you supplied?`
- `Which dataset, repository, branch, account, or environment should I use?`
- `Are any inputs incomplete, synthetic, confidential, or stale?`

## Constraints

- `Which constraint takes priority: compatibility, performance, maintainability, or delivery speed?`
- `May I add dependencies, or must I use the existing stack?`
- `What versions or platforms must be supported?`
- `Is there a hard limit for latency, memory, cost, size, or duration?`

## Acceptance criteria

- `What test or observable result would make you accept this as done?`
- `Should failure return an error, retry, fall back, or continue partially?`
- `Which edge case would be unacceptable to miss?`
- `Do you have expected outputs for one representative input?`

## Environment

- `Which operating system, runtime, framework version, and build runner should I target?`
- `Is this for local development, CI, staging, or production?`
- `Should I follow the repository's current conventions even when a newer approach exists?`

## Risk, reversibility, and authority

- `May I modify files directly, or should I provide a patch for review?`
- `May I send or publish the result, or only draft it?`
- `Is deletion allowed, and is there a rollback or backup?`
- `What spending, production, or external-communication limit requires approval?`

## Conflict resolution

Use this structure:

```text
I found a conflict:
- Requirement A: <requirement and consequence>
- Requirement B: <requirement and consequence>

Which should take priority?
  a) A
  b) B
  c) Use this alternative: <feasible compromise>
```

## Adaptive follow-up

Ask a follow-up only when the previous answer creates a necessary branch.

Example:

1. `Should this be a diagnosis or an implementation?`
2. If diagnosis: ask what evidence or environment can be inspected.
3. If implementation: ask compatibility, scope, and acceptance-test blockers.

Do not ask both branches in advance.
