# Kotlin Testing Tooling

Use this reference for Kotlin/JVM test-tool dependencies, test commands, coverage tasks, and report conventions.

Use the companion [gradle-dev](../../gradle-dev/SKILL.md) skill for general Gradle build engineering: wrapper, settings/build files, plugin management, version catalogs, dependency resolution, `tasks.test {}` lifecycle wiring, JVM test suites, CI/cache behavior, and custom Gradle tasks/plugins.

## Table of contents

1. Boundary with gradle-dev
2. Baseline test dependencies
3. Test command patterns
4. Kover coverage
5. Reports and CI handoff
6. Version policy
7. Command helper script

## 1. Boundary with gradle-dev

This skill owns:

- Choosing `kotlin.test`, JUnit Platform, Kotest, MockK, coroutine-test, property/data-driven testing, and Kover coverage policy.
- Writing test source files and fixtures.
- Debugging flaky tests and assertion failures.
- Explaining deterministic test seams.

Delegate to [gradle-dev](../../gradle-dev/SKILL.md) for:

- Where to put plugin/dependency versions.
- Version catalogs and repository policy.
- `tasks.test { useJUnitPlatform() }` placement in multi-project/convention-plugin builds.
- Gradle test suites and task graph wiring.
- CI cache, Gradle daemon, build cache, configuration cache, and dependency locks.

## 2. Baseline test dependencies

Minimal Kotlin/JVM test setup when no project convention exists:

```kotlin
dependencies {
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
```

JUnit parameterized tests:

```kotlin
dependencies {
    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter-params:<junit-version>")
}
```

Kotest:

```kotlin
dependencies {
    testImplementation("io.kotest:kotest-runner-junit5:<kotest-version>")
    testImplementation("io.kotest:kotest-assertions-core:<kotest-version>")
    testImplementation("io.kotest:kotest-property:<kotest-version>")
}
```

MockK:

```kotlin
dependencies {
    testImplementation("io.mockk:mockk:<mockk-version>")
}
```

Coroutine tests:

```kotlin
dependencies {
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:<coroutines-version>")
}
```

Rules:

- Prefer the versions already declared in the project catalog or convention plugins.
- Add only the dependency needed for the chosen test style.
- Prefer fakes over mocks before adding MockK.
- Keep one dominant assertion DSL per test class or module.
- Use [gradle-dev](../../gradle-dev/SKILL.md) when these snippets need to be integrated into a complex build.

## 3. Test command patterns

Common commands:

```bash
./gradlew test
./gradlew test --tests "com.example.EmailValidatorTest"
./gradlew test --tests "com.example.EmailValidatorTest.rejects blank email"
./gradlew check
./gradlew test --info
./gradlew test --stacktrace
./gradlew test --continuous
```

Rules:

- Use the smallest test command that reproduces a failure.
- Use `--stacktrace` for task failures and `--info` for deeper Gradle/test execution diagnostics.
- Use `--continuous` only for local feedback loops.
- Use [gradle-dev](../../gradle-dev/SKILL.md) for task discovery, custom test suites, filtering policy, CI command design, or cache behavior.

## 4. Kover coverage

Kover measures Kotlin/JVM test coverage and can generate reports and verification gates.

Minimal plugin marker:

```kotlin
plugins {
    id("org.jetbrains.kotlinx.kover") version "<kover-version>"
}
```

Coverage commands:

```bash
./gradlew koverHtmlReport
./gradlew koverXmlReport
./gradlew koverVerify
./gradlew check
```

Coverage policy:

- Use coverage as a risk signal, not a substitute for assertions.
- Cover public contracts, failure paths, boundary cases, and critical pure logic.
- Exclude generated/configuration/adaptor code deliberately with comments.
- Avoid chasing 100% coverage through brittle implementation-detail tests.
- Use [gradle-dev](../../gradle-dev/SKILL.md) for multi-project Kover wiring, plugin version placement, and CI integration.

## 5. Reports and CI handoff

Useful report locations in typical Gradle JVM builds:

```text
build/reports/tests/test/index.html
build/test-results/test/
build/reports/kover/
```

CI guidance from this skill:

- Ensure test reports are published as artifacts.
- Keep flaky tests visible and owned.
- Run coverage verification where coverage gates are part of project policy.

Use [gradle-dev](../../gradle-dev/SKILL.md) for exact CI cache keys, wrapper setup, Gradle daemon policy, parallelization, and task splitting.

## 6. Version policy

- Use placeholders (`<kotest-version>`) unless the user supplies an existing catalog or asks for current exact versions.
- Before recommending exact current versions, check official release sources or the project catalog.
- Kotlin Gradle plugin, Kotlin compiler/stdlib, and test libraries should be compatible with the project's Gradle/JDK baseline.
- JUnit Platform-based tools require the test task to use JUnit Platform; use [gradle-dev](../../gradle-dev/SKILL.md) for the cleanest place to configure that across a build.

## 7. Command helper script

This skill includes `scripts/kotlin_test_check.sh` for local command discovery. Default mode is `--dry-run` (prints commands without executing). Use `--quick` to run the primary test task; `--full` adds check, Kover, and lint/static-analysis tasks when configured. Use [gradle-dev](../../gradle-dev/SKILL.md)'s helper for general Gradle project diagnosis.
