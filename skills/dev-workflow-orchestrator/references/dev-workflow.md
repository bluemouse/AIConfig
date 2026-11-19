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

The **dev-workflow harness** automates the pipeline end-to-end with bounded doer/checker loops, backward edges for upstream root causes, artifact contracts, and deterministic validation scripts.

- **Full pipeline:** run `/run-dev-workflow` to orchestrate all phases (clarify → research → plan → implement → code-review → commit). It loads the [dev-workflow-orchestrator](../SKILL.md) skill, which owns state, routing, and integration.
- **Single phase:** run `/research`, `/plan`, `/implement`, or `/review` to run one phase's doer/checker loop to acceptance or escalation without driving the full pipeline.
- **Install the harness:** `python tools/installer.py /path/to/project --bundles dev-workflow-harness` (installs the orchestrator, all phase skills, the commands, and the `.agents/tools/dev-workflow/` validation scripts as a unit).

The harness relies on this guide's intake classification (§1) and governance tables to decide which phases and gates apply. When the harness is active, the orchestrator's artifact contracts and validation scripts enforce the workflow; this guide's prose describes the same workflow for manual or partial automation use.

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
| Ready-to-submit branch | [git-guide](../../git-guide/SKILL.md), [github-guide](../../github-guide/SKILL.md) | Delivery needs commit drafting + git mechanics, and a reviewable PR narrative |

Each subsequent phase hands off to the next skill's documented entry conditions; the per-skill SKILL.md bodies own their own procedure and quality bar — this guide does not restate them.

### Phase guidance, delivery, handoffs, and staged mode

- **Phase procedures and quality bars** (research → plan → implement → debug → QA → review): each owning skill's SKILL.md (see the intake table for routing).
- **Delivery** (commit → push → PR): [git-guide](../../git-guide/SKILL.md) (message drafting + mechanics), then [github-guide](../../github-guide/SKILL.md) — none commit, push, or open a PR unless explicitly asked; one concern per PR.
- **Handoff and return paths** (routing on each skill's terminal state, backward edges): the orchestrator's loop contracts in [../SKILL.md](../SKILL.md) and [loop-contracts.md](loop-contracts.md). Loops are intentional and human-gated — never auto-cycle between two skills without an explicit decision.
- **Staged mode** (when to use, per-stage topology, stage-exit review, final deep review): the orchestrator's Staged iterator and Final deep review sections in [../SKILL.md](../SKILL.md).
- **Post-delivery defects found after merge:** re-enter with [debugging-guide](../../debugging-guide/SKILL.md) for root cause, then a regression test via [test-driven-dev-guide](../../test-driven-dev-guide/SKILL.md) before the fix, then the audit → review → delivery chain.
- **Decision traceability:** after recording decisions with the `guidelines-minutes` guideline-skill, feed product decisions into the research report, constraints and action items into the plan, and commitments into audit verification criteria, referencing the minutes from the report or plan.

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

Staged-mode additions:

| Change class | Mandatory gates in staged mode |
| --- | --- |
| Cross-stage security/auth change | Full loop per stage AND final deep review |
| Migration spanning multiple stages | Full loop per stage AND final deep review AND techdoc-reviewer |
| Public API change across stages | Full loop per stage AND final deep review AND techdoc-reviewer |
| Refactor across 3+ modules (staged) | Full loop per stage AND final deep review |

[agent-runner](../../agent-runner/SKILL.md) is never mandatory; use it only when independent workstreams exist and the host supports subagents.
