# AGP Versions and Migration

## Table of contents

1. Compatibility checks
2. Upgrade workflow
3. Kotlin DSL migration
4. Namespace and DSL modernization
5. Deprecation handling
6. Rollback and validation

## 1. Compatibility checks

Before changing AGP, check compatibility among:

- Android Gradle Plugin version.
- Gradle wrapper version.
- JDK used to run Gradle.
- Kotlin Gradle plugin / Kotlin Android plugin version.
- Android Studio version if IDE sync is involved.
- Compile SDK and installed SDK packages.

Rules:

- Do not upgrade AGP, Gradle, Kotlin, and JDK blindly in one edit.
- If compatibility requires multiple upgrades, stage them and validate after each stage.
- Read official AGP release notes for required Gradle/JDK changes and breaking DSL/API changes.
- Use the AGP Upgrade Assistant when the project is opened in Android Studio and the migration is non-trivial.

## 2. Upgrade workflow

Recommended sequence:

1. Commit or otherwise preserve a known-good state.
2. Run current baseline:

```bash
./gradlew help
./gradlew :app:assembleDebug
./gradlew :app:testDebugUnitTest
./gradlew :app:lintDebug
```

3. Upgrade Gradle wrapper if required by the target AGP.
4. Upgrade AGP version in the catalog/root plugin declaration.
5. Upgrade Kotlin plugin only if compatibility requires it or the project wants it.
6. Run `./gradlew help --stacktrace`.
7. Fix configuration/deprecation errors.
8. Run assemble, unit tests, lint, and release/minified tasks as relevant.
9. Review generated artifacts and release notes for behavior changes.

## 3. Kotlin DSL migration

Use `gradle-dev` for generic Groovy-to-Kotlin DSL migration. Android-specific conversions include:

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 23
        targetSdk = 36
    }
}
```

Rules:

- Preserve values and behavior during the migration.
- Convert one module at a time and run `./gradlew help` after each module.
- Replace Groovy list/map/closure syntax with Kotlin function calls and assignments.
- Use typed APIs for `android`, `androidComponents`, `lint`, `packaging`, and test options.

## 4. Namespace and DSL modernization

Modern AGP projects should set `namespace` explicitly in each Android module.

Rules:

- Do not infer namespace from manifest package in new code.
- Avoid bulk scripts that guess namespaces for many modules without review.
- Libraries should not define `applicationId`.
- Move repeated Android defaults into convention plugins when many modules share them.

## 5. Deprecation handling

When AGP emits deprecations:

1. Identify whether the deprecation is Gradle-level, AGP-level, Kotlin plugin-level, or third-party plugin-level.
2. Find the owning build file or convention plugin.
3. Replace the API with the supported modern DSL/API.
4. Run with warning mode if needed:

```bash
./gradlew help --warning-mode all
```

Rules:

- Do not suppress warnings without an owner and removal plan.
- Prefer `androidComponents` for variant-aware logic.
- Replace legacy transform/variant APIs when the plugin supports the Android Components API.

## 6. Rollback and validation

Validation ladder:

```bash
./gradlew help --stacktrace
./gradlew :app:assembleDebug --stacktrace
./gradlew :app:testDebugUnitTest --stacktrace
./gradlew :app:lintDebug --stacktrace
./gradlew :app:assembleRelease --stacktrace
```

For libraries:

```bash
./gradlew :library:assembleDebug
./gradlew :library:testDebugUnitTest
./gradlew :library:lintDebug
```

Rollback if:

- Compatibility requires wider migration than planned.
- Release builds or R8 fail in ways unrelated to the intended upgrade.
- IDE sync requires Android Studio upgrades that are out of scope.
