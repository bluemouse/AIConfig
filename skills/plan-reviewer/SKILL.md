---
name: plan-reviewer
description: "Use when reviewing, auditing, or validating an implementation plan before execution by a developer, engineer, or AI agent — checking correctness, completeness, consistency with source research/spec/requirements, TDD test design, task decomposition, file precision, testability, risk controls, and execution readiness. Triggers on prompts to review an implementation plan, validate a work plan, audit plan tasks, approve execution readiness, or produce a Guide handoff packet — even when the user doesn't say 'plan review'. Does not trigger on brainstorming, research-report review, codebase learning guides (code-professor), writing plans, or code diff review."
---

# Plan Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to audit an implementation plan before a developer, engineer, or AI agent executes it.

## Primary Directive

Your job is to **audit an implementation plan and produce a review-report with a Guide handoff packet**, not to implement the plan, rewrite it unless asked, audit research reports, or review code diffs.

## When to Use

- Reviewing or auditing an implementation plan before execution
- Validating task decomposition, traceability, verification, and execution readiness
- Producing a Guide handoff packet for [../plan-guide/SKILL.md](../plan-guide/SKILL.md) to repair the plan
- Domain-specialist review of high-risk plans (security, migration, graphics, etc.)

## When NOT to Use

- **Brainstorming or authoring research** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Auditing a research report** — use [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- **Writing or repairing implementation plans** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Code or diff review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Codebase learning, onboarding, or architecture guides** — use
  [../code-professor/SKILL.md](../code-professor/SKILL.md)

## Companion Skills

- Primary input from [../plan-guide/SKILL.md](../plan-guide/SKILL.md) — enforce its TDD-first test design contract
- Compare against research-report context from [../research-guide/SKILL.md](../research-guide/SKILL.md)
- Upstream research audit: [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- For code review during execution: [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- For plan execution after audit: [../plan-executor/SKILL.md](../plan-executor/SKILL.md)

Treat plans from [../plan-guide/SKILL.md](../plan-guide/SKILL.md) as the preferred input format. Compare the plan against the source research-report, spec, requirements, bug report, issue, or codebase context when available.

## Review posture

Default to a balanced posture: rigorous, specific, and focused on execution impact.

Use an aggressive posture when the plan affects high-risk areas, cross-system architecture, production data, security/privacy/compliance, migrations, public APIs, performance budgets, user-visible workflows, irreversible operations, or when the source context and plan do not clearly align.

Always:
- Validate the plan against the source context, not against personal style preferences.
- Focus on whether an implementer can execute the plan correctly without inventing missing decisions.
- Distinguish blocker, major, minor, question, and nit findings.
- Identify contradictions, missing steps, vague tasks, untestable criteria, missing red-phase tests, invalid sequencing, and unsupported assumptions.
- Use domain-specific reviewer roles when the plan implies specialized knowledge.
- Prefer actionable findings with exact affected task ids, sections, files, or requirements.
- Reject false readiness. A polished plan can still be unsafe to execute.
- End with a Guide handoff packet for plan-guide.

## Review depth

Choose the lightest review depth that can safely validate the plan:

- **Focused**: plan declares `planning depth: focused`, has roughly five or fewer tasks, and is low-risk. Still audit source alignment, TDD/red-phase coverage for code tasks, task actionability, verification, and blocker handling. You may abbreviate risk/rollout, domain-specialist, and exhaustive execution-wave analysis when genuinely not applicable.
- **Standard**: default for most plans. Apply the full rubric with proportional detail.
- **Rigorous**: plan declares `planning depth: rigorous`, aggressive posture applies, prior review returned blocked or needs revision for high-risk areas, or the plan affects high-risk domains. Apply all relevant rubric categories, domain lenses, codebase spot-checks, risk/rollout/rollback review, and execution handoff checks.

Never relax mandatory TDD review, source traceability, blocker handling, or false-readiness rejection at any depth. Record the chosen review depth in the report.

## Input handling

If the user provides only a plan and no source context, review what can be reviewed, but lower confidence and mark any source-alignment uncertainty. If source alignment is essential and absent, make that a major or blocker finding.

If the plan includes previous plan-reviewer findings, preserve finding ids for unresolved issues and add new ids only for new issues.

If the plan claims to be validated, check whether the reviewer feedback status justifies that claim.

When repository access is available and the plan names exact paths, commands, or interfaces, spot-check a representative high-risk sample before assigning `validated`: task files, test paths, build or verification commands, public interfaces, migration files, or integration points. Record inspected paths or commands in the report. If repository access is unavailable, state the limitation and lower confidence when source precision matters.

## Workflow

### 1. Parse the plan and source context

Extract:
- Plan status, input mode, planning depth, and execution recommendation.
- Source artifact(s) and upstream readiness.
- Planning Blocker Summary, or template §4 **Blocking questions** and **Discovery items to inspect**, when status is `blocked` or `discovery-gated`.
- Goal, scope, non-goals, and first executable slice.
- Requirements, acceptance criteria, and source traceability matrix.
- Implementation strategy, architecture boundaries, interfaces, and dependencies.
- Test design section (TDD-first matrix, collaboration notes, red-phase specs; required for plan-guide plans — record a finding if missing).
- Task list, task ids, execution class, file ownership, files, steps, red-phase tests, test discipline, verification, and stop conditions.
- Verification matrix.
- Risk, rollout, rollback, migration, observability, and support notes.
- Execution handoff: execution waves, parallelizable work, sequential work, integration tasks, and file ownership constraints.
- Reviewer feedback status from prior loops.

If any major section is missing, continue reviewing and record it as a finding instead of stopping.

Choose review depth from the plan's planning depth, risk, source confidence, prior reviewer state, and domain. Do not use focused review when the plan has unresolved blockers, high-risk operations, cross-system dependencies, production data, security/privacy/compliance impact, migrations, or public API changes.

### 2. Select reviewer roles

Use roles as review lenses, not as a staged debate. State active reviewer roles near the start.

Default roles:
- Review Lead
- Source Alignment Auditor
- Task Decomposition Reviewer
- Technical Feasibility Reviewer
- Test Design Reviewer
- Verification Reviewer
- Risk and Release Reviewer
- Execution Readiness Reviewer

Add a Domain Specialist when the domain is explicit, implied, or requested. Use [references/reviewer-roles.md](references/reviewer-roles.md) for role selection and [references/domain-lenses.md](references/domain-lenses.md) for specialized checks.

Use fewer optional or domain-specific lenses for focused review only when the omitted lenses cannot affect execution readiness. Use all relevant domain lenses for rigorous review.

### 3. Audit the plan from multiple angles

Use the lenses that apply. Do not force irrelevant checks.

Core lenses:
- **Source alignment**: the plan covers source requirements, respects non-goals, and does not drift beyond agreed scope.
- **Completeness**: necessary tasks, dependencies, interfaces, tests, release concerns, and handoff details are present.
- **Consistency**: task ids, names, paths, types, schemas, commands, and dependencies do not contradict each other.
- **Task actionability**: a fresh implementer can execute each task without guessing what to build.
- **Task right-sizing**: tasks are reviewable and independently verifiable; independent subsystems are not tangled.
- **Technical feasibility**: architecture, data flow, integration, compatibility, migration, and performance assumptions are credible.
- **Test design quality** (plans from [../plan-guide/SKILL.md](../plan-guide/SKILL.md)): Test design section present; must-have requirements map to planned failing tests or verification checks; code tasks specify red-phase tests before production steps; test discipline is `mandatory` or justified `n/a`; Tests Designer collaboration is reflected; vague “add tests” placeholders are absent.
- **Verification quality**: validation commands and checks are concrete, expected outcomes are clear, and acceptance criteria are covered beyond automated tests alone.
- **Risk and release readiness**: rollout, rollback, observability, support, security, privacy, compliance, and operational concerns are handled when relevant.
- **Execution-agent readiness**: tasks contain enough local context for another AI agent to implement one task without reading the whole conversation.
- **Readiness and metadata quality** (plans from [../plan-guide/SKILL.md](../plan-guide/SKILL.md)): input mode and planning depth are stated; artifact status matches plan content; `validated` or `conditionally validated` is justified by review history or explicit acceptance; `blocked` or `discovery-gated` plans include a Planning Blocker Summary, or template §4 **Blocking questions** and **Discovery items to inspect**, with concrete content; research-guide handoff details are reflected when the source artifact is a research report.
- **Execution handoff quality**: each task has an execution class (`parallel`, `sequential`, or `integration`); parallel waves have disjoint file ownership; shared or ordering-dependent work is marked sequential or reserved for integration tasks; execution waves and file ownership constraints are explicit enough for [../plan-executor/SKILL.md](../plan-executor/SKILL.md).
- **Review-loop hygiene**: prior reviewer findings have visible and credible dispositions.

Apply input-mode-specific emphasis:

| input mode | review emphasis |
|---|---|
| Research handoff | Strictly compare against the research report's implementation-planning handoff, readiness, open questions, recommended slice, milestones, testing focus, and rollout notes. |
| Direct spec | Verify the plan does not invent product, architecture, or acceptance decisions absent from the spec; mark source-alignment confidence accordingly. |
| Codebase-led | Spot-check named files, interfaces, tests, commands, and repository conventions when tools are available; flag invented paths or unsupported assumptions. |
| Plan normalization | Confirm the thin/external plan was expanded into traceability, TDD-first tests, task-level verification, readiness status, and no placeholders. |
| Review repair loop | Preserve finding ids, audit dispositions before adding new findings, and use [references/re-review-protocol.md](references/re-review-protocol.md). |

Use [references/validation-rubric.md](references/validation-rubric.md) for severity and verdict rules.

### 4. Assign findings and verdict

Every material finding must include:
- Stable id such as pr-001.
- Severity.
- Affected plan section, task id, source requirement, file, or verification item.
- Issue.
- Why it matters for execution.
- Required fix.
- Recommended plan-guide action: revise plan, ask user, inspect codebase, research upstream, narrow scope, split plan, accept as execution risk, or re-review.
- Owner suggestion when useful.

Assign one verdict per [references/validation-rubric.md](references/validation-rubric.md): `validated`, `conditionally validated`, `needs revision`, or `blocked`. Never validate when source requirements, core tasks, critical verification, or mandatory TDD test design for code-producing work is missing. When essential source context is absent or unverifiable, the verdict cannot be `validated` or `conditionally validated`; use `needs revision` or `blocked` and record the missing context as a blocker finding.

### 5. Self-review before handoff

Before presenting the report, run [references/review-quality-checklist.md](references/review-quality-checklist.md). Fix the report inline when the checklist catches a mismatch between severity, verdict, gate, or Guide handoff content.

### 6. Produce the review-report

Use [references/review-report-template.md](references/review-report-template.md) as the default structure. Keep the report concise but specific enough for plan-guide to repair the plan.

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

For updated plans, follow [references/re-review-protocol.md](references/re-review-protocol.md): after a `blocked` verdict, the repaired plan must be re-reviewed before execution. After `needs revision`, re-review the updated plan unless every finding was trivial and self-evidently fixed. After `conditionally validated`, re-review only if the conditions changed the plan's structure or risk; otherwise proceed with the accepted risks recorded.

## Quality bar

A strong plan review:
- Names active reviewer lenses.
- Gives a clear verdict, confidence, and execution recommendation.
- Prioritizes findings by execution impact.
- Distinguishes source-alignment defects from plan-format defects.
- Identifies where an implementer would get stuck or build the wrong thing.
- Converts criticism into specific plan-guide repair actions.
- Avoids nitpicking when the plan is executable.
- Preserves uncertainty when source context is missing.
- Produces a Guide handoff packet that makes the next plan iteration obvious.
