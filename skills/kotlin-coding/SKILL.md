---
name: kotlin-coding
description: 'Write, review, refactor, debug, and test plain Kotlin/JVM code: language idioms, sealed hierarchies and exhaustive when, null safety, stdlib APIs, coroutines, kotlinc, and kotlin.test/JUnit/Kotest/MockK or flaky tests — even when the user says "Kotlin help" or "add tests". Excludes Gradle build files/caches/CI (gradle-dev), Android Gradle Plugin (gradle-android-dev), and Android/Compose/KMP/Ktor platforms.'
---

# Kotlin Coding

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Write, review, debug, and test plain Kotlin/JVM code: language semantics, standard-library APIs, idioms, coroutines-as-language, `kotlinc`, compiler/runtime debugging, test design, and maintainability. Read bundled references on demand — do not load all reference files unless the task requires them.

## Scope and Boundaries

Covers plain Kotlin/JVM programming and unit/module tests (`kotlinc`, stdlib, language-level coroutines, code review, refactoring, flaky-test triage). Excludes KMP, Kotlin/Native, Kotlin/JS/Web, Ktor, and server/framework architecture; when platform code is supplied, help with generic Kotlin language/API correctness only and defer build or platform wiring:

- Gradle build files, version catalogs, task wiring, CI, or build/configuration cache — [gradle-dev](../gradle-dev/SKILL.md)
- Android Gradle Plugin, variants, lint, R8, sync, or Android test **task** wiring — [gradle-android-dev](../gradle-android-dev/SKILL.md)
- Android app architecture, Jetpack Compose, CameraX/Media3, SDK code, and Android instrumentation/UI tests — [android-dev](../android-dev/SKILL.md)

## Testing

Test work is in scope. Non-obvious rules, stated once; framework mechanics live in the two test references:

- Test suspend functions with `runTest`, never production `runBlocking`. `runTest` runs on virtual time: `delay` skips instead of sleeping, so mixing it with `Thread.sleep` or wall-clock assertions hangs or flakes.
- Replace `Dispatchers.Main` in code under test with `Dispatchers.setMain` in setup and `Dispatchers.resetMain` in teardown; inject dispatchers/scopes instead of hard-coding `Dispatchers.IO`/`Default`.
- Drive time explicitly with `advanceTimeBy`, `runCurrent`, or `advanceUntilIdle`, and assert state before and after advancing. Cancel Flow collectors and launched jobs that do not complete naturally (e.g. `take(n)`, `job.cancel()`).
- Keep tests deterministic: no `Thread.sleep`, unseeded randomness, shared mutable globals (top-level `object` state, companion fields), order dependence, or fixed temp paths.
- Choose the framework deliberately: `kotlin.test` for light stdlib-only projects, JUnit 5 via Gradle's `useJUnitPlatform` for the standard case, Kotest for BDD-style/property-heavy suites.
- Property and data-driven tests: keep generators seeded and enumerable, keep one assertion theme per test, and parameterize with `@ParameterizedTest` or Kotest's `forAll`.
- MockK essentials: use `coEvery`/`coVerify` for suspend functions (never `every`), `relaxed = true` only for value stubs, prefer hand-written fakes over mocks for stateful collaborators, and clear shared mocks between tests.
- JUnit lifecycle: `@BeforeEach`/`@AfterEach` must be instance methods — test-class instances are recreated per test by default, so instance fields reset but companion state does not.
- On failure or flake, triage per [debugging-flaky-tests.md](references/debugging-flaky-tests.md): reproduce with the single test, isolate order/parallelism/shared state, fix the root cause, and add a regression test — never a blind retry.
- For `runTest` patterns, dispatcher injection, Flow tests, cancellation, and coroutine flake causes, read [coroutine-testing.md](references/coroutine-testing.md).

## Verification

Prefer the strongest available project command: `./gradlew compileKotlin`, then `./gradlew check` (tests plus configured ktlint/detekt). Re-run a single failing test with `./gradlew test --tests "com.example.UserServiceTest"`. For standalone files:

```bash
kotlinc file.kt -include-runtime -d app.jar && java -jar app.jar
```

`scripts/kotlin_project_check.sh` discovers and runs likely compile/test/lint checks when a local project exists (`--dry-run`, `--quick`, `--full`).

## Reference routing

| Task | Read |
|------|------|
| Extension static resolution, sealed `when` exhaustiveness | [patterns.md](references/patterns.md) |
| Toolchain rules, `kotlinc` repros, dependency hygiene, check script | [tooling.md](references/tooling.md) |
| Compiler/runtime/performance debugging | [debugging.md](references/debugging.md) |
| Non-obvious null-safety, coroutine, collection, and validation rules | [best-practices.md](references/best-practices.md) |
| `runTest`, virtual time, dispatchers, Flow tests, coroutine flakes | [coroutine-testing.md](references/coroutine-testing.md) |
| Failed-test diagnosis, flake triage, stabilization checklist | [debugging-flaky-tests.md](references/debugging-flaky-tests.md) |
