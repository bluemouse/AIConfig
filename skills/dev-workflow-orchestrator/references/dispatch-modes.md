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

Evaluate the dispatch mode **once per run** — at phase 0 (Clarify) for full
runs, or at bootstrap for command-bootstrapped runs (which skip phase 0; the
bootstrap commands record `Dispatch mode: delegated` in the manifest, since the
command host's subagent capability is unknown at bootstrap time). Record the selected
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
- Prior-round review paths (for loop rounds > 1, all `-r1` … `-r<N>` artifact paths).

The orchestrator reads the verdict from the **on-disk artifact** (`## Verdict` heading),
not from the subagent's return message. The subagent's return message is a convenience
(status + summary); the artifact is the source of truth.

## Delegated/simulated-mode dispatch

In delegated or simulated mode, the orchestrator invokes the checker skill as a named pass
with explicit input/output paths — the current behavior before the agent conversion. The
checker runs in the orchestrator's context (no fresh context), but the artifact contract,
loop contracts, and validation scripts all hold unchanged.

**Why doers stay in-context:** doer passes (research-guide, plan-guide, plan-executor,
code-review-resolver) always run in the orchestrator's context in every mode. This is
deliberate: doers own integration and state continuity — they write the artifacts the
orchestrator routes on, and moving them behind subagent returns adds round-trip latency
to every loop round for marginal fresh-context benefit. Implement-phase parallelism
lives *inside* plan-executor via agent-runner (invisible to the orchestrator); Research
may use advisory-council subagents internally. The fresh-context benefit is spent where
it matters most: checkers, whose value is independence from the author's reasoning.

## Fallback on spawn failure

If a subagent spawn fails (e.g., the pinned model is unavailable on the host), the
orchestrator records the failure in the dispatch log and falls back to delegated mode for
that checker. Do not silently retry or block the workflow.

## Fallback on a hung or failed checker

A checker subagent that spawns successfully but returns no verdict within the host's
bounded window — or returns `failed` without writing its output artifact — is
treated as a **failed dispatch**, not as "still running." Handle it the same way as
spawn failure: record the failure (cause: `timeout` or `failed`) in the dispatch
log and fall back to delegated mode for that checker. Do not silently retry or block
the workflow. This mirrors the hung-subagent semantics of the `agent-runner`
skill (doer-side parallel dispatch); the checker side never re-dispatches a hung
subagent with the same packet.
