# Android Build Model

## Table of contents

1. Module types and plugins
2. Settings and root build files
3. Android DSL essentials
4. Source layout
5. App vs library boundaries
6. Generated sources and resources

## 1. Module types and plugins

Common Android plugins:

```kotlin
plugins {
    id("com.android.application")
    alias(libs.plugins.kotlin.android)
}
```

```kotlin
plugins {
    id("com.android.library")
    alias(libs.plugins.kotlin.android)
}
```

Rules:

- Use `com.android.application` only for installable app modules that produce APK/AAB artifacts.
- Use `com.android.library` for reusable Android libraries that produce AARs.
- Use plain JVM/Kotlin modules for logic that does not need Android SDK/resources; this improves build speed and test simplicity.
- Use `com.android.test` only for dedicated test APK modules.

## 2. Settings and root build files

Use `gradle-dev` for repository/plugin/version-catalog policy. Android-specific root setup usually centralizes AGP and Kotlin Android plugin versions:

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.kotlin.android) apply false
}
```

Version catalog example:

```toml
[versions]
agp = "<agp-version>"
kotlin = "<kotlin-version>"

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
```

## 3. Android DSL essentials

Minimal app module:

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 23
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
}
```

Minimal library module:

```kotlin
android {
    namespace = "com.example.feature"
    compileSdk = 36

    defaultConfig {
        minSdk = 23
    }
}
```

Rules:

- `namespace` controls the package used for generated Android classes. Set it explicitly.
- `applicationId` is the runtime/package identity for app variants. It belongs in application modules.
- `compileSdk` controls which Android APIs can be compiled against.
- `minSdk` controls the minimum supported device API level.
- `targetSdk` is an app behavior compatibility contract and should be upgraded deliberately.
- Libraries generally do not set `applicationId`.

## 4. Source layout

Common module layout:

```text
app/
  build.gradle.kts
  src/main/AndroidManifest.xml
  src/main/kotlin/.../*.kt
  src/main/res/...
  src/debug/...
  src/release/...
  src/test/kotlin/...          # local JVM unit tests
  src/androidTest/kotlin/...   # device/emulator instrumentation tests
```

Rules:

- Keep generated files under `build/`, not source directories.
- Keep debug-only code/resources in `src/debug` and release-only code/resources in `src/release`.
- Keep instrumentation tests in `androidTest`; keep host JVM unit tests in `test`.
- Avoid source-set overlays that change behavior invisibly across variants; document intentional differences.

## 5. App vs library boundaries

Healthy Android builds separate concerns:

- App module owns application id, signing, release packaging, navigation composition, and top-level manifest.
- Android library modules own resources, manifests, and Android APIs for a feature or component.
- Plain JVM modules own platform-independent domain logic and run fast JVM tests.
- Build logic owns repeated AGP/Kotlin/lint/test configuration.

Avoid:

- App-to-app dependencies.
- Resource-heavy common modules used by every feature without need.
- Android SDK dependencies in pure domain modules.
- Per-module copy/paste of long `android {}` blocks when a convention plugin can own defaults.

## 6. Generated sources and resources

When registering generated sources:

- Use AGP's supported APIs when generation is variant-specific.
- Use `androidComponents { onVariants { ... } }` for modern variant-aware wiring.
- Register tasks lazily and wire outputs through providers.
- Do not write generated files into `src/main` or other checked-in source directories.
- Ensure generated outputs are variant-specific when their contents depend on variant inputs.
