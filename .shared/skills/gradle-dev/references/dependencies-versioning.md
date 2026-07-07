# Dependencies and Versioning

## Table of contents

1. Repository policy
2. Configurations and dependency scopes
3. Version catalogs
4. Platforms, BOMs, and constraints
5. Dependency diagnostics
6. Locking and verification
7. Dependency hygiene checklist

## 1. Repository policy

Prefer centralized repositories in settings:

```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
    }
}
```

Rules:

- Add a repository only when a dependency cannot be resolved from existing approved repositories.
- Use repository content filters for special repositories when possible.
- Avoid `mavenLocal()` in shared build logic unless the workflow explicitly depends on locally published artifacts.
- Keep credentials out of committed files. Use Gradle credentials/providers and CI secrets.
- Plugin repositories belong in `pluginManagement`, dependency repositories in `dependencyResolutionManagement` or module repositories for legacy builds.

## 2. Configurations and dependency scopes

Common JVM scopes:

```kotlin
dependencies {
    api("group:public-api-dependency:version")              // java-library only; leaks to consumers
    implementation("group:internal-dependency:version")     // implementation detail
    compileOnly("group:compile-only:version")               // needed to compile, not packaged/runtime
    runtimeOnly("group:runtime-only:version")               // runtime only
    testImplementation("group:test-lib:version")
    testRuntimeOnly("group:test-runtime:version")
}
```

Rules:

- Use `api` only when types appear in the published public API.
- Use `implementation` for normal library internals.
- Do not use deprecated `compile` or `testCompile` configurations.
- Do not put production dependencies in test configurations to make compilation pass; fix source-set boundaries instead.
- Prefer project dependencies for internal modules: `implementation(project(":core"))`.

## 3. Version catalogs

Use `gradle/libs.versions.toml` for shared versions:

```toml
[versions]
kotlin = "2.4.0"
junit = "5.11.4"

[libraries]
junit-bom = { module = "org.junit:junit-bom", version.ref = "junit" }
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
```

Build file:

```kotlin
plugins {
    alias(libs.plugins.kotlin.jvm)
}

dependencies {
    testImplementation(platform(libs.junit.bom))
    testImplementation(libs.junit.jupiter)
}
```

Rules:

- Prefer existing catalog aliases and naming conventions before adding new aliases.
- Keep aliases stable and descriptive; avoid encoding versions in alias names.
- Use bundles sparingly for dependencies that are always used together.
- For included build logic or `buildSrc`, import the main catalog explicitly if needed; it is not automatically inherited by `buildSrc`.

## 4. Platforms, BOMs, and constraints

Use platforms/BOMs to align families of dependencies:

```kotlin
dependencies {
    implementation(platform("org.jetbrains.kotlin:kotlin-bom:<version>"))
    testImplementation(platform("org.junit:junit-bom:<version>"))
}
```

Use constraints for policy:

```kotlin
dependencies {
    constraints {
        implementation("group:name:version") {
            because("aligns with supported runtime and avoids known bug")
        }
    }
}
```

Rules:

- Prefer a published BOM/platform for libraries designed to be aligned together.
- Use constraints to document required minimums, not to paper over unknown conflicts.
- Avoid `force` and broad resolution rules unless you understand every affected configuration.
- Use capabilities or excludes precisely when two artifacts provide the same classes.

## 5. Dependency diagnostics

List dependency graphs:

```bash
./gradlew :module:dependencies --configuration runtimeClasspath
./gradlew :module:dependencies --configuration testRuntimeClasspath
```

Find why a dependency/version is selected:

```bash
./gradlew :module:dependencyInsight --dependency kotlin-stdlib --configuration runtimeClasspath
./gradlew :module:dependencyInsight --dependency junit --configuration testRuntimeClasspath
```

Triage steps:

1. Identify the failing configuration from the error (`compileClasspath`, `runtimeClasspath`, `testRuntimeClasspath`, custom configuration).
2. Run `dependencyInsight` for the module coordinate or class owner.
3. Check repository availability, metadata, version constraints, platforms, and rejected versions.
4. Fix the narrowest source: version catalog, platform, direct dependency, exclude, capability selection, or repository filter.
5. Re-run the exact failing task.

## 6. Locking and verification

Dependency locking makes resolved versions reproducible:

```kotlin
dependencyLocking {
    lockAllConfigurations()
}
```

Verification validates artifacts against expected checksums/signatures:

```bash
./gradlew --write-verification-metadata sha256 help
```

Rules:

- Use locking for applications, reproducible CI, and dependency-heavy builds that should not drift.
- Update locks intentionally, review diffs, and include the reason in code review.
- Use dependency verification for supply-chain-sensitive builds.
- Do not disable verification globally to get a build passing; fix metadata or repository provenance.

## 7. Dependency hygiene checklist

- No dynamic versions (`+`, `latest.release`) in committed builds unless there is a controlled dependency-update task.
- No duplicate aliases for the same coordinate unless different variants are intentional.
- No hidden repositories in subprojects.
- No unnecessary direct dependencies where transitive dependencies should remain implementation details.
- No casual excludes at the root; use the narrowest dependency declaration.
- Compatibility matrices checked before major Gradle, Kotlin, Java, or plugin upgrades.
- Dependency changes validated by the smallest affected task and then `check`.
