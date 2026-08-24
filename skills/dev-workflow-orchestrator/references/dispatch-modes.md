# Dispatch Modes

The orchestrator selects a dispatch mode for checker phases. The mode determines how
checkers run: as isolated subagents with fresh context (native), or as named skill passes
in the orchestrator's context (delegated/simulated).

## Mode selection

| Mode | When | How checkers run |
| --- | --- | --- |
| **Native** | Host exposes a subagent/task primitive that satisfies the `agent-runner` contract (create isolated sessions, submit without waiting, preserve separate context) | Orchestrator spawns the checker agent as a subagent with a complete task packet. Fresh isolated context. Dispatch is by subagent type, not by agent description. |
| **Delegated** | Host has no subagent API but the orchestrator can invoke the checker skill as a named pass | Current behavior. Checker runs in orchestrator context. No fresh context, but artifact contract and validation still hold. |
| **Simulated** | Host has neither (e.g. Copilot Chat interactive with no agent-session) | Same as delegated. Label honestly in the manifest's dispatch log. |

## Capability detection

Before dispatching, inspect available tools for agent, subagent, task, session, worktree,
sandbox, or branch primitives. Prefer a documented native primitive over shelling out to
another assistant. Verify whether multiple calls in one turn are concurrent. Verify whether
isolation is automatic or must be configured. Avoid undocumented flags or invented tool
names.

If the available feature cannot satisfy the `agent-runner` contract (create isolated
sessions, submit without waiting, preserve separate context), report that concurrent
isolated dispatch is unavailable and fall back to delegated mode. Do not label
sequential execution as native mode — use delegated mode and label it honestly.

## Evaluation timing

Evaluate the dispatch mode **once per run**, at phase 0 (Clarify). Record the selected
mode in the manifest's `## Dispatch log` section. Host capability does not change mid-run,
so per-phase re-evaluation adds complexity for no benefit.

## Native-mode dispatch

In native mode, the orchestrator constructs a task packet per checker dispatch and spawns
the checker as a subagent. The task packet includes:

- Objective (one concrete outcome).
- Input artifact path (the doer's terminal artifact).
- Output artifact path (the checker's loop-output artifact).
- Read-only scope (which files the checker may inspect).
- Verdict format (the allowed verdicts for this phase).
- `root-cause-phase` requirement (the checker must include this field on every finding).
- Prior-round review path (for loop rounds > 1, the `-r1` artifact path).

The orchestrator reads the verdict from the **on-disk artifact** (`## Verdict` heading),
not from the subagent's return message. The subagent's return message is a convenience
(status + summary); the artifact is the source of truth.

## Delegated/simulated-mode dispatch

In delegated or simulated mode, the orchestrator invokes the checker skill as a named pass
with explicit input/output paths — the current behavior before the agent conversion. The
checker runs in the orchestrator's context (no fresh context), but the artifact contract,
loop contracts, and validation scripts all hold unchanged.

## Fallback on spawn failure

If a subagent spawn fails (e.g., the pinned model is unavailable on the host), the
orchestrator records the failure in the dispatch log and falls back to delegated mode for
that checker. Do not silently retry or block the workflow.
