# Reviewer Roles

Use roles as review lenses. Do not stage a dialogue. Select a compact set of roles, synthesize findings, and report the verdict.

## Core roles

| role | activate when | primary checks | common challenge |
|---|---|---|---|
| Review Lead | Always | Scope the audit, choose posture, synthesize verdict, avoid over-reviewing style. | Is the verdict justified by execution impact? |
| Source Alignment Auditor | Source context is provided or claimed. | Requirement coverage, non-goal respect, scope drift, source-to-task traceability. | Which source requirement is missing or contradicted? |
| Task Decomposition Reviewer | Always. | Task boundaries, sequencing, dependencies, independent verifiability. | Could one task be rejected while another is approved? |
| Technical Feasibility Reviewer | Architecture, codebase, data, dependencies, APIs, or integrations matter. | Feasibility, interfaces, migration, compatibility, complexity, implementation risks. | What would break if this is implemented as written? |
| Test Design Reviewer | Always for [../../plan-guide/SKILL.md](../../plan-guide/SKILL.md) plans. | TDD-first test design section, red-phase specs, requirement-to-failing-test-or-check traceability, test discipline, Tests Designer collaboration evidence. | Which requirement lacks a planned failing test or verification check? |
| Verification Reviewer | Always. | Validation commands, manual checks, observability, expected outcomes, verification matrix coverage beyond automated tests. | How would the implementer prove the task works end-to-end? |
| Risk and Release Reviewer | Production, users, data, migration, rollout, or operations matter. | Rollback, flags, observability, security/privacy, support, runbooks, release gates. | What failure mode is unhandled? |
| Execution Readiness Reviewer | Always before execution. | Completeness for a fresh engineer or AI agent, stop conditions, handoff clarity, execution class, file ownership, and execution waves for plan-executor. | What would the executor have to invent? |

## Optional specialist roles

| role | activate when | primary checks |
|---|---|---|
| Graphics / Rendering Reviewer | Graphics, CAD visualization, GPU, OpenGL, Vulkan, shaders, viewport, material, scene graph, realtime rendering, visual fidelity. | Rendering pipeline impact, GPU capability tiers, sync/resource lifetimes, memory/frame pacing, visual regression, golden images, fallback, platform constraints. |
| Security / Privacy Reviewer | Identity, permissions, data exposure, enterprise controls, compliance, secrets. | Threat model, least privilege, secret handling, auditability, retention, consent, abuse cases. |
| Data / AI Reviewer | Data models, analytics, ML, LLMs, recommendations, evals. | Data quality, ground truth, evaluation metrics, drift, bias, monitoring, rollback. |
| Infrastructure / DevOps Reviewer | Deployment, CI/CD, services, cloud, observability, reliability. | Environments, deployment gates, monitoring, SLOs, capacity, rollback, incident response. |
| UX / Workflow Reviewer | User-facing workflows, screens, interactions, onboarding, accessibility. | States, accessibility, localization, error handling, discoverability, support burden. |
| Performance Reviewer | Latency, throughput, memory, frame time, scalability, benchmarks. | Budgets, representative workloads, profiling, regression thresholds, observability. |
| Migration / Compatibility Reviewer | Schema changes, file formats, public APIs, versioning, backward compatibility. | Migration safety, reversibility, version gates, compatibility tests, data repair. |

## Role selection rules

- Use 6-8 roles for most reviews; include Test Design Reviewer for plans from plan-guide.
- Use fewer optional/specialist roles for small, low-risk plans; keep Test Design Reviewer for plan-guide output.
- Add specialized roles only when they can find issues a general reviewer would miss.
- Include Source Alignment Auditor when a research-report, spec, requirement set, or bug report is available.
- Include Domain Specialist when the user names a domain or the plan clearly implies one.
- In aggressive mode, strengthen Source Alignment Auditor, Test Design Reviewer, Verification Reviewer, and Risk and Release Reviewer.
