# Fix Report

## Run metadata
- Run directory: <path>
- Source review: <path to 40-code-review.md>
- Created: <ISO timestamp>
- Resolver: code-review-resolver

## Summary
- Total findings: <count>
- Fixed: <count>
- Unresolved: <count>
- Deferred: <count>
- Routed upstream: <count>

## Per-finding resolution

| Finding id | Severity | root-cause-phase | Resolution | What changed | Verification |
|------------|----------|------------------|------------|---------------|--------------|
| cr-001 | blocker | local | fixed | <description> | <command + result> |
| cr-002 | major | local | fixed | <description> | <command + result> |
| cr-003 | major | plan | upstream | — (backward packet) | — |
| cr-004 | minor | local | deferred | — (deferred, optional) | — |
| cr-005 | minor | local | unresolved | <reason: ambiguous location> | — |

## Upstream findings (backward handoff packets)

| Finding id | Target phase | Packet path | Root cause summary |
|------------|-------------|--------------|-------------------|
| cr-003 | plan | back-code-review-to-plan-1.md | <one-line summary> |

## Verification

| Command | Scope | Result |
|---------|-------|--------|
| <command> | <files/area> | pass / fail / skipped |

## Files changed

| File | Findings addressed | Lines changed |
|------|-------------------|---------------|
| <path> | cr-001, cr-002 | <range> |

## Risks and assumptions
- <risk or assumption, if any>

## Follow-up needs
- <unresolved findings needing user input or re-review attention>

## Readiness for re-review
- Status: ready for re-review | blocked
- Notes: <any context for code-reviewer>
