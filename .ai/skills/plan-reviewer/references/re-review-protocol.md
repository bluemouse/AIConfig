# Re-review Protocol

Use this protocol when reviewing an updated implementation plan after earlier `plan-reviewer` findings.

## 1. Preserve finding identity

- Keep the original finding id for unresolved or partially resolved issues.
- Mark a finding **resolved** only when the updated plan fully addresses the required fix.
- Mark a finding **reopened** when a previously resolved issue reappears or the repair introduces the same execution risk.
- Create a new finding id only for genuinely new issues.

## 2. Classify each prior finding

For every prior blocker, major, or material minor finding, assign one disposition:

- **Resolved**: required fix is present and credible.
- **Partially resolved**: progress was made, but execution still requires invention or risky assumptions.
- **Accepted risk**: user explicitly accepted a non-blocker risk and the plan records it.
- **Rejected with rationale**: the updated plan or source context shows the original finding was out of scope or mistaken.
- **Still blocking**: execution remains unsafe, impossible, or likely to build the wrong thing.
- **Reopened**: the issue returns after being marked resolved.

Do not silently drop prior blocker or major findings.

## 3. Adjust severity and verdict

- Escalate severity when a repair reveals broader source misalignment, unsafe execution, or missing core decisions.
- De-escalate severity only when the remaining issue no longer affects reliable execution.
- After a `blocked` verdict, require re-review before execution.
- After `needs revision`, re-review unless every finding was trivial and self-evidently fixed.
- After `conditionally validated`, re-review only if accepted conditions changed task structure, source alignment, execution risk, or rollout risk.

## 4. Preserve stable plan structure

- Encourage `plan-guide` to preserve stable task ids, test ids, verification ids, and validated sections.
- Recommend full rewrite only when the plan is broadly unsafe, internally inconsistent, or untraceable.
- Prefer targeted section repair when task structure and traceability are mostly sound.

## 5. Report re-review state

In the review report's Prior review disposition section, include:

- Resolved findings.
- Partially resolved findings.
- Reopened findings.
- New findings.
- Accepted risks.
- Re-review recommendation before execution.
