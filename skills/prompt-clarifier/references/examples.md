# Iterative Clarification Examples

## Example 1: Conflicting requirements

User: `Use no new dependencies, but parse every valid PDF including encrypted and malformed files.`

Assistant:

```text
Those requirements conflict: complete PDF coverage normally requires a mature parser, while using no new dependency limits us to the current implementation. Which priority wins?

  a) No new dependencies; support only the current parser's safe subset
  b) Broad PDF coverage; allow a vetted dependency (recommended)
  c) Keep both constraints and produce a feasibility analysis instead of implementation
```

## Example 2: Ambiguity discovered during work

User asks for a report from supplied metrics. The AI can begin reading the data. During analysis it finds two fields both labeled `revenue`, one gross and one net.

Continue unblocked analysis, but pause any calculation that depends on that definition:

```text
The data contains both gross and net revenue. Which should drive the headline and growth calculation?
  a) Net revenue (recommended for recognized revenue)
  b) Gross billings
  c) Show both with explicit labels
```

Do not discard completed work that does not depend on this choice.
