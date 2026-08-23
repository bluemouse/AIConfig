# Testing Anti-Patterns

Load this reference before adding or changing mocks, fixtures, test utilities, or test-only cleanup code.

## Test real behavior, not test scaffolding

A test should fail when user-visible or contract-level behavior is wrong. It should not primarily prove that a mock, fixture, spy, or stub was wired up.

Red flags:

- Assertions target elements or values named `mock`, `stub`, or `fake` instead of real behavior.
- Removing the mock makes the test meaningless rather than slower.
- The test checks that an internal helper was called when it could check the resulting behavior.

Fix by testing the public outcome, observable state, emitted event, returned value, persisted data, or user-facing output.

## Do not add test-only methods to production classes

Do not add production APIs solely to help tests clean up or inspect internals. Put test-only setup, teardown, and inspection in test utilities, fixtures, or dependency seams.

Gate before adding a production method:

1. Is this method used by production code?
2. Does this class own the lifecycle being controlled?
3. Would this method be safe and meaningful for a real caller?

If the answer is no, keep it out of production code.

## Mock only after understanding the dependency

Before mocking any dependency, answer:

1. What real side effects does this dependency provide?
2. Does the test rely on any of those side effects?
3. What is the narrowest slow, nondeterministic, or external boundary to replace?

Prefer mocking the boundary operation, not the higher-level behavior that the test is trying to verify.

## Keep mocks structurally complete

When mocking data from an API, file, IPC message, database row, or platform service, mirror the real structure closely enough that downstream assumptions are exercised. Partial mocks can hide integration failures.

Use examples, schema files, generated types, or captured fixtures when available. If the real structure is unknown, say so and avoid overclaiming test confidence.

## Avoid brittle implementation-detail tests

Do not assert private method calls, exact internal ordering, incidental formatting, or temporary data structures unless that detail is part of the public contract.

Good tests survive safe refactoring. If a refactor breaks many tests while behavior is unchanged, the tests are too coupled to implementation.

## Prefer integration over excessive mocking

A small integration test with real collaborators is often clearer than a unit test with elaborate mocks. Use integration tests when mock setup is longer than the behavior being tested or when correctness depends on interactions across components.
