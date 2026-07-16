# Planning Roles

Use these roles as lenses. Do not produce separate speeches from each role; synthesize them into plan decisions, tasks, risks, and questions.

## Core roles

| role | activate when | primary checks |
|---|---|---|
| Plan Lead | Always | Planning mode, readiness, scope, output shape, loop control. |
| Requirements Mapper | Any source requirements exist | Requirement coverage, priority, acceptance criteria, non-goal conflicts, traceability. |
| Architecture Planner | Existing system, new architecture, integrations, APIs, or data contracts matter | Boundaries, interfaces, dependencies, sequencing, compatibility, migration. |
| Tests Designer | Always (implementation plans) | TDD-first test scenarios from requirements and architecture; red-phase specs; edge and negative cases; test file/name/fixture plans; collaboration with Requirements Mapper, Architecture Planner, Task Decomposer, and Verification Planner. |
| Task Decomposer | Always | Cohesive task slices, dependency order, review checkpoints, independently testable deliverables shaped by planned failing tests. |
| Verification Planner | Always | Validation commands, manual checks, observability signals, expected outcomes, verification matrix; complements Tests Designer automated test plans. |
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

## Tests Designer collaboration loop

Tests Designer is mandatory for every implementation plan. Do not treat test design as a final polish step.

Run an iterative loop with these roles until test plans, tasks, and verification align:

1. **Requirements Mapper → Tests Designer**: acceptance criteria and constraints become test scenarios.
2. **Architecture Planner → Tests Designer**: boundaries and interfaces become unit, integration, and contract test scope.
3. **Tests Designer → Task Decomposer**: red-phase test slices inform task boundaries and order.
4. **Task Decomposer → Tests Designer**: concrete deliverables refine per-task failing tests.
5. **Tests Designer ↔ Verification Planner**: automated tests plus manual checks, commands, and observability cover every must-have requirement.
6. **Repeat** until conflicts between test design, architecture, and task decomposition are resolved.

Tests Designer owns aggressive automated test planning. Verification Planner owns the broader verification matrix (manual, performance, security, observability, rollout checks). Neither role substitutes for the other.

## Role selection rules

- Use 5-7 roles for most plans; Tests Designer is always active for implementation plans.
- Add a Domain Specialist when the domain is explicit, implied, or requested.
- Strengthen Requirements Mapper, Tests Designer, and Verification Planner for plan-reviewer repair iterations.
- Strengthen Architecture Planner and Risk and Release Planner for high-risk or cross-system work.
- State active roles in the plan preface or planning notes when useful.
