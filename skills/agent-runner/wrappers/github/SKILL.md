---
name: agent-runner
description: dispatch independent coding, debugging, research, or repository tasks to isolated subagents and run them concurrently, then verify and integrate their results. use when a request contains two or more separable workstreams, multiple unrelated failures, independent files or subsystems, parallel read-only audits, or explicit requests to delegate work across agents.
---

# agent-runner (GitHub Copilot)

Read the shared skill first — it is the source of truth for partitioning, isolation,
task packets, integration, and safety gates:

`../../../.shared/skills/agent-runner/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/agent-runner/`. Resolve paths to
`references/` from that directory.

This wrapper adds **GitHub Copilot / VS Code-native** execution. Copilot Chat does not
expose parallel subagents like Cursor or Claude Code — adapt dispatch accordingly.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Reload VS Code** after installing or editing skills so Copilot rediscovers them

## Install or refresh agent-runner

From repo root (or ask the user to run in a terminal):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name agent-runner --source skills/agent-runner --overwrite
```

If bootstrap source exists at `skills/agent-runner/`, use that path for `--source`
only.

## Dispatch mechanics in GitHub Copilot

Use the available Copilot coding-agent, custom-agent, or agent-session facility when it
supports multiple simultaneous sessions:

1. Partition work and build complete task packets per the shared skill and
   `<SKILL_ROOT>/references/task-packet.md`.
2. Assign separate issues, task sessions, branches, or workspaces when agents write.
3. Start all independent sessions before awaiting results.
4. In IDE modes that expose a subagent tool, invoke all independent calls in one batch.

If the active Copilot surface supports only a single agent session, report that concurrent
isolated dispatch is unavailable. Do not emulate parallelism with sequential prompts.
For read-only investigation, you may run packets sequentially in one session while still
following the shared integration and verification rules.

## Wrapper policy

- Edit cross-tool orchestration behavior in `../../../.shared/skills/agent-runner/`
- Edit Copilot-specific mechanics here
- Do not duplicate the full shared skill body in this file
