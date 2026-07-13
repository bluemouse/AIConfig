# Development Workflow

This guide describes how to run a classic software development workflow using the skill bundles defined in [tools/bundles.md](tools/bundles.md):

```text
research -> plan -> implement -> test/debug -> QA -> PR
```

It is intentionally stack-neutral. Add language, platform, framework, or domain-specific skills only after the workflow skill has established what kind of technical help is needed.

Use this guide when developing a software feature, new product requirement, bug report, product spec, or similarly scoped engineering change.

Skill bundle membership and selection guidance live in [tools/bundles.md](tools/bundles.md).
Machine-readable bundle configuration is in [tools/bundles.json](tools/bundles.json).

## Operational Workflow

### 1. Intake: classify the work

Start by deciding what kind of input you have.

| Input | Default first skill | Reason |
| --- | --- | --- |
| Vague idea, opportunity, product direction, roadmap item | [research-guide](skills/research-guide/SKILL.md) | Turns ambiguity into agreed scope, requirements, tradeoffs, and risks |
| Product requirement, product spec, design doc, issue, or feature request | [plan-guide](skills/plan-guide/SKILL.md) if clear; otherwise [research-guide](skills/research-guide/SKILL.md) | Clear inputs can be planned; unclear inputs need discovery first |
| Bug report, failing test, crash, regression, or flaky behavior | [debugging-guide](skills/debugging-guide/SKILL.md) | Root cause must be proven before implementation changes |
| Approved implementation plan | [plan-executor](skills/plan-executor/SKILL.md) | Execution needs task tracking, working-tree safety, edits, and verification |
| Finished code changes | [implementation-auditor](skills/implementation-auditor/SKILL.md), then [code-reviewer](skills/code-reviewer/SKILL.md) | Correctness evidence comes before reviewer-side diff risk analysis |
| Ready-to-submit branch | [commit-message-writer](skills/commit-message-writer/SKILL.md), [git-guide](skills/git-guide/SKILL.md), [pull-request-guide](skills/pull-request-guide/SKILL.md) | Delivery needs commits, git mechanics, and a reviewable PR narrative |

### 2. Research: make the requirement plannable

Use [research-guide](skills/research-guide/SKILL.md) when the work is not ready to plan. This includes early feature ideas, product concepts, architecture direction, broad requirements, and specs with unresolved assumptions.

The research output should answer:

- What problem are we solving?
- Who is affected?
- What is in scope and out of scope?
- What requirements and acceptance criteria matter?
- What alternatives were considered?
- What risks, edge cases, dependencies, and open questions remain?

For low-risk work, the developer can move directly from the research report to planning. For higher-risk work, use [research-reviewer](skills/research-reviewer/SKILL.md) before planning. The reviewer checks completeness, evidence quality, contradictions, risk awareness, and whether an implementation planner would have to invent missing decisions.

Research is done when the output is either:

- ready for planning;
- conditionally ready with explicit risks; or
- blocked with named questions that must be answered before planning.

### 3. Plan: convert intent into executable work

Use [plan-guide](skills/plan-guide/SKILL.md) after the requirement, product spec, bug context, or research report is clear enough to act on.

A good implementation plan should include:

- source requirements and acceptance criteria;
- architecture and execution strategy;
- ordered tasks with dependencies;
- exact files, interfaces, commands, or discovery gates when known;
- verification steps and expected outcomes;
- risk, rollout, rollback, observability, and stop conditions when relevant.

Use [plan-reviewer](skills/plan-reviewer/SKILL.md) when the plan is complex, high-risk, cross-cutting, or will be executed by another person or agent. The review should answer whether the plan is executable without guesswork. If the reviewer returns `needs revision` or `blocked`, send the handoff packet back to [plan-guide](skills/plan-guide/SKILL.md) for repair before execution.

Planning is done when:

- every must-have requirement maps to a task and a verification step;
- tasks are ordered and independently understandable;
- open questions are either resolved or explicitly accepted as execution risks;
- the plan has a clear execution recommendation.

### 4. Implement: execute with evidence

Use [plan-executor](skills/plan-executor/SKILL.md) when an implementation plan is ready. It owns working-tree safety, task tracking, scoped edits, verification, and the implementation report.

During implementation:

- Inspect the working tree before editing.
- Protect unrelated user changes.
- Follow the plan unless repository evidence shows a safer equivalent path.
- Run targeted checks after each meaningful unit of work.
- Record assumptions, skipped checks, and verification results.

Use [test-driven-dev-guide](skills/test-driven-dev-guide/SKILL.md) when the work should be test-first. This is especially useful for behavior changes, regression fixes, library code, business rules, and any area where a focused test can express the expected behavior. The required loop is red, verify red, green, verify green, refactor, and repeat.

Use [agent-runner](skills/agent-runner/SKILL.md) only when there are two or more independent workstreams and the host supports concurrent subagents. Work is "genuinely independent" only when all of these hold:

- Write scopes are disjoint (no two workstreams write the same file, branch, resource, or shared state).
- No workstream depends on another workstream's output or ordering.
- Each workstream can be verified on its own.
- Merging the results needs no cross-workstream conflict resolution.

If any of these fail, run the work sequentially. If the host has no concurrent subagent capability, [plan-executor](skills/plan-executor/SKILL.md) executes sequentially and states that it degraded to sequential execution rather than silently pretending to parallelize. Keep integration and final verification in the parent workflow.

Implementation is done when:

- the planned tasks are complete or explicitly blocked;
- targeted checks pass or blocked checks are documented;
- behavior, API, configuration, schema, or documentation changes are summarized;
- the implementation report identifies remaining risks and review focus areas.

### 5. Debug: prove root cause before fixing bugs

Use [debugging-guide](skills/debugging-guide/SKILL.md) for bug reports, failing tests, crashes, flaky behavior, build failures, regressions, and integration failures.

The debugging workflow is different from feature implementation. Do not jump straight to a production fix. First establish:

1. the observed symptom;
2. the expected behavior;
3. the smallest reproduction or failing command;
4. the earliest incorrect transition;
5. evidence that proves the transition is the root cause;
6. the regression test or durable reproducer that fails before the fix and passes after it.

For small bugs, [debugging-guide](skills/debugging-guide/SKILL.md) may be enough by itself. For larger bugs that require design changes or multiple tasks, use [debugging-guide](skills/debugging-guide/SKILL.md) to establish root cause, then [plan-guide](skills/plan-guide/SKILL.md) to plan the repair, then [plan-executor](skills/plan-executor/SKILL.md) to execute it.

Debugging is done when:

- the root cause is stated as the earliest incorrect transition, not just the symptom;
- a regression test or reproducer exists when practical;
- the minimal fix is applied;
- focused and relevant broader checks have been run or explicitly reported as blocked.

### 6. QA: audit correctness before review

Use [implementation-auditor](skills/implementation-auditor/SKILL.md) after implementation or bug repair when you need requirement-level proof.

The audit should map:

- requirement or acceptance criterion;
- implementation location;
- test or verification evidence;
- remaining gaps or risks.

This skill is not a diff review. It answers, "Did we build the requested behavior, and what evidence proves it?" After a passing or pass-with-risks audit, use [code-reviewer](skills/code-reviewer/SKILL.md) to inspect the actual diff for correctness, maintainability, security, performance, design, and test risks.

QA is done when:

- fresh command evidence exists for the relevant tests, build, lint, typecheck, or manual checks;
- requirement coverage is explicit;
- known gaps are classified by severity;
- the diff is ready for structured review.

### 7. Review: inspect the diff like a reviewer

Use [code-reviewer](skills/code-reviewer/SKILL.md) before merge readiness. It reviews staged changes, unstaged changes, the full working tree, the last commit, a specific commit, or a commit range.

Default review scopes are:

- design;
- correctness;
- maintainability;
- security;
- performance;
- tests.

Choose review effort by risk, not by feel:

- `basic` — diffs under ~50 lines in non-critical areas: docs, comments, isolated test edits, low-risk config.
- `standard` — normal feature or bug work, changes to shared code or public APIs, modified tests.
- `deep` — security/privacy/auth changes, data or schema migrations, public API design, performance-critical paths, build/deploy changes, cross-system changes, or any diff mixing refactor with behavior change.

Findings must be fixed or explicitly accepted before delivery. When the review finds issues that need code changes, route by finding type:

- Missing or incorrect behavior -> return to implementation via [plan-executor](skills/plan-executor/SKILL.md) or direct scoped edit.
- Regression, crash, or unexplained failure -> [debugging-guide](skills/debugging-guide/SKILL.md) to prove root cause first.
- Design or architecture mismatch -> [plan-guide](skills/plan-guide/SKILL.md) to plan the repair.
- Missing tests -> [test-driven-dev-guide](skills/test-driven-dev-guide/SKILL.md) or [implementation-auditor](skills/implementation-auditor/SKILL.md).

After fixes, re-run [code-reviewer](skills/code-reviewer/SKILL.md) on the amended diff before delivery.

Review is done when:

- all blocking findings are fixed or intentionally deferred with agreement;
- important findings have an owner or resolution;
- tests and audit evidence are reflected in the PR description;
- the change is small and clear enough for reviewers to evaluate.

### 8. Delivery: commit, push, and open the PR

Use [commit-message-writer](skills/commit-message-writer/SKILL.md) to draft Conventional Commit messages from actual git evidence. It should explain why the change exists, not just list files.

Use [git-guide](skills/git-guide/SKILL.md) for local git mechanics:

- staging and committing with a selected message;
- push and rebase before PR;
- conflict resolution;
- worktree creation, validation, merge, cleanup, or abandon flows;
- branch hygiene and history repair.

Use [pull-request-guide](skills/pull-request-guide/SKILL.md) to write the PR/MR description. A good PR should include:

- what changed;
- why it changed;
- how it was implemented;
- testing evidence with commands and outcomes;
- tradeoffs, limitations, risks, screenshots, or rollout notes when relevant;
- related issues, specs, or follow-up PRs.

Use [github-guide](skills/github-guide/SKILL.md) only for GitHub host delivery: `gh pr create`, posting structured reviews with inline comments, resolving review threads, or handling GitHub authentication and token scope. It does not replace [pull-request-guide](skills/pull-request-guide/SKILL.md) for PR writing or [code-reviewer](skills/code-reviewer/SKILL.md) for review judgment.

#### Delivery orchestration sequence

The delivery skills are separate on purpose; run them in order and pass each output to the next:

1. [commit-message-writer](skills/commit-message-writer/SKILL.md) drafts the Conventional Commit message from git evidence.
2. The developer reviews and approves (or iterates) the message.
3. [git-guide](skills/git-guide/SKILL.md) stages, commits with the approved message, and pushes or rebases the branch.
4. [pull-request-guide](skills/pull-request-guide/SKILL.md) writes the PR/MR description and saves it (for example `pr-body.md`) for host delivery.
5. [github-guide](skills/github-guide/SKILL.md) opens the PR (`gh pr create --body-file`) or posts a review, only when the host is GitHub.

If the developer already has a message, skip step 1 and start at [git-guide](skills/git-guide/SKILL.md). None of these skills commit, push, or open a PR unless explicitly asked.

#### Commit and PR granularity

One concern per PR. Within a PR, each commit should be coherent and independently describable:

- If the working tree mixes unrelated changes, split first. [commit-message-writer](skills/commit-message-writer/SKILL.md) flags mixed diffs at the commit level; [pull-request-guide](skills/pull-request-guide/SKILL.md) owns PR-level sizing and splitting.
- Closely related changes can be separate commits in one PR. Independent changes belong in separate PRs.
- Split a bundled refactor out of a feature PR into its own PR.

Delivery is done when:

- commits are coherent and messages match the actual diff;
- the branch is pushed and based on the intended target branch;
- the PR description is clear and test evidence is concrete;
- CI or required checks are passing or failures are documented;
- reviewers have enough context to review without reconstructing intent from the diff.

## Handoff and Return Paths

The lifecycle is not one-directional. Each quality gate can send work backward. Use this table to route on each skill's terminal state so defects are not silently carried forward.

| Producing skill | Terminal state | Next step |
| --- | --- | --- |
| [research-reviewer](skills/research-reviewer/SKILL.md) | `ready` / `conditionally ready` | Proceed to [plan-guide](skills/plan-guide/SKILL.md); carry accepted risks |
| [research-reviewer](skills/research-reviewer/SKILL.md) | `needs revision` / `blocked` | Return to [research-guide](skills/research-guide/SKILL.md) with the review handoff; re-review if the change was material |
| [plan-reviewer](skills/plan-reviewer/SKILL.md) | `validated` / `conditionally validated` | Proceed to [plan-executor](skills/plan-executor/SKILL.md); make accepted risks explicit |
| [plan-reviewer](skills/plan-reviewer/SKILL.md) | `needs revision` / `blocked` | Return the Guide handoff packet to [plan-guide](skills/plan-guide/SKILL.md); re-review before execution |
| [plan-executor](skills/plan-executor/SKILL.md) | verification fails unexpectedly | [debugging-guide](skills/debugging-guide/SKILL.md) to find root cause, then resume execution |
| [plan-executor](skills/plan-executor/SKILL.md) | plan is unsafe, impossible, or contradicts the repo | Return to [plan-guide](skills/plan-guide/SKILL.md) with an execution-blocker report |
| [debugging-guide](skills/debugging-guide/SKILL.md) | root cause found, fix applied | [implementation-auditor](skills/implementation-auditor/SKILL.md) for complex/shared fixes, then [code-reviewer](skills/code-reviewer/SKILL.md) |
| [implementation-auditor](skills/implementation-auditor/SKILL.md) | `pass` | Proceed to [code-reviewer](skills/code-reviewer/SKILL.md) |
| [implementation-auditor](skills/implementation-auditor/SKILL.md) | `pass with risks` | Proceed to [code-reviewer](skills/code-reviewer/SKILL.md); pass the risks in as review focus |
| [implementation-auditor](skills/implementation-auditor/SKILL.md) | `fail` | Return to [plan-executor](skills/plan-executor/SKILL.md) (missing behavior) or [debugging-guide](skills/debugging-guide/SKILL.md) (regression) |
| [implementation-auditor](skills/implementation-auditor/SKILL.md) | `blocked` | Document the blocker; resolve environment/dependency access, then re-audit |
| [code-reviewer](skills/code-reviewer/SKILL.md) | blocking findings | Route by finding type per the Review section, then re-review |
| [code-reviewer](skills/code-reviewer/SKILL.md) | no blocking findings | Proceed to delivery |

Loops are intentional and human-gated. Do not auto-cycle between two skills without an explicit decision.

## Governance: Mandatory vs Optional Gates

The core bundle is always available. The extended-bundle gates are optional by default but become mandatory for higher-risk change classes. Teams can tighten this table, not loosen the safety-critical rows.

| Change class | Mandatory gates | Rationale |
| --- | --- | --- |
| Small local bug fix | None beyond [code-reviewer](skills/code-reviewer/SKILL.md) `basic` | Low blast radius, reversible |
| Feature, single subsystem | [code-reviewer](skills/code-reviewer/SKILL.md) `standard`; [plan-reviewer](skills/plan-reviewer/SKILL.md) if delegated | Bounded scope |
| Security / auth / privacy change | [plan-reviewer](skills/plan-reviewer/SKILL.md), [implementation-auditor](skills/implementation-auditor/SKILL.md), `deep` [code-reviewer](skills/code-reviewer/SKILL.md) | High blast radius |
| Data or schema migration | [research-reviewer](skills/research-reviewer/SKILL.md) (when a research report exists), [plan-reviewer](skills/plan-reviewer/SKILL.md), [implementation-auditor](skills/implementation-auditor/SKILL.md) | Hard to roll back |
| Public API or contract change | [plan-reviewer](skills/plan-reviewer/SKILL.md), `deep` [code-reviewer](skills/code-reviewer/SKILL.md) | Cross-team impact |
| Refactor across 3+ modules | [plan-reviewer](skills/plan-reviewer/SKILL.md), `standard`+ [code-reviewer](skills/code-reviewer/SKILL.md) | Cascade risk |
| Production incident follow-up | [debugging-guide](skills/debugging-guide/SKILL.md), [implementation-auditor](skills/implementation-auditor/SKILL.md), [minutes-writer](skills/minutes-writer/SKILL.md) | Defect prevention and record |

[agent-runner](skills/agent-runner/SKILL.md) is never mandatory; use it only when independent workstreams exist and the host supports subagents.

## Post-Delivery: Defects Found After Merge

When a defect is found in merged or deployed code, re-enter the lifecycle:

1. [debugging-guide](skills/debugging-guide/SKILL.md) to reproduce and prove root cause.
2. [test-driven-dev-guide](skills/test-driven-dev-guide/SKILL.md) to write a regression test before the fix (required for production bugs).
3. [plan-guide](skills/plan-guide/SKILL.md) if the fix needs coordinated changes; otherwise a direct scoped fix.
4. [implementation-auditor](skills/implementation-auditor/SKILL.md) then [code-reviewer](skills/code-reviewer/SKILL.md), then the delivery chain.
5. [minutes-writer](skills/minutes-writer/SKILL.md) for the post-incident record when the impact warrants it.

## Decision Traceability

Decisions made in meetings should not be lost between phases. After [minutes-writer](skills/minutes-writer/SKILL.md) records decisions and action items:

- Feed product or scope decisions into the [research-guide](skills/research-guide/SKILL.md) report.
- Feed constraints and action items into the [plan-guide](skills/plan-guide/SKILL.md) plan as assumptions or tasks.
- Feed commitments into [implementation-auditor](skills/implementation-auditor/SKILL.md) as verification criteria.
- Reference the minutes from the research report or plan so decisions can be revisited if context changes.

## Common Paths

### Path A: New product requirement or product spec

Use this path when the work begins as a product requirement, customer problem, roadmap item, or product spec.

1. Use [research-guide](skills/research-guide/SKILL.md) if scope, users, success metrics, acceptance criteria, or tradeoffs are unclear.
2. Use [research-reviewer](skills/research-reviewer/SKILL.md) for important specs before planning.
3. Use [plan-guide](skills/plan-guide/SKILL.md) to create the implementation plan.
4. Use [plan-reviewer](skills/plan-reviewer/SKILL.md) if the plan is complex, risky, or delegated.
5. Use [plan-executor](skills/plan-executor/SKILL.md) to implement.
6. Use [implementation-auditor](skills/implementation-auditor/SKILL.md) to map results back to requirements.
7. Use [code-reviewer](skills/code-reviewer/SKILL.md) to review the diff.
8. Use [commit-message-writer](skills/commit-message-writer/SKILL.md), [git-guide](skills/git-guide/SKILL.md), and [pull-request-guide](skills/pull-request-guide/SKILL.md) for delivery.
9. Use [github-guide](skills/github-guide/SKILL.md) if delivery happens on GitHub through `gh`.

### Path B: Software feature request

Use this path when the requested behavior is already understandable.

1. Use [plan-guide](skills/plan-guide/SKILL.md) to produce a focused implementation plan.
2. Use [test-driven-dev-guide](skills/test-driven-dev-guide/SKILL.md) for behavior-first development when practical.
3. Use [plan-executor](skills/plan-executor/SKILL.md) to implement the plan.
4. Use [implementation-auditor](skills/implementation-auditor/SKILL.md) to verify acceptance criteria.
5. Use [code-reviewer](skills/code-reviewer/SKILL.md) to inspect the diff.
6. Use delivery skills to commit, push, and open the PR.

If the feature request turns out to have unresolved product, UX, architectural, data, or rollout questions, pause implementation and return to [research-guide](skills/research-guide/SKILL.md).

### Path C: Bug report or regression

Use this path when the input is a failure, not a new behavior request.

1. Use [debugging-guide](skills/debugging-guide/SKILL.md) to reproduce and prove root cause.
2. Use [test-driven-dev-guide](skills/test-driven-dev-guide/SKILL.md) to write the regression test before the production fix when practical.
3. Use [plan-guide](skills/plan-guide/SKILL.md) only if the fix requires multiple coordinated tasks or design changes.
4. Use [plan-executor](skills/plan-executor/SKILL.md) or direct scoped implementation, depending on plan size.
5. Use [implementation-auditor](skills/implementation-auditor/SKILL.md) to confirm the bug report, regression test, and related behavior are covered.
6. Use [code-reviewer](skills/code-reviewer/SKILL.md) to review the repair diff.
7. Use delivery skills to commit, push, and open the PR.

Do not treat a plausible explanation as a root cause. A bug fix is not done until the failure is reproduced or the limitation is documented, the cause is evidenced, and verification has been run.

### Path D: Existing plan ready for execution

Use this path when another person, agent, or process has already produced a plan.

1. Use [plan-reviewer](skills/plan-reviewer/SKILL.md) if the plan has not been reviewed and the change is meaningful.
2. Use [plan-executor](skills/plan-executor/SKILL.md) to run the plan on the current branch.
3. Use [agent-runner](skills/agent-runner/SKILL.md) through [plan-executor](skills/plan-executor/SKILL.md) if independent units can run safely in parallel.
4. Use [implementation-auditor](skills/implementation-auditor/SKILL.md) for requirement-level evidence.
5. Use [code-reviewer](skills/code-reviewer/SKILL.md) and delivery skills.

Do not use [plan-executor](skills/plan-executor/SKILL.md) without an implementation plan. If the plan is missing, use [plan-guide](skills/plan-guide/SKILL.md) first.

## Skill Switching Rules

- If the question is "what should we build?", use [research-guide](skills/research-guide/SKILL.md).
- If the question is "is this research ready for planning?", use [research-reviewer](skills/research-reviewer/SKILL.md).
- If the question is "how should we build it?", use [plan-guide](skills/plan-guide/SKILL.md).
- If the question is "is this plan safe and executable?", use [plan-reviewer](skills/plan-reviewer/SKILL.md).
- If the question is "execute this plan", use [plan-executor](skills/plan-executor/SKILL.md).
- If the question is "develop this behavior test-first", use [test-driven-dev-guide](skills/test-driven-dev-guide/SKILL.md).
- If the question is "why is this broken?", use [debugging-guide](skills/debugging-guide/SKILL.md).
- If the question is "did we satisfy the requirement with evidence?", use [implementation-auditor](skills/implementation-auditor/SKILL.md).
- If the question is "is this diff safe to merge?", use [code-reviewer](skills/code-reviewer/SKILL.md).
- If the question is "what should the commit say?", use [commit-message-writer](skills/commit-message-writer/SKILL.md).
- If the question is "perform the git operation", use [git-guide](skills/git-guide/SKILL.md).
- If the question is "what should the PR say?", use [pull-request-guide](skills/pull-request-guide/SKILL.md).
- If the question is "post this to GitHub or manage GitHub review threads", use [github-guide](skills/github-guide/SKILL.md).
- If the question is "summarize the meeting decisions", use [minutes-writer](skills/minutes-writer/SKILL.md).
- If the question is "can independent work happen in parallel?", use [agent-runner](skills/agent-runner/SKILL.md).
- If plan execution hits an unexpected verification failure, use [debugging-guide](skills/debugging-guide/SKILL.md), then resume execution.
- If the plan is unsafe, impossible, or contradicts the repo mid-execution, return to [plan-guide](skills/plan-guide/SKILL.md).
- If an implementation audit returns `fail`, return to [plan-executor](skills/plan-executor/SKILL.md) or [debugging-guide](skills/debugging-guide/SKILL.md); if `blocked`, resolve the environment and re-audit.
- If code review finds a design flaw, return to [plan-guide](skills/plan-guide/SKILL.md); if it finds a regression, use [debugging-guide](skills/debugging-guide/SKILL.md).
- If a defect is found after merge, follow the Post-Delivery loop.

## Experience-Level Guidance

### New developers

Follow the workflow one phase at a time. Do not skip planning or verification because the change looks small. Ask for a plan when you are unsure where to edit, ask for debugging when you have a failure, and ask for an implementation audit before claiming the work is complete.

Minimum habit:

1. clarify or research the request;
2. write or request a plan;
3. make one small change at a time;
4. run focused checks;
5. audit requirement coverage;
6. request code review;
7. write a clear PR.

### Experienced developers

Use judgment to choose the lightweight or rigorous path. You may skip formal research review or plan review for small local changes, but keep the handoff artifacts clear enough that another developer can understand intent, verification, and remaining risk.

Minimum habit:

1. preserve traceability from request to code;
2. make verification evidence fresh and reproducible;
3. separate correctness audit from diff review;
4. split large or mixed changes before PR;
5. document tradeoffs and known risks before reviewers discover them.

### Tech leads and reviewers

Use the extended bundle to protect high-risk work. Require research review when requirements affect product direction or cross-team contracts. Require plan review when the work is delegated, migration-heavy, security-sensitive, or hard to roll back. Require implementation audit before code review when the acceptance criteria are more important than the diff shape.

Minimum habit:

1. decide which gates are mandatory for the change class;
2. review artifacts, not only code;
3. make accepted risks explicit;
4. keep PRs small enough to review properly;
5. use GitHub delivery only after review content is sound.

## Done Criteria by Artifact

| Artifact | Done when |
| --- | --- |
| Research report | Scope, goals, requirements, acceptance criteria, alternatives, evidence, risks, and planning handoff are explicit |
| Research review | Verdict is clear and required fixes are identified or the report is accepted for planning |
| Implementation plan | Every must-have requirement maps to tasks and verification, with dependencies and stop conditions visible |
| Plan review | Verdict and Guide handoff packet make execution readiness or required repairs clear |
| Implementation report | Tasks, changed files, behavior changes, verification, assumptions, skipped checks, and risks are recorded |
| Debugging report | Reproduction, root cause, evidence, fix, regression test or reproducer, and verification are documented |
| Implementation audit | Requirement coverage and fresh command evidence support a pass, pass-with-risks, blocked, or fail verdict |
| Code review | Findings are prioritized by severity with file-level evidence and proposed fixes |
| Commit message | Conventional Commit subject and body explain the reason, approach, impact, and verification when relevant |
| PR description | What, why, how, testing evidence, tradeoffs, and related context are clear to reviewers |

## Practical Defaults

- Default to the core bundle for ordinary feature and bug work. See [tools/bundles.md](tools/bundles.md) for bundle membership and when to add extended-bundle skills.

The safest default sequence for meaningful product work is:

```text
research-guide
-> research-reviewer when needed
-> plan-guide
-> plan-reviewer when needed
-> plan-executor with test-driven-dev-guide or debugging-guide as appropriate
-> implementation-auditor
-> code-reviewer
-> commit-message-writer
-> git-guide
-> pull-request-guide
-> github-guide when delivering on GitHub
```