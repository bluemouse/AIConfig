# Backward Handoff Packet Format

A backward handoff packet carries context from a later phase to an earlier phase when a finding's root cause traces upstream. The packet must carry enough context for the target phase to fix the specific issue without re-doing everything.

## Template

```markdown
# Backward Handoff Packet

## Routing
- From phase: <research | plan | implement | code-review>
- To phase: <research | plan | implement | code-review>  (must be earlier)
- Backward edge count for target phase: <n> of 2
- Created: <ISO timestamp>

## Source finding
- Finding id: <rr-001 | pr-001 | ia-001 | cr-001>
- Severity: <blocker | major | minor>
- Source artifact: <path to the review/audit report>

## Root cause classification
- Classification: upstream
- Why this is not a local defect: <explanation>
- Why the target phase is the root: <explanation — trace to the earliest phase whose artifact is the cause>

## What the target phase must resolve
- Issue: <description>
- Why it matters: <explanation>
- Required fix: <what needs to change in the target phase's artifact>
- Evidence: <file paths, symbols, commands, test output, or report sections>

## Context from the source phase
- What was attempted: <what the source phase tried before classifying as upstream>
- Why local fix is insufficient: <explanation>
- Artifacts to review: <paths to source phase artifacts for context>
```

## Rules

- The `To phase` must be earlier in the pipeline than the `From phase`.
- The `Backward edge count for target phase` must not exceed 2.
- The `Finding id` must reference a real finding in the source artifact.
- The packet is write-once by the discovering checker. The target phase reads it but does not edit it.
- Filename: `back-<from>-<to>-<n>.md` where `<n>` is the sequential number for that from-to pair.
