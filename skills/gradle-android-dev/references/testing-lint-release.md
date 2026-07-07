# Android Testing, Lint, and Release Builds

## Table of contents

1. Unit test tasks
2. Instrumentation test tasks
3. Lint
4. R8 and keep rules
5. Signing and release packaging
6. Validation ladder

## 1. Unit test tasks

Local JVM unit tests run on the host:

```bash
./gradlew :app:testDebugUnitTest
./gradlew :app:testReleaseUnitTest
```

Rules:

- Put local unit tests in `src/test/kotlin` or `src/test/java`.
- Use `testImplementation` dependencies.
- For pure Kotlin test design and framework patterns, use [kotlin-testing](../../kotlin-testing/SKILL.md).
- For Gradle test task wiring, use [gradle-dev](../../gradle-dev/SKILL.md); this skill only maps Android variant task names and source sets.

## 2. Instrumentation test tasks

Device/emulator tests live in `src/androidTest` and use `androidTestImplementation`.

Common command:

```bash
./gradlew :app:connectedDebugAndroidTest
```

Rules:

- Do not run connected tests unless a device/emulator is available.
- Keep instrumentation tests focused on Android framework/device behavior.
- Prefer local JVM tests for pure Kotlin/domain behavior.
- In CI, use managed devices or explicit emulator setup when the project supports it; otherwise keep connected tests in a separate job.

## 3. Lint

Common commands:

```bash
./gradlew :app:lintDebug
./gradlew :app:lintRelease
./gradlew lint
```

Rules:

- Treat lint findings as code/build quality feedback.
- Do not blanket-disable lint checks to pass CI.
- Add suppressions narrowly with rationale.
- Run lint for release-relevant variants before publishing.
- Keep baseline files reviewed; shrinking a baseline is a quality improvement.

## 4. R8 and keep rules

Release builds often run R8/minification:

```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

Rules:

- Add keep rules narrowly for reflection, serialization, JNI, service loaders, or external API contracts.
- Prefer library-provided consumer rules for Android libraries.
- Validate release builds after dependency upgrades.
- Do not set `isMinifyEnabled = false` as the final fix for an R8 error unless product policy allows it.
- Use R8 diagnostics/mapping files when analyzing removed/renamed code.

## 5. Signing and release packaging

Rules:

- Do not commit keystore files, passwords, or signing secrets.
- Use `local.properties`, user-local Gradle properties, environment providers, or CI secrets.
- Keep debug signing separate from release signing.
- Validate release artifact creation after signing changes:

```bash
./gradlew :app:assembleRelease
./gradlew :app:bundleRelease
```

## 6. Validation ladder

For app modules:

```bash
./gradlew :app:assembleDebug
./gradlew :app:testDebugUnitTest
./gradlew :app:lintDebug
./gradlew :app:assembleRelease
./gradlew :app:bundleRelease
```

For library modules:

```bash
./gradlew :library:assembleDebug
./gradlew :library:testDebugUnitTest
./gradlew :library:lintDebug
./gradlew :library:assembleRelease
```

For device tests when available:

```bash
./gradlew :app:connectedDebugAndroidTest
```

Choose the smallest command that proves the change first; run release tasks when changing dependencies, manifests, resources, R8 rules, packaging, or signing.
