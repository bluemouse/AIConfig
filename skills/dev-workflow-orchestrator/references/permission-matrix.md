# Permission Matrix

Per-phase permissions define what each phase is allowed to do. The principle of least privilege applies: each phase gets only the permissions it needs.

## Matrix

| Phase | Read source | Write source | Write artifacts | Run tests/build | Commit | Push | Deploy/migrate |
|-------|------------|-------------|-----------------|-----------------|--------|------|----------------|
| Clarify | yes | no | yes (`02-*.md` only) | no | no | no | no |
| Research | yes | no | yes (artifacts only) | no | no | no | no |
| Plan | yes | no | yes (artifacts only) | no | no | no | no |
| Implement | yes | yes (per plan) | yes | yes | no | no | no |
| Code Review | yes | yes (fixes only) | yes | yes | no | no | no |
| Commit | yes | no | yes (commit record) | no | yes (staged only) | no (unless asked) | no |

## Principles

1. **Doer/checker = write/read split.** In each loop, the doer writes (research-guide writes the report, plan-executor writes code) and the checker reads (research-reviewer reads the report, implementation-auditor reads the code). The checker never writes the thing it's checking.

2. **Write permission expands forward, then contracts at Commit.** Research and Plan are read-only. Implement and Code Review can write source. Commit can only commit. Least privilege per phase.

3. **Subagents inherit the phase's mode.** If advisory-council dispatches subagents during Research, those subagents are also read-only. If plan-executor dispatches subagents during Implement, those subagents can write source per the plan.

## Mode enforcement

Mode is enforced by two layers:

1. **Orchestrator skill instructions (host-neutral):** The orchestrator skill contains per-phase mode instructions that tell the agent what it's allowed to do. This is the prevention layer.

2. **Validation scripts (deterministic):** `check_post_phase.py` runs after each phase step to verify only allowed artifacts were written and no forbidden files were touched. This is the detection layer.

Together: the skill prevents most violations, the scripts catch the rest. This is defense in depth.

## Forbidden actions (all phases unless explicitly allowed)

- No commits except in Commit phase.
- No pushes unless the user explicitly asks.
- No deploys or migrations unless the user explicitly asks.
- No editing of another phase's artifacts.
- No editing of the run manifest by any phase (only the orchestrator).
- No destructive git commands (force-push, reset --hard, etc.) unless the user explicitly asks.
