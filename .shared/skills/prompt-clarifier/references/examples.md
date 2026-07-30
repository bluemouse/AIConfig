# Iterative Clarification Examples

## Example 1: Vague coding request

User: `Make the renderer faster.`

First assessment:
- Outcome is directionally clear.
- "Faster" is undefined.
- Target workload and allowed tradeoffs are blockers.

First question:

```text
I need two decisions before optimizing:

1) Primary target?
   a) Lower average frame time
   b) Reduce worst-frame spikes
   c) Reduce startup or shader-compilation time

2) Allowed tradeoff?
   a) Preserve output exactly (recommended)
   b) Small visual differences are acceptable
   c) Not sure - preserve output exactly
```

User: `1b, and preserve output exactly.`

Updated assessment:
- Performance metric selected.
- Visual fidelity fixed.
- Representative workload and threshold remain blockers.

Follow-up:

```text
Which workload and threshold define success? For example: the city scene at 4K, with p99 frame time below 20 ms.
```

User: `The Vulkan city scene at 1440p; p99 under 16.7 ms on an RTX 4070.`

Confirmation and proceed:

```text
I will optimize worst-frame latency for the Vulkan city scene at 1440p on an RTX 4070, preserve rendering output exactly, and treat p99 below 16.7 ms as success.
```

## Example 2: Overloaded term

User: `Create a secure login flow.`

Do not ask for every security property. First identify context and authority:

```text
Which login flow is this?
  a) Web app using an existing identity provider (recommended)
  b) Native app using an existing identity provider
  c) New username/password authentication system

Also, should I design the flow, implement code, or review an existing implementation?
```

The next round depends on the selected branch. For an existing identity provider, ask provider, framework, redirect model, and acceptance tests. For a new authentication system, surface the higher risk and ask whether that requirement is fixed before proceeding.

## Example 3: Partial answer

User: `Write a migration plan for our database.`

Assistant:

```text
I need three blockers:
1) Source and target database/version?
2) Maximum acceptable downtime?
3) Is rollback required after cutover?
```

User: `Postgres 13 to 16, rollback required.`

Do not repeat all three questions:

```text
Postgres 13 to 16 with rollback is clear. What is the maximum acceptable downtime during cutover?
```

## Example 4: Conflicting requirements

User: `Use no new dependencies, but parse every valid PDF including encrypted and malformed files.`

Assistant:

```text
Those requirements conflict: complete PDF coverage normally requires a mature parser, while using no new dependency limits us to the current implementation. Which priority wins?

  a) No new dependencies; support only the current parser's safe subset
  b) Broad PDF coverage; allow a vetted dependency (recommended)
  c) Keep both constraints and produce a feasibility analysis instead of implementation
```

## Example 5: Ambiguity discovered during work

User asks for a report from supplied metrics. The AI can begin reading the data. During analysis it finds two fields both labeled `revenue`, one gross and one net.

Continue unblocked analysis, but pause any calculation that depends on that definition:

```text
The data contains both gross and net revenue. Which should drive the headline and growth calculation?
  a) Net revenue (recommended for recognized revenue)
  b) Gross billings
  c) Show both with explicit labels
```

Do not discard completed work that does not depend on this choice.

## Example 6: User delegates judgment

User: `Use your judgment; I do not know which format is best.`

Assistant:

```text
I will use a one-page executive summary followed by a detailed appendix because the audience needs both a decision view and supporting evidence. I will proceed unless the source material reveals a conflicting requirement.
```

No extra confirmation is needed for a reversible drafting choice.

## Example 7: Diminishing returns

After two rounds, the objective, scope, constraints, and acceptance criteria are clear. A minor stylistic preference remains unknown.

Do not ask another question. Follow the existing style or a standard default, state it briefly if material, and proceed.
