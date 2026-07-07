# Kotlin Test Process

## Table of contents

1. Contract-first test planning
2. TDD loop
3. Test type selection
4. Regression and characterization tests
5. Review workflow
6. Anti-patterns

## 1. Contract-first test planning

Start every testing task by writing the contract in testable terms:

- **Subject**: function, class, object, or module boundary.
- **Inputs**: valid values, invalid values, empty values, boundary values, repeated values, duplicate values, large values, and values with Kotlin/JVM nullability hazards.
- **Outputs**: exact return value, state transition, exception, sealed outcome, `Result`, emitted values, or collaborator call.
- **Invariants**: immutability, idempotence, ordering, normalization, round trip, monotonicity, cancellation, or resource closing.
- **Observability**: public API result first; collaborator interactions only when they are externally meaningful.

Good first-test matrix:

| Category | Examples |
|---|---|
| Happy path | typical valid input, expected output |
| Boundary | min/max, empty collection/string, single element, duplicate item |
| Invalid | malformed input, out-of-range value, forbidden state transition |
| Kotlin-specific | nullable/platform type, data-class equality, sealed `when`, collection mutation |
| Error contract | thrown type, failure object, null return, validation messages |
| Regression | exact bug reproduction before fix |

## 2. TDD loop

Use TDD when behavior is unclear, when fixing a bug, or when changing public contracts:

1. **Red**: write a small failing test that expresses one behavior. Ensure it fails for the expected reason.
2. **Green**: write the minimum code to pass. Avoid solving future requirements prematurely.
3. **Refactor**: improve names, duplication, state modeling, and edge handling while keeping tests green.
4. **Expand**: add boundary/property/error tests after the core behavior is stable.

Kotlin-specific TDD habits:

- Model invalid states away with `require`, value classes, sealed outcomes, or non-null types; then test those boundaries.
- Prefer immutable data so Arrange sections are short and assertions are stable.
- Use exhaustive `when` tests for sealed interfaces and enums when public behavior depends on variants.
- When introducing coroutines, test cancellation and virtual-time behavior before adding complex concurrency.

## 3. Test type selection

Choose the smallest test that can prove the contract:

| Test type | Use when | Tools |
|---|---|---|
| Pure unit test | deterministic function/value object logic | `kotlin.test`, JUnit, Kotest assertions |
| State/behavior unit test | class maintains invariants over calls | baseline or Kotest |
| Collaborator test | behavior depends on a protocol boundary | fake first, MockK if needed |
| Coroutine test | suspend/time/Flow/cancellation behavior | `kotlinx-coroutines-test` |
| Property test | invariant should hold for many generated inputs | Kotest property |
| Characterization test | existing behavior must be preserved during refactor | baseline or Kotest |
| Regression test | bug must not recur | same framework as nearby tests |
| Coverage gate | CI needs risk metric | Kover |

Avoid platform-specific integration tests in this skill. Keep examples plain Kotlin/JVM.

## 4. Regression and characterization tests

For a bug fix:

1. Reproduce the failure with the smallest test.
2. Assert the real contract, not the incidental stack trace unless the exception type/message is public API.
3. Fix production code.
4. Add a neighboring boundary test if the bug suggests a class of failures.

For legacy code:

- Add characterization tests that lock current externally visible behavior before refactoring.
- Use descriptive names such as ``preserves existing normalization of whitespace``.
- Avoid over-characterizing accidental internals that should be changed.

## 5. Review workflow

When reviewing Kotlin tests, check:

1. Does the test compile and use project-standard dependencies?
2. Is the subject public behavior, not private implementation?
3. Are test names behavior-focused and readable?
4. Does each test have one clear reason to fail?
5. Are assertions strong enough to catch realistic regressions?
6. Are fixtures local, immutable, and explicit?
7. Are mocks/fakes justified and reset between tests?
8. Are coroutine tests using `runTest`, virtual time, and injected dispatchers/scopes?
9. Are property tests seeded/reproducible and using constrained generators?
10. Do coverage exclusions and thresholds reflect risk?

## 6. Anti-patterns

Avoid:

- Testing only getters/setters or data-class generated behavior unless custom logic exists.
- Calling private functions by reflection to avoid testing a public behavior.
- Asserting implementation details such as internal helper call counts when the contract is returned data.
- Reusing mutable fixtures across tests.
- Large tests with many unrelated assertions and multiple reasons to fail.
- Random test data without a seed or failure reproduction path.
- `Thread.sleep`, real delays, or waiting on wall-clock time in coroutine tests.
- Catching broad `Exception` in tests and manually failing later.
- Overusing relaxed mocks so missing interactions are hidden.
- Raising coverage percentages by adding shallow tests with weak assertions.
