# Kotlin DSL and Build Logic

## Table of contents

1. Kotlin DSL defaults
2. Plugin application patterns
3. Type-safe accessors
4. Lazy configuration and Provider API
5. Convention plugins and included build logic
6. Custom tasks
7. Plugin testing with TestKit
8. Kotlin DSL migration checks

## 1. Kotlin DSL defaults

Prefer Kotlin DSL for new Gradle examples:

```kotlin
plugins {
    `java-library`
    alias(libs.plugins.kotlin.jvm)
}

repositories {
    mavenCentral()
}
```

Rules:

- Use Kotlin strings, function calls, and assignment semantics correctly: `property.set(value)` is always safe; `property = value` works only where Gradle/Kotlin DSL supports lazy property assignment.
- Use generated type-safe accessors for extensions/configurations/tasks when available.
- Prefer `configure<ExtensionType> { ... }` or `extensions.configure<ExtensionType>("name") { ... }` over dynamic lookup.
- Do not paste Groovy DSL syntax into `.gradle.kts` files (`id 'x'`, `implementation "g:n:v"`, bare property assignment where not supported).

## 2. Plugin application patterns

Root project with plugin versions but not applied everywhere:

```kotlin
plugins {
    alias(libs.plugins.kotlin.jvm) apply false
    id("com.example.company.jvm-library") apply false
}
```

Module project:

```kotlin
plugins {
    alias(libs.plugins.kotlin.jvm)
    id("com.example.company.jvm-library")
}
```

Settings plugin management:

```kotlin
pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}
```

Rules:

- Keep plugin versions centralized in `plugins {}` or version catalogs.
- Prefer plugin aliases from `libs.versions.toml` for repeated third-party plugins.
- Avoid legacy `buildscript { dependencies { classpath(...) } }` unless the project cannot use the plugins DSL.
- Apply plugins only to projects that need them.

## 3. Type-safe accessors

Gradle generates accessors after plugins create extensions/configurations. Examples:

```kotlin
tasks.test {
    useJUnitPlatform()
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(17))
}
```

If an accessor is unavailable:

- Check that the relevant plugin is applied before using the accessor.
- Use `extensions.configure<TheExtension> {}` or `tasks.named<TheTask>("taskName") {}`.
- Avoid `extensions.getByName("...") as ...` unless no typed API exists.

## 4. Lazy configuration and Provider API

Use lazy task APIs:

```kotlin
val generated = tasks.register<GenerateReport>("generateReport") {
    outputFile.set(layout.buildDirectory.file("reports/generated.txt"))
}

tasks.named("check") {
    dependsOn(generated)
}
```

Avoid eager APIs:

```kotlin
// Avoid in new build logic
tasks.create("generateReport")
tasks.getByName("check")
tasks.withType<Test> { }
tasks.matching { }.all { }
```

Prefer:

```kotlin
tasks.register("generateReport")
tasks.named("check")
tasks.withType<Test>().configureEach { }
```

Provider rules:

- Chain providers with `map`, `flatMap`, and `zip` instead of calling `.get()` during configuration.
- Use `layout.projectDirectory`, `layout.buildDirectory`, `providers.gradleProperty`, `providers.environmentVariable`, and `providers.fileContents`.
- Do not read files, execute processes, or resolve configurations during configuration unless explicitly modeled as providers/value sources.

## 5. Convention plugins and included build logic

Use convention plugins when several modules share the same setup.

Example structure:

```text
settings.gradle.kts
build-logic/
  settings.gradle.kts
  build.gradle.kts
  src/main/kotlin/company.kotlin-library-conventions.gradle.kts
lib-a/build.gradle.kts
lib-b/build.gradle.kts
```

Root `settings.gradle.kts`:

```kotlin
pluginManagement {
    includeBuild("build-logic")
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}
```

Precompiled convention plugin:

```kotlin
// build-logic/src/main/kotlin/company.kotlin-library-conventions.gradle.kts
plugins {
    `java-library`
    alias(libs.plugins.kotlin.jvm)
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(17))
}
```

Module:

```kotlin
plugins {
    id("company.kotlin-library-conventions")
}
```

Rules:

- Convention plugins should encode shared defaults, not project-specific dependencies.
- Prefer included `build-logic` for larger builds and plugin reuse.
- Use `buildSrc` for small local helpers when the whole build can tolerate rebuilds after build-logic edits.
- Do not use convention plugins to hide surprising behavior such as hidden repositories or unrelated task dependencies.

## 6. Custom tasks

Define typed task classes for non-trivial work:

```kotlin
abstract class GenerateManifest : DefaultTask() {
    @get:Input
    abstract val title: Property<String>

    @get:OutputFile
    abstract val outputFile: RegularFileProperty

    @TaskAction
    fun generate() {
        outputFile.get().asFile.writeText("title=${title.get()}\n")
    }
}
```

Register lazily:

```kotlin
tasks.register<GenerateManifest>("generateManifest") {
    title.set(providers.gradleProperty("manifestTitle").orElse("default"))
    outputFile.set(layout.buildDirectory.file("generated/manifest.properties"))
}
```

Correctness rules:

- Declare every input that affects outputs.
- Declare outputs precisely.
- Avoid reading `project` mutable state inside `@TaskAction`; capture values in task properties during configuration.
- Use `@PathSensitive` for file inputs when path sensitivity matters.
- Use Worker API for parallel/isolated expensive work.
- Add `@CacheableTask` only after inputs/outputs are complete and deterministic.

## 7. Plugin testing with TestKit

When creating binary Gradle plugins, test them with TestKit:

- Functional tests create a temporary project.
- Run Gradle with `GradleRunner`.
- Assert task outcomes and generated files.
- Test supported Gradle versions when compatibility matters.
- Include negative tests for invalid configuration.

Use TestKit for plugin behavior. Use normal unit tests for pure helper functions extracted from plugin code.

## 8. Kotlin DSL migration checks

When converting Groovy DSL to Kotlin DSL:

1. Convert one file/module at a time.
2. Keep plugin and dependency versions unchanged.
3. Replace Groovy strings/closures with Kotlin function calls/lambdas.
4. Use type-safe accessors only after applying the plugin that creates them.
5. Run `./gradlew help` after each module conversion.
6. Run the module's relevant compile/test task, then `./gradlew check`.

Common fixes:

- `id 'x' version '1.0'` -> `id("x") version "1.0"`.
- `implementation "g:n:v"` -> `implementation("g:n:v")`.
- `sourceCompatibility = JavaVersion.VERSION_17` stays similar, but toolchains are preferred.
- Dynamic `ext` properties should become typed Gradle properties, version catalog aliases, or convention plugin constants.
