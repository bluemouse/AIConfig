---
name: kotlin-testing
description: Write, fix, and configure plain Kotlin/JVM tests with kotlin.test, JUnit Platform, Kotest, MockK, coroutine tests, property/data-driven tests, Kover coverage, and flaky-test triage. Use when adding or updating Kotlin tests, fixing failing or flaky tests, choosing test frameworks, or debugging assertion/coroutine test failures — even if the user says "add tests" without naming a framework. For Gradle build engineering, test task wiring, version catalogs, dependency resolution, CI, or build cache, use gradle-dev. For production Kotlin language/API design, use kotlin-coding. Excludes Android, KMP, Native, JS/Web, backend, and platform-specific testing.
---

# Kotlin Testing

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Write, fix, and gate plain Kotlin/JVM tests. Read bundled references on demand — do not load all reference files unless the task requires them.

This skill supersedes test-design content in [kotlin-coding/references/testing-debugging.md](../kotlin-coding/references/testing-debugging.md). For production language/API fixes under test, use [kotlin-coding](../kotlin-coding/SKILL.md).

## Scope

Use this skill for testing plain Kotlin code: unit tests, module-level tests, deterministic integration tests that do not depend on a platform framework, coroutine tests, property-based tests, mocking, fixtures, coverage, Gradle test commands, and test-debugging workflows.

Do not provide Android, KMP, Kotlin/Native, Kotlin/JS/Web, browser, UI, device, Ktor/backend, database/server framework, or deployment testing guidance. When supplied code comes from those contexts, help only with generic Kotlin test design, assertions, coroutine behavior, and data modeling.

## When NOT to Use

- Gradle build-file edits, version catalogs, task wiring, CI cache policy, or configuration cache — [gradle-dev](../gradle-dev/SKILL.md)
- Production Kotlin language/API design without test changes — [kotlin-coding](../kotlin-coding/SKILL.md)
- Android instrumentation/UI test code (Compose, Espresso, Robolectric patterns) — [android-dev](../android-dev/SKILL.md)
- Android Gradle test **task** wiring (`testDebugUnitTest`, `connectedDebugAndroidTest`) — [gradle-android-dev](../gradle-android-dev/SKILL.md)

## Default workflow

1. Identify the test target and contract:
   - Public function/class/module boundary, not private implementation details.
   - Valid, invalid, boundary, empty, null/platform-type, large-input, state-transition, and failure cases.
   - Expected failure representation: exception, null, sealed result, `Result`, or validation object.
2. Select the smallest suitable test style:
   - Baseline Kotlin/JVM: `kotlin.test` + JUnit Platform.
   - Rich Kotlin DSL/matchers: Kotest.
   - Collaborator isolation: prefer fakes; use MockK for interaction-heavy or suspend dependencies.
   - Suspend/Flow/time behavior: `kotlinx-coroutines-test` with `runTest` and virtual time.
   - Invariants over many inputs: Kotest property testing.
   - Coverage gates: Kover for JVM test coverage.
3. Write the test before or alongside the production change:
   - Red: assert the intended failure or missing behavior.
   - Green: add the minimum implementation.
   - Refactor: simplify production and tests without weakening assertions.
4. Keep tests deterministic:
   - No `Thread.sleep`, wall-clock assumptions, unseeded randomness, shared mutable globals, order dependence, hidden network/filesystem dependencies, or reliance on test execution order.
5. Validate with project commands:
   - Prefer the project's existing test/check tasks. Use [gradle-dev](../gradle-dev/SKILL.md) for Gradle command selection, task wiring, CI behavior, dependency/version catalog edits, and cache-related test execution issues.
   - Use `scripts/kotlin_test_check.sh` only when a local project is available and the user wants command discovery/execution. Default mode is `--dry-run` (prints commands without executing).
6. If production Kotlin design is the blocker, apply [kotlin-coding](../kotlin-coding/SKILL.md) for language/API/design fixes and return to this skill for tests.

## Reference routing

| Task | Read |
|------|------|
| Test selection, TDD, regression, characterization, review | [test-process.md](references/test-process.md) |
| Test-framework dependencies, commands, Kover, reports | [tooling.md](references/tooling.md) |
| Baseline `kotlin.test` and JUnit Platform | [kotlin-test-junit.md](references/kotlin-test-junit.md) |
| Kotest specs, matchers, data/property tests | [kotest.md](references/kotest.md) |
| Fakes vs mocks, MockK syntax, suspend mocks | [mockk-fakes.md](references/mockk-fakes.md) |
| `runTest`, virtual time, Flow tests, coroutine flakes | [coroutine-testing.md](references/coroutine-testing.md) |
| Fixtures, builders, table tests, property generators | [test-data-patterns.md](references/test-data-patterns.md) |
| Failed-test diagnosis, flake triage | [debugging-flaky-tests.md](references/debugging-flaky-tests.md) |
| Gradle build files, catalogs, task wiring, CI, caches | [gradle-dev](../gradle-dev/SKILL.md) |
| Production Kotlin language/API design | [kotlin-coding](../kotlin-coding/SKILL.md) |

## Gradle boundary

Use [gradle-dev](../gradle-dev/SKILL.md) when the request is mainly about `build.gradle.kts`, `settings.gradle.kts`, version catalogs, `tasks.test {}`, Gradle test suites, dependency resolution, wrapper/JDK compatibility, CI, build cache, or configuration cache. Return to this skill for the actual Kotlin test design, assertions, fakes/mocks, coroutine scheduling, coverage policy, and flake analysis.

## Default Kotlin test conventions

- Put tests under `src/test/kotlin` in the same package as the production code unless testing only public API from a consumer package.
- Name test classes after the unit under test, for example `EmailValidatorTest`, `UserIdTest`, or `CsvParserTest`.
- Use readable backtick test names for behavior: ``fun `rejects blank email`()``.
- Prefer Arrange/Act/Assert or Given/When/Then. Do not hide essential setup in magic helpers.
- Assert exact behavior, not just non-nullness. Check returned values, thrown type/message when part of contract, state changes, and collaborator calls only when interactions are the contract.
- Prefer immutable test data and local `val`s. Use `lateinit` only for shared fixtures initialized before each test.
- Test public behavior. Extract a small pure function rather than testing private functions directly.
- Prefer fakes for simple repositories/clocks/id generators. Use mocks when verifying protocol, ordering, failure injection, or expensive collaborators.
- Keep one dominant assertion style per module or test class. Avoid mixing JUnit assertions, `kotlin.test`, Kotest matchers, and AssertJ casually.
- Add regression tests before fixing bugs. The test should fail for the observed bug and pass after the smallest correct fix.
- Add property tests for algebraic laws, round trips, parsers/serializers, normalization, ordering, and pure business rules.
- Use coverage as a risk signal, not a substitute for assertions. Exclude generated/configuration code deliberately.

## Tooling helper

```bash
scripts/kotlin_test_check.sh --dry-run
scripts/kotlin_test_check.sh --quick
scripts/kotlin_test_check.sh --full
```

Default mode is `--dry-run`. Use `--quick` to run the primary test task; `--full` adds check, Kover, and lint/static-analysis tasks when configured.

## Output patterns

When asked to write tests, return:

1. Required dependencies or Gradle snippets only if missing or requested.
2. The test file with package, imports, and complete examples.
3. Any minimal production seam required for deterministic testing, such as injected `Clock`, dispatcher, ID generator, or interface.
4. Exact commands to run.
5. A short note on why these tests cover the relevant contract. If build-file changes are needed, keep them minimal and refer to [gradle-dev](../gradle-dev/SKILL.md) for the full Gradle rationale.

When asked to fix failing tests, return:

1. The likely root cause from the failure output.
2. The smallest reproduction or failing assertion.
3. The corrected test or production code.
4. The verification command.
5. Any flake-prevention change if timing, randomness, concurrency, or shared state was involved.

## Companion skills

- Use [kotlin-coding](../kotlin-coding/SKILL.md) for production Kotlin language/API/design work.
- Use [gradle-dev](../gradle-dev/SKILL.md) for Gradle build engineering, version catalogs, task wiring, CI, and build/configuration cache.
- Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for Android Gradle test task names and AGP-specific test wiring only.
- Use [android-dev](../android-dev/SKILL.md) for Android instrumentation/UI test code and Compose testing patterns.

## References

- [test-process.md](references/test-process.md): test selection, TDD, regression, characterization, and review workflow.
- [tooling.md](references/tooling.md): test-framework dependencies, test commands, Kover coverage, and test-report conventions.
- [kotlin-test-junit.md](references/kotlin-test-junit.md): baseline `kotlin.test` and JUnit 5/JUnit Platform patterns.
- [kotest.md](references/kotest.md): Kotest spec styles, matchers, data tests, property tests, lifecycle, isolation, and project conventions.
- [mockk-fakes.md](references/mockk-fakes.md): fakes vs mocks, MockK syntax, suspend mocks, captures, relaxed mocks, and interaction rules.
- [coroutine-testing.md](references/coroutine-testing.md): `runTest`, dispatchers, virtual time, cancellation, Flow tests, and flaky coroutine triage.
- [test-data-patterns.md](references/test-data-patterns.md): fixtures, builders, table tests, property generators, golden samples, and edge-case matrices.
- [debugging-flaky-tests.md](references/debugging-flaky-tests.md): failed-test diagnosis, flake triage, concurrency/time/random/global-state failure modes.
- [source-notes.md](references/source-notes.md): base skill audit, source synthesis, exclusions, and versioning policy.
