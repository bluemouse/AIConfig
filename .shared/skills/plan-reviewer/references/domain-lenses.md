# Domain Lenses

Use these prompts when the plan involves the domain. Select only relevant checks.

## General software engineering

- Does the plan identify modules, interfaces, dependencies, and sequencing?
- Does each task have a concrete implementation and verification path?
- Are test commands and expected outcomes specific?
- Are compatibility, release, rollback, and observability addressed?
- Does the plan avoid inventing repository facts not present in context?

## Graphics and rendering

Use when the plan concerns graphics, rendering, CAD visualization, GPU features, OpenGL, Vulkan, shaders, viewports, materials, scene graphs, visual fidelity, or realtime rendering.

Check:
- Target platforms, graphics APIs, driver constraints, feature levels, and fallback behavior.
- Rendering pipeline impact, command submission, synchronization, resource lifetime, memory pressure, and frame pacing.
- Shader changes, material interactions, color management, units, precision, coordinate spaces, and asset/model complexity.
- Interaction with selection, highlighting, overlays, lighting, post-processing, and viewport invalidation.
- Performance budgets for representative and worst-case scenes.
- Visual regression strategy: golden images, tolerances, determinism, flake control, and manual visual QA.
- Debuggability, telemetry, crash diagnostics, and customer-support impact.

## Security, privacy, and compliance

- Are permissions, data access, secrets, audit logs, and retention handled?
- Is least privilege preserved?
- Are regulated or customer-sensitive data flows identified?
- Are destructive or irreversible operations gated?
- Are compliance claims supported by source context or marked for qualified review?

## Data and AI

- Are data contracts, lineage, quality checks, and failure modes defined?
- Are metrics, evaluation datasets, and acceptance thresholds specified?
- Are drift, bias, hallucination, feedback loops, and monitoring addressed where relevant?
- Is rollback possible if model or data behavior regresses?

## Infrastructure and DevOps

- Are deployment environments and CI/CD impacts explicit?
- Are feature flags, config, secrets, migrations, and rollback addressed?
- Are observability, alerts, SLO/SLA impact, runbooks, and incident response included?
- Does the plan avoid unsafe production assumptions?

## UX, accessibility, and workflow

- Are loading, empty, error, success, disabled, and permission states specified?
- Are accessibility, keyboard navigation, screen reader impact, contrast, localization, and responsive behavior covered when relevant?
- Does the plan preserve existing workflow conventions?
- Are support and onboarding implications addressed?

## Performance and reliability

- Are target metrics concrete, such as p95 latency, memory budget, frame time, throughput, or error budget?
- Are representative workloads named?
- Are profiling, regression thresholds, monitoring, and fallback behavior specified?
- Are concurrency, retries, timeouts, caching, and failure isolation considered?

## Migration and compatibility

- Is the migration reversible or safely recoverable?
- Are old and new formats/APIs supported during transition when needed?
- Are data validation, backfill, repair, and audit steps specified?
- Are versioning, deprecation, and customer communication handled?
