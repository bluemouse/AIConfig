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
- **`bundles`** — installable bundles shown in the installer GUI. Each bundle references zero or more base ids through its `bases` field and may add bundle-specific members in its own `skills`, `agents`, `commands`, and `guidelines` lists.

A bundle (or base) may include any combination of four member kinds:

| Field | Description |
| --- | --- |
| `skills` | Skill slugs (installed as single-root copies under `.agents/skills/<name>/`) |
| `agents` | Agent slugs (installed as dual-target copies: `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md`) |
| `commands` | Command slugs (installed as command-skills under `.agents/skills/cmd-<name>/` with `disable-model-invocation: true`) |
| `guidelines` | Guideline names (installed as skill packages under `.agents/skills/guidelines-<name>/`) |

Guidelines change agent behavior in the target, so they stay out of the no-selector default — but a bundle may carry them via its `guidelines` list, making the bundle selection itself the deliberate choice. The dynamic target bundle carries them too, mapping installed `guidelines-<name>` packages back to their guideline names. Guidelines remain individually selectable via `--guidelines` (CLI) or the Guidelines panel (GUI). Guidelines install as skill packages (`.agents/skills/guidelines-<name>/SKILL.md`) and activate through ordinary skill discovery.

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

- `--bundles <id>` selects all members (skills, agents, commands, and guidelines) from the resolved bundle for install or uninstall.
- Combine with `--skills`, `--agents`, `--commands`, or `--guidelines` to add individual items beyond the bundle.
- When no selector is passed, all discovered skills, agents, and commands are selected (guidelines never enter the default).
- Bundle membership is the **listed** set; at install time the dependency closure (below) expands it, reporting each auto-selected dependency under `Also selecting (dependencies):`. Guidelines are outside the dependency map, so bundle-carried guidelines never trigger closure expansion.

### Dependency map (auto-selection)

`tools/dependencies.json` is the **single source of truth** for the
dependency edges of the current catalog structure (skills, commands,
agents). Selecting a member automatically selects its transitive skill
closure at **install** time.

**Goal.** A dependency edge exists to prevent an incomplete install: if A
is installed into a user's project without a member A depends on, A has a
functional gap — an instruction in its body points at something that is
not there. The map is the mechanism that closes every such gap at install
time, so an installed member is always fully functional in the target.

**Definition.** A depends on B when A's own workflow *requires* B —
unconditionally or in a stated situation — to complete A's task: a
`Follow`/`apply`/`start with`/`switch to`/`hand off to` step inside a
procedure, a stop-and-route guard, or an operational link into B's
`references/`. The requirement may be conditional or situational; what
makes it a dependency is that in the situations it names, the task cannot
finish without B. A **scope boundary** is not a dependency: "When NOT to
use A → use B" hands B a *different* task — A stands down, and B triggers
on that task by its own description. Most cross-skill markdown links are
boundaries of that kind, which is why the map is authored explicitly and
never derived from a link scan.

**Evaluation.** Edges are judged against the member bodies by
`tools/test_installer_dependencies.py`, in two directions: every map edge
must have a body reference in the dependent's source (forward — catches
typos and stale entries), and every curated load-bearing body link class
must have a map edge (reverse — catches missing dependencies).

- **Schema:** `{"skills": {name: {"depends": [...]}}, "commands": {...},
  "agents": {...}}` — every `depends` target must be a discovered plain
  skill; unknown, misspelled, `guidelines-`-prefixed, or `cmd-`-prefixed
  targets are install-time errors naming the edge.
- **Edge kinds:** skill → skill, command → skill, agent → skill (a name
  that exists as both skill and agent always means the skill, since
  targets are skills by definition). Edges anchored only by a routing-class
  body link, or requirement phrasings outside the curated classes
  ("live in", "see X", "per X", "via X", arrow-routing rows), are deliberate
  over-inclusion: they satisfy the forward check but are exempt from the
  reverse curation, so removing one changes install sets without failing
  the suite.
- **Install-only:** uninstall stays exactly-what-you-selected — the
  closure applies only to install selections and `--dry-run` previews the
  expanded set.
- **All entry points route through the same resolution** (CLI explicit
  names, bundles, GUI Install press).
- **Drift protection:** `tools/test_installer_dependencies.py` runs the
  two-directional consistency check described under **Evaluation** above.
  When adding a member with a real runtime dependency, add its edges here
  in the same change.

#### Selection dynamics

The map drives the full selection lifecycle, not just install-time
expansion. Four behaviors, all reading the same `tools/dependencies.json`:

- **GUI auto-check.** Checking a member visibly checks its transitive
  dependency checkboxes — the panel state always equals the selection
  that would install (install mode only).
- **GUI cascade deselect.** Unchecking a dependency deselects every
  checked member that transitively depends on it. Unchecking a
  non-dependency cascades nothing.
- **CLI accounting.** Install expansion reports each auto-selected
  dependency in the operation output as
  `Also selecting (dependencies):` lines — the expansion is never
  silent. The default install-all path (no selectors) resolves a full
  closure already, so it prints no accounting lines.
- **Orphan report.** After an uninstall removes the named members, the
  operation output lists now-orphaned installed skills — skills no
  remaining installed member depends on — under
  `No longer needed by any installed member (remove with --skills <name>):`.
  A `--dry-run` uninstall previews the same list from the would-be-removed
  set (under the would-be heading `Would be no longer needed by any
  installed member …`, matching the dry-run install/remove verbs). "Needed" means map-reachability: a skill stays off the orphan list
  while any remaining installed member's transitive dependency closure
  includes it — even when that member itself was only pulled in by an
  earlier auto-selection, so a partial uninstall of an auto-installed
  group commonly leaves other members of the group shielding each other.
  Remove members outermost-first (dependents before dependencies) to
  surface the full chain — except inside a map cycle (e.g. the
  dev-workflow core: orchestrator ↔ plan-executor), where every member
  is reachable from the other and neither can surface as an orphan
  until the whole cycle is removed. agent-runner is deliberately not a
  member of the cycle — it is a dispatch primitive *under* it
  (plan-executor → agent-runner), so removing the orchestrator and
  plan-executor surfaces it as an orphan. The report is
  informational only: **orphans are never removed automatically** —
  removal is an explicit `--skills <name>` call.
- **Uninstall-mode exception.** Both GUI behaviors are disabled in
  uninstall mode (teardown stays exactly-what-you-selected); the orphan
  report is that mode's dependency awareness instead. Batch toggles
  (bundle check-toggles, Select all/none) reconcile once per batch with
  the closure winning: a checked dependent forces its dependency checked.

### Target bundle (dynamic)

The **Target bundle** is not stored in `bundles.json`. It is computed at runtime from members already installed in the destination project:

- GUI: set **Target project**, then toggle **Target bundle** (enabled only when the path is valid and matching installed members exist).
- CLI: pass `--bundles target-bundle` with a `TARGET` path.

Membership is the intersection of:

1. Skills and command-skills found under `<target>/.agents/skills/<name>/SKILL.md`; agents found under `<target>/.claude/agents/<name>.md` (and their `.github/agents/<name>.agent.md` twins); installed `guidelines-<name>` packages map back to their guideline names
2. The same kinds available in this AIConfig repository catalog

```bash
python tools/installer.py /path/to/project --bundles target-bundle
```

## Dev-workflow harness bundle

The **dev-workflow harness** is a bundle (`dev-workflow-harness`) that groups the complete dev-workflow harness as a single unit. It includes the orchestrator plus all phase doer/checker skills and the commands (the validation scripts the orchestrator invokes at runtime ship inside the orchestrator skill package):

```bash
python tools/installer.py /path/to/project --bundles dev-workflow-harness
python tools/installer.py /path/to/project --bundles dev-workflow-harness --uninstall
python tools/installer.py /path/to/project --dev-workflow
```

`--dev-workflow` is a CLI alias for `--bundles dev-workflow-harness`. The harness consists of:

- **Skills (11):** `dev-workflow-orchestrator` (the orchestrator) plus the phase doers and checkers — `prompt-clarifier`, `research-guide` / `research-reviewer`, `plan-guide` / `plan-reviewer`, `plan-executor` / `implementation-auditor`, `code-review-resolver` / `code-reviewer`, and `commit-message-writer`.
- **Agents (4):** the four checker agents — `research-reviewer`, `plan-reviewer`, `implementation-auditor`, `code-reviewer` — installed as dual-target copies (`.claude/agents/<name>.md` verbatim from AGENT.md + `.github/agents/<name>.agent.md`). These run the checker skills with fresh-context isolation; read-only behavior is instruction-level (the agent body's Boundaries plus the harness's `check_post_phase.py` detection), not host-enforced frontmatter.
- **Commands (6):** `run-dev-workflow` — installed as a command-skill (`.agents/skills/cmd-run-dev-workflow/SKILL.md` with `disable-model-invocation: true`) — plus four per-phase commands, `research`, `plan`, `implement`, and `review`, and the `commit` command for staged commits; each per-phase command runs a single phase's doer/checker loop to acceptance or escalation without driving the full pipeline.
- **Validation scripts:** the `scripts/` tree inside the orchestrator skill package (including the `checks/` subpackage) — installed with the skill to `<target>/.agents/skills/dev-workflow-orchestrator/scripts/`.
- **Guide:** the `dev-workflow.md` governance guide travels inside the orchestrator skill as `references/dev-workflow.md` — installing the skill installs the guide.

The 11 skills above are the harness's own membership; the dependency closure expands the install to 16 skills, also selecting `agent-runner`, `debugging-guide`, `git-guide`, `git-merge-guide`, and `test-driven-dev-guide` — the `commit` command pulls in `git-guide` alongside core-skill `commit-message-writer` (reported as `Also selecting (dependencies):` lines).

The orchestrator formats escalations per the `guidelines-response` guideline-skill. The harness does not carry guidelines itself; the core bundle does (see [Core dev workflow bundle](#core-dev-workflow-bundle)), and the escalation rules are restated inline in the orchestrator, so the harness works without it. Install the guideline alongside (`--guidelines response` or `--bundles core-dev-workflow`) when every-message output shaping is wanted in the target — it loads through ordinary skill discovery once installed.

The bundle composes with `--skills`, `--agents`, `--commands`, and other `--bundles` in a single invocation. Use `--override` to replace existing harness paths in the target.

## Personal output preferences

Chat-output shaping is distributed as the **`response` guideline** (installed as the `guidelines-response` skill). The core bundle carries it (along with `code-comment` and `coding-behavior`); install it individually when the bundle is not wanted:

```bash
python tools/installer.py /path/to/project --guidelines response
```

It installs as a skill package and loads through ordinary skill discovery in the target.

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
| [github-guide](../skills/github-guide/SKILL.md) | GitHub delivery and PR authoring | A GitHub PR or review must be created, updated, commented on, or resolved through `gh` / `gh api`, or the change needs a review-ready PR description, sizing, or self-review |

Beyond the skills, the core bundle carries:

- **Command (1):** `commit` — commits staged changes with a Conventional Commit message on explicit `/commit` invocation (its dependencies `commit-message-writer` and `git-guide` are core skills).
- **Guidelines (3):** `code-comment`, `coding-behavior`, and `response` — the always-on behavioral guidelines for coding agents working in the target. Selecting the bundle is the deliberate choice to install them; teams that want the skills without behavior shaping should install with explicit `--skills`/`--commands` selectors instead of the bundle, or uninstall the guideline packages afterwards (`--uninstall --guidelines <name>`).

## Extended dev workflow bundle

The extended bundle adds quality gates, collaboration support, parallel execution, and host-specific delivery. Use it for high-risk work, cross-team work, complex plans, expensive changes, ambiguous research, or formal review processes.

The extended bundle includes the full core bundle plus these additional skills:

| Skill | Primary role | Use when |
| --- | --- | --- |
| [dev-workflow-orchestrator](../skills/dev-workflow-orchestrator/SKILL.md) | Workflow routing, governance, and shared reviewer references | End-to-end phase routing or governance guidance is needed, and so `research-reviewer` / `plan-reviewer` shared `reviewer-core` references resolve (full automated script-gated harness execution uses `--dev-workflow` / `dev-workflow-harness`) |
| [research-reviewer](../skills/research-reviewer/SKILL.md) | Research readiness audit | A research report must be validated before planning starts |
| [plan-reviewer](../skills/plan-reviewer/SKILL.md) | Plan readiness audit | A plan must be checked before execution by a developer or AI agent |
| [advisory-council](../skills/advisory-council/SKILL.md) | Multi-perspective decision deliberation | Competing options, policy disputes, or explicit council/panel requests need ranked recommendations with dissent |
| [devil-advocate](../skills/devil-advocate/SKILL.md) | Adversarial proposal review | A single proposal needs red-teaming, show-stopper analysis, and a proceed/rework/reject verdict |
| [agent-runner](../skills/agent-runner/SKILL.md) | Parallel workstream coordination | Independent research, implementation, debug, or audit tasks can run concurrently |
| [techdoc-reviewer](../skills/techdoc-reviewer/SKILL.md) | Documentation review and synchronization | Reader-facing docs must be verified against code, tests, and configuration, or updated after a behavior change |
| [git-merge-guide](../skills/git-merge-guide/SKILL.md) | Deep local merge/rebase integration | A local merge or rebase needs intent reconstruction, semantic conflict resolution, combined-tree review, or impact-based verification |

## Choosing Core vs Extended

Both bundles are expanded by the dependency closure at install time (see [Dependency map](#dependency-map-auto-selection)). The core bundle's 12 listed skills install as 18: the closure adds `dev-workflow-orchestrator`, `research-reviewer`, `plan-reviewer`, `code-review-resolver`, `agent-runner`, and `git-merge-guide`. The extended bundle's real delta over core is therefore three skills — `advisory-council`, `devil-advocate`, and `techdoc-reviewer` — not the orchestrator or reviewers, which core already carries. Both bundles carry the same command (`commit`) and guidelines (`code-comment`, `coding-behavior`, `response`) through the shared base.

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
- A formal PR process or GitHub inline review posting is required.

When extending beyond core, add individual extended-bundle skills as the work warrants. Note that `research-reviewer`, `plan-reviewer`, and `agent-runner` are already part of every core install via the dependency closure, so they need no separate selection:

- [research-reviewer](../skills/research-reviewer/SKILL.md) when research will drive expensive or irreversible work.
- [plan-reviewer](../skills/plan-reviewer/SKILL.md) when execution risk is higher than normal.
- [advisory-council](../skills/advisory-council/SKILL.md) when a consequential decision has competing perspectives or needs structured dissent.
- [devil-advocate](../skills/devil-advocate/SKILL.md) when one proposal must be pressure-tested before commitment.
- [agent-runner](../skills/agent-runner/SKILL.md) only when workstreams are genuinely independent.

## Maintenance

1. Update shared skill sets in the `bases` array in [bundles.json](bundles.json) when core or other reusable membership changes.
2. Update bundle-specific `skills` only for additions beyond referenced bases.
3. Update bundle descriptions and per-skill tables in this file.
4. Operational workflow guidance that uses these bundles lives in [dev-workflow.md](../skills/dev-workflow-orchestrator/references/dev-workflow.md) (inside the orchestrator skill's `references/`).
