# Scope Checklists

Detailed checklist per selectable scope, used by `code-review-plus`'s `SKILL.md`. Read
the section for a scope right before running that scope's pass. At `deep` effort, paste
the relevant section's bullets verbatim into that scope's subagent prompt — the subagent
does not have this file loaded.

## Contents

- [design](#design)
- [correctness](#correctness)
- [maintainability](#maintainability)
- [security](#security)
- [performance](#performance)
- [tests](#tests)
- [Scope & Intent Alignment (always runs)](#scope--intent-alignment-always-runs)

## design

Architecture and design quality — does the change fit the codebase's shape, and is the
shape it introduces sound?

- Layering violations and dependency direction problems (e.g. a lower layer importing
  from a higher one, a domain module reaching into infrastructure details)
- Weak abstractions, leaking implementation details, or confusing public APIs
- Unclear ownership, lifecycle, or data flow for new types/modules
- Changes that conflict with existing architecture or established patterns elsewhere in
  the codebase
- SOLID violations: a type doing too much (SRP), a change that requires editing existing
  code instead of extending it (OCP), a subtype that breaks its supertype's contract
  (LSP), fat interfaces forcing unused methods (ISP), high-level code depending on
  concrete low-level details instead of abstractions (DIP)
- DRY violations introduced by the change (duplicated logic that should share an
  abstraction) vs. premature/unwarranted abstraction for a single use site
- Pattern appropriateness — is a design pattern used where a simpler construct would do,
  or is a simpler construct used where the pattern would prevent a real problem?
- Coupling and cohesion: does the change tighten coupling between modules that should be
  independent, or scatter related logic across unrelated places?
- Interface design: are new function/API signatures minimal, intention-revealing, and
  hard to misuse?
- Extensibility: does the design accommodate the next obvious variation, or will it need
  a rewrite for a foreseeable next step?

## correctness

Logic errors and regression risk — the highest-priority scope; findings here are usually
the most severe.

- Logic errors and incorrect edge-case handling (off-by-one, inverted conditions, wrong
  operator precedence, incorrect boolean logic)
- Broken invariants — state that the code assumes is always true but the change can
  violate
- Null/undefined/None handling issues, especially at new boundaries introduced by the
  change
- Race conditions and other concurrency bugs: unsynchronized shared state, non-atomic
  read-modify-write sequences, incorrect lock scope or ordering
- Backward compatibility risks and behavioral regressions for existing callers
- Incorrect assumptions about data shape, ordering, units, timezones, or encoding
- Error handling gaps: exceptions swallowed silently, error paths that leave state
  half-updated, missing handling for a documented failure mode of a called API
- Resource management: unclosed handles/connections, leaked subscriptions, missing
  cleanup in early-return or exception paths

## maintainability

Readability and long-term cost of the change.

- Poor naming that misleads about purpose, type, or units
- Confusing control flow (deep nesting, unclear early returns, mixed levels of
  abstraction in one function)
- Unnecessary complexity — code doing more work or handling more cases than the problem
  requires
- Misleading, stale, or redundant comments; comments that restate the code instead of
  explaining a non-obvious why
- Duplicate logic and brittle branching (e.g. a long if/elif chain that will need a new
  branch for every future case instead of a data-driven approach)
- Code smells: long functions/methods, large classes, feature envy, shotgun surgery
  required for a small conceptual change
- Outdated patterns or deprecated API usage introduced or left in place by the change
- TODOs added without an owner or without linking to a tracked follow-up
- Public APIs or tests that are harder to understand than the problem justifies

## security

Only raise items with concrete evidence in the diff — do not speculate about
hypothetical attackers with no supporting code path.

- Input validation: is untrusted input (user input, external API responses, file
  contents) validated/sanitized before use?
- Authentication checks: are auth checks present on newly added or changed entry points
  that need them?
- Authorization verification: does the change correctly scope access to the acting
  user/tenant, or could it leak or mutate another user's data?
- Injection vulnerabilities: SQL/NoSQL/command/template injection from unsanitized input
  reaching a query, shell command, or template render
- Cryptographic practices: weak/outdated algorithms, hardcoded keys/IVs, insufficient
  randomness for security-sensitive values
- Sensitive data handling: secrets, tokens, or PII logged, cached, or persisted in plain
  text; secrets committed in the diff itself
- Dependency risk: a newly added or upgraded dependency with a known vulnerability, or a
  vendored copy of a dependency
- Configuration security: overly permissive defaults, disabled TLS verification, debug
  flags left enabled

## performance

Only raise items where the change plausibly affects a hot path or measurably increases
resource cost — avoid micro-optimization nits on cold paths.

- Algorithmic efficiency: a change that turns an O(n) operation into O(n²) or worse,
  especially inside a loop over user-controlled or unbounded data
- Database query cost: N+1 query patterns, missing indexes implied by a new query shape,
  fetching more columns/rows than needed
- Memory usage: large objects held longer than necessary, unbounded caches/collections,
  loading a full dataset where streaming would do
- CPU utilization: unnecessary repeated computation that could be hoisted or memoized
- Network calls: new calls added inside a loop, missing batching, missing timeouts
- Caching effectiveness: cache keys that collide or never invalidate, caching something
  that must always be fresh
- Async/concurrency patterns: blocking calls on an async/event-loop thread, unnecessary
  serialization of independent work
- Resource leaks under load: connections/threads/file handles not bounded or pooled

## tests

- Coverage of important paths and edge cases introduced or changed by the diff
- Test quality: does each test actually exercise the behavior it claims to, or would it
  pass even if the logic were wrong?
- Edge cases: boundary values, empty/null inputs, error paths — not just the happy path
- Mock usage: mocks that assert only "was called" without verifying arguments/behavior;
  mocking so much that the test no longer exercises real logic
- Test isolation: shared mutable state between tests, order-dependent tests, tests that
  leave side effects
- Missing tests entirely for new or changed behavior that has no existing coverage
- Integration tests: is there any test exercising the changed code against a real (or
  realistic) collaborator, not just unit-level mocks, when the change crosses a boundary?

## Scope & Intent Alignment (always runs)

Not a selectable scope — this check always runs first, regardless of which of the six
scopes above are selected, because every other lens needs to know what the change was
actually trying to do.

- Does the change appear to implement what the user/task intended, based on available
  context (chat history, commit message, linked issue)?
- Incomplete changes: a rename, refactor, or feature that was started but not finished
  everywhere it needed to be
- Mismatched scope: the diff does noticeably more or less than what was asked
- Accidental side effects: unrelated files changed, debug code or commented-out code left
  in, formatting-only changes mixed into a behavioral diff
- Requirement drift: the implementation diverges from an earlier discussed design or
  constraint without an explanation
