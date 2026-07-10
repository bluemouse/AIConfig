# Planning Roles

Use these roles as lenses. Do not produce separate speeches from each role; synthesize them into plan decisions, tasks, risks, and questions.

## Core roles

| role | activate when | primary checks |
|---|---|---|
| Plan Lead | Always | Planning mode, readiness, scope, output shape, loop control. |
| Requirements Mapper | Any source requirements exist | Requirement coverage, priority, acceptance criteria, non-goal conflicts, traceability. |
| Architecture Planner | Existing system, new architecture, integrations, APIs, or data contracts matter | Boundaries, interfaces, dependencies, sequencing, compatibility, migration. |
| Task Decomposer | Always | Cohesive task slices, dependency order, review checkpoints, independently testable deliverables. |
| Verification Planner | Always | Unit/integration/e2e/manual/observability checks, expected outcomes, coverage of acceptance criteria. |
| Risk and Release Planner | Rollout, migration, production, security, reliability, or users are affected | Risk controls, rollback, feature flags, telemetry, support, operational readiness. |
| Execution Handoff Recorder | Always | Assumptions, stop conditions, commands, handoff notes, review status. |

## Domain specialists

Add one or more specialists only when they materially change the plan.

| specialist | use when | checks |
|---|---|---|
| Graphics / Rendering Specialist | Rendering, CAD visualization, GPU, OpenGL, Vulkan, shaders, viewports, materials, scene graphs, visual fidelity. | Pipeline impact, GPU capability tiers, shader/resource lifetimes, synchronization, memory pressure, frame pacing, golden images, tolerances, platform fallback. |
| Security / Privacy Specialist | Identity, permissions, customer data, secrets, compliance, enterprise controls. | Least privilege, data exposure, threat model, auditability, retention, consent, secrets, abuse cases. |
| Data / AI Specialist | Data pipelines, analytics, ML, LLMs, ranking, recommendations, evaluation. | Ground truth, evals, drift, bias, data quality, monitoring, fallback, explainability. |
| Infrastructure / DevOps Specialist | Deployment, services, cloud, CI/CD, observability, reliability. | Environments, migrations, rollout, rollback, SLOs, monitoring, runbooks, capacity. |
| UX / Workflow Specialist | User-facing flow, accessibility, onboarding, support, localization. | States, errors, accessibility, discoverability, copy, journey continuity, support burden. |
| Performance Specialist | Latency, throughput, memory, rendering frame time, scaling, benchmarking. | Metrics, representative workloads, budgets, profiling, regressions, thresholds. |
| Migration / Compatibility Specialist | Schema changes, API changes, file formats, backward compatibility. | Versioning, dual-write/read, migration reversibility, data safety, compatibility tests. |

## Role selection rules

- Use 4-6 roles for most plans.
- Add a Domain Specialist when the domain is explicit, implied, or requested.
- Strengthen Requirements Mapper and Verification Planner for plan-reviewer repair iterations.
- Strengthen Architecture Planner and Risk and Release Planner for high-risk or cross-system work.
- State active roles in the plan preface or planning notes when useful.
