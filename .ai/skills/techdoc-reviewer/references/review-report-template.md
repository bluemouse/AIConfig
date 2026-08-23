# Technical Documentation Review Report Template

Use this structure unless the user requested another format. Omit sections that are genuinely
irrelevant, but do not omit the evidence and verification basis for material findings.

```markdown
# Technical Documentation Review Report

## 1. Review target

- Mode: <document review | documentation-impact review | synchronization | targeted verification>
- Target: <documents, documentation area, or git ref/diff>
- Effort: <basic | standard | deep>
- Audience and purpose: <who the docs serve and what they help them do>
- Evidence inspected: <implementation/tests/config/build/schema/examples/design records>
- Coverage: <full | partial — reviewed and deferred paths or claim areas>

## 2. What was verified

| Area or claim group | Evidence | Result |
| --- | --- | --- |
| <API/config/workflow/architecture/etc.> | `<path:line>` or command | verified / mismatch / unverified |

## 3. Findings

Order by severity: `critical`, `high`, `medium`, `low`.

If none were found, write `No material findings.` Do not create filler findings.

| id | severity | drift type | documentation location | summary |
| --- | --- | --- | --- | --- |
| td-001 | high | semantic drift | `docs/path.md:line` | <short title> |

### Finding details

#### td-001: <short title>

- Severity: <critical | high | medium | low>
- Drift type: <contradiction | omission | removal | rename | semantic | example | workflow | architecture | default/configuration | discoverability | safety/security>
- Documentation location: `<path:line or section>`
- Finding: <specific mismatch or missing material>
- Evidence: `<repository path:line, command result, or design source>`
- Reader impact: <concrete failure, unsafe action, misunderstanding, or blocked workflow>
- Recommended fix: <smallest complete correction>
- Verification status: <confirmed | plausible — use plausible only when evidence is incomplete and retain it as an open question where appropriate>

## 4. Documentation impact map

Include for change-set and synchronization modes; omit only when no implementation change is in
scope.

| Semantic change | Related documentation | Status | Required action |
| --- | --- | --- | --- |
| <change> | `<path>` or `not found` | updated / needs change / verified unaffected / unverified | <action> |

## 5. Unresolved conflicts or questions

List only decisions that evidence cannot resolve, especially code-versus-contract conflicts.
Use `none` when there are no material questions.

## 6. Documentation changes

Include only when files were edited. For each file, state the semantic correction rather than
only the filename.

- `<path>` — <what contract, workflow, or safety information changed>

## 7. Verification

| Check | Result | Notes |
| --- | --- | --- |
| Implementation/test/config comparison | pass / mismatch / skipped / blocked | <actual evidence> |
| Executable docs or examples | pass / fail / static-only / skipped / blocked | <actual command or reason> |
| Stale-reference and cross-document search | pass / findings / partial | <scope> |
| Links and local references | pass / fail / skipped | <scope> |
| Final documentation diff review | pass / skipped | <synchronization only> |

## 8. Overall assessment

- Documentation state: <synchronized | needs fixes | blocked by unresolved contract>
- Risk summary: <one or two sentences>
- Next actions:
  1. <highest-priority action>
  2. <next action, if needed>
```

Rules:

- Every finding must include documentation location, concrete evidence, reader impact, and an
  actionable correction.
- Never claim a command, example, link check, or test ran unless it actually ran.
- Mark static inspection separately from execution.
- Keep findings larger than process narration.
- If no material issues are found, state the residual risks and coverage limits rather than
  inventing concerns.
- Do not patch documentation during a review-only request. In synchronization mode, list exact
  semantic corrections and re-verify them.
