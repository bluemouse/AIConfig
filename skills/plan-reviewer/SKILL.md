---
name: plan-reviewer
description: "Use when reviewing, auditing, or validating an implementation plan before execution by a developer, engineer, or AI agent — checking correctness, completeness, consistency with source research/spec/requirements, task decomposition, file precision, testability, risk controls, and execution readiness. Triggers on prompts to review an implementation plan, validate a work plan, audit plan tasks, approve execution readiness, or produce a Guide handoff packet — even when the user doesn't say 'plan review'. Does not trigger on brainstorming, research-report review, writing plans, or code diff review."
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

## Companion Skills

- Primary input from [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- Compare against research-report context from [../research-guide/SKILL.md](../research-guide/SKILL.md)
- Upstream research audit: [../research-reviewer/SKILL.md](../research-reviewer/SKILL.md)
- For code review during execution: [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)

Treat plans from [../plan-guide/SKILL.md](../plan-guide/SKILL.md) as the preferred input format. Compare the plan against the source research-report, spec, requirements, bug report, issue, or codebase context when available.

## Review posture

Default to a balanced posture: rigorous, specific, and focused on execution impact.

Use an aggressive posture when the plan affects high-risk areas, cross-system architecture, production data, security/privacy/compliance, migrations, public APIs, performance budgets, user-visible workflows, irreversible operations, or when the source context and plan do not clearly align.

Always:
- Validate the plan against the source context, not against personal style preferences.
- Focus on whether an implementer can execute the plan correctly without inventing missing decisions.
- Distinguish blocker, major, minor, question, and nit findings.
- Identify contradictions, missing steps, vague tasks, untestable criteria, invalid sequencing, and unsupported assumptions.
- Use domain-specific reviewer roles when the plan implies specialized knowledge.
- Prefer actionable findings with exact affected task ids, sections, files, or requirements.
- Reject false readiness. A polished plan can still be unsafe to execute.
- End with a Guide handoff packet for plan-guide.

## Input handling

If the user provides only a plan and no source context, review what can be reviewed, but lower confidence and mark any source-alignment uncertainty. If source alignment is essential and absent, make that a major or blocker finding.

If the plan includes previous plan-reviewer findings, preserve finding ids for unresolved issues and add new ids only for new issues.

If the plan claims to be validated, check whether the reviewer feedback status justifies that claim.

## Workflow

### 1. Parse the plan and source context

Extract:
- Plan status and execution recommendation.
- Source artifact(s) and upstream readiness.
- Goal, scope, non-goals, and first executable slice.
- Requirements, acceptance criteria, and source traceability matrix.
- Implementation strategy, architecture boundaries, interfaces, and dependencies.
- Task list, task ids, files, steps, tests, verification, and stop conditions.
- Verification matrix.
- Risk, rollout, rollback, migration, observability, and support notes.
- Reviewer feedback status from prior loops.

If any major section is missing, continue reviewing and record it as a finding instead of stopping.

### 2. Select reviewer roles

Use roles as review lenses, not as a staged debate. State active reviewer roles near the start.

Default roles:
- Review Lead
- Source Alignment Auditor
- Task Decomposition Reviewer
- Technical Feasibility Reviewer
- Verification Reviewer
- Risk and Release Reviewer
- Execution Readiness Reviewer

Add a Domain Specialist when the domain is explicit, implied, or requested. Use [references/reviewer-roles.md](references/reviewer-roles.md) for role selection and [references/domain-lenses.md](references/domain-lenses.md) for specialized checks.

### 3. Audit the plan from multiple angles

Use the lenses that apply. Do not force irrelevant checks.

Core lenses:
- **Source alignment**: the plan covers source requirements, respects non-goals, and does not drift beyond agreed scope.
- **Completeness**: necessary tasks, dependencies, interfaces, tests, release concerns, and handoff details are present.
- **Consistency**: task ids, names, paths, types, schemas, commands, and dependencies do not contradict each other.
- **Task actionability**: a fresh implementer can execute each task without guessing what to build.
- **Task right-sizing**: tasks are reviewable and independently verifiable; independent subsystems are not tangled.
- **Technical feasibility**: architecture, data flow, integration, compatibility, migration, and performance assumptions are credible.
- **Verification quality**: tests and checks are concrete, expected outcomes are clear, and acceptance criteria are covered.
- **Risk and release readiness**: rollout, rollback, observability, support, security, privacy, compliance, and operational concerns are handled when relevant.
- **Execution-agent readiness**: tasks contain enough local context for another AI agent to implement one task without reading the whole conversation.
- **Review-loop hygiene**: prior reviewer findings have visible and credible dispositions.

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

Assign one verdict per [references/validation-rubric.md](references/validation-rubric.md): `validated`, `conditionally validated`, `needs revision`, or `blocked`. Never validate when source requirements, core tasks, or critical verification are missing.

### 5. Produce the review-report

Use [references/review-report-template.md](references/review-report-template.md) as the default structure. Keep the report concise but specific enough for plan-guide to repair the plan.

The review-report must include a **Guide handoff packet**. This packet is the contract with plan-guide; use [references/guide-handoff-contract.md](references/guide-handoff-contract.md) for semantics.

### 6. End with a review gate

End with one gate unless the user requested only a final audit:

```markdown
Review gate: choose one:
1. return-to-guide: give the Guide handoff packet to plan-guide for targeted repair
2. re-review: review an updated plan or run a stricter pass
3. specialize: review again with a named domain specialist lens
4. accept: treat the plan as executable at the stated verdict level
```

If the verdict is blocked or needs revision, do not offer execution as ready. If the verdict is conditionally validated, make the accepted execution risks explicit before any execution handoff.

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
