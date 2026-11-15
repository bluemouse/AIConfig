# Re-review Protocol

Use this protocol when reviewing an updated research report after earlier `research-reviewer` findings.

## 1. Preserve finding identity

- Keep the original finding id for unresolved or partially resolved issues.
- Mark a finding **resolved** only when the updated report fully addresses the required fix.
- Mark a finding **reopened** when a previously resolved issue reappears or the repair introduces the same planning-readiness risk.
- Create a new finding id only for genuinely new issues.

## 2. Classify each prior finding

For every prior blocker, major, or material minor finding, assign one disposition:

- **Resolved**: required fix is present and credible.
- **Partially resolved**: progress was made, but implementation planning would still require invention or risky assumptions.
- **Accepted risk**: user explicitly accepted a non-blocker risk and the report records it as a planning risk.
- **Rejected with rationale**: the updated report or source context shows the original finding was out of scope or mistaken.
- **Still blocking**: planning remains unsafe, misleading, or likely to build the wrong thing.
- **Reopened**: the issue returns after being marked resolved.

Do not silently drop prior blocker or major findings.

## 3. Adjust severity and verdict

- Escalate severity when a repair reveals broader inconsistency, unsupported evidence, unsafe assumptions, or missing core decisions.
- De-escalate severity only when the remaining issue no longer affects reliable implementation planning.
- After a `blocked` verdict, require re-review before implementation planning.
- After `needs revision`, re-review unless every finding was trivial and self-evidently fixed.
- After `conditionally ready`, re-review only if accepted conditions changed scope, requirements, risk, recommendation, or implementation-planning handoff.

## 4. Preserve stable report structure

- Encourage `research-guide` to preserve stable requirement ids, evidence ledger entries, risk ids, open-question ids, and validated sections.
- Recommend full rewrite only when the report is broadly unsafe, internally inconsistent, or untraceable.
- Prefer targeted section repair when structure and traceability are mostly sound.

## 5. Report re-review state

In the review report's Prior review disposition section, include:

- Resolved findings.
- Partially resolved findings.
- Reopened findings.
- New findings.
- Accepted planning risks.
- Re-review recommendation before implementation planning.
