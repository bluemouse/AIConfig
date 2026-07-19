# Skill Bundles

This document defines the workflow skill bundles for a classic software development lifecycle:

```text
research -> plan -> implement -> test/debug -> QA -> PR
```

Bundles are intentionally stack-neutral. Add language, platform, framework, or domain-specific skills only after a workflow skill has established what kind of technical help is needed.

Canonical skill membership for tooling lives in [bundles.json](bundles.json). Edit that file first when adding or removing bundle skills, then keep the descriptions and tables in this document in sync.

## Bundle composition

[bundles.json](bundles.json) modularizes bundles with two layers:

- **`bases`** — reusable skill sets keyed by id. Shared membership (for example the core workflow skills) is defined once in the top-level `bases` array.
- **`bundles`** — installable bundles shown in the installer GUI. Each bundle references zero or more base ids through its `bases` field and may add bundle-specific skills in its own `skills` list.

Resolved membership for tooling is:

```text
resolved_skills = union(base.skills for each referenced base id) ∪ bundle.skills
```

The extended dev workflow bundle references the `core-dev-workflow` base and lists only its five additional skills in `skills`.

### CLI usage

`tools/install-skills.py` resolves bundle ids the same way as the GUI:

```bash
python tools/install-skills.py /path/to/project --bundles core-dev-workflow
python tools/install-skills.py /path/to/project --bundles extended-dev-workflow --override
python tools/install-skills.py /path/to/project --bundles core-dev-workflow --skills cpp-coding
```

- `--bundles <id>` selects skills from the resolved bundle membership for install or uninstall.
- Combine with `--skills` to add individual skills beyond the bundle.
- Agents are independent: `--bundles` does not limit agents. Pass `--agents` to select specific agents; otherwise all discovered agents are included.

### Target bundle (dynamic)

The **Target bundle** is not stored in `bundles.json`. It is computed at runtime from skills already installed in the destination project:

- GUI: set **Target project**, then toggle **Target bundle** (enabled only when the path is valid and matching installed skills exist).
- CLI: pass `--bundles target-bundle` with a `TARGET` path.

Membership is the intersection of:

1. Skills found under `<target>/.shared/skills/*/SKILL.md`
2. Skills available in this AIConfig repository catalog

```bash
python tools/install-skills.py /path/to/project --bundles target-bundle
```

## Core dev workflow bundle

The core bundle is the minimum workflow set a team should rely on for ordinary feature, bug, and product-spec development. Not every skill fires on every task, but every skill covers a responsibility that appears regularly in healthy delivery work.

| Skill | Primary role | Use when |
| --- | --- | --- |
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
| [agent-runner](../skills/agent-runner/SKILL.md) | Parallel workstream coordination | Independent research, implementation, debug, or audit tasks can run concurrently |
| [minutes-writer](../skills/minutes-writer/SKILL.md) | Meeting and decision record | Engineering discussions need grounded minutes, decisions, and action items |
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
- [agent-runner](../skills/agent-runner/SKILL.md) only when workstreams are genuinely independent.
- [minutes-writer](../skills/minutes-writer/SKILL.md) when decisions are made in meetings or chat and need a durable record.
- [github-guide](../skills/github-guide/SKILL.md) only when the delivery host is GitHub and `gh` or `gh api` mechanics are part of the task.

## Maintenance

1. Update shared skill sets in the `bases` array in [bundles.json](bundles.json) when core or other reusable membership changes.
2. Update bundle-specific `skills` only for additions beyond referenced bases.
3. Update bundle descriptions and per-skill tables in this file.
4. Operational workflow guidance that uses these bundles lives in [dev-workflow.md](../dev-workflow.md).
