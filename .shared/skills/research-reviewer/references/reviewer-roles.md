# Reviewer Roles

Use roles as review lenses. Do not stage a dialogue between roles. Select a compact set of roles, synthesize their findings, and report the result.

## Core roles

| role | activate when | primary checks | common challenges |
|---|---|---|---|
| Review Lead | Always | Scope the audit, choose posture, synthesize verdict, avoid over-reviewing low-risk material. | Is the verdict justified by the findings? Are we blocking on issues that truly block planning? |
| Requirements Auditor | Requirements, acceptance criteria, or scope are present. | Testability, priority, traceability to goals, non-goal conflicts, missing acceptance signals. | Could two implementers build different things from this requirement? |
| Evidence Auditor | Claims, assumptions, research conclusions, or metrics are present. | Source quality, confidence labels, unsupported claims, inference vs fact separation. | Which claims would fail if the evidence is wrong or stale? |
| Skeptic / Red Team | Always; strengthen in aggressive mode. | Hidden assumptions, counterexamples, failure cases, untested trade-offs, premature convergence. | What would make the recommendation wrong? |
| Implementation Readiness Reviewer | Always before a planning handoff. | Dependencies, open questions, rollout, testing focus, owners, planning-blocking decisions. | What would an implementation planner have to invent? |
| Domain Specialist | A domain is stated, implied, or requested. | Domain constraints, terminology, risks, standards, specialized failure modes. | What domain-specific issue would a general reviewer miss? |

## Optional roles

| role | activate when | primary checks |
|---|---|---|
| Product Strategy Reviewer | Adoption, market, prioritization, roadmap, value, or differentiation matters. | Strategic fit, value clarity, opportunity cost, adoption path, stakeholder incentives. |
| UX / Workflow Reviewer | End users, workflows, accessibility, or change management matters. | Workflow fit, friction, accessibility, localization, cognitive load, support burden. |
| Technical Architecture Reviewer | Architecture, integrations, APIs, data contracts, performance, or platform impact matters. | Feasibility, coupling, migration, compatibility, observability, technical debt. |
| Security / Privacy / Compliance Reviewer | Data, identity, permissions, regulated contexts, enterprise deployments, or auditability matters. | Threat model gaps, data exposure, consent, retention, least privilege, compliance claims. |
| Data / AI Evaluation Reviewer | Analytics, data pipelines, recommendations, automation, ml, llms, or evaluation matters. | Ground truth, eval metrics, drift, bias, data quality, explainability, monitoring. |
| Operations / Support Reviewer | Rollout, incident handling, support, reliability, or administration matters. | Runbooks, monitoring, rollback, sla/slo impact, support ownership, customer communication. |
| Financial / Business Reviewer | Cost, pricing, revenue, procurement, or resourcing matters. | Cost model, return assumptions, budget risk, commercial constraints. |

## Role selection rules

- Use 4-6 roles for most reviews.
- Use fewer roles for short or low-risk reports.
- Add specialized roles only when they materially change findings.
- In aggressive mode, include Skeptic / Red Team and Evidence Auditor.
- If a user names a domain, include a Domain Specialist for that domain.
- If the domain is unclear but implied, state the inferred domain and confidence.

## Domain Specialist behavior

The Domain Specialist must use domain knowledge as a lens, not as invented authority.

Always:
- State the domain being applied.
- Identify domain-specific assumptions, terminology, constraints, and failure modes.
- Mark unsupported domain claims as assumptions unless the report provides evidence.
- Avoid legal, medical, financial, or compliance certainty unless supported by qualified sources.
- Recommend targeted follow-up research when domain facts are uncertain or current.
