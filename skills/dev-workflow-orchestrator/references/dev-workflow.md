# Development Workflow

> **Path note.** This guide lives in the dev-workflow-orchestrator skill's `references/`
> directory and travels with that skill. Sibling-skill links (`../../<name>/SKILL.md`)
> resolve both in the AIConfig bootstrap layout (`skills/<name>/`) and in the installed
> shared layout (`.agents/skills/<name>/`). Mentions of `tools/bundles.md` and
> `tools/bundles.json` refer to the AIConfig repository's installer documentation and
> do not exist in target projects.

This guide describes how to run a classic software development workflow using the skill bundles defined in `tools/bundles.md`:

```text
clarify -> research -> plan -> implement -> test/debug -> QA -> PR
```

It is intentionally stack-neutral. Add language, platform, framework, or domain-specific skills only after the workflow skill has established what kind of technical help is needed.

Use this guide when developing a software feature, new product requirement, bug report, product spec, or similarly scoped engineering change.

Skill bundle membership and selection guidance live in `tools/bundles.md`.
Machine-readable bundle configuration is in `tools/bundles.json`.

## Automation: the dev-workflow harness

This guide describes the workflow skill-by-skill. The **dev-workflow harness** automates the same pipeline end-to-end with bounded doer/checker loops, backward edges for upstream root causes, artifact contracts, and deterministic validation scripts.

- **Full pipeline:** run `/run-dev-workflow` to orchestrate all phases (clarify → research → plan → implement → code-review → commit). It loads the [dev-workflow-orchestrator](../SKILL.md) skill, which owns state, routing, and integration.
- **Single phase:** run `/research`, `/plan`, `/implement`, or `/review` to run one phase's doer/checker loop to acceptance or escalation without driving the full pipeline.
- **Install the harness:** `python tools/installer.py /path/to/project --bundles dev-workflow-harness` (installs the orchestrator, all phase skills, the commands, and the `.agents/tools/dev-workflow/` validation scripts as a unit).

The harness relies on this guide's intake classification (§1) and governance tables (Mandatory vs Optional Gates) to decide which phases and gates apply. When the harness is active, the orchestrator's artifact contracts and validation scripts enforce the workflow; this guide's prose describes the same workflow for manual or partial automation use.

## Operational Workflow

### 1. Intake: classify the work

Start by deciding what kind of input you have.

| Input | Default first skill | Reason |
| --- | --- | --- |
| Ambiguous request — conflicting requirements, undefined deliverable, vague or overloaded terms, or several plausible readings | [prompt-clarifier](../../prompt-clarifier/SKILL.md) | Settle blocking decisions in the request itself before research, planning, or implementation |
| Complex decision, policy dispute, competing options, or explicit council/panel/think-tank request | [advisory-council](../../advisory-council/SKILL.md) | Multi-perspective deliberation with ranked recommendations, dissent, and decision gates (use [prompt-clarifier](../../prompt-clarifier/SKILL.md) first if the decision question itself is still ambiguous) |
| Single proposal to challenge, red-team, pressure-test, or reject with a proceed/rework/reject verdict | [devil-advocate](../../devil-advocate/SKILL.md) | Adversarial review of one proposal with findings, resolutions, and a verdict |
| Vague idea, opportunity, product direction, roadmap item | [research-guide](../../research-guide/SKILL.md) | Turns an unformed idea into agreed scope, requirements, tradeoffs, and risks (use [prompt-clarifier](../../prompt-clarifier/SKILL.md) first if what is being asked for is still unclear) |
| Product requirement, product spec, design doc, issue, or feature request | [plan-guide](../../plan-guide/SKILL.md) if clear; otherwise [research-guide](../../research-guide/SKILL.md) | Clear inputs can be planned; unclear product direction needs discovery first (use [prompt-clarifier](../../prompt-clarifier/SKILL.md) first if the request wording is ambiguous) |
| Bug report, failing test, crash, regression, or flaky behavior | [debugging-guide](../../debugging-guide/SKILL.md) | Root cause must be proven before implementation changes |
| Approved implementation plan | [plan-executor](../../plan-executor/SKILL.md) | Execution needs task tracking, working-tree safety, edits, and verification |
| Finished code changes | [implementation-auditor](../../implementation-auditor/SKILL.md), then [code-reviewer](../../code-reviewer/SKILL.md), then [techdoc-reviewer](../../techdoc-reviewer/SKILL.md) when reader-visible contracts or documentation are in scope | Correctness evidence comes before reviewer-side diff risk analysis; documentation truth follows when APIs, setup, migration, or operational docs may be affected |
| Ready-to-submit branch | [commit-message-writer](../../commit-message-writer/SKILL.md), [git-guide](../../git-guide/SKILL.md), [github-guide](../../github-guide/SKILL.md) | Delivery needs commits, git mechanics, and a reviewable PR narrative |

Each subsequent phase hands off to the next skill's documented entry conditions; the per-skill SKILL.md bodies own their own procedure and quality bar — this guide does not restate them.

### 2-7. Phase guidance

Each phase's procedure, quality bar, and done criteria live in the owning skill:

- **Research** — [research-guide](../../research-guide/SKILL.md); audit via [research-reviewer](../../research-reviewer/SKILL.md).
- **Plan** — [plan-guide](../../plan-guide/SKILL.md); audit via [plan-reviewer](../../plan-reviewer/SKILL.md).
- **Implement** — [plan-executor](../../plan-executor/SKILL.md), with [test-driven-dev-guide](../../test-driven-dev-guide/SKILL.md) per the plan's task discipline and [agent-runner](../../agent-runner/SKILL.md) for genuinely independent parallel units (disjoint write scopes, no ordering dependency, independently verifiable, no cross-unit conflict resolution — otherwise sequential).
- **Debug** — [debugging-guide](../../debugging-guide/SKILL.md): root cause is the earliest incorrect transition, proven by evidence before any production fix. Small bugs may need only debugging-guide; larger ones add plan-guide (repair plan) then plan-executor.
- **QA** — [implementation-auditor](../../implementation-auditor/SKILL.md): maps requirement → implementation → evidence, and is not a diff review.
- **Review** — [code-reviewer](../../code-reviewer/SKILL.md) at the effort the risk class demands (`basic` for small isolated diffs, `standard` for normal shared-code work, `deep` for security/migration/public-API/performance-critical changes); [techdoc-reviewer](../../techdoc-reviewer/SKILL.md) when reader-visible contracts changed. A passing code review is never proof that documentation is correct.

### 8. Delivery: commit, push, and open the PR

The delivery skills are separate on purpose; run them in order and pass each output to the next:

1. [commit-message-writer](../../commit-message-writer/SKILL.md) drafts the Conventional Commit message from git evidence (skip if the developer already has one).
2. The developer reviews and approves (or iterates) the message.
3. [git-guide](../../git-guide/SKILL.md) stages, commits with the approved message, and pushes or rebases the branch.
4. [github-guide](../../github-guide/SKILL.md) writes the PR/MR description, saves it (for example `pr-body.md`), and opens the PR (`gh pr create --body-file`) or posts a review when the host is GitHub.

None of these skills commit, push, or open a PR unless explicitly asked. One concern per PR; split bundled refactors or unrelated changes out before delivery — commit-message-writer flags mixed diffs at the commit level, github-guide owns PR-level sizing and splitting.

## Handoff and Return Paths

The lifecycle is not one-directional. Each quality gate can send work backward. Use this table to route on each skill's terminal state so defects are not silently carried forward.

| Producing skill | Terminal state | Next step |
| --- | --- | --- |
| [research-reviewer](../../research-reviewer/SKILL.md) | `ready` / `conditionally ready` | Proceed to [plan-guide](../../plan-guide/SKILL.md); carry accepted risks |
| [research-reviewer](../../research-reviewer/SKILL.md) | `needs revision` / `blocked` | Return to [research-guide](../../research-guide/SKILL.md) with the review handoff; re-review if the change was material |
| [plan-reviewer](../../plan-reviewer/SKILL.md) | `validated` / `conditionally validated` | Proceed to [plan-executor](../../plan-executor/SKILL.md); make accepted risks explicit |
| [plan-reviewer](../../plan-reviewer/SKILL.md) | `needs revision` / `blocked` | Return the Guide handoff packet to [plan-guide](../../plan-guide/SKILL.md); re-review before execution |
| [plan-executor](../../plan-executor/SKILL.md) | verification fails unexpectedly | [debugging-guide](../../debugging-guide/SKILL.md) to find root cause, then resume execution |
| [plan-executor](../../plan-executor/SKILL.md) | plan is unsafe, impossible, or contradicts the repo | Return to [plan-guide](../../plan-guide/SKILL.md) with an execution-blocker report |
| [debugging-guide](../../debugging-guide/SKILL.md) | root cause found, fix applied | [implementation-auditor](../../implementation-auditor/SKILL.md) for complex/shared fixes, then [code-reviewer](../../code-reviewer/SKILL.md) |
| [implementation-auditor](../../implementation-auditor/SKILL.md) | `pass` | Proceed to [code-reviewer](../../code-reviewer/SKILL.md) |
| [implementation-auditor](../../implementation-auditor/SKILL.md) | `pass with risks` | Proceed to [code-reviewer](../../code-reviewer/SKILL.md); pass the risks in as review focus |
| [implementation-auditor](../../implementation-auditor/SKILL.md) | `fail` | Return to [plan-executor](../../plan-executor/SKILL.md) (missing behavior) or [debugging-guide](../../debugging-guide/SKILL.md) (regression) |
| [implementation-auditor](../../implementation-auditor/SKILL.md) | `blocked` | Document the blocker; resolve environment/dependency access, then re-audit |
| [code-reviewer](../../code-reviewer/SKILL.md) | blocking findings | Route by finding type per the Review section, then re-review |
| [code-reviewer](../../code-reviewer/SKILL.md) | no blocking findings | Proceed to delivery |

Loops are intentional and human-gated. Do not auto-cycle between two skills without an explicit decision.

## Staged Mode

For large, complex tasks that are too big for a single implementation pass, the dev-workflow supports an opt-in **staged mode**. Staged mode decomposes the work into self-contained, verifiable, committable stages, each running the full implement → audit → review → commit loop, with plan refinement between stages and a final deep code review on the cumulative diff.

### When to use staged mode

[plan-guide](../../plan-guide/SKILL.md) recommends staged mode when any of the following hold:

- Planning depth is `rigorous` (high-risk, cross-cutting, security/privacy/compliance-sensitive, migration-heavy, or user-visible work).
- Task count exceeds 5 (the plan has 6 or more tasks).
- The user explicitly requests staged mode.

The user confirms at the plan gate. [plan-guide](../../plan-guide/SKILL.md) does not recommend staged mode for single-stage plans (a single stage degenerates to linear plus overhead).

### Staged-mode topology

```text
For each stage (1..N):
  implement → audit → review(light) → commit
       ↓ (on failure: full loop for this stage)
  plan-reviewer stage-exit review (plan-current / plan-stale)
       ↓ (plan-stale: full re-plan, re-derive stages)
  next stage
       ↓ (all stages committed)
Final deep code review (full Loop 4, deep effort, cumulative commit range)
       ↓
Terminal delivery: github-guide (PR authoring + creation)
```

### How staged mode differs from linear

| Aspect | Linear mode | Staged mode |
| --- | --- | --- |
| Implementation | Single pass: all tasks, then one audit, one review | Per-stage: each stage runs implement → audit → review → commit |
| Plan refinement | None (plan is fixed after plan-reviewer) | Between stages: `plan-reviewer` stage-exit review judges if remaining plan is still valid |
| Code review | Single review after all implementation | Light review per stage + final deep review on cumulative diff |
| Commits | Single commit chain at delivery | Per-stage commit (no push by default); PR at end |
| Quality gates | One audit, one review | N light audits + N light reviews + 1 final deep review |

### Stage-exit review

Between stages, [plan-reviewer](../../plan-reviewer/SKILL.md) runs a stage-exit review comparing the completed stage's implementation against the plan's assumptions for remaining stages. It emits:

- **`plan-current`**: No plan assumption is contradicted. [plan-guide](../../plan-guide/SKILL.md) performs light refinement of the next stage's task details.
- **`plan-stale`**: At least one plan assumption is contradicted (with explicit evidence). [plan-guide](../../plan-guide/SKILL.md) performs a full re-plan with [plan-reviewer](../../plan-reviewer/SKILL.md) re-audit.

### Final deep review

After all stages commit, a full deep code review ([code-reviewer](../../code-reviewer/SKILL.md) with `deep` effort) runs on the cumulative commit range. Fixes are applied as **new commits on top** (no history rewrite, no amend). This catches cross-stage and cumulative issues that per-stage light reviews cannot detect.

### Backward edges in staged mode

In-stage backward edges (root-cause repair) and between-stage stage-exit reviews (forward-looking plan validity) are independent. An in-stage backward edge does not trigger a stage-exit review. A stage-exit review does not create a backward edge.

### Governance: staged-mode change classes

| Change class | Mandatory gates in staged mode |
| --- | --- |
| Cross-stage security/auth change | Full loop per stage AND final deep review |
| Migration spanning multiple stages | Full loop per stage AND final deep review AND techdoc-reviewer |
| Public API change across stages | Full loop per stage AND final deep review AND techdoc-reviewer |
| Refactor across 3+ modules (staged) | Full loop per stage AND final deep review |

## Governance: Mandatory vs Optional Gates

The core bundle is always available. The extended-bundle gates are optional by default but become mandatory for higher-risk change classes. Teams can tighten this table, not loosen the safety-critical rows.

| Change class | Mandatory gates | Rationale |
| --- | --- | --- |
| Small local bug fix | None beyond [code-reviewer](../../code-reviewer/SKILL.md) `basic` | Low blast radius, reversible |
| Feature, single subsystem | [code-reviewer](../../code-reviewer/SKILL.md) `standard`; [plan-reviewer](../../plan-reviewer/SKILL.md) if executed by another person or agent | Bounded scope |
| Security / auth / privacy change | [plan-reviewer](../../plan-reviewer/SKILL.md), [implementation-auditor](../../implementation-auditor/SKILL.md), `deep` [code-reviewer](../../code-reviewer/SKILL.md) | High blast radius |
| Data or schema migration | [research-reviewer](../../research-reviewer/SKILL.md) (when a research report exists), [plan-reviewer](../../plan-reviewer/SKILL.md), [implementation-auditor](../../implementation-auditor/SKILL.md) | Hard to roll back |
| Public API or contract change | [plan-reviewer](../../plan-reviewer/SKILL.md), `deep` [code-reviewer](../../code-reviewer/SKILL.md), [techdoc-reviewer](../../techdoc-reviewer/SKILL.md) | Cross-team impact and reader-visible contracts |
| Refactor across 3+ modules | [plan-reviewer](../../plan-reviewer/SKILL.md), `standard`+ [code-reviewer](../../code-reviewer/SKILL.md) | Cascade risk |
| Production incident follow-up | [debugging-guide](../../debugging-guide/SKILL.md), [implementation-auditor](../../implementation-auditor/SKILL.md), `guidelines-minutes` guideline-skill | Defect prevention and record |

[agent-runner](../../agent-runner/SKILL.md) is never mandatory; use it only when independent workstreams exist and the host supports subagents.

## Post-Delivery: Defects Found After Merge

When a defect is found in merged or deployed code, re-enter the lifecycle:

1. [debugging-guide](../../debugging-guide/SKILL.md) to reproduce and prove root cause.
2. [test-driven-dev-guide](../../test-driven-dev-guide/SKILL.md) to write a regression test before the fix (required for production bugs).
3. [plan-guide](../../plan-guide/SKILL.md) if the fix needs coordinated changes; otherwise a direct scoped fix.
4. [implementation-auditor](../../implementation-auditor/SKILL.md) then [code-reviewer](../../code-reviewer/SKILL.md), then [techdoc-reviewer](../../techdoc-reviewer/SKILL.md) when reader-visible contracts or docs are in scope, then the delivery chain.
5. The `guidelines-minutes` guideline-skill for the post-incident record when the impact warrants it.

## Decision Traceability

Decisions made in meetings should not be lost between phases. After applying the `guidelines-minutes` guideline-skill to record decisions and action items:

- Feed product or scope decisions into the [research-guide](../../research-guide/SKILL.md) report.
- Feed constraints and action items into the [plan-guide](../../plan-guide/SKILL.md) plan as assumptions or tasks.
- Feed commitments into [implementation-auditor](../../implementation-auditor/SKILL.md) as verification criteria.
- Reference the minutes from the research report or plan so decisions can be revisited if context changes.
