# Reviewer Roles (shared by plan-reviewer and research-reviewer)

Use roles as review lenses. Do not stage a dialogue between roles. Select a compact
set of roles, synthesize their findings, and report the result. Per-skill parameters:

| parameter | plan-reviewer | research-reviewer |
|---|---|---|
| Artifact under review | implementation plan | research report |
| Success verdict | `validated` | `ready` |

## Shared core roles

| role | activate when | primary checks | common challenge |
|---|---|---|---|
| Review Lead | Always | Scope the audit, choose posture, synthesize verdict, avoid over-reviewing style. | Is the verdict justified by downstream impact? Are we blocking on issues that truly block it? |
| Source Alignment Auditor | Source context is provided or claimed. | Requirement coverage, non-goal respect, scope drift, source-to-artifact traceability. | Which source requirement is missing or contradicted? |
| Skeptic / Red Team | Always; strengthen in aggressive mode. | Hidden assumptions, counterexamples, failure cases, untested trade-offs, premature convergence. | What would make the recommendation wrong? |
| Downstream Readiness Reviewer | Always before the downstream step (execution for plans; implementation planning for reports). | Completeness for a fresh consumer, stop conditions, handoff clarity, dependencies, blocking decisions. | What would the downstream consumer have to invent? |

## Plan-specific roles (plan-reviewer)

| role | activate when | primary checks | common challenge |
|---|---|---|---|
| Task Decomposition Reviewer | Always | Task boundaries, sequencing, dependencies, independent verifiability. | Could one task be rejected while another is approved? |
| Technical Feasibility Reviewer | Architecture, codebase, data, dependencies, APIs, or integrations matter. | Feasibility, interfaces, migration, compatibility, complexity, implementation risks. | What would break if implemented as written? |
| Test Design Reviewer | Always for plan-guide plans. | Test and verification design, red-phase specs for `mandatory` tasks, alternative-verification specs for `verification-led` tasks, requirement-to-failing-test-or-check traceability. | Which requirement lacks a planned failing test or verification check? |
| Verification Reviewer | Always | Validation commands, manual checks, observability, expected outcomes, verification matrix coverage beyond automated tests. | How would the implementer prove the task works end-to-end? |
| Risk and Release Reviewer | Production, users, data, migration, rollout, or operations matter. | Rollback, flags, observability, security/privacy, support, runbooks, release gates. | What failure mode is unhandled? |

## Research-specific roles (research-reviewer)

| role | activate when | primary checks | common challenge |
|---|---|---|---|
| Requirements Auditor | Requirements, acceptance criteria, or scope are present. | Testability, priority, traceability to goals, non-goal conflicts, missing acceptance signals. | Could two implementers build different things from this requirement? |
| Evidence Auditor | Claims, assumptions, research conclusions, or metrics are present. | Source quality, confidence labels, unsupported claims, inference vs fact separation. | Which claims would fail if the evidence is wrong or stale? |
| Domain Specialist | A domain is stated, implied, or requested. | Domain constraints, terminology, risks, standards, specialized failure modes. | What domain-specific issue would a general reviewer miss? |

## Optional specialist roles (both reviewers)

Activate only when the domain materially changes findings:

| role | activate when | primary checks |
|---|---|---|
| Graphics / Rendering Reviewer | Graphics, CAD visualization, GPU, OpenGL, Vulkan, shaders, viewport, material, scene graph, realtime rendering, visual fidelity. | Rendering pipeline impact, GPU capability tiers, sync/resource lifetimes, memory/frame pacing, visual regression, golden images, fallback, platform constraints. |
| Security / Privacy Reviewer | Identity, permissions, data exposure, enterprise controls, compliance, secrets. | Threat model, least privilege, secret handling, auditability, retention, consent, abuse cases. |
| Data / AI Reviewer | Data models, analytics, ML, LLMs, recommendations, evals. | Data quality, ground truth, evaluation metrics, drift, bias, monitoring, rollback. |
| Infrastructure / DevOps Reviewer | Deployment, CI/CD, services, cloud, observability, reliability. | Environments, deployment gates, monitoring, SLOs, capacity, rollback, incident response. |
| UX / Workflow Reviewer | User-facing workflows, screens, interactions, onboarding, accessibility. | States, accessibility, localization, error handling, discoverability, support burden. |
| Performance Reviewer | Latency, throughput, memory, frame time, scalability, benchmarks. | Budgets, representative workloads, profiling, regression thresholds, observability. |
| Migration / Compatibility Reviewer | Schema changes, file formats, public APIs, versioning, backward compatibility. | Migration safety, reversibility, version gates, compatibility tests, data repair. |
| Product Strategy Reviewer (research) | Adoption, market, prioritization, roadmap, value, or differentiation matters. | Strategic fit, value clarity, opportunity cost, adoption path, stakeholder incentives. |
| Financial / Business Reviewer (research) | Cost, pricing, revenue, procurement, or resourcing matters. | Cost model, return assumptions, budget risk, commercial constraints. |
| Operations / Support Reviewer (research) | Rollout, incident handling, support, reliability, or administration matters. | Runbooks, monitoring, rollback, SLA/SLO impact, support ownership, customer communication. |

## Role selection rules

- plan-reviewer: 6-8 roles for most reviews; always include Test Design Reviewer for plan-guide plans. research-reviewer: 4-6 roles for most reviews.
- Use fewer optional/specialist roles for small, low-risk artifacts.
- Add specialized roles only when they can find issues a general reviewer would miss.
- Include Source Alignment Auditor when a research report, spec, requirement set, or bug report is available; include Domain Specialist when the user names a domain or the artifact clearly implies one (state the inferred domain and confidence if only implied).
- In aggressive mode, strengthen Skeptic / Red Team and the alignment/evidence/verification roles.

## Domain Specialist behavior

The Domain Specialist must use domain knowledge as a lens, not as invented authority. State the domain being applied; identify domain-specific assumptions, terminology, constraints, and failure modes; mark unsupported domain claims as assumptions unless the artifact provides evidence; avoid legal, medical, financial, or compliance certainty unless supported by qualified sources; recommend targeted follow-up research when domain facts are uncertain or current.
