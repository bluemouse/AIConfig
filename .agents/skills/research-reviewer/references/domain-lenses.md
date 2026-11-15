# Domain Lenses

Use these prompts when a domain is stated, implied, or requested. Select only the relevant questions.

## Technical architecture

- Are architecture constraints explicit enough to plan?
- Are dependencies, integrations, and data contracts identified?
- Are backward compatibility, migration, versioning, and rollout considered?
- Are performance, scalability, reliability, and observability requirements testable?
- Does the report confuse research outcomes with implementation tasks?

## Graphics and rendering

Use when the report concerns graphics, rendering, cad visualization, gpu features, opengl, vulkan, shaders, scene graphs, viewports, materials, ray tracing, realtime rendering, or visual fidelity.

Check:
- Target platforms, graphics apis, driver constraints, gpu capability tiers, and fallback behavior.
- Rendering pipeline impact, shader changes, resource lifetimes, synchronization, memory pressure, and frame pacing.
- Visual quality criteria, golden images, tolerances, determinism, and regression testing approach.
- Asset/model complexity, units, precision, color management, and coordinate-system assumptions.
- Interaction with existing viewport, selection, highlighting, overlays, materials, lighting, and post-processing.
- Performance targets for representative scenes and worst-case workloads.
- Debuggability, telemetry, crash diagnostics, and customer-support implications.

## Product and strategy

- Is the target user and job-to-be-done clear?
- Is the value proposition specific and measurable?
- Are adoption barriers and stakeholder incentives addressed?
- Are alternatives evaluated against strategy, not just feasibility?
- Are scope and prioritization aligned with the stated goal?

## UX, accessibility, and workflow

- Is the primary workflow concrete enough to test?
- Are edge workflows and error states considered?
- Are accessibility, localization, onboarding, and discoverability addressed where relevant?
- Does the report account for change management and support burden?
- Are success metrics observable from user behavior?

## Security, privacy, and compliance

- Are data classification, identity, authorization, retention, audit, and consent issues identified?
- Are trust boundaries, abuse cases, and threat models addressed at the right depth?
- Are compliance claims sourced or marked as assumptions?
- Are mitigations actionable and assigned to a planning phase or owner?
- Is sensitive data minimized and protected by design?

## Data and analytics

- Are data sources, definitions, ownership, freshness, quality, and lineage clear?
- Are metrics defined with numerator, denominator, segment, and measurement window when needed?
- Are instrumentation and validation plans included?
- Are privacy, retention, access, and governance constraints addressed?
- Are decisions robust to missing, biased, stale, or low-quality data?

## AI, ML, and automation

- Is the task suitable for automation or model assistance?
- Are evaluation metrics, ground truth, acceptable error bounds, and failure handling defined?
- Are hallucination, bias, drift, prompt injection, privacy, explainability, and human override considered where relevant?
- Is monitoring and rollback addressed?
- Are model capability claims supported or marked as assumptions?

## Infrastructure and devops

- Are deployment, scaling, observability, incident response, and rollback addressed?
- Are operational owners and support boundaries clear?
- Are build, release, environment, and compatibility constraints identified?
- Are cost and capacity assumptions visible?
- Are reliability targets testable?

## Enterprise workflow

- Are permissions, tenant boundaries, admin controls, auditability, and governance addressed?
- Are integration points with existing systems and workflows clear?
- Are migration, rollout, training, and support plans considered?
- Are enterprise buyer, admin, and end-user needs separated?

## Regulated or high-stakes domains

For healthcare, finance, legal, safety-critical, education assessment, or compliance-heavy domains:
- Do not provide unsupported professional certainty.
- Mark regulatory or policy claims as requiring qualified verification unless cited.
- Review for auditability, accountability, explainability, human oversight, and harm mitigation.
- Escalate unsupported high-impact claims to blocker or major depending on planning impact.
