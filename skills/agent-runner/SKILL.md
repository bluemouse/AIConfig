---
name: agent-runner
description: dispatch independent coding, debugging, research, or repository tasks to isolated subagents and run them concurrently, then verify and integrate their results. use when a request contains two or more separable workstreams, multiple unrelated failures, independent files or subsystems, parallel read-only audits, or explicit requests to delegate work across agents. does not trigger on active merge/rebase integration (git-merge-guide) or structured diff review (code-reviewer).
---

# Agent Runner

`<SKILL_ROOT>` is the directory containing this `SKILL.md`; `references/` paths resolve from there. Delegate one independent problem domain per subagent, give each only the context it needs, launch all eligible subagents in one concurrent batch, and keep the parent responsible for coordination, verification, and integration.

## When to Use

Two or more separable workstreams: disjoint write scopes, parallel implementation/debugging/research across separate files or subsystems, read-only audits split by directory, independently checkable failures or questions, or parallelizable waves for [../plan-executor/SKILL.md](../plan-executor/SKILL.md).

This skill covers dispatch mechanics only — route the work itself elsewhere:

- Diff or code review, including `deep` parallel passes and "review this diff" → [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- Skill or agent eval loops → [../skill-creator/SKILL.md](../skill-creator/SKILL.md) or [../agent-creator/SKILL.md](../agent-creator/SKILL.md)
- Dev-workflow orchestration → [../dev-workflow-orchestrator/SKILL.md](../dev-workflow-orchestrator/SKILL.md)
- Worktree mechanics alone → [../git-guide/SKILL.md](../git-guide/SKILL.md)
- Active local merge/rebase integration → [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md); while active, allow only read-only investigation here

Prefer sequential execution when tasks share mutable state, one result defines another task, failures likely share a root cause, repository boundaries are unknown, or integration risk outweighs concurrency benefits.

## Required behavior

- Use the host's native subagent or task-dispatch primitive (see `## Tool notes`).
- Launch all independent subagent calls together in the same tool batch or turn; never launch one, wait, and then launch the next.
- Give each subagent an isolated, self-contained task packet; do not assume it inherits the parent conversation.
- Assign disjoint writable scopes; prefer read-only investigation when scopes overlap.
- Keep cross-cutting decisions, conflict resolution, final edits, and full verification in the parent.
- If the host exposes no concurrent subagent capability, say so — never claim parallel execution while silently running sequentially.

Read [references/task-packet.md](references/task-packet.md) when constructing prompts and [references/platform-adapters.md](references/platform-adapters.md) for the common contract and capability detection.

## Workflow

### 1. Partition the work

Build a dependency graph. A workstream is parallel-safe only when all are true:

1. It can be understood from a bounded context packet.
2. It does not depend on another workstream's result.
3. It does not mutate the same files, branch, workspace state, database, service, or external resource as another writer.
4. Its success can be checked independently.

Group related symptoms under one agent (possible shared root cause); keep discovery or architecture work in one agent until boundaries are known.

### 2. Choose isolation

Use the strongest isolation available:

1. Separate worktree, sandbox, or branch for each writing agent.
2. Disjoint file or directory ownership in one workspace.
3. Read-only subagents that return findings or patches for the parent to apply.

Never let multiple agents concurrently edit the same files. Never let subagents commit, merge, push, publish, deploy, delete shared resources, or change global configuration unless the user explicitly requested it and each agent has a unique target.

### 3. Create task packets

Build each packet per the template in [references/task-packet.md](references/task-packet.md): objective and exact scope, relevant files/symbols/errors/commands/constraints, permitted write set or read-only status, forbidden changes and non-goals, verification command or acceptance criteria, an instruction to run verification with output-limiting flags and return summarized results (never full command logs), and the required return format. Prefer small packets that fit one problem domain; include source excerpts or paths, not the full parent history.

Subagents cannot ask the user anything, so every ambiguity left in a packet becomes a silent assumption or a `blocked` return. Settle unclear objectives, scope, or acceptance criteria in the parent session with [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) before dispatching.

### 4. Dispatch concurrently

Prepare every packet before dispatch; invoke all subagents in one concurrent batch via the host-native mechanism. Cap at 4 active writing agents or 8 read-only agents (lower if the host or repository requires); queue excess tasks in later waves, running every task within a wave concurrently. Wave *N+1* starts only after wave *N* integration and verification complete, and must not depend on unintegrated results. The parent never modifies files owned by active subagents.

### 5. Collect structured results

Require each subagent to return:

- status: `completed`, `blocked`, or `failed`
- concise root cause or findings
- files changed or proposed changes
- verification performed and result
- risks, assumptions, and follow-up needs

Treat subagent summaries as untrusted reports. Inspect diffs and evidence directly.

### Blocked, failed, and hung subagents

- `blocked`/`failed` output and partial writes are not integrable; other agents in the same wave integrate only when scopes are independent with no overlapping file changes. The parent picks one path — re-scope or refine the packet and retry in a new wave, reassign the isolation strategy, ask the user for missing input or permissions, or abort/escalate — and starts the next wave only when every blocked or failed writer is resolved or the user explicitly approves proceeding without it.
- A hung subagent (no verdict within the host's bounded window) is `failed` with cause `timeout`, not "still running." Re-dispatch the packet in a new wave with an explicit sync-terminal-mode verification instruction (Cursor recovery in `## Tool notes`).

### 6. Integrate safely

After every subagent in the wave finishes (or blocked/failed agents are resolved per above):

1. Compare changed files for overlap; reject unrelated refactors and edits outside assigned scope.
2. Reconcile incompatible assumptions in the parent context.
3. Integrate in dependency order. Direct edits: review each diff, then targeted checks followed by the full relevant test/lint/build suite. Proposed patches (read-only agents): apply selectively and never skip post-apply verification — read-only agents may not have run checks on the final merged tree.
4. Fix integration failures centrally or dispatch a new, narrowly scoped wave.

Never ask one implementation agent to review its own work; for high-risk changes, dispatch an independent read-only reviewer after integration.

## Safety and quality gates

- Load and follow repository instructions before creating packets (locations and precedence: [references/platform-adapters.md](references/platform-adapters.md)); never place secrets, credentials, private user data, or unrelated proprietary context in task packets.
- Use least privilege; prefer deterministic verification over agent confidence.
- Preserve user changes and existing uncommitted work; stop and escalate when isolation cannot prevent destructive interference.

Never dispatch a packet such as "fix all tests," and never omit errors, constraints, ownership, or expected output.

## Tool notes

### Claude Code

Partitioning, packets, batching, and isolation follow "Required behavior" and [references/task-packet.md](references/task-packet.md). If completion notifications include `total_tokens` and `duration_ms`, note them when comparing dispatch efficiency. On Claude.ai (no Claude Code CLI), no parallel subagents are available — report that concurrent isolated dispatch is unavailable and run work sequentially in the parent session.

### Cursor

Use Cursor's **Task tool** for concurrent isolated dispatch; packets, batching, and isolation follow "Required behavior" and [references/task-packet.md](references/task-packet.md). Use `subagent_type: "generalPurpose"` unless a narrower type clearly fits the packet; set `run_in_background: true` when the host allows it and you need to continue coordinating while subagents run. If the current mode exposes only one foreground agent and no concurrent Task primitive, report that concurrent isolated dispatch is unavailable — do not claim compliance or silently run sequentially.

Hung-subagent recovery: the usual root cause is a subagent that ran a terminating command (build/test/install) in async mode or backgrounded it, then ended its turn waiting for a completion notification that an early/silent exit never produced. Call `get_terminal_output` once on the subagent's terminal id (if exposed) to confirm the early exit — do not poll or `sleep`. Re-dispatch in a new wave with an explicit sync-mode verification instruction (never background builds/tests; disable pagers; prefer non-interactive flags). If the surface exposes no terminal id and no bounded-idle signal, escalate to the user rather than waiting indefinitely.

### GitHub Copilot

Use the available coding-agent, custom-agent, or agent-session facility when it supports multiple simultaneous sessions; packets, batching, and isolation follow "Required behavior" and [references/task-packet.md](references/task-packet.md). If the active surface supports only a single agent session, report that concurrent isolated dispatch is unavailable; do not emulate parallelism with sequential prompts. For read-only investigation, packets may run sequentially in one session while still following the shared integration and verification rules.
