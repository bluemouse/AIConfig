# Kotlin Gradle Plugin for JVM Builds

## Table of contents

1. Apply Kotlin JVM plugin
2. Source layout
3. Toolchains and JVM target alignment
4. Compiler options
5. Kotlin incremental compilation and daemon
6. Annotation processing boundaries
7. Diagnostics

## 1. Apply Kotlin JVM plugin

Minimal Kotlin/JVM project:

```kotlin
plugins {
    alias(libs.plugins.kotlin.jvm)
}

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(17)
}
```

Without a version catalog:

```kotlin
plugins {
    kotlin("jvm") version "<kotlin-version>"
}
```

Rules:

- Keep Kotlin Gradle plugin, Kotlin compiler, and Kotlin stdlib aligned unless the project explicitly supports a split.
- Check Kotlin Gradle plugin compatibility with the Gradle version before upgrading either side.
- Do not add Android, Kotlin Multiplatform, Kotlin/JS, or Kotlin/Native plugin guidance here; use companion/platform skills.

## 2. Source layout

Default JVM layout:

```text
src/main/kotlin
src/main/java
src/test/kotlin
src/test/java
```

Rules:

- Do not put `.java` files under `src/*/kotlin`; they are not compiled by the Java compiler there.
- Keep packages aligned with directory names.
- Use custom source sets only when the module has a real additional test/runtime boundary.

## 3. Toolchains and JVM target alignment

Prefer toolchains:

```kotlin
kotlin {
    jvmToolchain(17)
}
```

or through Java:

```kotlin
java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(17))
}
```

Rules:

- Toolchains select JDKs for compilation/tests and help cache correctness across machines.
- Align Kotlin `jvmTarget` and Java `targetCompatibility` when explicitly set.
- If target mismatch errors occur, inspect `compileKotlin`, `compileJava`, `compileTestKotlin`, and `compileTestJava` tasks separately.
- The JDK running Gradle may differ from the toolchain used for compilation.

## 4. Compiler options

Prefer the modern `compilerOptions` DSL at extension or target/task level:

```kotlin
kotlin {
    compilerOptions {
        allWarningsAsErrors.set(true)
        freeCompilerArgs.add("-Xjsr305=strict")
    }
}
```

Use explicit API mode for libraries when public API discipline matters:

```kotlin
kotlin {
    explicitApi()
}
```

Rules:

- Set language/API versions only when the project needs a specific compatibility policy.
- Use `optIn.add("...")` or `freeCompilerArgs.add("-opt-in=...")` consistently according to the Kotlin plugin version in use.
- Do not copy obsolete `kotlinOptions {}` snippets into projects using a newer `compilerOptions` convention unless the project already uses that API.
- Treat `allWarningsAsErrors` as a team policy; it can break builds after compiler upgrades.

## 5. Kotlin incremental compilation and daemon

Kotlin Gradle builds normally use incremental compilation and the Kotlin daemon.

Guidelines:

- Do not disable incremental compilation to fix ordinary errors.
- When diagnosing stale or daemon issues, collect the exact Kotlin plugin version and Gradle/JDK versions.
- Use `--rerun-tasks` to verify stale-output suspicions without permanently adding `clean` to CI.
- Reserve `./gradlew clean` for confirming stale generated outputs or build cache issues, not as a routine build step.

## 6. Annotation processing boundaries

For JVM builds:

- Prefer KSP when the processor/library supports it.
- Use kapt only when needed for Java annotation processors.
- Keep processor dependencies in processor configurations, not `implementation`.
- Annotation processors often affect incremental compilation and build cache behavior; measure before and after large changes.

Avoid Android-specific processor advice here. Use `gradle-android-dev` for Android annotation processing, resource generation, and AGP variant behavior.

## 7. Diagnostics

Useful commands:

```bash
./gradlew :module:compileKotlin --stacktrace
./gradlew :module:compileKotlin --info
./gradlew :module:dependencies --configuration compileClasspath
./gradlew :module:dependencyInsight --dependency kotlin-stdlib --configuration runtimeClasspath
```

Common fixes:

- Plugin version mismatch: align catalog/plugin versions and check compatibility.
- JVM target mismatch: configure toolchain or explicit target compatibility consistently.
- Missing stdlib: apply Kotlin JVM plugin correctly or declare the dependency if using a custom setup.
- Generated sources missing: ensure generator task outputs are registered as source directories and wired through providers/builtBy.
- Java/Kotlin mixed sources: keep Java files under Java source dirs and verify compile task dependencies.
