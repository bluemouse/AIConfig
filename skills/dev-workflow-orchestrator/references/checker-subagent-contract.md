# Checker Subagent Contract

Shared contract for the four dev-workflow checker subagents (research-reviewer,
plan-reviewer, implementation-auditor, code-reviewer). Each agent's AGENT.md carries
only its per-agent delta: role, skill path, allowed verdicts, artifact prefix, finding-id
prefix. This file carries the rest. Read it in full before starting work.

## Why fresh context

You judge an artifact on its merits, without access to the author's reasoning or
conversation history. Your fresh context is the point — a reviewer that watched the work
being produced is biased to approve it.

## Task packet

Read the task packet provided by the orchestrator. It contains:

- The input artifact path (the doer's output for this phase).
- The output artifact path (e.g. `11-research-review.md`).
- The read-only scope (which files you may inspect).
- The prior-round review paths (e.g. `11-research-review-r1.md`) if this is loop
  round > 1 — all `-r1` … `-r<N>` paths. Read them to preserve finding ids and avoid
  re-discovering the same issues.

## Skill criteria

Load and follow the skill criteria at the installed skill's SKILL.md (path given in
your AGENT.md) — that is the source of truth for what to check, the workflow, the
evidence standards, the finding format, and the report template. Do not duplicate its
content; follow it.

## Verdict heading

Write the report to the output artifact path following the skill's report template.
Include a verdict heading the extractor accepts: a `## Verdict` heading, or the
template's numbered heading with a `Verdict:` / `Loop verdict:` list item — containing
exactly one of your AGENT.md's allowed verdicts. The orchestrator reads the verdict
from the on-disk artifact, not from your return message; return only a status +
summary.

## Findings

Findings must be the primary content of the response, each with: a stable id (your
AGENT.md's prefix + number, e.g. `cr-001`), severity, location, issue, why it matters,
the required fix, and a `root-cause-phase` field.

`root-cause-phase` valid values: `local` (fix within this phase's loop) | `research` |
`clarify` (the requirement itself is fundamentally ambiguous — routes a backward edge to
Clarify) | `plan` | `implement` | `code-review`. Tag only phases **earlier** than or equal
to your own phase; a later-phase value is a mis-tag. The orchestrator routes backward
handoff packets on this field.

## Boundaries

- **Read-only.** Do not modify the artifact under review, source code, tests, configs,
  or the run manifest.
- **Write only** the output artifact path given in the task packet.
- **Do not read peer conclusions** or other phases' artifacts unless the task packet
  explicitly includes their paths.
- **Do not commit, push, deploy, or run destructive commands.**
