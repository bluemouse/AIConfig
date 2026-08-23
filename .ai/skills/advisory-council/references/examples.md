# Examples

## Example 1: Architecture Decision

**Request:** "Should our eight-person team split a stable monolith into microservices this year?"

**Council:**

- delivery lead: optimizes time-to-value and team throughput;
- distributed-systems architect: examines boundaries, coupling, and failure modes;
- reliability operator: evaluates observability and operational burden;
- finance stakeholder: tests total cost and opportunity cost;
- evidence auditor: checks whether scaling pain is measured or assumed.

**Likely convergence:** Keep the monolith, improve modular boundaries and observability, then extract one service only after a measured bottleneck and ownership boundary meet explicit thresholds. Preserve a minority trigger: extract sooner if release contention or independent scaling costs exceed agreed limits.

Why this works: roles differ in objectives and exposure, the answer is conditional, and the recommendation includes a reversible gate instead of generic pros and cons.

## Example 2: Product Launch Plan

**Request:** "Create the best launch approach for a paid collaboration feature."

**Council:**

- product strategist: value proposition and market fit;
- customer advocate: adoption friction and trust;
- growth lead: acquisition and monetization;
- support operator: readiness and failure handling;
- risk lead: pricing backlash, churn, and reputational downside;
- alternative architect: staged beta, packaging, and non-launch options.

**Debate movement:** Growth initially favors a broad launch; support demonstrates unresolved migration and entitlement edge cases; the customer advocate shows that pricing comprehension is weak. The council refines the recommendation to a cohort beta with explicit support readiness and pricing-comprehension gates.

## Example 3: Policy Disagreement

**Request:** "Resolve whether our team should require three office days each week."

**Council:**

- executive sponsor: coordination and organizational goals;
- employee advocate: autonomy, accessibility, and retention;
- team manager: execution and coaching;
- workplace operations lead: capacity and cost;
- evidence auditor: separates measured collaboration issues from preference;
- alternative architect: outcome-based or team-specific arrangements.

**Expected result:** Do not force consensus when the dispute is partly values-based. Return ranked policy options, state which values each privileges, identify measurable outcomes, and recommend a time-bounded pilot when evidence is weak.

## Example 4: Simulated Fallback

When agent tools are unavailable, say:

> I am running this as a simulated advisory council because independent agent tools are not available in this environment.

Then write all Round 1 positions before writing any cross-examination. Do not silently revise an earlier position to make later synthesis look cleaner; show the revision during the debate record.

## Example 5: Poor Versus Strong Role Design

**Poor council:** optimist, pessimist, realist, expert.

These labels do not define distinct evidence standards, responsibilities, or stakeholders.

**Stronger council:** security owner, delivery lead, end-user advocate, compliance specialist, systems integrator, evidence auditor.

Each role owns a different failure surface and can rationally disagree.
