---
name: agent-runner
description: "dispatch independent coding, debugging, research, or repository tasks to isolated subagents and run them concurrently, then verify and integrate their results. use when a request contains two or more separable workstreams, multiple unrelated failures, independent files or subsystems, parallel read-only audits, or explicit requests to delegate work across agents."
---

# agent-runner (Cursor)

Read the shared skill first — it is the source of truth for partitioning, isolation,
task packets, integration, and safety gates:

`../../../.shared/skills/agent-runner/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/agent-runner/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for
workflow content and output structure.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under
  `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the
  agent rediscovers them

## Install or refresh agent-runner

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name agent-runner --source skills/agent-runner --overwrite
```

If bootstrap source exists at `skills/agent-runner/`, use that path for `--source`
only.

## Dispatch mechanics in Cursor

Use Cursor's **Task tool** for concurrent isolated dispatch:

1. Partition work and build complete task packets per the shared skill and
   `<SKILL_ROOT>/references/task-packet.md`.
2. In a **single message**, issue one Task call per independent workstream — multiple
   tool calls in one turn, not sequential calls.
3. Use `subagent_type: "generalPurpose"` unless a narrower type clearly fits the packet.
4. Paste the full task packet into each Task `prompt`; subagents do not inherit parent
   chat history.
5. Set `run_in_background: true` when the host allows it and you need to continue
   coordinating while subagents run.
6. **Always await every Task in the wave** — poll with `Await` or equivalent if
   background — before starting shared-skill §6 Integrate safely. Never integrate
   while any subagent may still be writing.
7. Use isolated worktrees or sandboxes when offered; otherwise enforce disjoint write
   sets per packet.
8. If the current Cursor mode exposes only one foreground agent and no concurrent Task
   primitive, report that concurrent isolated dispatch is unavailable — do not claim
   compliance or silently run sequentially.

### Task prompt additions (Cursor)

Append to each packet:

```
You are an isolated subagent. You do not inherit the parent conversation.

Use Read/Grep/Shell as needed within your assigned scope before changing anything.

Return exactly the structured status block from your task packet: Status, Findings,
Changes, Verification, and Risks.
```

## Wrapper policy

- Edit cross-tool orchestration behavior in `../../../.shared/skills/agent-runner/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
