# Kotlin Tooling

Use this reference for command-line compiler, project layout, compiler options, formatting, static analysis, documentation, and dependency hygiene.

For Gradle build engineering — plugin wiring, version catalogs, task configuration, CI, build cache, and configuration cache — use [gradle-dev](../../gradle-dev/SKILL.md). For Kotlin Gradle plugin specifics, see [gradle-dev/references/kotlin-gradle.md](../../gradle-dev/references/kotlin-gradle.md).

## Table of contents

1. Toolchain baseline
2. Project layout
3. Command-line compiler
4. Compiler options
5. Formatting and static analysis
6. Documentation
7. Dependency hygiene
8. Local check script

## 1. Toolchain baseline

For plain Kotlin programs:

- Prefer the Gradle wrapper (`./gradlew`) committed with the project when a Gradle build exists.
- Use a current JDK supported by the project; configure a Java toolchain rather than relying on the Gradle daemon JDK.
- Keep Kotlin Gradle plugin, Kotlin stdlib, and compiler plugin versions aligned unless the project has an explicit compatibility reason.
- Do not add Android, KMP, JS, Native, Compose, or server plugins in this skill.

## 2. Project layout

Plain Kotlin/JVM Gradle layout:

```text
project/
  settings.gradle.kts
  build.gradle.kts
  src/main/kotlin/com/example/.../*.kt
  src/test/kotlin/com/example/.../*Test.kt
```

Rules:

- Use package-shaped directories under `src/main/kotlin` and `src/test/kotlin`.
- Put multiple closely related top-level declarations in one file when the file remains readable.
- Name a file after its single public class/interface/object when there is one; otherwise use a name that describes the declarations, not `Util.kt`.
- Keep test packages aligned with production packages unless testing through public APIs only.

For Gradle Kotlin/JVM plugin setup, source sets, toolchains, and compiler options in build files, use [gradle-dev](../../gradle-dev/SKILL.md) and [kotlin-gradle.md](../../gradle-dev/references/kotlin-gradle.md).

## 3. Command-line compiler

Standalone file:

```bash
kotlinc hello.kt -include-runtime -d hello.jar
java -jar hello.jar
```

Library jar without runtime:

```bash
kotlinc src/main/kotlin/*.kt -d library.jar
kotlin -classpath library.jar com.example.MainKt
```

Use command-line compilation for small reproductions, examples, and compiler-error isolation. For real projects, prefer Gradle so dependencies, source sets, and compiler options are accurate.

## 4. Compiler options

Useful options/concepts (configure in Gradle via [gradle-dev](../../gradle-dev/SKILL.md)):

- `allWarningsAsErrors`: enforce warning-free builds in CI when codebase is ready.
- `explicitApi()`: require explicit visibility and return types for public library APIs.
- `jvmToolchain(n)`: use a consistent JDK for compile/test tasks.
- `languageVersion` and `apiVersion`: pin language/API compatibility when supporting older consumers.
- `-Xjsr305=strict`: make Java nullability annotations stricter at Kotlin boundaries when useful.
- Progressive mode: consider only with deliberate migration/testing.

Avoid copying experimental `-X` flags without confirming project version and need.

## 5. Formatting and static analysis

Common tools:

- Official Kotlin style in IntelliJ IDEA or compatible editor.
- `ktlint` for formatting/style enforcement.
- `detekt` for static analysis and maintainability checks.

Typical Gradle tasks if configured:

```bash
./gradlew ktlintCheck
./gradlew ktlintFormat
./gradlew detekt
./gradlew check
```

Rules:

- Format before review to avoid style noise.
- Treat static-analysis suppressions as code comments: narrow scope, explain why, and remove when obsolete.
- Do not fight official style with custom alignment or tabs.

## 6. Documentation

KDoc:

```kotlin
/**
 * Parses a TCP port from [raw].
 *
 * @return a valid port in 1..65535, or null when [raw] is not a valid port.
 */
fun parsePort(raw: String): Int? = raw.toIntOrNull()?.takeIf { it in 1..65535 }
```

Rules:

- Document public APIs whose contract is not obvious from the signature.
- Document nullability, failure behavior, threading/coroutine expectations, units, and ownership/mutability.
- Use Dokka for generated API docs when maintaining a library.

## 7. Dependency hygiene

- Prefer stdlib first. Add dependencies only when they reduce real complexity.
- Keep dependencies out of core domain code when simple data classes/functions suffice.
- Pin plugin and dependency versions through Gradle convention or catalogs — use [gradle-dev](../../gradle-dev/SKILL.md) for catalog and repository policy.
- Avoid mixing multiple test assertion/mocking styles in a small module — use [kotlin-testing](../../kotlin-testing/SKILL.md) for test-library choice.
- For examples, show minimal dependencies and note optional libraries separately.

## 8. Local check script

The bundled helper can run likely verification commands:

```bash
scripts/kotlin_project_check.sh --dry-run
scripts/kotlin_project_check.sh --quick
scripts/kotlin_project_check.sh --full
```

Behavior:

- Uses `./gradlew` when present, otherwise `gradle` if available.
- Default mode is `--quick` (runs compile/test/check when available).
- Inspects available task names when possible.
- Quick mode prioritizes compile/test/check tasks.
- Full mode includes clean/check plus configured lint/static-analysis tasks.
- Without Gradle, tries `kotlinc` for simple `.kt` files.

Do not use this as a replacement for project-specific CI; use it as a safe local first pass.
