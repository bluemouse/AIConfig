# Bundles

This document defines the workflow bundles for a classic software development lifecycle:

```text
clarify -> research -> plan -> implement -> test/debug -> QA -> PR
```

Bundles are intentionally stack-neutral. Add language, platform, framework, or domain-specific skills only after a workflow skill has established what kind of technical help is needed.

Canonical bundle membership for tooling lives in [bundles.json](bundles.json). Edit that file first when adding or removing bundle members, then keep the descriptions and tables in this document in sync.

## Bundle composition

[bundles.json](bundles.json) modularizes bundles with two layers:

- **`bases`** — reusable member sets keyed by id. Shared membership (for example the core workflow skills) is defined once in the top-level `bases` array.
- **`bundles`** — installable bundles shown in the installer GUI. Each bundle references zero or more base ids through its `bases` field and may add bundle-specific members in its own `skills`, `agents`, `commands`, and `scripts` lists.

A bundle (or base) may include any combination of four member kinds:

| Field | Description |
| --- | --- |
| `skills` | Skill slugs (installed via the skill mechanism: shared + tool wrappers) |
| `agents` | Agent slugs (installed via the agent mechanism: shared + tool wrappers) |
| `commands` | Command slugs (installed via the command mechanism: shared + tool wrappers) |
| `scripts` | Scripts directory names under `.ai/tools/` (copied verbatim as directory trees) |

Resolved membership for tooling is:

```text
resolved = union(base.<kind> for each referenced base id, for each kind) ∪ bundle.<kind>
```

The extended dev workflow bundle references the `core-dev-workflow` base and lists only its additional skills in `skills`.

### CLI usage

`tools/installer.py` resolves bundle ids the same way as the GUI:

```bash
python tools/installer.py /path/to/project --bundles core-dev-workflow
python tools/installer.py /path/to/project --bundles extended-dev-workflow --override
python tools/installer.py /path/to/project --bundles core-dev-workflow --skills cpp-coding
python tools/installer.py /path/to/project --bundles dev-workflow-harness
```

- `--bundles <id>` selects all members (skills, agents, commands, scripts) from the resolved bundle for install or uninstall.
- Combine with `--skills`, `--agents`, `--commands`, or `--scripts` to add individual items beyond the bundle.
- When no selector is passed, all discovered skills, agents, commands, and scripts are selected.

### Target bundle (dynamic)

The **Target bundle** is not stored in `bundles.json`. It is computed at runtime from members already installed in the destination project:

- GUI: set **Target project**, then toggle **Target bundle** (enabled only when the path is valid and matching installed members exist).
- CLI: pass `--bundles target-bundle` with a `TARGET` path.

Membership is the intersection of:

1. Skills, agents, commands, and scripts found under `<target>/.ai/` (`skills/*/SKILL.md`, `agents/*.md`, `commands/*.md`, `tools/*/`)
2. The same kinds available in this AIConfig repository catalog

```bash
python tools/installer.py /path/to/project --bundles target-bundle
```

## Dev-workflow harness bundle

The **dev-workflow harness** is a bundle (`dev-workflow-harness`) that groups the complete dev-workflow harness as a single unit. It includes the orchestrator plus all phase doer/checker skills, the command, and the validation scripts the orchestrator invokes at runtime:

```bash
python tools/installer.py /path/to/project --bundles dev-workflow-harness
python tools/installer.py /path/to/project --bundles dev-workflow-harness --uninstall
python tools/installer.py /path/to/project --dev-workflow
```

`--dev-workflow` is a CLI alias for `--bundles dev-workflow-harness`. The harness consists of:

- **Skills (11):** `dev-workflow-orchestrator` (the orchestrator) plus the phase doers and checkers — `prompt-clarifier`, `research-guide` / `research-reviewer`, `plan-guide` / `plan-reviewer`, `plan-executor` / `implementation-auditor`, `finding-resolver` / `code-reviewer`, and `commit-message-writer`.
- **Agents (4):** the four checker agents — `research-reviewer`, `plan-reviewer`, `implementation-auditor`, `code-reviewer` — installed via the agent mechanism (shared `.ai/agents/<name>.md` + tool wrappers). These wrap the checker skills with fresh-context isolation, read-only enforcement, and model pinning for native-mode dispatch.
- **Command (1):** `dev-workflow` — installed via the standard command mechanism (shared + tool wrappers).
- **Validation scripts:** the `.ai/tools/dev-workflow/` tree (including the `checks/` subpackage) — copied verbatim to `<target>/.ai/tools/dev-workflow/`.

The bundle composes with `--skills`, `--agents`, `--commands`, and other `--bundles` in a single invocation. Use `--override` to replace existing harness paths in the target.

## Core dev workflow bundle

The core bundle is the minimum workflow set a team should rely on for ordinary feature, bug, and product-spec development. Not every skill fires on every task, but every skill covers a responsibility that appears regularly in healthy delivery work.

| Skill | Primary role | Use when |
| --- | --- | --- |
| [prompt-clarifier](../skills/prompt-clarifier/SKILL.md) | Requirement clarification | The request has multiple plausible readings, vague terms, conflicting requirements, or missing decisions that would change the result |
| [research-guide](../skills/research-guide/SKILL.md) | Discovery and requirements shaping | The idea, requirement, or product direction is still unclear |
| [code-professor](../skills/code-professor/SKILL.md) | Codebase learning and documentation | Onboarding, architecture maps, module deep dives, workflow traces, or failure investigation guides are needed |
| [plan-guide](../skills/plan-guide/SKILL.md) | Implementation planning | Requirements, specs, or bug context must become executable tasks |
| [plan-executor](../skills/plan-executor/SKILL.md) | Plan execution | An implementation plan is ready to run in the current working tree |
| [test-driven-dev-guide](../skills/test-driven-dev-guide/SKILL.md) | Test-first implementation | The change should be developed through red-green-refactor |
| [debugging-guide](../skills/debugging-guide/SKILL.md) | Root-cause debugging | There is a defect, failing test, build failure, crash, regression, or flaky behavior |
| [implementation-auditor](../skills/implementation-auditor/SKILL.md) | Requirement and evidence audit | Code changes need proof against acceptance criteria before claiming done |
| [code-reviewer](../skills/code-reviewer/SKILL.md) | Structured diff review | A diff, commit, branch, or PR needs reviewer-side risk analysis |
| [commit-message-writer](../skills/commit-message-writer/SKILL.md) | Commit narrative | A Conventional Commit message is needed from staged, unstaged, or committed changes |
| [git-guide](../skills/git-guide/SKILL.md) | Git mechanics | Staging, committing, pushing, rebasing, resolving conflicts, or worktrees are needed |
| [pull-request-guide](../skills/pull-request-guide/SKILL.md) | PR authoring | The change needs a clear review-ready PR/MR description, testing evidence, or split advice |

## Extended dev workflow bundle

The extended bundle adds quality gates, collaboration support, parallel execution, and host-specific delivery. Use it for high-risk work, cross-team work, complex plans, expensive changes, ambiguous research, or formal review processes.

The extended bundle includes the full core bundle plus these additional skills:

| Skill | Primary role | Use when |
| --- | --- | --- |
| [research-reviewer](../skills/research-reviewer/SKILL.md) | Research readiness audit | A research report must be validated before planning starts |
| [plan-reviewer](../skills/plan-reviewer/SKILL.md) | Plan readiness audit | A plan must be checked before execution by a developer or AI agent |
| [advisory-council](../skills/advisory-council/SKILL.md) | Multi-perspective decision deliberation | Competing options, policy disputes, or explicit council/panel requests need ranked recommendations with dissent |
| [devil-advocate](../skills/devil-advocate/SKILL.md) | Adversarial proposal review | A single proposal needs red-teaming, show-stopper analysis, and a proceed/rework/reject verdict |
| [agent-runner](../skills/agent-runner/SKILL.md) | Parallel workstream coordination | Independent research, implementation, debug, or audit tasks can run concurrently |
| [minutes-writer](../skills/minutes-writer/SKILL.md) | Meeting and decision record | Engineering discussions need grounded minutes, decisions, and action items |
| [techdoc-reviewer](../skills/techdoc-reviewer/SKILL.md) | Documentation review and synchronization | Reader-facing docs must be verified against code, tests, and configuration, or updated after a behavior change |
| [github-guide](../skills/github-guide/SKILL.md) | GitHub delivery | A GitHub PR or review must be created, updated, commented on, or resolved through `gh` / `gh api` |

## Choosing Core vs Extended

Use the core bundle for normal work when:

- The requirement is small or moderately sized.
- The system impact is local and reversible.
- The team can review the result directly from the diff and tests.
- The plan does not require formal sign-off.

Use the extended bundle when:

- The product direction is ambiguous or politically important.
- The change affects security, privacy, compliance, data migration, public APIs, production reliability, or cross-team contracts.
- The plan will be executed by someone who was not part of the original discussion.
- Multiple independent subsystems, test failures, or research tracks can be split safely.
- A formal PR process, GitHub inline review posting, or meeting record is required.

When extending beyond core, add individual extended-bundle skills as the work warrants:

- [research-reviewer](../skills/research-reviewer/SKILL.md) when research will drive expensive or irreversible work.
- [plan-reviewer](../skills/plan-reviewer/SKILL.md) when execution risk is higher than normal.
- [advisory-council](../skills/advisory-council/SKILL.md) when a consequential decision has competing perspectives or needs structured dissent.
- [devil-advocate](../skills/devil-advocate/SKILL.md) when one proposal must be pressure-tested before commitment.
- [agent-runner](../skills/agent-runner/SKILL.md) only when workstreams are genuinely independent.
- [minutes-writer](../skills/minutes-writer/SKILL.md) when decisions are made in meetings or chat and need a durable record.
- [github-guide](../skills/github-guide/SKILL.md) only when the delivery host is GitHub and `gh` or `gh api` mechanics are part of the task.

## Maintenance

1. Update shared skill sets in the `bases` array in [bundles.json](bundles.json) when core or other reusable membership changes.
2. Update bundle-specific `skills` only for additions beyond referenced bases.
3. Update bundle descriptions and per-skill tables in this file.
4. Operational workflow guidance that uses these bundles lives in [dev-workflow.md](../dev-workflow.md).
