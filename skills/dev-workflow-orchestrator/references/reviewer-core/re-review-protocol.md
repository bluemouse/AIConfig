# Re-review Protocol (shared by plan-reviewer and research-reviewer)

Use this protocol when reviewing an updated **artifact** after earlier reviewer findings.
Per-skill parameters:

| parameter | plan-reviewer | research-reviewer |
|---|---|---|
| Artifact under review | implementation plan | research report |
| Producing skill to encourage | plan-guide | research-guide |
| Success verdict | `validated` | `ready` |
| Conditional verdict | `conditionally validated` | `conditionally ready` |
| Downstream consumer | execution (plan-executor) | implementation planning (plan-guide) |

## 1. Preserve finding identity

- Keep the original finding id for unresolved or partially resolved issues.
- Mark a finding **resolved** only when the updated artifact fully addresses the required fix.
- Mark a finding **reopened** when a previously resolved issue reappears or the repair introduces the same readiness risk.
- Create a new finding id only for genuinely new issues.

## 2. Classify each prior finding

For every prior blocker, major, or material minor finding, assign one disposition:

- **Resolved**: required fix is present and credible.
- **Partially resolved**: progress was made, but the downstream consumer would still require invention or risky assumptions.
- **Accepted risk**: user explicitly accepted a non-blocker risk and the artifact records it.
- **Rejected with rationale**: the updated artifact or source context shows the original finding was out of scope or mistaken.
- **Still blocking**: the downstream step remains unsafe, impossible, misleading, or likely to build the wrong thing.
- **Reopened**: the issue returns after being marked resolved.

Do not silently drop prior blocker or major findings.

## 3. Adjust severity and verdict

- Escalate severity when a repair reveals broader inconsistency, source misalignment, unsupported evidence, unsafe assumptions, or missing core decisions.
- De-escalate severity only when the remaining issue no longer affects reliable downstream use.
- After a `blocked` verdict, require re-review before the downstream step.
- After `needs revision`, re-review unless every finding was trivial and self-evidently fixed.
- After the conditional verdict, re-review only if accepted conditions changed scope, structure, requirements, risk, recommendation, or the handoff; otherwise proceed with the accepted risks recorded.

## 4. Preserve stable structure

- Encourage the producing skill to preserve stable requirement/task/test/verification ids, evidence ledger entries, and validated sections.
- Recommend full rewrite only when the artifact is broadly unsafe, internally inconsistent, or untraceable.
- Prefer targeted section repair when structure and traceability are mostly sound.

## 5. Report re-review state

In the review report's Prior review disposition section, include:

- Resolved findings.
- Partially resolved findings.
- Reopened findings.
- New findings.
- Accepted risks.
- Re-review recommendation before the downstream step.
