# Plan Review Report Template

Use this structure for the review output. Keep it concise, but include enough detail for `plan-guide` to repair the plan.

```markdown
# Plan Review Report: [Plan Name]

## 1. Verdict
- Verdict: validated | conditionally validated | needs revision | blocked
- Confidence: high | medium | low
- Execution recommendation: proceed | proceed with accepted risks | revise first | do not execute
- Review posture: balanced | aggressive
- Active reviewer roles/lenses: [list]
- Source context reviewed: [research-report/spec/requirements/bug/codebase/prior review]

## 2. Executive summary
[Short summary of whether the plan is executable and the main reason.]

## 3. Findings
| id | severity | affected area | issue | required fix | plan-guide action |
|---|---|---|---|---|---|
| pr-001 | blocker/major/minor/question/nit | section/task/source item |  |  | revise plan / ask user / inspect codebase / research upstream / narrow scope / split plan / accept as execution risk / re-review |

### Finding details
#### pr-001: [short title]
- Severity:
- Affected area:
- Issue:
- Why it matters for execution:
- Required fix:
- Suggested owner/resolver:
- Recommended plan-guide action:

## 4. Source alignment check
- Requirements covered:
- Requirements missing or weakly covered:
- Scope drift or non-goal conflicts:
- Source contradictions:

## 5. Task and sequencing check
- Task decomposition quality:
- Dependency issues:
- Interface or file precision issues:
- Parallelization or critical-path notes:

## 6. Test design and verification check
- Test design section (TDD-first matrix, collaboration notes):
- Requirement → planned failing test or verification check coverage:
- Red-phase test gaps (code tasks missing failing tests before production steps):
- Test discipline issues (`mandatory` vs unjustified `n/a`):
- Acceptance criteria coverage:
- Verification matrix gaps:
- Rollout, rollback, observability, security, privacy, or migration gaps:
- Domain-specific concerns:

## 7. Prior review disposition
[Use when reviewing an updated plan.]
- Resolved findings:
- Reopened findings:
- New findings:

## 8. Guide handoff packet
- Target skill: plan-guide
- Review verdict:
- Confidence:
- Execution recommendation:
- Iteration required:
- Highest-priority repair track:
- Findings requiring plan-guide action:
  - [finding id]: [severity] [summary]
    - required action:
    - affected plan area:
    - expected repair:
- User decisions needed:
- Codebase/project facts to inspect:
- Upstream research/spec issues:
- Findings that may be accepted as execution risks:
- Findings rejected or out of scope:
- Re-review required before execution:

## 9. Review gate
Review gate: choose one:
1. return-to-guide: give the Guide handoff packet to plan-guide for targeted repair
2. re-review: review an updated plan or run a stricter pass
3. specialize: review again with a named domain specialist lens
4. accept: treat the plan as executable at the stated verdict level
```

Rules:
- Do not include the accept option as executable-ready for blocked or needs revision verdicts.
- Do not bury blocker findings in prose.
- Do not block on nits or style preferences.
- Make each material finding actionable by `plan-guide`.
