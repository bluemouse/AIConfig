# Domain Lenses (shared by plan-reviewer and research-reviewer)

Use these prompts when the domain is stated, implied, or requested. Select only the
relevant questions. plan-reviewer applies them to an implementation plan;
research-reviewer applies them to a research report.

## Shared lenses

### Graphics and rendering

Use when the artifact concerns graphics, rendering, CAD visualization, GPU features, OpenGL, Vulkan, shaders, scene graphs, viewports, materials, ray tracing, realtime rendering, or visual fidelity.

Check:
- Target platforms, graphics APIs, driver constraints, GPU capability tiers, and fallback behavior.
- Rendering pipeline impact, command submission, synchronization, resource lifetimes, memory pressure, and frame pacing.
- Shader changes, material interactions, color management, units, precision, coordinate spaces, and asset/model complexity.
- Interaction with existing viewport, selection, highlighting, overlays, lighting, and post-processing.
- Performance budgets for representative and worst-case scenes.
- Visual regression strategy: golden images, tolerances, determinism, flake control, and manual visual QA.
- Debuggability, telemetry, crash diagnostics, and customer-support implications.

### Security, privacy, and compliance

- Are permissions, data classification, identity, authorization, data access, secrets, audit logs, retention, and consent handled?
- Are trust boundaries, abuse cases, and threat models addressed at the right depth?
- Is least privilege preserved; are destructive or irreversible operations gated?
- Are compliance claims supported by source context or marked for qualified review?
- (research) Are mitigations actionable and assigned to a planning phase or owner?

### Data and AI

- Are data contracts, sources, definitions, lineage, quality checks, ownership, and failure modes defined?
- Are metrics, evaluation datasets, ground truth, and acceptance thresholds specified (research: numerator, denominator, segment, measurement window when needed)?
- Are drift, bias, hallucination, feedback loops, prompt injection, and monitoring addressed where relevant?
- Is rollback possible if model or data behavior regresses?
- Are model/automation capability claims supported or marked as assumptions?

### Infrastructure and DevOps

- Are deployment environments, scaling, CI/CD impacts, and release constraints explicit?
- Are feature flags, config, secrets, migrations, and rollback addressed?
- Are observability, alerts, SLO/SLA impact, runbooks, incident response, and operational owners included?
- Are cost and capacity assumptions visible, and reliability targets testable?

### UX, accessibility, and workflow

- Are loading, empty, error, success, disabled, and permission states specified; are edge workflows considered?
- Are accessibility, keyboard navigation, screen reader impact, contrast, localization, and responsive behavior covered when relevant?
- Does the artifact preserve existing workflow conventions and account for change management, onboarding, and support burden?
- (research) Are success metrics observable from user behavior?

### Performance and reliability

- Are target metrics concrete, such as p95 latency, memory budget, frame time, throughput, or error budget?
- Are representative workloads named; are profiling, regression thresholds, monitoring, and fallback behavior specified?
- Are concurrency, retries, timeouts, caching, and failure isolation considered?

### Migration and compatibility

- Is the migration reversible or safely recoverable?
- Are old and new formats/APIs supported during transition when needed?
- Are data validation, backfill, repair, versioning, deprecation, and customer communication handled?

## Plan-specific lens (plan-reviewer)

### General software engineering

- Does the plan identify modules, interfaces, dependencies, and sequencing?
- Does each task have a concrete implementation and verification path?
- Does each code-producing task specify red-phase failing tests before production steps (`mandatory`), or a stated alternative verification (`verification-led`)?
- Are test commands and expected outcomes specific?
- Does the plan avoid inventing repository facts not present in context?

## Research-specific lenses (research-reviewer)

### Technical architecture

- Are architecture constraints explicit enough to plan?
- Are dependencies, integrations, and data contracts identified?
- Are backward compatibility, migration, versioning, and rollout considered?
- Are performance, scalability, reliability, and observability requirements testable?
- Does the report confuse research outcomes with implementation tasks?

### Product and strategy

- Is the target user and job-to-be-done clear; is the value proposition specific and measurable?
- Are adoption barriers and stakeholder incentives addressed?
- Are alternatives evaluated against strategy, not just feasibility?
- Are scope and prioritization aligned with the stated goal?

### Enterprise workflow

- Are permissions, tenant boundaries, admin controls, auditability, and governance addressed?
- Are integration points with existing systems and workflows clear?
- Are migration, rollout, training, and support plans considered?
- Are enterprise buyer, admin, and end-user needs separated?

### Regulated or high-stakes domains

For healthcare, finance, legal, safety-critical, education assessment, or compliance-heavy domains:
- Do not provide unsupported professional certainty.
- Mark regulatory or policy claims as requiring qualified verification unless cited.
- Review for auditability, accountability, explainability, human oversight, and harm mitigation.
- Escalate unsupported high-impact claims to blocker or major depending on planning impact.
