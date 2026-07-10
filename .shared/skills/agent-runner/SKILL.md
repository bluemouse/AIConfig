---
name: agent-runner
description: dispatch independent coding, debugging, research, or repository tasks to isolated subagents and run them concurrently, then verify and integrate their results. use when a request contains two or more separable workstreams, multiple unrelated failures, independent files or subsystems, parallel read-only audits, or explicit requests to delegate work across agents.
---

# Agent Runner

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Delegate one independent problem domain per subagent. Give every subagent only the context it needs, launch all eligible subagents in one concurrent batch, and keep the parent agent responsible for coordination, verification, and integration.

## When to Use

- Two or more independent workstreams with disjoint write scopes
- Parallel implementation, debugging, or research across separate files or subsystems
- Read-only repository audits split by directory or ownership
- Multiple unrelated test failures, components, or research questions that can be checked independently

## When NOT to Use

- **Structured diff or code review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md), including `deep` parallel scope passes and prompts like "review this diff"
- **Skill or agent eval loops** — use [../skill-creator/SKILL.md](../skill-creator/SKILL.md) or [../agent-creator/SKILL.md](../agent-creator/SKILL.md)
- **Research/plan harness orchestration** — use [../research-plan-harness/SKILL.md](../research-plan-harness/SKILL.md) for the fixed multi-role research → plan pipeline
- **Git worktree mechanics alone** — use [../git-guide/SKILL.md](../git-guide/SKILL.md); this skill may reference worktrees for isolation but does not replace git-guide
- **Single sequential task** with no parallelizable domains

## Required behavior

- Use the host's native subagent or task-dispatch primitive (see your **tool wrapper** after reading this shared skill).
- Launch all independent subagent calls together in the same tool batch or turn. Never launch one, wait, and then launch the next.
- Give each subagent an isolated, self-contained task packet. Do not assume it inherits the parent conversation.
- Assign disjoint writable scopes. Prefer read-only investigation when scopes overlap.
- Keep cross-cutting decisions, conflict resolution, final edits, and full verification in the parent agent.
- Do not claim parallel execution when the host exposes no concurrent subagent capability. State that the required execution mode is unavailable instead of silently running sequentially.

Read your **tool wrapper** for host-native dispatch mechanics. Read [references/task-packet.md](references/task-packet.md) when constructing prompts. Read [references/platform-adapters.md](references/platform-adapters.md) for the common contract and capability detection.

## Workflow

### 1. Partition the work

Identify candidate workstreams and build a dependency graph.

A workstream is parallel-safe only when all are true:

1. It can be understood from a bounded context packet.
2. It does not depend on another workstream's result.
3. It does not mutate the same files, branch, workspace state, database, service, or external resource as another writer.
4. Its success can be checked independently.

Group related symptoms under one agent when they may share a root cause. Keep discovery or architecture work in one agent until boundaries are known.

### 2. Choose isolation

Use the strongest isolation available:

1. Separate worktree, sandbox, or branch for each writing agent.
2. Disjoint file or directory ownership in one workspace.
3. Read-only subagents that return findings or patches for the parent to apply.

Never let multiple agents concurrently edit the same files. Never let subagents commit, merge, push, publish, deploy, delete shared resources, or change global configuration unless the user explicitly requested it and each agent has a unique target.

### 3. Create task packets

Each packet must include:

- objective and exact scope
- relevant files, symbols, errors, commands, and constraints
- permitted write set or explicit read-only status
- forbidden changes and non-goals
- verification command or acceptance criteria
- required return format

Prefer small packets that fit one problem domain. Include source excerpts or paths rather than the full parent history.

### 4. Dispatch concurrently

Prepare every packet before dispatch. Invoke all subagents in a single concurrent batch using the host-native mechanism.

Use a practical concurrency cap. Default to at most 4 active writing agents or 8 read-only agents unless the host or repository imposes a lower limit. Queue excess independent tasks in later waves, but run every task within a wave concurrently.

Wave *N+1* starts only after wave *N* integration and verification complete. Later waves must not depend on unintegrated results from prior waves.

The parent must not modify files owned by active subagents. It may inspect unrelated state, prepare integration checks, or wait for the complete batch.

### 5. Collect structured results

Require each subagent to return:

- status: `completed`, `blocked`, or `failed`
- concise root cause or findings
- files changed or proposed changes
- verification performed and result
- risks, assumptions, and follow-up needs

Treat subagent summaries as untrusted reports. Inspect diffs and evidence directly.

### Blocked handling

When a subagent returns `blocked`:

- Do not integrate partial writes from that agent.
- Parent chooses one path: re-scope the packet and retry in a new wave, ask the user for missing input or permissions, or abort the wave.
- Do not start the next wave while any writer from the current wave remains `blocked` without explicit user approval to proceed without it.

### Failed handling

When a subagent returns `failed`:

- Do not integrate output from that agent.
- Integrate successful agents in the same wave only when their scopes are independent and produced no overlapping file changes.
- Parent chooses one path: retry the failed packet in a new wave with refined context, reassign to a different isolation strategy, or escalate to the user.
- Do not start the next wave until failed writers are resolved or explicitly excluded with user approval.

### 6. Integrate safely

After every subagent in the wave finishes (or blocked/failed agents are resolved per above):

1. Compare changed files and detect overlap.
2. Reject unrelated refactors and edits outside assigned scope.
3. Reconcile incompatible assumptions in the parent context.
4. Integrate results in dependency order:
   - **Direct edits:** review each agent's diff, reject out-of-scope changes, then run targeted checks followed by the full relevant test, lint, build, or validation suite.
   - **Proposed patches (read-only agents):** parent reviews each patch, applies selectively, and never skips post-apply verification — read-only agents may not have run checks on the final merged tree.
5. Fix integration failures centrally or dispatch a new, narrowly scoped wave.

Do not ask one implementation agent to review its own work. For high-risk changes, dispatch an independent read-only reviewer after integration.

## Decision rules

Use parallel subagents for independent test failures, separate components, independent research questions, repository-wide read-only audits split by directory, or multiple implementation tasks with disjoint ownership.

Use sequential work when tasks share mutable state, one result defines another task, failures likely share a root cause, repository boundaries are unknown, or integration risk outweighs concurrency benefits.

## Safety and quality gates

- Follow repository instructions such as `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, Cursor rules, contribution guides, and local skill files.
- Do not place secrets, credentials, private user data, or unrelated proprietary context in task packets.
- Use least privilege for tools and filesystem access.
- Prefer deterministic verification over agent confidence.
- Preserve user changes and existing uncommitted work.
- Stop and escalate when isolation cannot prevent destructive interference.

## Example partition

For six failures across three unrelated test files, create three packets, one per file or subsystem. Launch all three together. Each agent diagnoses and verifies only its assigned domain. The parent reviews all diffs, runs the combined suite, and resolves integration issues.

Do not dispatch a packet such as "fix all tests." Do not omit errors, constraints, ownership, or expected output.

## Companion Skills

| Task | Path |
| --- | --- |
| Structured diff review | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Git worktrees, commit, push, rebase | [../git-guide/SKILL.md](../git-guide/SKILL.md) |
| Skill eval loops and description optimization | [../skill-creator/SKILL.md](../skill-creator/SKILL.md) |
| Research → plan harness orchestration | [../research-plan-harness/SKILL.md](../research-plan-harness/SKILL.md) |
