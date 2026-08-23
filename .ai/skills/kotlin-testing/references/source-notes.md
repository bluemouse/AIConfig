# Source Notes and Audit Decisions

This skill is based on the requested `affaan-m/ECC/skills/kotlin-testing` skill and refined into a plain Kotlin testing skill.

## Base skill audit

Retained and expanded:

- TDD red/green/refactor workflow.
- Kotest spec styles, matchers, data-driven tests, and property-based tests.
- MockK usage including coroutine mocks and argument capture.
- Coroutine testing with `runTest`, test dispatchers, and virtual time.
- Kover coverage commands and verification gates.
- Gradle test commands and CI-style validation.

Corrected or scoped down:

- Removed Ktor/backend-specific `testApplication` material because this skill must not cover backend or framework-specific testing.
- Avoided Android, KMP, Kotlin/Native, Kotlin/JS/Web, UI, browser, device, and deployment testing.
- Replaced hard-coded dependency versions with placeholders unless version freshness is explicitly checked.
- Reframed “do not mix testing frameworks” into a more precise convention: use one dominant assertion/style per module/test class, while allowing a runner, assertion library, property library, and mocking library to coexist intentionally.
- Prefer fakes over mocks for simple dependencies and use MockK only when interaction/failure injection matters.
- Added failure/flakiness triage, fixture design, property generator constraints, and Kotlin-specific pitfalls.

## Kotlin-coding audit alignment

This testing skill supersedes test-design content in [kotlin-coding/references/testing-debugging.md](../../kotlin-coding/references/testing-debugging.md). It delegates production-language design questions to [kotlin-coding](../../kotlin-coding/SKILL.md) and aligns with its rules:

- Prefer `val`, immutable public APIs, and explicit domain types.
- Avoid unsafe `!!`; test nullability and platform-type boundaries.
- Use sealed hierarchies/enums/value objects for explicit states and exhaustive behavior.
- Use structured concurrency; avoid `GlobalScope`, production `runBlocking`, swallowed cancellation, and unowned scopes.
- Use Gradle wrapper, Kotlin/JVM source layout, `kotlin("test")`, JUnit Platform, ktlint/detekt/Kover when configured.

## Documentation sources consulted

- Base skill: `https://github.com/affaan-m/ECC/tree/main/skills/kotlin-testing` and raw `SKILL.md`.
- Kotlin docs: Gradle configuration, JVM testing with JUnit, and `kotlin.test` API.
- kotlinx.coroutines test API documentation for `runTest`, virtual time, `Dispatchers.setMain`, and test dispatchers.
- Kotest documentation for setup, spec styles, assertions, and property testing.
- MockK documentation for Kotlin mocking syntax and coroutine stubbing/verification.
- Kover Gradle plugin documentation for JVM coverage reports and verification tasks.

## Gradle integration update

Detailed Gradle build engineering, task wiring, dependency/version catalog edits, CI, and cache behavior are delegated to the companion [gradle-dev](../../gradle-dev/SKILL.md) skill to avoid duplication.
