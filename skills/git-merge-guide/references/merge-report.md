# Merge reporting

Use two reporting levels. Always produce a compact inline summary. Generate the detailed merge report only when the user explicitly asks for a merge report or detailed report.

## Contents

- [Compact default summary](#compact-default-summary)
- [Detailed report trigger](#detailed-report-trigger)
- [Detailed report structure](#detailed-report-structure)
- [Accuracy rules](#accuracy-rules)

## Compact default summary

Keep the default response concise but make integration-specific fixes visible. Use this shape and adapt wording to the operation:

```text
Merge/Rebase: <operation and source/target refs>
Git state: <COMPLETED | RESOLVED AND STAGED | still active>
Integration verification: <VERIFIED SUCCESS | NOT VERIFIED>

Conflicts:
- <logical conflict/file summary>
- <semantic rewrites, if any>

Integration review:
- <non-conflicted interaction issues found/fixed>
- <unresolved decisions, if any>

Additional integration fixes:
- <important fix 1>
- <important fix 2>

Verification:
- <affected tests/suites and pass/fail totals>
- <build/typecheck/static/lint/format/codegen checks>
- <blocked/skipped required tests, if any>

Final local state:
- <HEAD/merge state/staged post-rebase fixes>
- push performed: no
- <remaining user action>
```

Highlight changes made specifically because the two branches interacted, especially modifications outside Git conflict markers.

## Detailed report trigger

Generate the detailed report only on an explicit request such as:

- "generate the merge report";
- "give me a detailed merge report";
- "document this rebase/merge".

Provide Markdown inline by default. Create/save a report file only when the user asks for a file/artifact.

## Detailed report structure

### 1. Executive Summary

Record:

```text
Operation:
Source:
Target/upstream:
Merge base:
Original HEAD:
Final HEAD:
Git operation status:
Integration verification:
Overall result:
```

Then explain the integration scope, complexity, major semantic work, and verification outcome in 1-3 concise paragraphs.

### 2. Change-Set Overview

Describe each original side independently:

- major commits/change groups;
- intended behavioral changes;
- important APIs/types/state/configuration modified;
- tests introduced or changed;
- architectural assumptions relevant to integration.

Use recorded pre-operation SHAs so post-rebase moving refs do not distort the analysis.

### 3. Conflict Resolution Log

Document each **logical conflict**, not every marker.

Use:

```markdown
### Conflict: <logical name>

Files:
- ...

Side A intent:
...

Side B intent:
...

Interaction:
...

Resolution:
...

Why this resolution:
...

Additional code changed outside conflict markers:
...

Focused validation:
...
```

Group multi-file conflicts when they implement one semantic change.

### 4. Non-Conflicted Integration Review

This is a primary section. For each significant interaction reviewed, record:

```text
Area:
Branches/change sets involved:
Risk category:
Finding:
Evidence:
Resolution:
Files changed:
Verification:
```

Include:

- actual bugs found and fixed;
- significant high-risk interactions reviewed and found safe.

Do not imply every unchanged line was reviewed. Describe the interaction boundary and reasoning used.

### 5. Additional Integration Fixes

Inventory changes not directly required to remove Git conflict markers.

For each fix, record:

- symptom or risk;
- root cause;
- why the problem appears only when the branches are combined;
- implementation;
- changed files;
- regression/integration test added or updated;
- verification result.

This section should make hidden integration work easy for a human reviewer to identify.

### 6. User Decisions

For every ambiguity gate, record:

```text
Decision:
Options presented:
Recommendation given:
User choice:
Implementation resulting from decision:
```

If no semantic decisions were required, state that explicitly.

### 7. Testing Impact Analysis

Explain why the final test set was considered affected.

Cover:

- directly affected tests;
- transitive/dependent tests;
- component/subsystem suites;
- cross-component integration tests;
- concurrency/async tests;
- platform/configuration/feature-flag variants;
- serialization/schema/compatibility tests;
- full suite, if required because the boundary could not be confidently limited.

State the dependency/test-discovery evidence used.

### 8. Verification Results

For each meaningful command/suite, record:

```text
Command / target:
Reason selected:
Relevant scope:
Result:
```

Summarize:

```text
Passed:
Failed:
Skipped:
Blocked:
```

Never label the integration `VERIFIED SUCCESS` if a required affected test/check remains failed, skipped, or blocked.

### 9. Static and Structural Validation

Include applicable results for:

- unresolved Git entries;
- conflict-marker scan;
- `git diff --check`;
- compile/build;
- type checking;
- static analysis;
- lint;
- formatting validation;
- generated-file/codegen consistency;
- repository-specific structural checks.

Only list checks relevant to the repository.

### 10. Final Integrated-State Review

Summarize the result against both original intentions:

- behavior preserved from side A;
- behavior preserved from side B;
- behavior intentionally adapted during integration;
- invariants/contracts specifically checked;
- combined design assumptions confirmed.

Answer the practical question: did the process integrate both designs, rather than merely merge their patches?

### 11. Residual Risks and Unverified Areas

Explicitly identify anything that local evidence/testing could not prove, including:

- unavailable tests or dependencies;
- unavailable hardware/platforms;
- timing/concurrency behavior not sufficiently exercised;
- environment-specific paths;
- incomplete historical evidence;
- assumptions that remain despite passing tests.

If none are known, state that no residual unverified area was identified within the locally discoverable impact boundary.

### 12. Final Git State

Record:

```text
Current branch:
Current HEAD:
Operation metadata remaining:
Unmerged entries:
Staged integration changes:
Unstaged changes:
Untracked files:
Final merge commit created: no/fast-forward not applicable
Remote operations performed: none
```

For rebase, include old-to-new commit correspondence or a local `range-diff` summary when useful. Distinguish post-rebase staged integration fixes from commits created by the rebase itself.

### 13. Required User Actions

List only actual remaining actions, such as:

- create the final merge commit via [../../git-guide/SKILL.md](../../git-guide/SKILL.md)
  (optionally draft the message with
  [../../commit-message-writer/SKILL.md](../../commit-message-writer/SKILL.md));
- review and commit staged post-rebase integration fixes;
- resolve an outstanding semantic decision;
- run required tests in unavailable hardware/platform environments;
- optional read-only final diff review via
  [../../code-reviewer/SKILL.md](../../code-reviewer/SKILL.md);
- requirement-coverage audit via
  [../../implementation-auditor/SKILL.md](../../implementation-auditor/SKILL.md) when needed
  beyond integration verification.

If nothing remains, state that no additional integration action is required locally.

## Accuracy rules

- Use exact locally observed SHAs, refs, commands, and results where available.
- Separate observed facts from inferred intent.
- Do not claim tests ran when they did not.
- Do not hide failed/skipped/blocked required tests inside prose.
- Do not claim a merge commit exists when the no-commit workflow intentionally left the merge staged.
- Do not claim remote publication; this skill performs no remote operations.
