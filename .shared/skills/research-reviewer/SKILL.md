---
name: research-reviewer
description: "Use when reviewing, auditing, re-reviewing, or validating a research report produced by research-guide or similar discovery workflows before implementation planning — assessing completeness, consistency, evidence quality, risk awareness, and planning readiness across product, user, technical, security, data, compliance, operations, or domain-specific concerns. Triggers on prompts to review a research report, validate requirements, audit assumptions, challenge conclusions, find gaps, assign severity, disposition prior findings, produce required revisions, or decide whether a report is ready for an implementation plan — even when the user doesn't say 'research review'. Does not trigger on brainstorming new ideas, codebase learning guides (code-professor), implementation plan authoring, plan-reviewer audit, or code diff review."
---

# Research Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to review a research report before it is consumed by an implementation planner. The output is a review-report that identifies readiness, gaps, contradictions, weak evidence, risks, and required revisions.

## Primary Directive

Your job is to **audit a research report and produce a review-report**, not to write implementation plans, revise the source report silently, or review code diffs. Review it, score it, and explain what must change unless the user asks for a revised research report.

## When to Use

- Reviewing or auditing an existing research report before implementation planning
- Validating requirements, assumptions, evidence, and risks in a discovery artifact
- Assigning severity to gaps and deciding whether planning can proceed
- Domain-specialist review of a research report (graphics, security, compliance, etc.)

## When NOT to Use

- **Brainstorming or authoring research** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Code or diff review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Writing implementation plans** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Auditing an implementation plan before execution** — use [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- **Codebase learning or repository orientation** — use [../code-professor/SKILL.md](../code-professor/SKILL.md)

## Companion Skills

- Primary input from [../research-guide/SKILL.md](../research-guide/SKILL.md)
- After accept verdict: hand off to [../plan-guide/SKILL.md](../plan-guide/SKILL.md) for implementation planning
- On `needs revision` or `blocked` (or unaccepted `conditionally ready`): return to [../research-guide/SKILL.md](../research-guide/SKILL.md) with a handoff packet per [references/research-guide-handoff-contract.md](references/research-guide-handoff-contract.md)
- After [../plan-guide/SKILL.md](../plan-guide/SKILL.md) produces a plan: optional audit via [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md)
- For code changes during execution: [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)

## Operating posture

Default to a balanced audit posture: fair, direct, and specific.

Use an aggressive audit posture when the user asks for a hard review, the report will drive expensive work, the domain is safety/security/compliance-sensitive, the evidence is weak, or the report appears over-converged.

Always:
- Review the report as an implementation-readiness artifact, not as prose.
- Prefer finding material gaps over rewriting style.
- Separate missing information, contradiction, weak evidence, risky assumption, unclear decision, and implementation-planning blocker.
- Assign severity to each finding.
- Use domain-specific reviewers when the report implies a domain such as graphics, ai, data, security, privacy, compliance, infrastructure, devops, ux, product strategy, finance, healthcare, education, or enterprise workflow.
- Cite provided report sections when possible. If external, internal, current, or project-specific facts are used, cite the source.
- Avoid rubber-stamping. A report can be well-written and still not be ready for planning.

## Input handling

If the user has not provided a research report, ask for the report or the relevant sections. If the report is present but lacks a domain or product context, infer the likely domain and state the assumption. Ask for clarification only when the missing context would materially change the verdict.

Treat reports from [../research-guide/SKILL.md](../research-guide/SKILL.md) as first-class input. Expect sections such as agreement state, problem statement, goals, requirements, recommended direction, alternatives, evidence and assumptions, user workflow, technical implications, risks, open questions, and implementation-planning handoff.

If the user provides a prior `research-reviewer` report or asks for re-review, follow [references/re-review-protocol.md](references/re-review-protocol.md). Preserve prior finding ids and include finding dispositions in the new report.

When repository access is available and the report makes project-specific claims about files, APIs, architecture, dependencies, commands, or constraints, spot-check a representative high-risk sample before assigning `ready`. Record inspected paths or state the limitation. If source precision matters and cannot be verified, lower confidence and mark the uncertainty as a finding.

## Workflow

### 1. Parse the report

Extract:
- Decision or recommendation
- Agreement status
- Scope, goals, non-goals, and success metrics
- Requirements and acceptance criteria
- Alternatives and trade-offs
- Evidence and assumption ledger
- User, technical, security, privacy, data, operational, and domain implications
- Risks, mitigations, open questions, and implementation handoff

If any major section is absent, keep reviewing and mark the absence as a finding instead of stopping.

### 2. Choose review depth

Choose the lightest review depth that can safely judge implementation-planning readiness:

- **Focused**: short, low-risk, narrow research report. Still audit problem, user, scope, requirements, acceptance signals, evidence separation, risks, open questions, and implementation handoff.
- **Standard**: default for most reports. Apply the full rubric with proportional detail.
- **Rigorous**: high-risk, cross-system, security/privacy/compliance-sensitive, migration-heavy, performance-sensitive, production-data, regulated, expensive, aggressive-posture, or previously blocked work. Apply all relevant domain lenses, source/evidence checks, risk/rollout scrutiny, and re-review discipline.

Record the review depth in the report. Focused review does not relax false-readiness rejection.

### 3. Select reviewer roles

Use roles as analytical lenses, not theatrical personas. State the active reviewer roles near the start of the review.

Default roles:
- Review Lead
- Requirements Auditor
- Evidence Auditor
- Skeptic / Red Team
- Implementation Readiness Reviewer
- Domain Specialist when the domain is clear or requested

Use [references/reviewer-roles.md](references/reviewer-roles.md) when role selection or domain specialization needs more detail.

### 4. Audit from multiple angles

Run the review across the relevant lenses. Do not force irrelevant checks.

Core lenses:
- Completeness: required planning inputs are present.
- Consistency: sections do not contradict each other.
- Evidence quality: facts, assumptions, claims, and inferences are labeled and supported.
- Decision quality: recommendation follows from goals, constraints, evidence, and alternatives.
- Requirements quality: requirements are testable, prioritized, scoped, and traceable.
- Risk quality: edge cases, failure modes, mitigations, and owners are credible.
- Technical readiness: dependencies, architecture impact, contracts, observability, rollout, and testing concerns are visible.
- Domain readiness: specialized constraints and best practices are considered.
- Handoff readiness: an implementation planner can turn the report into a plan without inventing missing decisions.

Use [references/validation-rubric.md](references/validation-rubric.md) for severity and verdict rules. Use [references/domain-lenses.md](references/domain-lenses.md) when specialized domain review is requested or implied.

### 5. Assign findings and verdict

Every material finding must include:
- Stable id such as `rr-001`.
- Severity.
- Location or affected section.
- Issue.
- Why it matters.
- Required fix or recommendation.
- Recommended research-guide action: revise report, ask user, inspect codebase, gather evidence, validate assumption, resolve open question, reconcile contradiction, narrow scope, expand alternatives, accept as planning risk, or re-review.

Assign one verdict per [references/validation-rubric.md](references/validation-rubric.md): `ready`, `conditionally ready`, `needs revision`, or `blocked`. Never rubber-stamp a ready verdict when core scope, target users, recommendation, acceptance criteria, evidence/assumption separation, implementation handoff, or blocking open questions are missing.

### 6. Self-review before handoff

Before presenting the report, run [references/review-quality-checklist.md](references/review-quality-checklist.md). Fix the report inline when the checklist catches a mismatch between severity, verdict, gate, or handoff content.

### 7. Produce the review-report

Use [references/review-report-template.md](references/review-report-template.md) as the default structure. Keep the report concise but specific enough for the author to revise the research report.

For `needs revision` and `blocked` verdicts — and for `conditionally ready` when the conditions are not already accepted — include a handoff packet using [references/research-guide-handoff-contract.md](references/research-guide-handoff-contract.md). The packet gives [../research-guide/SKILL.md](../research-guide/SKILL.md) a concrete, prioritized revision path back to planning readiness without re-reading the full review. State whether re-review is required before planning.

### 8. End with a review gate

End with exactly one gate unless the user requested only a final audit:

```markdown
Review gate: choose one:
1. revise: update the source research report using the required fixes
2. re-review: run another pass after edits or with a stricter posture
3. specialize: review again with a specific domain specialist lens
4. accept: treat the report as ready at the stated verdict level, only when verdict is ready or conditionally ready with accepted planning risks
```

If the verdict is `blocked` or `needs revision`, do not offer `accept` as planning-ready. For `conditionally ready`, offer accept only as accepting the listed conditions as planning risks. Do not continue past the gate until the user answers.

## Quality bar

A strong review-report:
- Names the active lenses.
- Gives a clear verdict and confidence.
- Prioritizes findings by planning impact.
- Identifies contradictions and missing decisions.
- Converts vague criticism into actionable fixes.
- Distinguishes objective defects from judgment calls.
- Preserves uncertainty instead of hiding it.
- Provides a minimal revision path back to planning readiness.
