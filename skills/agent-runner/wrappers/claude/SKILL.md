---
name: agent-runner
description: dispatch independent coding, debugging, research, or repository tasks to isolated subagents and run them concurrently, then verify and integrate their results. use when a request contains two or more separable workstreams, multiple unrelated failures, independent files or subsystems, parallel read-only audits, or explicit requests to delegate work across agents.
---

# agent-runner (Claude Code)

Read the shared skill first — it is the source of truth for partitioning, isolation,
task packets, integration, and safety gates:

`../../../.shared/skills/agent-runner/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/agent-runner/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh agent-runner

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name agent-runner --source skills/agent-runner --overwrite
```

If bootstrap source exists at `skills/agent-runner/`, use that path for `--source`
only.

## Dispatch mechanics in Claude Code

Use Claude Code's native subagent/task facility:

1. Partition work and build complete task packets per the shared skill and
   `<SKILL_ROOT>/references/task-packet.md`.
2. Put multiple independent agent invocations in the **same assistant turn** or
   concurrent tool batch — never launch one, wait, and then launch the next.
3. When agents will write, prefer separate worktrees or explicitly disjoint path
   ownership.
4. Pass a complete prompt to each invocation; do not rely on inherited chat history.

When subagent completion notifications include `total_tokens` and `duration_ms`, note
them if comparing efficiency across dispatch runs.

## Claude.ai (no Claude Code CLI)

If you are on Claude.ai rather than Claude Code: no parallel subagents. Report that
concurrent isolated dispatch is unavailable and run work sequentially in the parent
session, or ask the user to switch to Claude Code.

## Wrapper policy

- Edit cross-tool orchestration behavior in `../../../.shared/skills/agent-runner/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
