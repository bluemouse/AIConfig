# Examples

These examples demonstrate structure and decision logic. Keep real reviews specific to the user's facts.

## Example 1: Fixable Critical Finding

### Input

"Move every service to microservices this quarter to improve team velocity."

### Condensed Finding

#### F-01 - Shared data model makes independent deployment illusory

- **Severity:** S3 - Critical
- **Disposition:** Conditionally fixable
- **Affected claim:** Splitting services will let teams deploy independently.
- **Reasoning chain:** Shared transactional schema -> services require coordinated schema changes -> releases remain coupled while operational complexity increases -> velocity falls and incident surface expands -> teams lose trust in the migration.
- **Evidence and confidence:** Existing services share cross-domain transactions; confidence medium until dependency mapping is complete.
- **Why current controls are insufficient:** Service boundaries alone do not remove data coupling.
- **Resolution A:** Map domain ownership and extract one bounded context with an anti-corruption layer. Measure lead time and cross-team coordination before scaling.
- **Resolution B:** Keep a modular monolith and enforce module boundaries if independent scaling is not yet required.
- **Validation gate:** Proceed to a second extraction only if the pilot reduces lead time by at least 20% without increasing severity-one incidents or on-call load.
- **Residual risk:** Temporary duplication and migration overhead remain.

**Verdict:** REWORK, not reject. The objective is viable, but the all-services/one-quarter implementation is not.

## Example 2: Evidence Weakness with Experiment

### Input

"Raise prices 20% because pilot customers said the product is underpriced."

### Condensed Finding

#### F-02 - Stated willingness to pay is not representative purchase behavior

- **Severity:** S2 - Material
- **Disposition:** Fixable
- **Affected claim:** Existing customer comments predict broad retention at a 20% increase.
- **Reasoning chain:** Favorable pilot sample -> overstated willingness to pay -> broad increase causes segment-specific churn -> revenue gain is offset and acquisition becomes harder.
- **Evidence and confidence:** Small, self-selected sample; evidence grade C and confidence medium.
- **Resolution A:** Run a segmented price test with explicit retention and expansion thresholds.
- **Resolution B:** Package the increase with differentiated value and grandfather price-sensitive cohorts.
- **Validation gate:** Expand only if net revenue retention improves and churn remains within the predefined segment limit for two billing cycles.
- **Residual risk:** Competitor response and long-term brand perception remain uncertain.

**Verdict:** PROCEED WITH CONDITIONS.

## Example 3: Show-Stopper Marked Not Fixable

### Input

"Launch a medical diagnostic feature next month. The launch date cannot move, no clinical validation is planned, and the output will directly determine treatment."

### Condensed Finding

#### F-01 - Required safety evidence cannot exist before irreversible clinical use

- **Severity:** S4 - Show-stopper
- **Disposition:** Not fixable
- **Affected claim:** The feature can safely determine treatment next month without validation.
- **Reasoning chain:** No clinical validation -> unknown error rates and population bias -> incorrect treatment recommendations -> patient harm and unacceptable legal/regulatory exposure -> product and organizational viability are threatened.
- **Evidence and confidence:** The absence of validation is explicit; confidence high.
- **Why all repair classes fail:** Guardrails, monitoring, or rollback do not prevent first-use harm when the output directly determines treatment. Proper validation cannot be completed within the non-negotiable launch date. Changing the output to non-clinical decision support would create a fundamentally different proposal.
- **Changed constraint that restores viability:** Move the date, validate clinically, obtain specialist and regulatory review, and restrict use until safety thresholds are met.
- **Rejection recommendation:** Do not launch the proposal as defined.

**Verdict:** REJECT.

## Example 4: Replace with a Superior Alternative

### Input

"Build a custom workflow engine to automate an internal approval process used by twelve people."

### Condensed Synthesis

The custom engine is technically possible, but maintenance, exception handling, auditability, and ownership create recurring cost disproportionate to the use case. A configurable existing workflow platform or a constrained rules service achieves the objective sooner and preserves exit options.

**Verdict:** REPLACE.

**Preferred replacement:** Configure an existing platform for the common path, retain a manual exception route, and reassess custom development only after volume or constraints exceed explicit thresholds.
