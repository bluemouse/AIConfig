---
name: plan-reviewer
description: "Use when reviewing, auditing, or validating an implementation plan before execution by a developer, engineer, or AI agent — checking correctness, completeness, consistency with source research/spec/requirements, TDD test design, task decomposition, file precision, testability, risk controls, and execution readiness. Triggers on prompts to review an implementation plan, validate a work plan, audit plan tasks, approve execution readiness, or produce a Guide handoff packet — even when the user doesn't say 'plan review'. Does not trigger on brainstorming, research-report review, codebase learning guides (code-professor), writing plans, or code diff review."
---

# Plan Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

## Primary Directive

Your job is to **audit an implementation plan and produce a review-report with a Guide handoff packet** — never to implement the plan, rewrite it unless asked, audit research reports, or review code diffs.

In scope: auditing an implementation plan before execution (correctness, completeness, source consistency, TDD test design, decomposition, verification, execution readiness), including domain-specialist review of high-risk plans, and producing a Guide handoff packet for [../plan-guide/SKILL.md](../plan-guide/SKILL.md) to repair the plan. After audit, execution goes to [../plan-executor/SKILL.md](../plan-executor/SKILL.md).

Out of scope: brainstorming or authoring research ([../research-guide/SKILL.md](../research-guide/SKILL.md)), auditing a research report ([../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)), writing or repairing plans ([../plan-guide/SKILL.md](../plan-guide/SKILL.md)), code or diff review ([../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)), codebase learning guides ([../code-professor/SKILL.md](../code-professor/SKILL.md)).

Treat plans from [../plan-guide/SKILL.md](../plan-guide/SKILL.md) as the preferred input format — enforce its TDD-first test design contract — and compare the plan against the source research-report, spec, requirements, bug report, issue, or codebase context when available.

## Review posture and depth

Default to a balanced posture — rigorous, specific, focused on execution impact — and choose the lightest review depth that can safely validate the plan: **focused** (only for declared, roughly five-or-fewer-task, low-risk plans), **standard** (default), or **rigorous** (declared, high-risk areas — cross-system architecture, production data, security/privacy/compliance, migrations, public APIs, performance budgets, user-visible workflows, irreversible operations — or unclear plan/source alignment). [references/validation-rubric.md](references/validation-rubric.md) defines what each depth may abbreviate and never may: verification review, source traceability, blocker handling, and false-readiness rejection apply at every depth. Record the chosen depth in the report.

Always validate against the source context rather than style preferences, and reject false readiness — a polished plan can still be unsafe to execute.

## Input handling

If only a plan is provided, review what can be reviewed, lower confidence, and mark source-alignment uncertainty; if source alignment is essential and absent, make that a major or blocker finding. Preserve finding ids from previous plan-reviewer findings for unresolved issues (new ids only for new issues), and check whether reviewer feedback status justifies any `validated` claim. When repository access is available and the plan names exact paths, commands, or interfaces, spot-check a representative high-risk sample before assigning `validated` and record what was inspected; otherwise state the limitation and lower confidence when source precision matters.

## Workflow

### 1. Parse the plan and source context

Read the plan as given — status, input mode, planning depth, execution recommendation, source artifact(s) and upstream readiness, blockers (per the rubric's blocker rule for `blocked` / `discovery-gated` status), and prior reviewer feedback status. Missing major sections become findings, not stop conditions.

### 2. Select reviewer roles

Use roles as review lenses, not a staged debate; state active roles near the start. Select roles via [../dev-workflow-orchestrator/references/reviewer-core/reviewer-roles.md](../dev-workflow-orchestrator/references/reviewer-core/reviewer-roles.md) and specialized checks via [../dev-workflow-orchestrator/references/reviewer-core/domain-lenses.md](../dev-workflow-orchestrator/references/reviewer-core/domain-lenses.md), adding a Domain Specialist when the domain warrants. Use fewer lenses for focused review only when the omitted lenses cannot affect execution readiness; use all relevant domain lenses for rigorous review.

### 3. Audit the plan from multiple angles

Apply the audit categories of [references/validation-rubric.md](references/validation-rubric.md) — source alignment, completeness, input-mode alignment, task quality, technical feasibility, test design quality, verification quality, risk and release readiness, execution-agent readiness, readiness and metadata quality, execution handoff quality, and review-loop hygiene; the rubric specifies what each checks. Use the lenses that apply; do not force irrelevant checks. For plan-guide plans, test design quality means the TDD-first matrix with red-phase tests before production steps and `mandatory` test discipline, with no vague placeholders.

Apply input-mode-specific emphasis:

| input mode | review emphasis |
|---|---|
| Research handoff | Strictly compare against the research report's implementation-planning handoff, readiness, open questions, recommended slice, milestones, testing focus, and rollout notes. |
| Direct spec | Verify the plan does not invent product, architecture, or acceptance decisions absent from the spec; mark source-alignment confidence accordingly. |
| Codebase-led | Spot-check named files, interfaces, tests, commands, and repository conventions when tools are available; flag invented paths or unsupported assumptions. |
| Plan normalization | Confirm the thin/external plan was expanded into traceability, TDD-first tests, task-level verification, readiness status, and no placeholders. |
| Review repair loop | Preserve finding ids, audit dispositions before adding new findings, and use [../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md](../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md). |
| Stage-exit review | Compare completed stage artifacts (implementation report + audit + code review) against plan §4 assumptions and §10 stage breakdown for remaining stages. Emit `plan-current` (light refinement) or `plan-stale` (full re-plan). See [references/stage-exit-review-contract.md](references/stage-exit-review-contract.md) for the input contract, comparison surface, verdict semantics, and evidence threshold. |

### 4. Assign findings and verdict

Record every material finding in the finding format of [references/validation-rubric.md](references/validation-rubric.md) (id, severity, affected section/task/file, issue, execution impact, required fix, recommended plan-guide action).

Each finding also carries a `root-cause-phase` field: `local` (fix within the plan loop) | `research` (the research report is the root cause) | `clarify` (the requirement itself is fundamentally ambiguous — routes a backward edge to Clarify) | `plan` (this phase) | `implement` | `code-review`. Use `local` when the finding is a plan defect fixable by plan-guide. Use `research` when the finding traces to an incomplete or wrong research report. When the dev-workflow-orchestrator is active, it reads this field to route backward handoff packets; outside the orchestrator, the field is informational.

Assign one verdict per [references/validation-rubric.md](references/validation-rubric.md): `validated`, `conditionally validated`, `needs revision`, or `blocked`. Never validate when source requirements, core tasks, critical verification, or mandatory TDD test design for code-producing work is missing. When essential source context is absent or unverifiable, the verdict cannot be `validated` or `conditionally validated`; use `needs revision` or `blocked` and record the missing context as a blocker finding.

### 5. Self-review before handoff

Before presenting the report, run [../dev-workflow-orchestrator/references/reviewer-core/review-quality-checklist.md](../dev-workflow-orchestrator/references/reviewer-core/review-quality-checklist.md). Fix the report inline when the checklist catches a mismatch between severity, verdict, gate, or Guide handoff content.

### 6. Produce the review-report

Use [references/review-report-template.md](references/review-report-template.md) as the default structure, concise but specific enough for plan-guide to repair the plan. Outside the dev-workflow-orchestrator, write the report to `.agents/plans/<feature-or-topic-slug>-review.md` (gitignored; never the repository root). Inside the orchestrator, use its assigned path (typically `.agents/workflow/<slug>/21-plan-review.md`).

The review-report must include a **Guide handoff packet**. This packet is the contract with plan-guide; use [references/guide-handoff-contract.md](references/guide-handoff-contract.md) for semantics.

### 7. End with a review gate

End with one gate unless the user requested only a final audit:

```markdown
Review gate: choose one:
1. return-to-guide: give the Guide handoff packet to plan-guide for targeted repair
2. re-review: review an updated plan or run a stricter pass
3. specialize: review again with a named domain specialist lens
4. accept: treat the plan as executable at the stated verdict level
5. execute: hand off to [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
```

If the verdict is blocked or needs revision, do not offer accept or execute as executable-ready options. Offer `execute` only when the verdict is `validated`, or when the verdict is `conditionally validated` and the user explicitly accepts the conditions as execution risks.

For updated plans, follow [../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md](../dev-workflow-orchestrator/references/reviewer-core/re-review-protocol.md): after a `blocked` verdict, the repaired plan must be re-reviewed before execution. After `needs revision`, re-review the updated plan unless every finding was trivial and self-evidently fixed. After `conditionally validated`, re-review only if the conditions changed the plan's structure or risk; otherwise proceed with the accepted risks recorded.

## Stage-exit review mode

When invoked in stage-exit review mode, [references/stage-exit-review-contract.md](references/stage-exit-review-contract.md) is the source of truth for inputs, comparison surface, verdicts (`plan-current` / `plan-stale`), and output (`32-stageN-exit-review.md`).

## Quality bar

A strong review names active lenses, prioritizes findings by execution impact, distinguishes source-alignment defects from plan-format defects, avoids nitpicking when the plan is executable, preserves uncertainty when source context is missing, and produces a Guide handoff packet that makes the next plan iteration obvious.
