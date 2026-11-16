---
name: research-reviewer
description: "Use when reviewing, auditing, re-reviewing, grilling, or validating a research report produced by research-guide or similar discovery workflows before implementation planning — assessing completeness, consistency, evidence quality, risk awareness, and planning readiness across product, user, technical, security, data, compliance, operations, or domain-specific concerns. Triggers on prompts to review or grill a research report, validate requirements, audit assumptions, challenge conclusions, find gaps, assign severity, disposition prior findings, produce required revisions, or decide whether a report is ready for an implementation plan — even when the user doesn't say 'research review'. Does not trigger on brainstorming new ideas, codebase learning guides (code-professor), implementation plan authoring, plan-reviewer audit, or code diff review."
---

# Research Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

## Primary Directive

Audit a research report and produce a review-report identifying readiness, gaps, contradictions, weak evidence, risks, and required revisions — not write implementation plans, revise the source report silently, or review code diffs. Explain what must change unless the user asks for a revised research report.

Default to a balanced audit posture: fair, direct, and specific. Use an aggressive posture when the user asks for a hard review, the work is expensive or safety/security/compliance-sensitive, the evidence is weak, or the report appears over-converged.

Always review the report as an implementation-readiness artifact, not as prose; prefer material gaps over style rewrites and assign severity to each finding; use domain-specific reviewers when the report implies a domain (see [references/domain-lenses.md](references/domain-lenses.md)); cite provided report sections when possible and the source of any external or project-specific fact used.

## Input handling

If no research report is provided, ask for it or the relevant sections. Infer an unstated domain and state the assumption; ask for clarification only when the missing context would materially change the verdict. Treat reports from [../research-guide/SKILL.md](../research-guide/SKILL.md) as first-class input. If the user provides a prior `research-reviewer` report or asks for re-review, follow [references/re-review-protocol.md](references/re-review-protocol.md); preserve prior finding ids and include finding dispositions in the new report.

When repository access is available, spot-check a high-risk sample of project-specific claims before assigning `ready`; record inspected paths or the limitation, and lower confidence with a finding if verification is impossible.

## Routing

Defer instead of reviewing: research authoring — [../research-guide/SKILL.md](../research-guide/SKILL.md) (also the return path on `needs revision` / `blocked`, with a handoff packet per [references/research-guide-handoff-contract.md](references/research-guide-handoff-contract.md)); code or diff review — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md); codebase learning — [../code-professor/SKILL.md](../code-professor/SKILL.md); writing implementation plans, the handoff target after an accept verdict — [../plan-guide/SKILL.md](../plan-guide/SKILL.md); auditing an implementation plan, optional after plan-guide — [../plan-reviewer/SKILL.md](../plan-reviewer/SKILL.md).

## Workflow

### 1. Choose review depth and roles

Choose the lightest review depth that can safely judge implementation-planning readiness, and record it in the report:

- **Focused**: short, low-risk, narrow report. Still audit problem, user, scope, requirements, acceptance signals, evidence, risks, open questions, and handoff.
- **Standard**: default for most reports. Apply the full rubric with proportional detail.
- **Rigorous**: high-risk, cross-system, security/privacy/compliance-sensitive, migration-heavy, performance-sensitive, regulated, expensive, aggressive-posture, or previously blocked work. Apply all relevant domain lenses, source/evidence checks, risk/rollout scrutiny, and re-review discipline.

Select reviewer roles as analytical lenses, not theatrical personas, per [references/reviewer-roles.md](references/reviewer-roles.md); include a Domain Specialist whenever the domain is stated, implied, or requested. State the active roles near the start of the review.

### 2. Parse and audit the report

Extract decision, scope, requirements, evidence ledger, risks, and handoff; absent sections become findings — keep reviewing instead of stopping. Then run the review across the relevant lenses. Do not force irrelevant checks.

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

Use [references/validation-rubric.md](references/validation-rubric.md) for severity and verdict rules; use [references/domain-lenses.md](references/domain-lenses.md) when specialized domain review is requested or implied.

### 3. Assign findings and verdict

Every material finding must include:
- Stable id such as `rr-001`.
- Severity.
- Location or affected section.
- Issue.
- Why it matters.
- Required fix or recommendation.
- Recommended research-guide action (revise report, ask user, inspect codebase, gather evidence, resolve open question, narrow scope, accept as planning risk, re-review, etc.).
- `root-cause-phase`: `local` (fix within the research loop) | `research` (this phase) | `plan` | `implement` | `code-review`. Use `local` for a research-report defect fixable by research-guide; an earlier phase is rare, since research is the first phase. The dev-workflow-orchestrator reads this field to route backward handoff packets; outside the orchestrator, it is informational.

Assign one verdict per [references/validation-rubric.md](references/validation-rubric.md): `ready`, `conditionally ready`, `needs revision`, or `blocked`. Never rubber-stamp a ready verdict — the rubric lists the sections whose absence or contradiction blocks `ready`.

### 4. Run Grilling Mode

Run Grilling Mode for standard and rigorous reviews by default; skip it for focused reviews unless explicitly requested, and at any depth on an explicit no-grilling request. It supplements — never replaces — evidence gathering, severity assignment, and the verdict. Build a decision tree from blocker and major findings, material questions, contradictions, and high-impact assumptions, and work it per [references/grilling-protocol.md](references/grilling-protocol.md), which defines rounds, question format, option limits, Recommended marking, stop-grilling semantics, and completion criteria.

### 5. Self-review and produce the review-report

Run [references/review-quality-checklist.md](references/review-quality-checklist.md) and fix inline any severity, verdict, gate, or handoff mismatch. Then produce the review-report using [references/review-report-template.md](references/review-report-template.md) — concise but specific enough for the author to revise the research report.

#### Artifact output path

Outside the dev-workflow-orchestrator (no assigned artifact path), write the review report to `.agents/researches/<feature-or-topic-slug>-review.md` (gitignored; never to the repository root, which risks accidental commits). Inside the orchestrator, use the assigned path instead (typically `.agents/workflow/<slug>/11-research-review.md`).

For `needs revision` and `blocked` verdicts — and unaccepted `conditionally ready` — include a handoff packet per [references/research-guide-handoff-contract.md](references/research-guide-handoff-contract.md): a concrete, prioritized revision path back to planning readiness, stating whether re-review is required before planning.

### 6. End with a review gate

End with exactly one gate unless the user requested only a final audit:

```markdown
Review gate: choose one:
1. revise: update the source research report using the required fixes
2. re-review: run another pass after edits or with a stricter posture
3. specialize: review again with a specific domain specialist lens
4. accept: treat the report as ready at the stated verdict level, only when verdict is ready or conditionally ready with accepted planning risks
```

If the verdict is `blocked` or `needs revision`, do not offer `accept` as planning-ready; for `conditionally ready`, offer accept only as accepting the listed conditions as planning risks. Do not continue past the gate until the user answers.
